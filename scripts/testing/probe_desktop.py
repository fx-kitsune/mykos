#!/usr/bin/env python3
"""Thu bằng chứng Plasma qua console của bản sao ISO; không gắn đĩa cài đặt."""
import argparse
import base64
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import time

from boot_iso import QMP, digest, prepare_menu

MARKER = 'MYKOS_DESKTOP_RESULT='
# Chạy bằng tài khoản live thông thường, không dùng sudo hoặc thay cấu hình guest.
GUEST = r'''
import json, os, shutil, subprocess, time
def running(name):
    return subprocess.run(['pgrep', '-u', str(os.getuid()), '-x', name], capture_output=True, text=True)
deadline = time.monotonic() + 180
while time.monotonic() < deadline and running('plasmashell').returncode:
    time.sleep(2)
shell = running('plasmashell')
result = {'uid': os.getuid(), 'plasma': shell.returncode == 0,
          'kwin': any(running(name).returncode == 0 for name in ['kwin_x11', 'kwin_wayland']),
          'applications': {}}
if result['plasma']:
    print('MYKOS_DESKTOP_READY', flush=True)
    time.sleep(5)
    pid = shell.stdout.split()[0]
    env = os.environ.copy()
    for item in open('/proc/' + pid + '/environ', 'rb').read().split(b'\0'):
        if b'=' in item:
            key, value = item.split(b'=', 1)
            env[key.decode()] = value.decode(errors='replace')
    for app in ['dolphin', 'konsole', 'systemsettings']:
        executable = shutil.which(app)
        if app == 'systemsettings' and not executable:
            executable = shutil.which('systemsettings5')
        if not executable:
            result['applications'][app] = False
            continue
        with open('/tmp/mykos-probe-' + app + '.log', 'w') as log:
            subprocess.Popen([executable], env=env, stdout=log, stderr=subprocess.STDOUT)
        time.sleep(5)
        result['applications'][app] = running(os.path.basename(executable)).returncode == 0
    if shutil.which('kreadconfig5'):
        result['color_scheme'] = subprocess.run(
            ['kreadconfig5', '--file', 'kdeglobals', '--group', 'General', '--key', 'ColorScheme'],
            capture_output=True, text=True).stdout.strip()
print('MYKOS_DESKTOP_RESULT=' + json.dumps(result), flush=True)
'''


def guest_result(text):
    for line in reversed(text.splitlines()):
        if line.startswith(MARKER):
            result = json.loads(line[len(MARKER):])
            if not isinstance(result, dict):
                raise ValueError('Kết quả guest phải là JSON object.')
            return result
    return None


def has_prompt(phase, text):
    pattern = r'mykos-live login:' if phase == 'boot' else r'mykos@mykos-live:[^\n]*[$]'
    return re.search(pattern, text) is not None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('iso', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--timeout', type=int, default=1200)
    args = parser.parse_args()
    iso, output = args.iso.resolve(), args.output.resolve()
    if not iso.is_file() or output.exists() or args.timeout < 300:
        parser.error('Cần ISO có sẵn, thư mục mới và thời gian chờ ít nhất 300 giây.')
    output.mkdir(parents=True)
    report = {'iso_sha256': digest(iso), 'status': 'failed',
              'scope': 'Tiến trình Plasma/KWin và mở ứng dụng; ảnh cần rà soát trực quan. Chưa nghiệm thu cài đặt hoặc thiết bị.',
              'instrumentation': 'Bản sao chỉ thêm console nối tiếp; không gắn đĩa cài đặt.'}
    machine = serial = qmp = None
    started = time.monotonic()
    transcript = ''
    try:
        menu = output / 'isolinux.cfg'
        subprocess.run(['xorriso', '-osirrox', 'on', '-indev', str(iso), '-extract',
                        '/isolinux/isolinux.cfg', str(menu)], check=True)
        prepare_menu(menu)
        probe_iso = output / 'desktop-probe.iso'
        subprocess.run(['xorriso', '-indev', str(iso), '-outdev', str(probe_iso),
                        '-boot_image', 'any', 'replay', '-map', str(menu),
                        '/isolinux/isolinux.cfg', '-commit'], check=True)
        report['probe_iso_sha256'] = digest(probe_iso)
        accel = 'kvm' if os.access('/dev/kvm', os.R_OK | os.W_OK) else 'tcg'
        serial_path, qmp_path = output / 'serial.sock', output / 'qmp.sock'
        command = ['qemu-system-x86_64', '-accel', accel, '-m', '4096', '-smp', '2',
                   '-boot', 'order=d', '-cdrom', str(probe_iso), '-display', 'none',
                   '-vga', 'std', '-nic', 'user,model=virtio-net-pci',
                   '-serial', 'unix:' + str(serial_path) + ',server=on,wait=on',
                   '-qmp', 'unix:' + str(qmp_path) + ',server=on,wait=off', '-no-reboot']
        report['command'] = command
        with (output / 'qemu.log').open('w') as log:
            machine = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            deadline = time.monotonic() + args.timeout
            while not serial_path.exists():
                if machine.poll() is not None or time.monotonic() >= deadline:
                    raise RuntimeError('QEMU không mở console.')
                time.sleep(.2)
            serial = socket.socket(socket.AF_UNIX)
            serial.connect(str(serial_path))
            serial.settimeout(1)
            phase = 'boot'
            phase_started = time.monotonic()
            desktop_captured = False
            print('Desktop probe: waiting for live console', flush=True)
            while time.monotonic() < deadline:
                if machine.poll() is not None:
                    raise RuntimeError('QEMU thoát trước khi thu được kết quả.')
                try:
                    chunk = serial.recv(65536)
                    if not chunk:
                        raise RuntimeError('Console đã đóng.')
                    transcript += chunk.decode(errors='replace').replace('\r', '')
                except socket.timeout:
                    pass
                if qmp is None and qmp_path.exists():
                    qmp = QMP(qmp_path)
                if not desktop_captured and qmp is not None and '\nMYKOS_DESKTOP_READY\n' in transcript:
                    qmp.command('screendump', {'filename': str(output / 'desktop.ppm')})
                    desktop_captured = True
                # systemd có thể ghi thêm trạng thái sau lời nhắc getty/shell.
                # Không đòi prompt nằm ở cuối toàn bộ console.
                if phase == 'boot' and has_prompt(phase, transcript):
                    serial.sendall(b'mykos\n')
                    phase = 'login'
                    phase_started = time.monotonic()
                    print('Desktop probe: logging in as live user mykos', flush=True)
                elif phase == 'login' and has_prompt(phase, transcript):
                    payload = base64.b64encode(GUEST.encode()).decode()
                    serial.sendall(('python3 -c "import base64; exec(base64.b64decode(\'' + payload + '\'))"\n').encode())
                    phase = 'probe'
                    phase_started = time.monotonic()
                    print('Desktop probe: checking Plasma and applications', flush=True)
                if phase == 'login' and time.monotonic() - phase_started > 60:
                    raise TimeoutError('Không vào được shell live trong 60 giây; xem serial.log.')
                if phase == 'probe' and time.monotonic() - phase_started > 300:
                    raise TimeoutError('Guest không trả kết quả desktop trong 300 giây; xem serial.log.')
                result = guest_result(transcript)
                if result is not None:
                    report['guest'] = result
                    if result.get('uid', 0) != 0 and result.get('plasma') and result.get('kwin') and all(
                            result.get('applications', {}).get(app) for app in ['dolphin', 'konsole', 'systemsettings']):
                        report['status'] = 'desktop-services-ready'
                    else:
                        report['error'] = 'Chưa đạt đủ tiến trình desktop và ứng dụng; xem kết quả guest.'
                    break
            else:
                raise TimeoutError('Hết thời gian chờ ở bước ' + phase + '; xem console và ảnh.')
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        report['error'] = str(error)
    finally:
        if qmp is not None:
            try:
                qmp.command('screendump', {'filename': str(output / 'screen.ppm')})
            except OSError as error:
                report['screenshot_error'] = str(error)
            qmp.close()
        if serial is not None:
            serial.close()
        if machine is not None:
            machine.terminate()
            try:
                machine.wait(timeout=15)
            except subprocess.TimeoutExpired:
                machine.kill()
                machine.wait()
        (output / 'serial.log').write_text(transcript)
        report['elapsed_seconds'] = round(time.monotonic() - started, 1)
        (output / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['status'] == 'desktop-services-ready' else 1


if __name__ == '__main__':
    raise SystemExit(main())
