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
import shutil
import time
import zlib

from boot_iso import QMP, digest, prepare_menu, instrument_grub
from vm_session import refresh_kvm_access

MARKER = 'MYKOS_DESKTOP_RESULT='
SOFTWARE_PARAMETERS = ' systemd.setenv=KWIN_COMPOSE=N systemd.setenv=QT_QUICK_BACKEND=software'
# Chạy bằng tài khoản live thông thường, không dùng sudo hoặc thay cấu hình guest.
GUEST = r'''
import json, os, shutil, subprocess, time
def running(name):
    return subprocess.run(['pgrep', '-u', str(os.getuid()), '-x', name], capture_output=True, text=True)
def diagnostic(command, env=None):
    try:
        proc = subprocess.run(command, env=env, capture_output=True, text=True, timeout=15)
        return {'returncode': proc.returncode, 'stdout': proc.stdout[-8000:], 'stderr': proc.stderr[-2000:]}
    except (OSError, subprocess.TimeoutExpired) as error:
        return {'error': str(error)}
deadline = time.monotonic() + 180
while time.monotonic() < deadline and running('plasmashell').returncode:
    time.sleep(2)
shell = running('plasmashell')
result = {'uid': os.getuid(), 'firmware_uefi': os.path.isdir('/sys/firmware/efi'), 'plasma': shell.returncode == 0,
          'kwin': any(running(name).returncode == 0 for name in ['kwin_x11', 'kwin_wayland']),
          'applications': {}, 'sessions': diagnostic(['loginctl', 'list-sessions', '--no-legend', '--no-pager']),
          'processes': diagnostic(['ps', '-u', str(os.getuid()), '-o', 'pid,comm,args'])}
if result['plasma']:
    pid = shell.stdout.split()[0]
    env = os.environ.copy()
    for item in open('/proc/' + pid + '/environ', 'rb').read().split(b'\0'):
        if b'=' in item:
            key, value = item.split(b'=', 1)
            env[key.decode()] = value.decode(errors='replace')
    result['rendering_environment'] = {key: env.get(key) for key in ['KWIN_COMPOSE', 'QT_QUICK_BACKEND']}
    env['QT_SELECT'] = 'qt5'
    if shutil.which('qdbus'):
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            response = diagnostic(['qdbus', 'org.kde.plasmashell', '/PlasmaShell',
                'org.kde.PlasmaShell.evaluateScript', 'print(JSON.stringify({panels:panels().length,desktops:desktops().length}))'], env)
            result['containments'] = response
            try:
                counts = json.loads(response.get('stdout', ''))
            except ValueError:
                counts = {}
            if response.get('returncode') == 0 and counts.get('panels', 0) > 0 and counts.get('desktops', 0) > 0:
                print('MYKOS_DESKTOP_READY', flush=True)
                time.sleep(5)
                break
            print('MYKOS_PLASMA_WAIT=' + json.dumps(response), flush=True)
            time.sleep(3)
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
        if not result['applications'][app]:
            result.setdefault('application_errors', {})[app] = open('/tmp/mykos-probe-' + app + '.log').read()[-2000:]
    if shutil.which('kreadconfig5'):
        result['color_scheme'] = subprocess.run(
            ['kreadconfig5', '--file', 'kdeglobals', '--group', 'General', '--key', 'ColorScheme'],
            capture_output=True, text=True).stdout.strip()
    time.sleep(30)
    result['user_journal'] = diagnostic(['journalctl', '--user', '-b', '--no-pager', '-n', '80', '-o', 'cat'], env)
    config = os.path.expanduser('~/.config/plasma-org.kde.plasma.desktop-appletsrc')
    if os.path.isfile(config):
        result['desktop_config'] = open(config).read()[-8000:]
    if shutil.which('calamares') and not result['firmware_uefi']:
        installer_log = '/tmp/mykos-installer-probe.log'
        installer_env = env.copy()
        installer_env['MYKOS_INSTALL_DEBUG'] = '1'
        if shutil.which('mykos-install'):
            with open(installer_log, 'w') as log:
                subprocess.Popen(['sudo', '-n', '--preserve-env=DISPLAY,XAUTHORITY,QT_QUICK_BACKEND,KWIN_COMPOSE,MYKOS_INSTALL_DEBUG',
                                  '/usr/bin/mykos-install'], env=installer_env, stdin=subprocess.DEVNULL,
                                 stdout=log, stderr=subprocess.STDOUT)
            time.sleep(2)
        installer_ready = False
        deadline = time.monotonic() + 300
        while time.monotonic() < deadline:
            alive = subprocess.run(['pgrep', '-x', 'calamares'], capture_output=True).returncode == 0
            log_text = open(installer_log).read() if os.path.isfile(installer_log) else ''
            installer_ready = (alive and 'STARTUP: Window now visible' in log_text
                               and 'All requirements have been checked.' in log_text)
            if installer_ready or not alive:
                break
            time.sleep(3)
        alive = subprocess.run(['pgrep', '-x', 'calamares'], capture_output=True).returncode == 0
        result['installer'] = {'running': alive, 'ready': installer_ready}
        if os.path.isfile(installer_log):
            result['installer']['log_tail'] = open(installer_log).read()[-14000:]
        if installer_ready:
            print('MYKOS_INSTALLER_READY', flush=True)
            time.sleep(5)
print('MYKOS_DESKTOP_RESULT=' + json.dumps(result), flush=True)
'''


def guest_result(text):
    # UART có thể chia một dòng JSON thành nhiều lần recv; chỉ parse khi
    # đã nhận newline, không coi một gói chưa đủ là lỗi của guest.
    for line in reversed(text.splitlines(keepends=True)):
        if not line.endswith('\n'):
            continue
        if line.startswith(MARKER):
            result = json.loads(line[len(MARKER):])
            if not isinstance(result, dict):
                raise ValueError('Kết quả guest phải là JSON object.')
            return result
    return None


def has_prompt(phase, text):
    pattern = r'mykos-live login:' if phase == 'boot' else r'mykos@mykos-live:[^\n]*[$]'
    return re.search(pattern, text) is not None


def guest_command():
    # N_TTY giới hạn một dòng canonical ở khoảng 4096 byte. Nén payload
    # để bổ sung chẩn đoán không làm lệnh bị UART/tty cắt giữa chừng.
    payload = base64.b64encode(zlib.compress(GUEST.encode())).decode()
    return ('python3 -c "import base64,zlib; exec(zlib.decompress(base64.b64decode(\''
            + payload + '\')))"\n').encode()


def desktop_ready(result):
    if result.get('uid', 0) == 0 or not result.get('plasma') or not result.get('kwin'):
        return False
    if not all(result.get('applications', {}).get(app) for app in ['dolphin', 'konsole', 'systemsettings']):
        return False
    if 'installer' in result and not (result['installer'].get('running') and result['installer'].get('ready')):
        return False
    response = result.get('containments', {})
    if response.get('returncode') != 0:
        return False
    try:
        counts = json.loads(response.get('stdout', '').strip())
        return counts.get('panels', 0) > 0 and counts.get('desktops', 0) > 0
    except (ValueError, AttributeError, TypeError):
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('iso', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--timeout', type=int, default=1200)
    parser.add_argument('--firmware', choices=['bios', 'uefi'], default='bios')
    parser.add_argument('--media', choices=['cdrom', 'usb'], default='cdrom')
    parser.add_argument('--ovmf-code', type=Path, default=Path('/usr/share/OVMF/OVMF_CODE_4M.fd'))
    parser.add_argument('--ovmf-vars', type=Path, default=Path('/usr/share/OVMF/OVMF_VARS_4M.fd'))
    parser.add_argument('--software-rendering', action='store_true',
                        help='Bản sao dùng Qt Quick software và tắt compositor X11 cho QEMU/TCG.')
    args = parser.parse_args()
    iso, output = args.iso.resolve(), args.output.resolve()
    if not iso.is_file() or output.exists() or args.timeout < 300:
        parser.error('Cần ISO có sẵn, thư mục mới và thời gian chờ ít nhất 300 giây.')
    output.mkdir(parents=True)
    report = {'iso_sha256': digest(iso), 'status': 'failed',
              'rendering_profile': 'software' if args.software_rendering else 'default',
              'firmware': args.firmware, 'media': args.media,
              'scope': 'Tiến trình Plasma/KWin và mở ứng dụng; ảnh cần rà soát trực quan. Chưa nghiệm thu cài đặt hoặc thiết bị.',
              'instrumentation': 'Bản sao chỉ thêm console nối tiếp; không gắn đĩa cài đặt.'}
    machine = serial = qmp = None
    started = time.monotonic()
    transcript = ''
    try:
        menu = output / ('grub.cfg' if args.firmware == 'uefi' else 'isolinux.cfg')
        menu_path = '/boot/grub/grub.cfg' if args.firmware == 'uefi' else '/isolinux/isolinux.cfg'
        subprocess.run(['xorriso', '-osirrox', 'on', '-indev', str(iso), '-extract',
                        menu_path, str(menu)], check=True)
        if args.firmware == 'uefi':
            menu.chmod(0o600)
            menu.write_text(instrument_grub(menu.read_text(), args.software_rendering))
        else:
            prepare_menu(menu)
        if args.software_rendering and args.firmware == 'bios':
            menu.write_text('\n'.join(line + SOFTWARE_PARAMETERS if line.lstrip().startswith('append ')
                                      else line for line in menu.read_text().splitlines()) + '\n')
        probe_iso = output / 'desktop-probe.iso'
        subprocess.run(['xorriso', '-indev', str(iso), '-outdev', str(probe_iso),
                        '-boot_image', 'any', 'replay', '-map', str(menu),
                        menu_path, '-commit'], check=True)
        report['probe_iso_sha256'] = digest(probe_iso)
        report['kvm_access'] = refresh_kvm_access()
        accel = 'kvm' if os.access('/dev/kvm', os.R_OK | os.W_OK) else 'tcg'
        serial_path, qmp_path = output / 'serial.sock', output / 'qmp.sock'
        command = ['qemu-system-x86_64', '-accel', accel, '-m', '4096', '-smp', '2',
                   '-display', 'none',
                   '-vga', 'std', '-nic', 'user,model=virtio-net-pci',
                   '-serial', 'unix:' + str(serial_path) + ',server=on,wait=on',
                   '-qmp', 'unix:' + str(qmp_path) + ',server=on,wait=off', '-no-reboot']
        if args.firmware == 'uefi':
            if not args.ovmf_code.is_file() or not args.ovmf_vars.is_file():
                raise ValueError('Missing OVMF firmware')
            variables = output / 'OVMF_VARS.fd'
            shutil.copyfile(args.ovmf_vars, variables)
            report['ovmf_code_sha256'] = digest(args.ovmf_code)
            report['ovmf_vars_template_sha256'] = digest(args.ovmf_vars)
            command += ['-machine', 'q35', '-drive', 'if=pflash,format=raw,readonly=on,file=' + str(args.ovmf_code),
                        '-drive', 'if=pflash,format=raw,file=' + str(variables)]
        if args.media == 'usb':
            command += ['-device', 'qemu-xhci', '-drive', 'if=none,id=liveusb,format=raw,readonly=on,file=' + str(probe_iso),
                        '-device', 'usb-storage,drive=liveusb,bootindex=1']
        else:
            command += ['-boot', 'order=d', '-cdrom', str(probe_iso)]
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
            last_progress = phase_started
            last_input = phase_started
            desktop_captured = False
            installer_captured = False
            empty_password_sent = False
            print('Desktop probe: waiting for live console', flush=True)
            while time.monotonic() < deadline:
                if machine.poll() is not None:
                    raise RuntimeError('QEMU thoát trước khi thu được kết quả.')
                try:
                    chunk = serial.recv(65536)
                    if not chunk:
                        raise RuntimeError('Console đã đóng.')
                    transcript += chunk.decode(errors='replace').replace('\r', '')
                    # Giữ console kể cả khi runner hủy lệnh trước khối finally.
                    (output / 'serial.log').write_text(transcript)
                except socket.timeout:
                    pass
                if qmp is None and qmp_path.exists():
                    qmp = QMP(qmp_path)
                if qmp is not None and time.monotonic() - last_input > 30:
                    qmp.command('send-key', {'keys': [{'type': 'qcode', 'data': 'shift'}], 'hold-time': 60})
                    last_input = time.monotonic()
                if not desktop_captured and qmp is not None and 'MYKOS_DESKTOP_READY\n' in transcript:
                    qmp.command('screendump', {'filename': str(output / 'desktop.ppm')})
                    desktop_captured = True
                if not installer_captured and qmp is not None and 'MYKOS_INSTALLER_READY\n' in transcript:
                    qmp.command('screendump', {'filename': str(output / 'installer.ppm')})
                    installer_captured = True
                # systemd có thể ghi thêm trạng thái sau lời nhắc getty/shell.
                # Không đòi prompt nằm ở cuối toàn bộ console.
                if phase == 'boot' and has_prompt(phase, transcript):
                    serial.sendall(b'mykos\r')
                    phase = 'login'
                    phase_started = time.monotonic()
                    print('Desktop probe: logging in as live user mykos', flush=True)
                elif phase == 'login' and has_prompt(phase, transcript):
                    serial.sendall(guest_command())
                    phase = 'probe'
                    phase_started = time.monotonic()
                    print('Desktop probe: checking Plasma and applications', flush=True)
                elif phase == 'login' and not empty_password_sent and re.search(r'(?im)^password:', transcript):
                    # Casper 25adduser đặt hash của mật khẩu rỗng khi có SDDM;
                    # PAM vẫn có thể hỏi Password. Chỉ gửi Enter một lần cho
                    # tài khoản live định sẵn, không thử mật khẩu khác.
                    serial.sendall(b'\r')
                    empty_password_sent = True
                    print('Desktop probe: submitting the live account empty password once', flush=True)
                if phase == 'login' and empty_password_sent and 'Login incorrect' in transcript:
                    raise RuntimeError('Tài khoản live từ chối mật khẩu rỗng; không thử lại.')
                if phase == 'login' and time.monotonic() - phase_started > 60:
                    raise TimeoutError('Không vào được shell live trong 60 giây; xem serial.log.')
                if phase == 'probe' and time.monotonic() - phase_started > 900:
                    raise TimeoutError('Guest không trả kết quả desktop trong 900 giây; xem serial.log.')
                if time.monotonic() - last_progress > 60:
                    tail = transcript.splitlines()[-3:]
                    print(json.dumps({'phase': phase, 'console_tail': tail}, ensure_ascii=False), flush=True)
                    last_progress = time.monotonic()
                result = guest_result(transcript)
                if result is not None:
                    report['guest'] = result
                    if desktop_ready(result) and result.get('firmware_uefi') == (args.firmware == 'uefi'):
                        report['status'] = 'desktop-ready'
                    else:
                        report['error'] = 'Desktop chưa phản hồi hoặc thiếu panel/màn hình/ứng dụng; xem kết quả guest.'
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
        if report['status'] != 'desktop-ready':
            print('Desktop probe console tail:\n' + transcript[-4000:], flush=True)
        report['elapsed_seconds'] = round(time.monotonic() - started, 1)
        (output / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['status'] == 'desktop-ready' else 1


if __name__ == '__main__':
    raise SystemExit(main())
