#!/usr/bin/env python3
"""Native, unprivileged MyKOS Workspace application for MyKOS Desktop."""
import os
from pathlib import Path
import shutil
import sys

from PyQt6.QtCore import QObject, pyqtProperty as Property, QProcess, QStandardPaths, QTimer, QUrl, pyqtSignal as Signal, pyqtSlot as Slot
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtQuick import QQuickWindow

from state import MAX_NOTE, SPACES, StateStore

HERE = Path(__file__).resolve().parent


class Workspace(QObject):
    changed = Signal()
    notice = Signal(str)
    # Fixed argv, never a shell or commands supplied by QML/user text.
    COMMANDS = {"files": ["thunar"], "terminal": ["x-terminal-emulator"],
                "settings": ["mykos-shell", "--show-settings"],
                "apps": ["mykos-shell", "--show-launcher"],
                "workspace": ["mykos-workspace"], "install": ["mykos-install"],
                "notes": ["mousepad"], "photos": ["ristretto"]}

    def __init__(self, store):
        super().__init__()
        self.store = store
        self.data = store.load()
        self.pending = QTimer(self)
        self.pending.setSingleShot(True)
        self.pending.setInterval(350)
        self.pending.timeout.connect(self.flush)
        self.assets = HERE / "assets"

    @Property(str, notify=changed)
    def theme(self):
        return self.data["theme"]

    @Slot()
    def toggleTheme(self):
        self.data["theme"] = "light" if self.theme == "dark" else "dark"
        self.changed.emit()
        self.pending.start()

    @Slot(str, result=str)
    def note(self, space):
        return self.data["notes"].get(space, "")

    @Slot(str, str)
    def saveNote(self, space, text):
        if space not in SPACES or len(text) > MAX_NOTE:
            self.notice.emit("Ghi chú quá dài; tối đa 100.000 ký tự.")
            return
        self.data["notes"][space] = text
        self.pending.start()

    @Slot(result=bool)
    def flush(self):
        self.pending.stop()
        try:
            self.store.save(self.data)
        except OSError:
            self.notice.emit("Chưa lưu được. Kiểm tra quyền ghi và dung lượng ổ đĩa.")
            return False
        return True

    @Slot(str, result=str)
    def icon(self, name):
        # Only local original assets; no remote fonts, requests or arbitrary paths.
        if name not in {"files", "terminal", "settings", "notes", "photos", "browser", "mark-dark", "mark-light"}:
            return ""
        return QUrl.fromLocalFile(str(self.assets / f"{name}.svg")).toString()

    @Slot(str)
    def launch(self, name):
        command = self.COMMANDS.get(name)
        if command is None:
            self.notice.emit("Ứng dụng không được hỗ trợ.")
            return
        executable = shutil.which(command[0])
        if not executable:
            self.notice.emit("Ứng dụng chưa được cài đặt trên máy này.")
            return
        started = self.startCommand(executable, command[1:])
        if not started:
            self.notice.emit("Không mở được ứng dụng. Vui lòng thử lại từ launcher.")

    def startCommand(self, executable, arguments):
        return QProcess.startDetached(executable, arguments)[0]


def main():
    app = QGuiApplication(sys.argv)
    app.setOrganizationName("MyKOS")
    app.setApplicationName("Workspace")
    directory = os.environ.get("MYKOS_WORKSPACE_DATA") or QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    workspace = Workspace(StateStore(directory))
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("workspace", workspace)
    engine.load(QUrl.fromLocalFile(str(HERE / "qml/Main.qml")))
    if not engine.rootObjects():
        return 1
    app.aboutToQuit.connect(workspace.flush)
    if "--smoke-test" in sys.argv:
        def capture():
            target = os.environ.get("MYKOS_SCREENSHOT")
            try:
                if target:
                    engine.rootObjects()[0].grabWindow().save(target)
            finally:
                app.quit()
        QTimer.singleShot(1200, capture)
    result = app.exec()
    del engine  # Destroy QML bindings while the Python context object is alive.
    return result


if __name__ == "__main__":
    sys.exit(main())
