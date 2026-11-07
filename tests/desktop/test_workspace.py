"""Exercise real Qt/QML, local state and the command boundary headlessly."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QUICK_BACKEND", "software")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "desktop/workspace"))
from PyQt6.QtCore import QObject, QUrl, QMetaObject, Q_ARG, Qt
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtQuick import QQuickWindow
from PyQt6.QtTest import QTest
from main import Workspace, HERE
from state import StateStore

APP = QGuiApplication.instance() or QGuiApplication([])


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.workspace = Workspace(StateStore(self.folder.name))
        self.messages = []
        self.workspace.notice.connect(self.messages.append)

    def tearDown(self):
        self.workspace.pending.stop()
        self.folder.cleanup()

    def test_notes_are_isolated_and_saved_with_theme(self):
        self.workspace.saveNote("personal", "Cá nhân")
        self.workspace.saveNote("creative", "Sáng tạo")
        self.workspace.toggleTheme()
        self.assertTrue(self.workspace.flush())
        restored = Workspace(StateStore(self.folder.name))
        self.assertEqual(restored.note("personal"), "Cá nhân")
        self.assertEqual(restored.note("creative"), "Sáng tạo")
        self.assertEqual(restored.theme, "light")
        self.workspace.saveNote("../../outside", "invalid")
        self.assertNotIn("../../outside", self.workspace.data["notes"])

    def test_launch_rejects_arbitrary_commands_and_reports_missing_apps(self):
        with patch("main.QProcess.startDetached") as launch:
            self.workspace.launch("sh -c malicious")
            launch.assert_not_called()
            with patch("main.shutil.which", return_value=None):
                self.workspace.launch("files")
            launch.assert_not_called()
        self.assertEqual(len(self.messages), 2)
        with patch("main.shutil.which", return_value="/usr/bin/dolphin"), \
                patch("main.QProcess.startDetached", return_value=(True, 123)) as launch:
            self.workspace.launch("files")
            launch.assert_called_once_with("/usr/bin/dolphin", [])

    def test_real_qml_loads_edits_switches_searches_and_renders_both_themes(self):
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda messages: warnings.extend(m.toString() for m in messages))
        engine.rootContext().setContextProperty("workspace", self.workspace)
        engine.load(QUrl.fromLocalFile(str(HERE / "qml/Main.qml")))
        self.assertTrue(engine.rootObjects(), warnings)
        root = engine.rootObjects()[0]
        QTest.qWait(100)
        note = root.findChild(QObject, "quickNote")
        QMetaObject.invokeMethod(note, "forceActiveFocus")
        note.setProperty("text", "Ghi chú native")
        self.assertEqual(self.workspace.note("personal"), "Ghi chú native")
        QMetaObject.invokeMethod(root, "switchSpace", Q_ARG("QVariant", 1))
        self.assertEqual(note.property("text"), "")
        QMetaObject.invokeMethod(root, "switchSpace", Q_ARG("QVariant", 0))
        self.assertEqual(note.property("text"), "Ghi chú native")
        focus = root.findChild(QObject, "focusButton")
        QMetaObject.invokeMethod(focus, "clicked")
        self.assertEqual(root.property("remaining"), 1500)
        QMetaObject.invokeMethod(focus, "clicked")
        self.assertEqual(root.property("remaining"), 0)
        popup = root.findChild(QObject, "appSearchPopup")
        QMetaObject.invokeMethod(popup, "open")
        root.findChild(QObject, "appSearch").setProperty("text", "Terminal")
        self.assertTrue(popup.property("visible"))
        QMetaObject.invokeMethod(popup, "close")
        dark = root.grabWindow()
        self.assertFalse(dark.isNull())
        self.workspace.toggleTheme()
        QTest.qWait(100)
        light = root.grabWindow()
        self.assertFalse(light.isNull())
        self.assertNotEqual(dark.pixelColor(0, 0), light.pixelColor(0, 0))
        root.setWidth(900); root.setHeight(700)
        QTest.qWait(100)
        self.assertFalse(root.grabWindow().isNull())
        self.assertEqual(warnings, [])
        root.close()
        del root, engine
