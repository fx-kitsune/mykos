#!/usr/bin/env python3
"""MyKOS installer: select an internal disk, confirm erase, and install automatically.

The default wizard creates GPT partitions, formats and mounts them, bootstraps
the OS, installs the desktop and bootloader, and unmounts its filesystems.
Explicit --target retains the advanced prepared-partition installation mode.
"""
import argparse
import fcntl
import getpass
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from contextlib import contextmanager

sys.path.insert(0, str(Path(__file__).resolve().parent))
import disk_layout
import bootstrap_tools

ROOT = Path(__file__).resolve().parents[2]
LIVE_ONLY = {'live-boot', 'live-config', 'live-config-systemd', 'calamares', 'grub-pc-bin', 'grub2-common'}


def run(argv, **kwargs):
    return subprocess.run(argv, check=True, text=True, **kwargs)


def output(argv):
    return run(argv, capture_output=True).stdout.strip()


def settings():
    return json.loads((ROOT / 'distribution/base/build.json').read_text())


def packages(mode):
    names = [line.split('#', 1)[0].strip() for line in
             (ROOT / 'distribution/packages/desktop.list.chroot').read_text().splitlines()]
    names = [name for name in names if name and name not in LIVE_ONLY]
    names += ['grub2-common', 'grub-pc-bin' if mode == 'bios' else 'grub-efi-amd64-bin']
    return list(dict.fromkeys(names))


def validate_options(args):
    target = Path(args.target)
    if not target.is_absolute() or '..' in target.parts or target.resolve() != target:
        raise ValueError('Target must be an absolute path without symlinks or .. components.')
    if not any(target.is_relative_to(Path(base)) and target != Path(base)
               for base in ['/mnt', '/media', '/run/media']):
        raise ValueError('Mount the empty target below /mnt, /media or /run/media (for example /mnt/mykos).')
    if ROOT.is_relative_to(target) or target.is_relative_to(ROOT):
        raise ValueError('The installation target must not overlap this repository.')
    validate_identity(args)
    if args.mode == 'bios' and not args.boot_disk:
        raise ValueError('BIOS installation requires an explicit --boot-disk /dev/whole-disk.')
    if args.boot_disk and not re.fullmatch(r'/dev/[A-Za-z0-9_.+/-]+', args.boot_disk):
        raise ValueError('Boot disk must be a local /dev block device.')
    return target


def validate_identity(args):
    if not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}', args.username) or args.username == 'root':
        raise ValueError('Choose a regular lowercase username, not root.')
    if not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', args.hostname):
        raise ValueError('Hostname must be a single lowercase DNS label, at most 63 characters.')


def plan(args):
    target = validate_options(args)
    cfg = settings()
    return {'target': str(target), 'mode': args.mode, 'boot_disk': args.boot_disk,
            'suite': cfg['suite'], 'architecture': cfg['architecture'],
            'mirror': cfg['mirror'], 'security_mirror': cfg['security_mirror'],
            'username': args.username, 'hostname': args.hostname,
            'packages': packages(args.mode),
            'steps': ['Validate empty mounted ext4 target and device identity',
                      'debootstrap minbase with Debian archive signature verification',
                      'Install Debian kernel and MyKOS desktop dependencies',
                      'Deploy MyKOS session, shell and branding from this checkout',
                      'Write UUID-based fstab; create password-protected account; lock root',
                      'Generate initramfs and GRUB configuration',
                      ('Install GRUB to the selected BIOS disk boot area' if args.mode == 'bios' else
                       'Install unsigned UEFI fallback loader to an empty ESP, without NVRAM changes')],
            'formats_disks': False, 'partitions_disks': False,
            'acceptance': 'experimental; not yet accepted by a full disk-install/reboot test'}


def mount_record(path):
    data = json.loads(output(['findmnt', '--json', '--mountpoint', str(path),
                              '--output', 'TARGET,SOURCE,FSTYPE,UUID']))
    rows = data.get('filesystems', [])
    if len(rows) != 1 or rows[0].get('target') != str(path):
        raise ValueError('Expected a filesystem mounted exactly at ' + str(path))
    return rows[0]


def disk_ancestors(source):
    if not source.startswith('/dev/') or not stat.S_ISBLK(Path(source).stat().st_mode):
        raise ValueError('Target must be a direct block-device partition, not a bind/overlay mount.')
    if output(['lsblk', '--nodeps', '--noheadings', '--output', 'TYPE', source]) != 'part':
        raise ValueError('Target must be a plain disk partition; whole disks, LVM and encrypted mappings are not supported yet.')
    rows = output(['lsblk', '--inverse', '--noheadings', '--raw', '--output', 'PATH,TYPE', source])
    return {str(Path(parts[0]).resolve()) for line in rows.splitlines()
            if len(parts := line.split()) == 2 and parts[1] == 'disk'}


def validate_boot_layout(mode, disk, esp):
    if mode == 'uefi':
        parttype = output(['lsblk', '--nodeps', '--noheadings', '--output', 'PARTTYPE', esp['source']]).lower()
        if parttype not in {'c12a7328-f81f-11d2-ba4b-00a0c93ec93b', '0xef'}:
            raise ValueError('The FAT partition must be marked as an EFI System Partition.')
    elif output(['lsblk', '--nodeps', '--noheadings', '--output', 'PTTYPE', disk]) == 'gpt':
        data = json.loads(output(['lsblk', '--json', '--output', 'PATH,PARTTYPE', disk]))
        partitions = data.get('blockdevices', [{}])[0].get('children', [])
        if not any((row.get('parttype') or '').lower() == '21686148-6449-6e6f-744e-656564454649'
                   for row in partitions):
            raise ValueError('BIOS on GPT requires a prepared BIOS boot (bios_grub) partition.')


def require_empty(directory, allowed=()):
    unexpected = [path.name for path in directory.iterdir() if path.name not in allowed]
    if unexpected:
        raise ValueError('Target is not empty; refusing to replace existing files: ' + ', '.join(unexpected[:8]))


def inspect_target(args):
    target = validate_options(args)
    if not target.is_dir():
        raise ValueError('Mount the prepared target partition before installation.')
    root = mount_record(target)
    host = mount_record(Path('/'))
    if root.get('source') == host.get('source') or root.get('uuid') == host.get('uuid') and root.get('uuid'):
        raise ValueError('Refusing to install onto the currently running root filesystem.')
    if root.get('fstype') != 'ext4' or not re.fullmatch(r'[A-Za-z0-9-]+', root.get('uuid') or ''):
        raise ValueError('This first installer requires an ext4 root partition with a UUID.')
    ancestors = disk_ancestors(root['source'])
    if len(ancestors) != 1:
        raise ValueError('Only a simple partition on one physical/virtual disk is supported; no RAID/LVM.')
    disk = next(iter(ancestors))
    if args.boot_disk and str(Path(args.boot_disk).resolve()) != disk:
        raise ValueError('--boot-disk must be the parent disk of the target root partition.')
    require_empty(target, {'lost+found', 'boot'})
    esp = None
    boot = target / 'boot'
    if boot.is_symlink():
        raise ValueError('The target boot directory must not be a symlink.')
    if boot.exists():
        require_empty(boot, {'efi'} if args.mode == 'uefi' else set())
    if args.mode == 'uefi':
        esp = mount_record(boot / 'efi')
        if esp.get('fstype') != 'vfat' or not re.fullmatch(r'[A-Za-z0-9-]+', esp.get('uuid') or ''):
            raise ValueError('UEFI requires an empty FAT32 ESP mounted at TARGET/boot/efi.')
        if disk_ancestors(esp['source']) != {disk}:
            raise ValueError('The ESP must be on the same disk as the new root partition.')
        require_empty(boot / 'efi')
    nested = json.loads(output(['findmnt', '--json', '--submounts', '--mountpoint', str(target), '--output', 'TARGET']))
    def mounted(rows):
        return [row['target'] for row in rows] + [p for row in rows for p in mounted(row.get('children', []))]
    allowed = {str(target)} | ({str(boot / 'efi')} if esp else set())
    if set(mounted(nested.get('filesystems', []))) != allowed:
        raise ValueError('Unexpected nested mounts under the installation target.')
    validate_boot_layout(args.mode, disk, esp)
    return target, root, esp, disk


@contextmanager
def target_mounts(target):
    created = []
    try:
        for name in ['dev', 'sys']:
            path = target / name
            path.mkdir(exist_ok=True)
            run(['mount', '--rbind', '/' + name, str(path)])
            created.append(path)
            run(['mount', '--make-rslave', str(path)])
        for name, fstype in [('proc', 'proc'), ('run', 'tmpfs')]:
            path = target / name
            path.mkdir(exist_ok=True)
            run(['mount', '-t', fstype, fstype, str(path)])
            created.append(path)
        yield
    finally:
        failures = []
        for path in reversed(created):
            try:
                run(['umount', '--recursive', str(path)])
            except subprocess.CalledProcessError:
                failures.append(str(path))
        if failures:
            raise RuntimeError('Could not unmount installer mounts; inspect before touching the target: ' + ', '.join(failures))


def write(target, relative, text, mode=0o644):
    path = target / relative
    if not path.resolve().is_relative_to(target):
        raise ValueError('Target path escaped through a symlink: ' + relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    path.chmod(mode)


def deploy_desktop(target):
    shutil.copytree(ROOT / 'distribution/branding/overlay', target, dirs_exist_ok=True)
    for folder in ['workspace', 'session', 'shell']:
        shutil.copytree(ROOT / 'desktop' / folder, target / 'usr/share/mykos' / folder,
                        dirs_exist_ok=True, ignore=shutil.ignore_patterns('overlay', '__pycache__', '*.pyc', 'requirements-dev.txt'))
    for folder in [target / 'usr/share/mykos', target / 'usr/share/icons/MyKOSFold']:
        for path in [folder, *folder.rglob('*')]:
            if not path.is_symlink():
                path.chmod(0o755 if path.is_dir() else 0o644)
    for command in ['mykos-session', 'mykos-shell', 'mykos-workspace']:
        write(target, 'usr/bin/' + command, (ROOT / 'desktop/integration' / command).read_text(), 0o755)
    for source, destination in [
        ('desktop/integration/mykos.desktop', 'usr/share/xsessions/mykos.desktop'),
        ('desktop/integration/mykos-workspace.desktop', 'usr/share/applications/mykos-workspace.desktop'),
        ('desktop/session/overlay/etc/sddm.conf.d/10-mykos.conf', 'etc/sddm.conf.d/10-mykos.conf'),
        ('desktop/session/overlay/usr/share/xdg-desktop-portal/mykos-portals.conf',
         'usr/share/xdg-desktop-portal/mykos-portals.conf')]:
        write(target, destination, (ROOT / source).read_text())
    release = target / 'etc/os-release'
    release.unlink(missing_ok=True)
    write(target, 'usr/lib/os-release', 'NAME="MyKOS"\nID=mykos\nID_LIKE=debian\nPRETTY_NAME="MyKOS development"\nVERSION_ID="0.1"\n')
    release.symlink_to('../usr/lib/os-release')


def read_password():
    password = getpass.getpass('Mật khẩu mới (ít nhất 12 ký tự) / Password: ')
    if len(password) < 12 or len(password) > 1024 or any(c in password for c in '\n\r\x00'):
        raise ValueError('Mật khẩu phải có 12–1024 ký tự, không có xuống dòng hoặc NUL.')
    if password != getpass.getpass('Nhập lại / Repeat password: '):
        raise ValueError('Hai mật khẩu không khớp; chưa bắt đầu ghi ổ.')
    return password


def install_system(args, password, summary, bootstrap=None):
    target, root, esp, disk = inspect_target(args)
    with (target / '.mykos-install.lock').open('x') as lock:
        os.chmod(lock.name, 0o600)
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        cfg = settings()
        print('Bootstrapping signed Debian base...', flush=True)
        run([str(bootstrap[0]) if bootstrap else 'debootstrap', '--arch=' + cfg['architecture'], '--variant=minbase',
             '--include=ca-certificates', '--force-check-gpg', '--keyring=' + str(Path(args.keyring).resolve()),
             cfg['suite'], str(target), cfg['mirror']], env=bootstrap[2] if bootstrap else None)
        areas = ' '.join(cfg['archive_areas'])
        sources = ''.join('deb ' + mirror + ' ' + suite + ' ' + areas + '\n' for mirror, suite in [
            (cfg['mirror'], cfg['suite']), (cfg['mirror'], cfg['suite'] + '-updates'),
            (cfg['security_mirror'], cfg['suite'] + '-security')])
        write(target, 'etc/apt/sources.list', sources)
        def chroot(argv, **kwargs):
            return run(['chroot', str(target), '/usr/bin/env', 'DEBIAN_FRONTEND=noninteractive', *argv], **kwargs)
        write(target, 'usr/sbin/policy-rc.d', '#!/bin/sh\nexit 101\n', 0o755)
        with target_mounts(target):
            print('Installing kernel and MyKOS Desktop...', flush=True)
            chroot(['apt-get', 'update'])
            chroot(['apt-get', 'install', '-y', *packages(args.mode)])
            deploy_desktop(target)
            write(target, 'etc/hostname', args.hostname + '\n')
            write(target, 'etc/hosts', '127.0.0.1 localhost\n127.0.1.1 ' + args.hostname + '\n::1 localhost ip6-localhost\n')
            fstab = 'UUID=' + root['uuid'] + ' / ext4 defaults 0 1\n'
            if esp:
                fstab += 'UUID=' + esp['uuid'] + ' /boot/efi vfat umask=0077 0 2\n'
            write(target, 'etc/fstab', fstab)
            write(target, 'etc/locale.gen', 'en_US.UTF-8 UTF-8\nvi_VN.UTF-8 UTF-8\n')
            chroot(['locale-gen'])
            chroot(['update-locale', 'LANG=en_US.UTF-8'])
            chroot(['useradd', '--create-home', '--shell', '/bin/bash', '--groups', 'sudo', args.username])
            chroot(['chpasswd'], input=args.username + ':' + password + '\n')
            password = None
            chroot(['passwd', '--lock', 'root'])
            chroot(['systemctl', 'enable', 'sddm.service', 'NetworkManager.service'])
            chroot(['systemctl', 'set-default', 'graphical.target'])
            write(target, 'etc/default/grub.d/60-mykos.cfg', 'GRUB_DISTRIBUTOR=MyKOS\nGRUB_DISABLE_OS_PROBER=true\n')
            chroot(['update-initramfs', '-u', '-k', 'all'])
            if args.mode == 'bios':
                chroot(['grub-install', '--target=i386-pc', '--recheck', disk])
            else:
                chroot(['grub-install', '--target=x86_64-efi', '--efi-directory=/boot/efi',
                        '--bootloader-id=MyKOS', '--no-nvram', '--removable'])
            chroot(['update-grub'])
            chroot(['apt-get', 'clean'])
            (target / 'usr/sbin/policy-rc.d').unlink()
            write(target, 'etc/machine-id', '')
            dbus_id = target / 'var/lib/dbus/machine-id'
            dbus_id.unlink(missing_ok=True)
            dbus_id.symlink_to('../../../etc/machine-id')
            resolv = target / 'etc/resolv.conf'
            resolv.unlink(missing_ok=True)
            resolv.symlink_to('../run/NetworkManager/resolv.conf')
            write(target, 'etc/mykos-install.json', json.dumps(summary, indent=2) + '\n')
    (target / '.mykos-install.lock').unlink()
    print('Đã cài xong hệ thống và bootloader.', flush=True)



def install_prepared(args):
    if os.geteuid() != 0:
        raise ValueError('Installation requires root; run plan first, then sudo install.')
    for tool in ['debootstrap', 'gpgv', 'findmnt', 'lsblk', 'mount', 'umount', 'chroot']:
        if not shutil.which(tool):
            raise ValueError('Missing host tool: ' + tool)
    if not Path(args.keyring).is_file():
        raise ValueError('A trusted Debian archive keyring is required.')
    target, root, esp, disk = inspect_target(args)
    summary = plan(args)
    summary.update(root_device=root['source'], root_uuid=root['uuid'], parent_disk=disk,
                   esp_device=esp['source'] if esp else None)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    if args.confirm_uuid != root['uuid']:
        raise ValueError('Advanced prepared-partition mode requires --confirm-uuid ' + root['uuid'])
    password = read_password()
    inspect_target(args)
    install_system(args, password, summary)


def install(args):
    if getattr(args, 'disk', None) or not args.target:
        return install_automatic(args)
    return install_prepared(args)


def protected_paths(extra=()):
    return [ROOT.resolve(), Path.cwd().resolve(), Path(sys.executable).resolve(), *map(Path, extra)]


def show_disk(disk, mode):
    info = disk_layout.describe(disk, mode)
    print('\nỔ cài MyKOS: ' + (info['model'] or 'Internal disk'), flush=True)
    print(f"  {info['disk']} — {info['size_gib']} GiB — Serial: {info['serial']}")
    print('  Toàn bộ phân vùng và dữ liệu trên ổ này sẽ bị XÓA.')
    for part in info['current_partitions']:
        print(f"  Đang có: {part['path']} — {part['size_gib']} GiB — {part['fstype'] or 'chưa có filesystem'}")
    print('  Sẽ tạo: ' + ' + '.join(info['new_layout']))
    print('  Cài MyKOS Desktop và bootloader tự động.', flush=True)
    return info


def wizard_options(args):
    if not sys.stdin.isatty():
        raise ValueError('Cần terminal tương tác để chọn và xác nhận ổ cài.')
    print('MyKOS / Cài đặt tự động\n')
    args.mode = args.mode or ('uefi' if Path('/sys/firmware/efi').exists() else 'bios')
    snapshot = disk_layout.scan(protected_paths())
    choices = snapshot['candidates']
    if not choices:
        raise ValueError('Không có ổ trong đủ điều kiện để cài. ' + '; '.join(x['path'] + ': ' + x['reason'] for x in snapshot['excluded']))
    if not args.disk:
        for index, disk in enumerate(choices, 1):
            print(f"  {index}. {(disk.get('model') or 'Ổ trong').strip()} — {int(disk['size']) / 1024**3:.1f} GiB ({disk['path']})")
        answer = input('Chọn ổ cài' + (' [1]' if len(choices) == 1 else '') + ': ').strip()
        if not answer and len(choices) == 1:
            answer = '1'
        if not answer.isdigit() or not 1 <= int(answer) <= len(choices):
            raise ValueError('Chưa chọn ổ hợp lệ; đã hủy.')
        args.disk = choices[int(answer) - 1]['path']
    disk = next((d for d in choices if d['path'] == str(Path(args.disk).resolve())), None)
    if disk is None:
        raise ValueError('Ổ chỉ định không nằm trong danh sách có thể cài an toàn.')
    args.disk_identity = disk_layout.identity(disk)
    args.username = input('Tên tài khoản [' + args.username + ']: ').strip() or args.username
    validate_identity(args)
    return args


@contextmanager
def mounted_new_system(root_device, esp_device):
    # Never use rmtree/TemporaryDirectory around a filesystem mount: if unmount
    # fails that could delete the new OS. Only remove an empty, unmounted dir.
    target = Path(tempfile.mkdtemp(prefix='mykos-install-', dir='/mnt'))
    created = []
    try:
        run(['mount', root_device, str(target)])
        created.append(target)
        if esp_device:
            (target / 'boot/efi').mkdir(parents=True)
            run(['mount', esp_device, str(target / 'boot/efi')])
            created.append(target / 'boot/efi')
        yield target
    finally:
        for path in reversed(created):
            try:
                run(['umount', str(path)])
            except BaseException as error:
                raise RuntimeError('Không tháo được mount; giữ nguyên dữ liệu tại ' + str(target)) from error
        target.rmdir()


def firmware_secure_boot(directory):
    variable = directory / 'SecureBoot-8be4df61-93ca-11d2-aa0d-00e098032b8c'
    if not variable.exists():
        # Non-Secure-Boot OVMF/older firmware has other runtime variables but no
        # SecureBoot variable. An empty/unreadable efivarfs is not that proof.
        if not list(directory.iterdir()):
            raise ValueError('Không đọc được biến firmware UEFI; chưa xóa ổ.')
        return False
    data = variable.read_bytes()
    if len(data) != 5 or data[4] not in (0, 1):
        raise ValueError('Trạng thái Secure Boot không hợp lệ; chưa xóa ổ.')
    return data[4] == 1


def check_firmware(mode):
    if mode != 'uefi' or not Path('/sys/firmware/efi').exists():
        return
    directory = Path('/sys/firmware/efi/efivars')
    created = False
    try:
        if not os.path.ismount(directory):
            directory.mkdir(exist_ok=True)
            run(['mount', '-t', 'efivarfs', '-o', 'ro', 'efivarfs', str(directory)])
            created = True
        if firmware_secure_boot(directory):
            raise ValueError('Secure Boot đang bật. MyKOS chưa có bootloader ký; chưa xóa ổ.')
    finally:
        if created:
            run(['umount', str(directory)])


def install_automatic(args):
    if os.geteuid() != 0:
        raise ValueError('Cần quyền root để cài hệ thống.')
    if not sys.stdin.isatty():
        raise ValueError('Cần terminal tương tác để xác nhận xóa ổ.')
    if os.uname().machine != 'x86_64':
        raise ValueError('Hiện hỗ trợ máy amd64/x86_64.')
    bootstrap_tools.ensure_host_tools()
    args.mode = args.mode or ('uefi' if Path('/sys/firmware/efi').exists() else 'bios')
    validate_identity(args)
    check_firmware(args.mode)
    paths = protected_paths()
    disk, _ = disk_layout.selected(args.disk, paths, getattr(args, 'disk_identity', None))
    with tempfile.TemporaryDirectory(prefix='mykos-bootstrap-') as tools:
        paths = protected_paths([tools])
        bootstrap = bootstrap_tools.prepare(tools, settings()['suite'])
        with disk_lock(disk):
            disk, _ = disk_layout.selected(args.disk, paths, disk_layout.identity(disk))
            summary = show_disk(disk, args.mode)
            print('  Tài khoản mới: ' + args.username + ' | Tên máy: ' + args.hostname)
            print('\nGõ ' + disk_layout.CONFIRMATION + ' để xóa ĐÚNG ổ trên và cài MyKOS. Enter để hủy.', flush=True)
            if input('Confirm: ').strip() != disk_layout.CONFIRMATION:
                print('Đã hủy. Chưa xóa hoặc ghi ổ đích.')
                return
            password = read_password()
            root_device, esp_device = disk_layout.prepare(disk, args.mode, paths)
            with mounted_new_system(root_device, esp_device) as target:
                args.target, args.boot_disk, args.keyring = str(target), disk['path'], str(bootstrap[1])
                root = mount_record(target)
                args.confirm_uuid = root['uuid']  # Internal check; never ask the user to copy it.
                summary.update(root_uuid=root['uuid'], root_device=root_device, esp_device=esp_device)
                install_system(args, password, summary, bootstrap)
        print('\nMYKOS_INSTALL_COMPLETE')
        print('Cài đặt hoàn tất. Bạn có thể tắt máy, tháo USB cứu hộ và khởi động MyKOS.', flush=True)


@contextmanager
def disk_lock(disk):
    directory = Path('/run/lock/mykos-installer')
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    if directory.is_symlink() or directory.stat().st_uid != 0 or directory.stat().st_mode & 0o077:
        raise ValueError('Thư mục khóa trình cài không an toàn.')
    filename = directory / (disk['maj:min'].replace(':', '-') + '.lock')
    descriptor = os.open(filename, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally:
        os.close(descriptor)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', nargs='?', default='wizard', choices=['wizard', 'plan', 'install'])
    parser.add_argument('--disk', help='Whole internal disk to erase and install automatically')
    parser.add_argument('--target', help='Advanced mode: existing mounted root partition')
    parser.add_argument('--mode', choices=['bios', 'uefi'])
    parser.add_argument('--boot-disk', help='Explicit parent disk for BIOS (for example /dev/sda); writes its boot area')
    parser.add_argument('--username', default='mykos')
    parser.add_argument('--hostname', default='mykos')
    parser.add_argument('--keyring', default='/usr/share/keyrings/debian-archive-keyring.gpg')
    parser.add_argument('--confirm-uuid', help='Exact UUID of the empty mounted root partition; required to write')
    args = parser.parse_args()
    try:
        if args.action == 'wizard' and args.target:
            parser.error('Advanced prepared --target requires explicit plan or install action')
        if args.disk and args.target:
            parser.error('Choose automatic --disk or advanced --target, not both')
        if args.action != 'plan' and os.geteuid() != 0:
            if not shutil.which('sudo') or not sys.stdin.isatty():
                raise ValueError('Chạy ./install từ terminal có quyền sudo/root.')
            os.execvp('sudo', ['sudo', '--', sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]])
        if args.action == 'wizard':
            bootstrap_tools.ensure_host_tools()
            wizard_options(args)
        if args.action == 'plan' and not args.target:
            snapshot = disk_layout.scan(protected_paths())
            args.mode = args.mode or ('uefi' if Path('/sys/firmware/efi').exists() else 'bios')
            disks = snapshot['candidates']
            if args.disk:
                disks = [d for d in disks if d['path'] == str(Path(args.disk).resolve())]
                if not disks:
                    raise ValueError('Ổ không đủ điều kiện an toàn để cài.')
            print(json.dumps({'disks': [disk_layout.describe(d, args.mode) for d in disks],
                              'excluded': snapshot['excluded']}, ensure_ascii=False, indent=2))
        elif args.action == 'plan':
            print(json.dumps(plan(args), ensure_ascii=False, indent=2))
        else:
            if args.target and not args.mode:
                parser.error('Advanced --target requires --mode')
            install(args)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print('mykos-install: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
