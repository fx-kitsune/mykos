"""Exercise session lifetime and the actual image integration, without root/Qt."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('mykos_session', ROOT / 'desktop/session/session.py')
session = importlib.util.module_from_spec(spec)
spec.loader.exec_module(session)


class MykosSessionTests(unittest.TestCase):
    def test_environment_requires_x11_and_declares_own_desktop(self):
        with self.assertRaises(ValueError):
            session.session_environment({})
        env = session.session_environment({'DISPLAY': ':42', 'XDG_CURRENT_DESKTOP': 'KDE'})
        self.assertEqual(env['XDG_CURRENT_DESKTOP'], 'MyKOS')
        self.assertEqual(env['XDG_SESSION_TYPE'], 'x11')
        self.assertEqual(env['MYKOS_SESSION'], '1')

    def test_shell_exit_stops_window_manager_and_agents(self):
        children = []
        def spawn(*args, **kwargs):
            child = subprocess.Popen(*args, **kwargs)
            children.append(child)
            return child
        result = session.supervise(
            [[sys.executable, '-c', 'import time; time.sleep(30)'],
             [sys.executable, '-c', 'import sys; sys.exit(0)']],
            dict(os.environ), [[sys.executable, '-c', 'import time; time.sleep(30)']], popen=spawn)
        self.assertEqual(result, 0)
        self.assertTrue(all(child.poll() is not None for child in children))
        self.assertLess(children[0].returncode, 0)

    def test_failure_to_spawn_shell_cleans_already_started_window_manager(self):
        children = []
        def spawn(*args, **kwargs):
            child = subprocess.Popen(*args, **kwargs)
            children.append(child)
            return child
        with self.assertRaises(FileNotFoundError):
            session.supervise([[sys.executable, '-c', 'import time; time.sleep(30)'],
                               ['/nonexistent-mykos-shell']], dict(os.environ), popen=spawn)
        self.assertIsNotNone(children[0].poll())

    def test_image_owns_login_and_has_no_plasma_runtime_overlay(self):
        packages = set((ROOT / 'distribution/packages/desktop.list.chroot').read_text().splitlines())
        self.assertTrue({'openbox', 'wmctrl', 'thunar', 'lxpolkit', 'dunst'} <= packages)
        self.assertFalse({'plasma-desktop', 'plasma-workspace', 'kwin-x11', 'plasma-discover'} & packages)
        self.assertFalse((ROOT / 'distribution/branding/overlay/usr/share/plasma').exists())
        config = ROOT / 'distribution/installer/overlay/etc/calamares/modules/displaymanager.conf'
        self.assertEqual(json.loads(config.read_text())['defaultDesktopEnvironment']['desktopFile'], 'mykos')
        entry = (ROOT / 'desktop/integration/mykos.desktop').read_text()
        self.assertIn('Exec=/usr/bin/mykos-session', entry)
        live = (ROOT / 'desktop/session/overlay/usr/lib/live/config/0099-mykos-session').read_text()
        self.assertIn('Session=mykos.desktop', live)
