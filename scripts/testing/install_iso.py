#!/usr/bin/env python3
"""Kiểm thử Calamares và boot bản cài trên một QCOW2 mới, dùng riêng."""
import argparse
import base64
import hashlib
import json
import os
import re
import secrets
from pathlib import Path
import subprocess
import time

from boot_iso import digest, prepare_menu
from probe_desktop import GUEST, SOFTWARE_PARAMETERS, desktop_ready
from vm_session import VM, empty_test_disk


def installation_state(log):
    # A failure must override any earlier completion message.
    if 'Installation failed:' in log or 'completion: failed' in log:
        return 'failed'
    if 'completion: succeeded' in log:
        return 'complete'
    return 'waiting'


def planned_ext4_root(log):
    return ('CreatePartitionJob' in log
            and re.search(r'mountPoint: :\s*"/"\s+fs: :\s*"ext4"', log) is not None)


INSTALLED_CHECK = r'''
import json, subprocess
from pathlib import Path
def command(args):
    return subprocess.run(['sudo','-n',*args],capture_output=True,text=True,timeout=30)
target=Path('/mnt/mykos-installed-check')
mounts=command(['findmnt','--json','--source','/dev/vda1','-o','SOURCE,TARGET,FSTYPE'])
previous=json.loads(mounts.stdout).get('filesystems',[]) if mounts.returncode == 0 else []
for mount in previous:
    path=Path(mount['target'])
    if (mount['source'] != '/dev/vda1' or mount['fstype'] != 'ext4'
            or path.parent != Path('/tmp') or not path.name.startswith('calamares-root-')):
        raise RuntimeError('Unexpected existing mount of the disposable partition: '+str(path))
    p=command(['umount',str(path)])
    if p.returncode: raise RuntimeError(p.stderr)
p=command(['install','-d','-m','0755',str(target)])
if p.returncode: raise RuntimeError(p.stderr)
p=command(['mount','-o','ro,noload','/dev/vda1',str(target)])
if p.returncode: raise RuntimeError(p.stderr)
try:
    passwd=(target/'etc/passwd').read_text()
    groups=(target/'etc/group').read_text()
    shadow=command(['cat',str(target/'etc/shadow')])
    if shadow.returncode: raise RuntimeError(shadow.stderr)
    hashes={line.split(':')[0]:line.split(':')[1] for line in shadow.stdout.splitlines()}
    package_status={}
    for package in ['casper','calamares']:
        p=command(['dpkg-query','--admindir='+str(target/'var/lib/dpkg'),'-W','-f=${db:Status-Status}',package])
        package_status[package]=p.stdout.strip()
    result={'previous_calamares_mounts':previous,
            'root_filesystem':command(['blkid','-s','TYPE','-o','value','/dev/vda1']).stdout.strip(),
            'account_present':any(line.startswith('vmtester:') for line in passwd.splitlines()),
            'sudo_membership':any(line.startswith('sudo:') and 'vmtester' in line.split(':')[3].split(',') for line in groups.splitlines()),
            'root_locked':hashes.get('root','').startswith(('!','*')),
            'user_password_set':bool(hashes.get('vmtester')) and not hashes['vmtester'].startswith(('!','*')),
            'live_sudoers_removed':not (target/'etc/sudoers.d/casper').exists(),
            'launcher_removed':not (target/'usr/bin/mykos-install').exists(),
            'packages':package_status,
            'kernel_present':bool(list((target/'boot').glob('vmlinuz-*'))),
            'initrd_present':bool(list((target/'boot').glob('initrd.img-*'))),
            'grub_core_present':(target/'boot/grub/i386-pc/core.img').is_file(),
            'grub_config':command(['cat',str(target/'boot/grub/grub.cfg')]).stdout[-16000:],
            'fstab':(target/'etc/fstab').read_text(),
            'hostname':(target/'etc/hostname').read_text().strip()}
finally:
    p=command(['umount',str(target)])
    if p.returncode: raise RuntimeError(p.stderr)
'''


def installed_target_ready(result):
    return (all(result.get(key) is True for key in ['account_present', 'sudo_membership',
            'root_locked', 'user_password_set', 'live_sudoers_removed', 'launcher_removed',
            'kernel_present', 'initrd_present', 'grub_core_present'])
            and result.get('root_filesystem') == 'ext4'
            and result.get('hostname') == 'mykos-installed'
            and all(result.get('packages', {}).get(package) in {'', 'not-installed', 'config-files'}
                    for package in ['casper', 'calamares'])
            and 'menuentry ' in result.get('grub_config', '')
            and 'UUID=' in result.get('fstab', ''))


ENABLE_TEST_CONSOLE = r'''
import subprocess
target='/mnt/mykos-installed-check'
def checked(args):
    p=subprocess.run(['sudo','-n',*args],capture_output=True,text=True,timeout=30)
    if p.returncode: raise RuntimeError(p.stderr)
checked(['mount','/dev/vda1',target])
try:
    checked(['systemctl','--root='+target,'enable','serial-getty@ttyS0.service'])
finally:
    checked(['umount',target])
checked(['sync'])
result={'instrumentation':'Enabled serial-getty@ttyS0.service only in the disposable installed system; GRUB and kernel options unchanged.'}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('iso', type=Path)
    parser.add_argument('--expected-sha', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--diagnostic-direct', action='store_true',
                        help='Chỉ chẩn đoán Calamares trực tiếp; không nghiệm thu launcher của ISO.')
    parser.add_argument('--diagnostic-overlay', type=Path, help='Chỉ chẩn đoán: chép overlay hiện tại vào guest live, không nghiệm thu ISO gốc.')
    parser.add_argument('--prepare-install', action='store_true',
                        help='Chọn đĩa ảo trống và nhập tài khoản thử; dừng ở Summary, chưa ghi phân vùng.')
    parser.add_argument('--install', action='store_true',
                        help='Cài thật vào QCOW2 mới đã xác minh; chưa nghiệm thu boot bản cài.')
    parser.add_argument('--boot-installed', action='store_true',
                        help='Sau cài đặt, tháo ISO và đăng nhập console bản cài bằng mật khẩu đã nhập trong GUI.')
    args = parser.parse_args()
    if args.install and not args.prepare_install:
        parser.error('--install cần --prepare-install để rà soát toàn bộ luồng trước xác nhận.')
    if args.boot_installed and not args.install:
        parser.error('--boot-installed cần --install trong cùng phiên để giữ mật khẩu dùng một lần trong bộ nhớ.')
    iso, output = args.iso.resolve(), args.output.resolve()
    if not iso.is_file() or output.exists() or ',' in str(output):
        parser.error('Cần ISO có sẵn và thư mục kết quả mới, không chứa dấu phẩy.')
    actual_sha = digest(iso)
    if actual_sha != args.expected_sha:
        parser.error('ISO không khớp mã SHA-256 đã nghiệm thu desktop; không tạo hoặc gắn đĩa.')
    output.mkdir(parents=True)
    report = {'status': 'failed', 'iso_sha256': actual_sha,
              'diagnostic_direct': args.diagnostic_direct, 'diagnostic_overlay': bool(args.diagnostic_overlay),
              'scope': 'Xem installer với đĩa ảo mới; chưa cài đặt hoặc ghi phân vùng.',
              'disk': 'install-disk.qcow2', 'disk_size_bytes': 40 * 1024**3}
    vm = None
    started = time.monotonic()
    try:
        disk = output / 'install-disk.qcow2'
        subprocess.run(['qemu-img', 'create', '-f', 'qcow2', str(disk), '40G'], check=True)
        disk.chmod(0o600)
        menu = output / 'isolinux.cfg'
        subprocess.run(['xorriso', '-osirrox', 'on', '-indev', str(iso), '-extract',
                        '/isolinux/isolinux.cfg', str(menu)], check=True)
        prepare_menu(menu)
        menu.write_text('\n'.join(line + SOFTWARE_PARAMETERS if line.lstrip().startswith('append ')
                                  else line for line in menu.read_text().splitlines()) + '\n')
        probe = output / 'install-probe.iso'
        subprocess.run(['xorriso', '-indev', str(iso), '-outdev', str(probe), '-boot_image', 'any',
                        'replay', '-map', str(menu), '/isolinux/isolinux.cfg', '-commit'], check=True)
        report['probe_iso_sha256'] = digest(probe)
        accel = 'kvm' if os.access('/dev/kvm', os.R_OK | os.W_OK) else 'tcg'
        command = ['qemu-system-x86_64', '-accel', accel, '-m', '4096', '-smp', '2',
                   '-boot', 'order=d', '-cdrom', str(probe), '-display', 'none', '-vga', 'std',
                   '-nic', 'user,model=virtio-net-pci', '-usb', '-device', 'usb-tablet',
                   '-drive', 'file=' + str(disk) + ',format=qcow2,if=virtio',
                   '-serial', 'unix:' + str(output / 'serial.sock') + ',server=on,wait=on',
                   '-qmp', 'unix:' + str(output / 'qmp.sock') + ',server=on,wait=off', '-no-reboot']
        report['command'] = command
        vm = VM(command, output)
        print('Installer preview: waiting for live login', flush=True)
        vm.login()
        inventory = vm.guest("import json,subprocess\nresult=json.loads(subprocess.check_output(['lsblk','--json','--bytes','-o','NAME,TYPE,SIZE,MOUNTPOINTS']))")
        report['inventory'] = inventory
        if not empty_test_disk(inventory):
            raise RuntimeError('Chỉ chấp nhận đúng một đĩa vda mới, 40 GiB và chưa có phân vùng.')
        if args.diagnostic_overlay:
            overlay = args.diagnostic_overlay.resolve()
            if not overlay.is_dir():
                raise ValueError('Không tìm thấy overlay chẩn đoán.')
            report['overlay_files'] = []
            for path in sorted(overlay.rglob('*')):
                if path.is_symlink():
                    raise ValueError('Overlay chẩn đoán không chấp nhận symlink.')
                if not path.is_file():
                    continue
                relative = path.relative_to(overlay).as_posix()
                content = path.read_bytes()
                destination = '/' + relative
                mode = '0755' if relative == 'usr/bin/mykos-install' else '0644'
                script = 'import base64,subprocess,tempfile\n'
                script += 'with tempfile.NamedTemporaryFile() as f:\n'
                script += '    f.write(base64.b64decode(' + repr(base64.b64encode(content).decode()) + ')); f.flush()\n'
                script += '    p=subprocess.run(["sudo","-n","install","-D","-m",' + repr(mode) + ',f.name,' + repr(destination) + '],capture_output=True,text=True)\n'
                script += '    result={"returncode":p.returncode,"stderr":p.stderr}\n'
                copied = vm.guest(script, timeout=30)
                if copied.get('returncode') != 0:
                    raise RuntimeError('Không chép được overlay vào guest: ' + relative + ' ' + copied.get('stderr', ''))
                report['overlay_files'].append({'path': relative, 'sha256': hashlib.sha256(content).hexdigest()})
            print('Installer diagnostic: current overlay applied only to live guest', flush=True)
        print('Installer preview: verified fresh vda; opening Calamares', flush=True)
        payload = GUEST
        if args.diagnostic_direct:
            needle = "'/usr/bin/mykos-install'"
            if payload.count(needle) != 1:
                raise RuntimeError('Cấu trúc lệnh chẩn đoán đã thay đổi; không tự đoán lệnh chạy.')
            payload = payload.replace(needle, "'/usr/bin/calamares', '--debug'")
        result = vm.guest(payload, timeout=900)
        report['guest'] = result
        if not desktop_ready(result) or not result.get('installer', {}).get('running'):
            raise RuntimeError('Desktop hoặc Calamares chưa sẵn sàng.')
        vm.capture('installer-welcome')
        for name in ['location', 'keyboard', 'partition']:
            vm.key('alt', 'n')
            time.sleep(3)
            vm.capture('installer-' + name)
        if args.prepare_install:
            # The 1280x800 partition page and its empty /dev/vda were reviewed.
            vm.click(334, 158)
            time.sleep(3)
            vm.capture('installer-erase-selected')
            vm.key('alt', 'n')
            time.sleep(3)
            vm.capture('installer-users-empty')
            # Calamares 3.3.5 UsersPage::onActivate focuses FullName. Its UI
            # declares login, hostname, password, confirmation in this order.
            password = 'Vm' + secrets.token_hex(12)
            for index, value in enumerate(['Mykos Tester', 'vmtester', 'mykos-installed', password, password]):
                if index:
                    vm.key('tab')
                vm.key('ctrl', 'a')
                vm.type(value)
            time.sleep(5)
            vm.capture('installer-users-filled')
            vm.key('alt', 'n')
            time.sleep(3)
            vm.capture('installer-summary')
            report['prepared_account'] = {'username': 'vmtester', 'hostname': 'mykos-installed',
                                          'password': 'ephemeral, not retained'}
            report['after_preparation'] = vm.guest("import json,subprocess\nresult=json.loads(subprocess.check_output(['lsblk','--json','--bytes','-o','NAME,TYPE,SIZE,MOUNTPOINTS']))")
            if not empty_test_disk(report['after_preparation']):
                raise RuntimeError('Đĩa thay đổi trong bước chuẩn bị; chưa được phép coi preview là cài đặt.')
            report['preparation_log'] = vm.guest("from pathlib import Path\nresult={'log':Path('/tmp/mykos-installer-probe.log').read_text(errors='replace')[-24000:]}")
        report['status'] = 'installer-diagnostic-preview' if args.diagnostic_direct or args.diagnostic_overlay else 'installer-preview'
        # Reviewed panel layout: show desktop exposes the actual wallpaper.
        vm.click(1266, 777)
        time.sleep(3)
        vm.capture('live-wallpaper')
        vm.click(1266, 777)
        if args.install:
            report['status'] = 'failed'
            report['scope'] = 'Cài vào QCOW2 mới và kiểm tra đích; chưa boot bản cài hoặc nghiệm thu thiết bị.'
            if not planned_ext4_root(report.get('preparation_log', {}).get('log', '')):
                raise RuntimeError('Kế hoạch không có phân vùng gốc ext4; dừng trước Install.')
            # Both Install accelerators are defined in Calamares 3.3.5 ViewManager.
            vm.key('alt', 'i')
            time.sleep(2)
            vm.capture('installer-confirmation')
            vm.key('alt', 'i')
            print('Installer test: confirmed installation on disposable vda only', flush=True)
            deadline = time.monotonic() + 1800
            while time.monotonic() < deadline:
                probe_result = vm.guest("from pathlib import Path\nresult={'log':Path('/tmp/mykos-installer-probe.log').read_text(errors='replace')[-40000:]}", timeout=60)
                log = probe_result['log']
                (output / 'installer-execution.log').write_text(log)
                state = installation_state(log)
                if state == 'failed':
                    raise RuntimeError('Calamares báo cài đặt thất bại; xem installer-execution.log.')
                if state == 'complete':
                    break
                print('Installer test: waiting; ' + log.splitlines()[-1][:200] if log.splitlines() else 'Installer test: waiting for log', flush=True)
                vm.capture('installer-progress')
                time.sleep(10)
            else:
                raise TimeoutError('Calamares chưa hoàn tất trong 1800 giây.')
            vm.capture('installer-complete')
            report['installed_target'] = vm.guest(INSTALLED_CHECK, timeout=120)
            if not installed_target_ready(report['installed_target']):
                raise RuntimeError('Calamares kết thúc nhưng đích chưa đạt kiểm tra kernel/GRUB/tài khoản/chính sách live.')
            report['status'] = 'installer-diagnostic-complete' if args.diagnostic_direct or args.diagnostic_overlay else 'installer-complete'
        if args.boot_installed:
            report['status'] = 'failed'
            report['installed_console'] = vm.guest(ENABLE_TEST_CONSOLE, timeout=120)
            vm.close()
            vm = None
            boot_output = output / 'installed-boot'
            boot_output.mkdir()
            # Deliberately construct a new command with no CD-ROM or probe ISO.
            installed_command = ['qemu-system-x86_64', '-accel', accel, '-m', '4096', '-smp', '2',
                '-boot', 'order=c', '-display', 'none', '-vga', 'std',
                '-nic', 'user,model=virtio-net-pci', '-usb', '-device', 'usb-tablet',
                '-drive', 'file=' + str(disk) + ',format=qcow2,if=virtio',
                '-serial', 'unix:' + str(boot_output / 'serial.sock') + ',server=on,wait=on',
                '-qmp', 'unix:' + str(boot_output / 'qmp.sock') + ',server=on,wait=off', '-no-reboot']
            report['installed_boot_command'] = installed_command
            vm = VM(installed_command, boot_output)
            print('Installed boot: ISO detached; waiting for GRUB and installed console', flush=True)
            vm.login(username='vmtester', hostname='mykos-installed', password=password)
            vm.capture('installed-login-screen')
            report['installed_boot'] = vm.guest("import os,subprocess,json\nresult={'uid':os.getuid(),'root':subprocess.check_output(['findmnt','--json','/'],text=True),'cmdline':open('/proc/cmdline').read(),'hostname':open('/etc/hostname').read().strip()}")
            installed = report['installed_boot']
            filesystem = json.loads(installed['root'])['filesystems'][0]
            if (installed['uid'] == 0 or installed['hostname'] != 'mykos-installed'
                    or filesystem['source'] != '/dev/vda1' or filesystem['fstype'] != 'ext4'
                    or 'boot=casper' in installed['cmdline']):
                raise RuntimeError('Bản cài chưa đạt kiểm tra tài khoản thường và root trên đĩa sau tháo ISO.')
            report['scope'] = 'Cài QCOW2, boot GRUB không ISO, đăng nhập console tài khoản thường. Chưa nghiệm thu đăng nhập GUI hoặc thiết bị.'
            report['status'] = 'installed-diagnostic-userspace-ready' if args.diagnostic_direct or args.diagnostic_overlay else 'installed-userspace-ready'
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        report['error'] = str(error)
    finally:
        if vm is not None:
            try:
                vm.capture('last-screen')
            except OSError as error:
                report['screenshot_error'] = str(error)
            vm.close()
        report['elapsed_seconds'] = round(time.monotonic() - started, 1)
        (output / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['status'] in {'installer-preview', 'installer-diagnostic-preview',
                                    'installer-complete', 'installer-diagnostic-complete',
                                    'installed-userspace-ready', 'installed-diagnostic-userspace-ready'} else 1


if __name__ == '__main__':
    raise SystemExit(main())
