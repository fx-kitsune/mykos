"""Boot the real DE on its own X server; never attach to the user's desktop."""
import json
import os
from pathlib import Path
import select
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ['Xvfb', 'openbox', 'wmctrl', 'xprop', 'xmessage', 'xwininfo', 'dbus-daemon']


@unittest.skipUnless(all(shutil.which(tool) for tool in TOOLS), 'Requires Xvfb, Openbox and X11 utilities')
class X11SessionTests(unittest.TestCase):
    def test_real_shell_reserves_panel_space_switches_workspaces_and_logs_out(self):
        children, logs = [], []
        with tempfile.TemporaryDirectory(prefix='mykos-x11-') as folder:
            base = Path(folder)
            env = dict(os.environ, XDG_RUNTIME_DIR=folder, MYKOS_WORKSPACE_DATA=str(base / 'state'),
                       XDG_CACHE_HOME=str(base / 'cache'), QT_QUICK_BACKEND='software', QT_QPA_PLATFORM='xcb')
            env.pop('DBUS_SESSION_BUS_ADDRESS', None)
            def spawn(args, name, **kwargs):
                log = (base / (name + '.log')).open('w')
                logs.append(log)
                child = subprocess.Popen(args, cwd=ROOT, env=env, stderr=log,
                                         stdout=kwargs.pop('stdout', log), **kwargs)
                children.append(child)
                return child
            def run(args):
                return subprocess.run(args, cwd=ROOT, env=env, text=True, capture_output=True, timeout=5)
            shell = [sys.executable, str(ROOT / 'desktop/shell/main.py')]
            try:
                server = spawn(['Xvfb', '-displayfd', '1', '-screen', '0', '1280x800x24', '-nolisten', 'tcp'],
                               'xvfb', stdout=subprocess.PIPE)
                self.assertTrue(select.select([server.stdout], [], [], 10)[0], 'Xvfb startup timeout')
                display = server.stdout.readline().decode().strip()
                self.assertTrue(display.isdigit(), (base / 'xvfb.log').read_text())
                server.stdout.close()
                env['DISPLAY'] = ':' + display
                session = spawn([sys.executable, 'desktop/session/session.py'], 'session')
                deadline = time.monotonic() + 15
                while time.monotonic() < deadline:
                    self.assertIsNone(session.poll(), (base / 'session.log').read_text())
                    reply = run([*shell, '--check'])
                    if reply.returncode == 0 and json.loads(reply.stdout).get('ticks', 0) > 0:
                        break
                    time.sleep(0.2)
                else:
                    self.fail('Shell did not become responsive: ' + (base / 'session.log').read_text())
                self.assertTrue(json.loads(reply.stdout)['panel'])
                tree = run(['xwininfo', '-root', '-tree']).stdout
                for title, kind in [('MyKOS Desktop', 'DESKTOP'), ('MyKOS Panel', 'DOCK')]:
                    identifier = next(line.split()[0] for line in tree.splitlines() if '"' + title + '"' in line)
                    self.assertIn('_' + kind, run(['xprop', '-id', identifier, '_NET_WM_WINDOW_TYPE']).stdout)
                self.assertIn('1280, 744', run(['xprop', '-root', '_NET_WORKAREA']).stdout)
                self.assertEqual(run([*shell, '--show-launcher']).returncode, 0)
                time.sleep(0.2)
                self.assertIn('Ứng dụng MyKOS', run(['wmctrl', '-l']).stdout)
                self.assertEqual(run([*shell, '--show-settings']).returncode, 0)
                marker = spawn(['xmessage', '-title', 'MyKOS test client', 'Hello'], 'client')
                time.sleep(0.3)
                windows = run(['wmctrl', '-l']).stdout
                self.assertIn('MyKOS test client', windows)
                identifier = next(line.split()[0] for line in windows.splitlines() if line.endswith('MyKOS test client'))
                self.assertEqual(run(['wmctrl', '-ia', identifier]).returncode, 0)
                self.assertEqual(run(['wmctrl', '-s', '1']).returncode, 0)
                self.assertIn('= 1', run(['xprop', '-root', '_NET_CURRENT_DESKTOP']).stdout)
                self.assertIn(' -1 ', run(['wmctrl', '-l']).stdout)  # Shell surfaces remain on all desktops.
                session.terminate()
                session.wait(timeout=8)
                self.assertNotEqual(run([*shell, '--check']).returncode, 0)
            finally:
                for child in reversed(children):
                    if child.poll() is None:
                        child.terminate()
                        try:
                            child.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            child.kill()
                            child.wait()
                for log in logs:
                    log.close()
