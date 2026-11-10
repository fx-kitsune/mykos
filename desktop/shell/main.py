#!/usr/bin/env python3
"""MyKOS desktop shell: wallpaper, panel, launcher and window switching."""
import ctypes
import json
import os
import signal
import subprocess
from pathlib import Path
import sys

from PyQt6.QtCore import (QCoreApplication, QMetaObject, QObject, QRect, Qt, QTimer, QUrl,
                          pyqtProperty as Property, pyqtSignal as Signal, pyqtSlot as Slot)
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtQuick import QQuickWindow

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'workspace'))
from main import Workspace  # loaded as module 'main'; this file executes as __main__
from state import StateStore
import x11


def socket_name():
    runtime = os.environ.get('XDG_RUNTIME_DIR')
    if not runtime or not Path(runtime).is_dir() or Path(runtime).stat().st_uid != os.getuid():
        raise ValueError('A user-owned XDG_RUNTIME_DIR is required.')
    display = os.environ.get('DISPLAY', 'offscreen').replace('/', '_')
    return str(Path(runtime) / ('mykos-shell-' + display))


def request(action):
    socket = QLocalSocket()
    socket.connectToServer(socket_name())
    if not socket.waitForConnected(1000):
        return None
    socket.write(action.encode() + b'\n')
    socket.waitForBytesWritten(1000)
    if not socket.waitForReadyRead(1500):
        return None
    return json.loads(bytes(socket.readAll()).decode())


class Desktop(Workspace):
    windowsChanged = Signal()
    def __init__(self, store):
        super().__init__(store)
        self.children = []
        self.rows = []
        self.exclude = set()
        self.panel = None
        self.ticks = 0
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.refresh)

    def startCommand(self, executable, arguments):
        try:
            self.children.append(subprocess.Popen([executable, *arguments], start_new_session=True))
            return True
        except OSError:
            return False

    def stopApplications(self):
        sys.path.insert(0, str(HERE.parent / 'session'))
        from session import stop_children
        stop_children(self.children)

    @Property('QVariantList', notify=windowsChanged)
    def windows(self):
        return self.rows

    def refresh(self):
        self.ticks += 1
        if QGuiApplication.platformName() != 'xcb':
            return
        try:
            rows = x11.list_windows(self.exclude)
            if rows != self.rows:
                self.rows = rows
                self.windowsChanged.emit()
        except (OSError, subprocess.SubprocessError):
            self.notice.emit('Chưa đọc được danh sách cửa sổ.')

    @Slot(str)
    def activate(self, identifier):
        if identifier not in {row['id'] for row in self.rows}:
            return
        try:
            x11.command(['wmctrl', '-ia', identifier])
        except (OSError, subprocess.SubprocessError):
            self.notice.emit('Không chuyển được cửa sổ.')

    @Slot(int)
    def switchDesktop(self, index):
        if index not in (0, 1, 2):
            return
        try:
            x11.command(['wmctrl', '-s', str(index)])
        except (OSError, subprocess.SubprocessError):
            self.notice.emit('Không chuyển được màn hình làm việc.')

    @Slot(str)
    def openSetting(self, name):
        # These dialogs are unprivileged and use the existing system services.
        import shutil
        commands = {'network': ['nm-connection-editor'], 'audio': ['pavucontrol'], 'display': ['arandr']}
        argv = commands.get(name)
        if not argv or not shutil.which(argv[0]):
            self.notice.emit('Công cụ thiết lập chưa được cài.')
            return
        if not self.startCommand(argv[0], argv[1:]):
            self.notice.emit('Không mở được thiết lập.')

    @Slot()
    def logout(self):
        if os.environ.get('MYKOS_SESSION') == '1':
            QCoreApplication.quit()
        else:
            self.notice.emit('Đây là bản xem thử, không phải phiên đăng nhập MyKOS.')


def serve(server, bridge):
    while server.hasPendingConnections():
        client = server.nextPendingConnection()
        client.setParent(server)
        def read(client=client):
            if not client.canReadLine():
                if client.bytesAvailable() > 128:
                    client.disconnectFromServer()
                return
            action = bytes(client.readLine(129)).decode(errors='replace').strip()
            if action in ('launcher', 'settings'):
                QMetaObject.invokeMethod(bridge.panel, 'openLauncher' if action == 'launcher' else 'openSettings')
            result = {'desktop': 'MyKOS', 'panel': bool(bridge.panel and bridge.panel.isVisible()),
                      'ticks': bridge.ticks}
            client.write(json.dumps(result).encode() + b'\n')
            client.flush()
            client.disconnectFromServer()
        client.readyRead.connect(read)
        client.disconnected.connect(client.deleteLater)
        if client.bytesAvailable():
            read()


def main():
    action = next((value for flag, value in [('--check', 'check'), ('--show-launcher', 'launcher'),
                   ('--show-settings', 'settings')] if flag in sys.argv), None)
    if action:
        app = QCoreApplication(sys.argv)
        result = request(action)
        if result:
            print(json.dumps(result))
        return 0 if result else 1
    app = QGuiApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setOrganizationName('MyKOS')
    app.setApplicationName('Desktop')
    ctypes.CDLL(None).prctl(15, b'mykos-shell', 0, 0, 0)
    if app.platformName() != 'xcb' and '--smoke-test' not in sys.argv:
        raise ValueError('The desktop session currently supports X11 only.')
    location = os.environ.get('MYKOS_WORKSPACE_DATA') or str(Path.home() / '.local/share/MyKOS/Workspace')
    bridge = Desktop(StateStore(location))
    server = QLocalServer()
    server.setSocketOptions(QLocalServer.SocketOption.UserAccessOption)
    name = socket_name()
    if not server.listen(name):
        # Never replace an active shell. Only unlink a dead Unix socket.
        if request('check'):
            raise ValueError('MyKOS Shell is already running on this display.')
        QLocalServer.removeServer(name)
        if not server.listen(name):
            raise ValueError(server.errorString())
    server.newConnection.connect(lambda: serve(server, bridge))
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty('workspace', bridge)
    engine.load(QUrl.fromLocalFile(str(HERE / 'Shell.qml')))
    if not engine.rootObjects():
        server.close()
        return 1
    desktop = engine.rootObjects()[0]
    panel = desktop.findChild(QQuickWindow, 'mykosPanel')
    bridge.panel = panel
    desktop.setFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnBottomHint)
    panel.setFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
    bridge.exclude = {int(desktop.winId()), int(panel.winId())}
    def layout():
        geometry = app.primaryScreen().geometry()
        height = 56
        desktop.setGeometry(geometry)
        panel.setGeometry(QRect(geometry.x(), geometry.bottom() - height + 1, geometry.width(), height))
        if app.platformName() == 'xcb':
            x11.describe_window(desktop.winId(), 'DESKTOP')
            x11.describe_window(panel.winId(), 'DOCK', (geometry.x(), geometry.bottom() - height + 1,
                                                      geometry.width(), height, geometry.bottom() + 1))
    layout()
    app.primaryScreen().geometryChanged.connect(layout)
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: app.quit())
    desktop.show()
    panel.show()
    bridge.timer.start()
    app.aboutToQuit.connect(bridge.flush)
    if '--smoke-test' in sys.argv:
        def capture():
            target = os.environ.get('MYKOS_SCREENSHOT')
            if target:
                desktop.grabWindow().save(target)
                panel.grabWindow().save(str(Path(target).with_stem(Path(target).stem + '-panel')))
            app.quit()
        QTimer.singleShot(1500, capture)
    result = app.exec()
    bridge.timer.stop()
    bridge.stopApplications()
    server.close()
    del engine
    return result


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f'MyKOS shell: {error}', file=sys.stderr)
        sys.exit(1)
