#!/usr/bin/env python3
"""Install MyKOS from another Linux rescue system onto prepared, mounted partitions.

Never partitions or formats disks. `plan` is read-only. `install` requires an
empty, independently mounted ext4 target, exact UUID confirmation and a password
entered interactively. BIOS writes the explicitly selected parent disk's boot
area; UEFI writes only an empty ESP, without changing firmware NVRAM.
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
from contextlib import contextmanager

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
    if not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}', args.username) or args.username == 'root':
        raise ValueError('Choose a regular lowercase username, not root.')
    if not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', args.hostname):
        raise ValueError('Hostname must be a single lowercase DNS label, at most 63 characters.')
    if args.mode == 'bios' and not args.boot_disk:
        raise ValueError('BIOS installation requires an explicit --boot-disk /dev/whole-disk.')
    if args.boot_disk and not re.fullmatch(r'/dev/[A-Za-z0-9_.+/-]+', args.boot_disk):
        raise ValueError('Boot disk must be a local /dev block device.')
    return target


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


def install(args):
    if os.geteuid() != 0:
        raise ValueError('Installation requires root; run plan first, then sudo install.')
    for tool in ['debootstrap', 'gpgv', 'findmnt', 'lsblk', 'mount', 'umount', 'chroot']:
        if not shutil.which(tool):
            raise ValueError('Missing host tool: ' + tool + '. Install it using the rescue system package manager.')
    if os.uname().machine != 'x86_64':
        raise ValueError('The first installer supports an amd64 host and target only.')
    if not Path(args.keyring).is_file():
        raise ValueError('A trusted Debian archive keyring is required; signature verification will not be disabled.')
    target, root, esp, disk = inspect_target(args)
    summary = plan(args)
    summary.update(root_device=root['source'], root_uuid=root['uuid'], parent_disk=disk,
                   esp_device=esp['source'] if esp else None)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    if args.action == 'wizard':
        args.confirm_uuid = input('Confirm the exact root UUID shown above (Enter cancels): ').strip()
    if args.confirm_uuid != root['uuid']:
        raise ValueError('Review this exact target, then rerun with --confirm-uuid ' + root['uuid'])
    password = getpass.getpass('New installed-user password (at least 12 characters): ')
    if len(password) < 12 or len(password) > 1024 or any(c in password for c in '\n\r\x00'):
        raise ValueError('Password must be 12–1024 characters without line breaks or NUL.')
    if password != getpass.getpass('Repeat password: '):
        raise ValueError('Passwords did not match; no installation was started.')
    # Recheck mounts/emptiness after interactive review before any write.
    inspect_target(args)
    with (target / '.mykos-install.lock').open('x') as lock:
        os.chmod(lock.name, 0o600)
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        cfg = settings()
        print('Bootstrapping signed Debian base...', flush=True)
        run(['debootstrap', '--arch=' + cfg['architecture'], '--variant=minbase',
             '--include=ca-certificates', '--force-check-gpg', '--keyring=' + str(Path(args.keyring).resolve()),
             cfg['suite'], str(target), cfg['mirror']])
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
    print('Installation commands completed. Target and ESP remain mounted for inspection. Reboot acceptance is still required.')


def wizard_options(args):
    if not sys.stdin.isatty():
        raise ValueError('The wizard requires an interactive terminal; use plan with explicit arguments instead.')
    print('MyKOS / Install from rescue\nUse prepared, mounted partitions. This wizard never formats disks.\n')
    args.target = input('Mounted empty root [/mnt/mykos]: ').strip() or '/mnt/mykos'
    default = 'uefi' if Path('/sys/firmware/efi').exists() else 'bios'
    args.mode = input('Target boot mode [bios/uefi; default ' + default + ']: ').strip().lower() or default
    if args.mode not in {'bios', 'uefi'}:
        raise ValueError('Boot mode must be bios or uefi.')
    if args.mode == 'bios':
        args.boot_disk = input('Whole parent disk for GRUB (for example /dev/sda): ').strip()
    args.username = input('Installed username [mykos]: ').strip() or 'mykos'
    args.hostname = input('Hostname [mykos]: ').strip() or 'mykos'
    validate_options(args)
    return args


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', nargs='?', default='wizard', choices=['wizard', 'plan', 'install'])
    parser.add_argument('--target')
    parser.add_argument('--mode', choices=['bios', 'uefi'])
    parser.add_argument('--boot-disk', help='Explicit parent disk for BIOS (for example /dev/sda); writes its boot area')
    parser.add_argument('--username', default='mykos')
    parser.add_argument('--hostname', default='mykos')
    parser.add_argument('--keyring', default='/usr/share/keyrings/debian-archive-keyring.gpg')
    parser.add_argument('--confirm-uuid', help='Exact UUID of the empty mounted root partition; required to write')
    args = parser.parse_args()
    try:
        if args.action == 'wizard':
            wizard_options(args)
        elif not args.target or not args.mode:
            parser.error('plan and install require --target and --mode')
        if args.action == 'plan':
            print(json.dumps(plan(args), ensure_ascii=False, indent=2))
        else:
            install(args)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print('mykos-install: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
