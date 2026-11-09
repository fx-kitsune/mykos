#!/usr/bin/env python3
"""Kiểm thử BIOS của bản sao ISO có bổ sung console; không gắn ổ đĩa cài đặt."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import time

READY = re.compile(r"(?:mykos-live login:|Reached target[^\n]*(?:Graphical Interface|Multi-User System))")
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
FAILURE = re.compile(r"Kernel panic|ALERT!.*does not exist|Unable to find a medium containing a live file system")


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def serial_state(text):
    text = ANSI.sub('', text)
    if FAILURE.search(text):
        return 'failed'
    return 'userspace-ready' if READY.search(text) else 'waiting'


def instrument_menu(text):
    lines = text.splitlines()
    if not any(line.lstrip().startswith('append ') for line in lines):
        raise ValueError('Menu không có tham số nhân để bổ sung console.')
    return '\n'.join(line + ' console=ttyS0,115200n8 systemd.show_status=1'
                     if line.lstrip().startswith('append ') else line for line in lines) + '\n'


def prepare_menu(path):
    # Rock Ridge giữ quyền chỉ đọc từ ISO; chỉ đổi bản sao vừa trích xuất.
    path.chmod(0o600)
    path.write_text(instrument_menu(path.read_text()))


def instrument_grub(text, software=False):
    """Change kernel arguments only; keep the tested EFI loader and payload."""
    count = 0
    lines = []
    for line in text.splitlines():
        if line.lstrip().startswith('linux '):
            count += 1
            line += ' console=ttyS0,115200n8 systemd.show_status=1'
            if software:
                line += ' systemd.setenv=KWIN_COMPOSE=N systemd.setenv=QT_QUICK_BACKEND=software'
        lines.append(line)
    if count != 3:
        raise ValueError('Expected three EFI live kernel entries')
    return '\n'.join(lines) + '\n'


class QMP:
    def __init__(self, path):
        self.sock = socket.socket(socket.AF_UNIX)
        self.sock.settimeout(5)
        self.sock.connect(str(path))
        self.stream = self.sock.makefile('rwb')
        self.read()
        self.command('qmp_capabilities')

    def read(self):
        line = self.stream.readline()
        if not line:
            raise OSError('Kết nối QMP đã đóng.')
        return json.loads(line)

    def command(self, command, arguments=None):
        self.stream.write((json.dumps({'execute': command, 'arguments': arguments or {}})+'\n').encode())
        self.stream.flush()
        while True:
            result = self.read()
            if 'error' in result:
                raise OSError(str(result['error']))
            if 'return' in result:
                return result['return']

    def close(self):
        self.stream.close()
        self.sock.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('iso', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--timeout', type=int, default=1200)
    args = parser.parse_args()
    iso, output = args.iso.resolve(), args.output.resolve()
    if not iso.is_file() or output.exists() or args.timeout < 30:
        parser.error('Cần ISO có sẵn, thư mục kết quả mới và thời gian chờ ít nhất 30 giây.')
    output.mkdir(parents=True)
    report = {'iso_sha256': digest(iso), 'status': 'failed',
              'scope': 'BIOS và môi trường chạy trực tiếp; chưa xác nhận Plasma hoặc cài đặt',
              'instrumentation': 'Bản sao ISO thêm console nối tiếp; giữ nguyên nhân, initrd và squashfs.'}
    machine = None
    qmp = None
    started = time.monotonic()
    try:
        menu = output / 'isolinux.cfg'
        subprocess.run(['xorriso', '-osirrox', 'on', '-indev', str(iso),
                        '-extract', '/isolinux/isolinux.cfg', str(menu)], check=True)
        prepare_menu(menu)
        probe_iso = output / 'boot-probe.iso'
        subprocess.run(['xorriso', '-indev', str(iso), '-outdev', str(probe_iso),
                        '-boot_image', 'any', 'replay', '-map', str(menu), '/isolinux/isolinux.cfg',
                        '-commit'], check=True)
        report['probe_iso_sha256'] = digest(probe_iso)
        accel = 'kvm' if os.access('/dev/kvm', os.R_OK | os.W_OK) else 'tcg'
        report['acceleration'] = accel
        serial = output / 'serial.log'
        qmp_path = output / 'qmp.sock'
        command = ['qemu-system-x86_64', '-accel', accel, '-m', '4096', '-smp', '2',
                   '-boot', 'order=d', '-cdrom', str(probe_iso), '-display', 'none',
                   '-vga', 'std', '-nic', 'user,model=virtio-net-pci',
                   '-serial', 'file:' + str(serial), '-qmp', 'unix:' + str(qmp_path) + ',server=on,wait=off',
                   '-no-reboot']
        report['command'] = command
        with (output / 'qemu.log').open('w') as log:
            machine = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            deadline = time.monotonic() + args.timeout
            while time.monotonic() < deadline:
                text = serial.read_text(errors='replace') if serial.exists() else ''
                state = serial_state(text)
                if state == 'failed' or machine.poll() is not None:
                    raise RuntimeError('Máy ảo báo lỗi hoặc thoát trước khi vào môi trường chạy trực tiếp.')
                if qmp is None and qmp_path.exists():
                    qmp = QMP(qmp_path)
                if state == 'userspace-ready':
                    # Cho màn hình đồ họa thêm thời gian trước khi lưu bằng chứng.
                    time.sleep(15)
                    final_text = serial.read_text(errors='replace') if serial.exists() else ''
                    if machine.poll() is not None or serial_state(final_text) == 'failed':
                        raise RuntimeError('Máy ảo lỗi trong thời gian chờ ổn định sau khởi động.')
                    report['status'] = state
                    break
                time.sleep(2)
            else:
                raise TimeoutError('Hết thời gian chờ khởi động; xem serial.log và ảnh màn hình.')
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        report['status'] = 'failed'
        report['error'] = str(error)
    finally:
        if qmp is not None:
            try:
                qmp.command('screendump', {'filename': str(output / 'screen.ppm')})
            except OSError as error:
                report['screenshot_error'] = str(error)
            qmp.close()
        if machine is not None:
            machine.terminate()
            try:
                machine.wait(timeout=15)
            except subprocess.TimeoutExpired:
                machine.kill()
                machine.wait()
        report['elapsed_seconds'] = round(time.monotonic() - started, 1)
        (output / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['status'] == 'userspace-ready' else 1


if __name__ == '__main__':
    raise SystemExit(main())
