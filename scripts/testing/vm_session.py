"""Phiên QEMU dùng riêng cho kiểm thử installer trên một đĩa mới."""
import base64
import json
from pathlib import Path
import re
import secrets
import socket
import subprocess
import time
import zlib

from boot_iso import FAILURE, QMP

CSI = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')


def frame(text, marker):
    for line in reversed(text.splitlines(keepends=True)):
        line = CSI.sub('', line)
        if line.endswith('\n') and line.startswith(marker):
            return json.loads(line[len(marker):])
    return None


def key_sequence(text):
    result = []
    for character in text:
        if 'a' <= character <= 'z' or '0' <= character <= '9':
            result.append([character])
        elif 'A' <= character <= 'Z':
            result.append(['shift', character.lower()])
        elif character == ' ':
            result.append(['spc'])
        elif character == '-':
            result.append(['minus'])
        else:
            raise ValueError('Ký tự chưa được hỗ trợ trong dữ liệu kiểm thử bàn phím.')
    return result


def empty_test_disk(inventory, size=40 * 1024**3):
    try:
        disks = [disk for disk in inventory.get('blockdevices', []) if disk.get('type') == 'disk'
                 and not (re.fullmatch(r'fd[0-9]+', disk.get('name', ''))
                          and int(disk.get('size', 0)) <= 4 * 1024**2)]
        return (len(disks) == 1 and disks[0].get('name') == 'vda'
                and int(disks[0].get('size', 0)) == size and not disks[0].get('children'))
    except (ValueError, TypeError):
        return False


def command_for_guest(script, marker):
    wrapped = ('import json\nn={}\ntry:\n    exec(' + repr(script) + ',n)\n'
               '    result=n["result"]\nexcept Exception as error:\n'
               '    result={"__mykos_guest_error__":type(error).__name__+": "+str(error)}\n'
               'print(' + repr(marker) + '+json.dumps(result),flush=True)\n')
    payload = base64.b64encode(zlib.compress(wrapped.encode())).decode()
    command = ('python3 -c "import base64,zlib; exec(zlib.decompress(base64.b64decode(\''
               + payload + '\')))"\n')
    if len(command.encode()) >= 4096:
        raise ValueError('Lệnh guest vượt giới hạn một dòng của tty.')
    return command


class VM:
    def __init__(self, command, output):
        self.output = Path(output)
        self.transcript = ''
        self.serial = self.qmp = None
        self.log = (self.output / 'qemu.log').open('w')
        self.process = subprocess.Popen(command, stdout=self.log, stderr=subprocess.STDOUT)
        serial_path = self.output / 'serial.sock'
        deadline = time.monotonic() + 30
        while not serial_path.exists():
            if self.process.poll() is not None or time.monotonic() > deadline:
                self.close()
                raise RuntimeError('QEMU không mở console; xem qemu.log.')
            time.sleep(.2)
        self.serial = socket.socket(socket.AF_UNIX)
        self.serial.connect(str(serial_path))
        self.serial.settimeout(1)
        qmp_path = self.output / 'qmp.sock'
        while not qmp_path.exists():
            if self.process.poll() is not None or time.monotonic() > deadline:
                self.close()
                raise RuntimeError('QEMU không mở QMP.')
            time.sleep(.2)
        self.qmp = QMP(qmp_path)
        self.last_input = time.monotonic()

    def wait(self, predicate, timeout=600, start=0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if FAILURE.search(self.transcript):
                raise RuntimeError('Guest báo lỗi khởi động; xem serial.log.')
            if time.monotonic() - self.last_input > 30:
                self.key('shift')
            value = predicate(self.transcript[start:])
            if value:
                return value
            if self.process.poll() is not None:
                raise RuntimeError('Máy ảo thoát trước khi hoàn tất kiểm thử.')
            try:
                chunk = self.serial.recv(65536)
                if not chunk:
                    raise RuntimeError('Console của máy ảo đã đóng.')
                self.transcript += chunk.decode(errors='replace').replace('\r', '')
                (self.output / 'serial.log').write_text(self.transcript)
            except socket.timeout:
                pass
        raise TimeoutError('Hết thời gian chờ máy ảo; xem serial.log và ảnh màn hình.')

    def login(self, username='mykos', hostname='mykos-live', password=''):
        self.wait(lambda text: hostname + ' login:' in text)
        start = len(self.transcript)
        self.serial.sendall((username + '\r').encode())
        prompt = re.compile(re.escape(username + '@' + hostname) + r':[^\n]*[$]')
        state = self.wait(lambda text: 'shell' if prompt.search(text) else ('password' if re.search(r'(?im)^password:', text) else None), 90, start)
        if state == 'password':
            start = len(self.transcript)
            self.serial.sendall((password + '\r').encode())
            def authenticated(text):
                if 'Login incorrect' in text:
                    raise RuntimeError('Tài khoản kiểm thử không đăng nhập được; không thử lại.')
                return prompt.search(text)
            self.wait(authenticated, 90, start)

    def guest(self, script, timeout=600):
        marker = 'MYKOS_EXEC_' + secrets.token_hex(8) + '='
        command = command_for_guest(script, marker)
        start = len(self.transcript)
        self.serial.sendall(command.encode())
        result = self.wait(lambda text: frame(text, marker), timeout, start)
        if isinstance(result, dict) and '__mykos_guest_error__' in result:
            raise RuntimeError('Guest: ' + result['__mykos_guest_error__'])
        return result

    def key(self, *codes):
        self.qmp.command('send-key', {'keys': [{'type': 'qcode', 'data': code} for code in codes], 'hold-time': 60})
        self.last_input = time.monotonic()
        time.sleep(.1)

    def type(self, text):
        for codes in key_sequence(text):
            self.key(*codes)

    def click(self, x, y, expected_size=(1280, 800)):
        # Coordinates come from reviewed screenshots; refuse a changed display mode.
        from PIL import Image
        self.capture('before-pointer-input')
        with Image.open(self.output / 'before-pointer-input.png') as screenshot:
            width, height = screenshot.size
        if (width, height) != expected_size or not (0 <= x < width and 0 <= y < height):
            raise RuntimeError('Kích thước màn hình khác ảnh đã rà soát; dừng thao tác chuột.')
        events = [{'type': 'abs', 'data': {'axis': axis, 'value': round(value * 32767 / (extent - 1))}}
                  for axis, value, extent in [('x', x, width), ('y', y, height)]]
        self.qmp.command('input-send-event', {'events': events})
        for down in [True, False]:
            self.qmp.command('input-send-event', {'events': [
                {'type': 'btn', 'data': {'button': 'left', 'down': down}}]})
            time.sleep(.1)
        self.last_input = time.monotonic()

    def capture(self, name):
        from PIL import Image
        path = self.output / (name + '.ppm')
        self.qmp.command('screendump', {'filename': str(path)})
        Image.open(path).save(path.with_suffix('.png'))

    def close(self):
        if self.qmp is not None:
            self.qmp.close()
            self.qmp = None
        if self.serial is not None:
            self.serial.close()
            self.serial = None
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        self.log.close()
