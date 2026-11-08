#!/usr/bin/env python3
"""Mở và rà soát installer trên đĩa QCOW2 mới; dừng trước chọn phân vùng."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

from boot_iso import digest, prepare_menu
from probe_desktop import GUEST, SOFTWARE_PARAMETERS, desktop_ready
from vm_session import VM, empty_test_disk


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('iso', type=Path)
    parser.add_argument('--expected-sha', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--diagnostic-direct', action='store_true',
                        help='Chỉ chẩn đoán Calamares trực tiếp; không nghiệm thu launcher của ISO.')
    parser.add_argument('--diagnostic-overlay', type=Path, help='Chỉ chẩn đoán: chép overlay hiện tại vào guest live, không nghiệm thu ISO gốc.')
    args = parser.parse_args()
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
        result = vm.guest(payload, timeout=600)
        report['guest'] = result
        if not desktop_ready(result) or not result.get('installer', {}).get('running'):
            raise RuntimeError('Desktop hoặc Calamares chưa sẵn sàng.')
        vm.capture('installer-welcome')
        for name in ['location', 'keyboard', 'partition']:
            vm.key('alt', 'n')
            time.sleep(3)
            vm.capture('installer-' + name)
        # Không chọn xóa đĩa hoặc bấm Install trong phép thử preview.
        report['status'] = 'installer-diagnostic-preview' if args.diagnostic_direct or args.diagnostic_overlay else 'installer-preview'
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
    return 0 if report['status'] in {'installer-preview', 'installer-diagnostic-preview'} else 1


if __name__ == '__main__':
    raise SystemExit(main())
