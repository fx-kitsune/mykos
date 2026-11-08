"""Phân biệt kết quả guest thật với lệnh được console echo lại."""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[2] / 'scripts/testing'
spec = importlib.util.spec_from_file_location('desktop_probe', SCRIPTS / 'probe_desktop.py')
probe = importlib.util.module_from_spec(spec)
with patch.object(sys, 'path', [str(SCRIPTS), *sys.path]):
    spec.loader.exec_module(probe)


class DesktopProbeTests(unittest.TestCase):
    def test_prompt_is_not_lost_when_systemd_logs_continue(self):
        self.assertTrue(probe.has_prompt('boot', 'mykos-live login: \n[ OK ] Started a service.\n'))
        self.assertTrue(probe.has_prompt('login', 'mykos@mykos-live:~$ \n[ OK ] Started a service.\n'))
        self.assertFalse(probe.has_prompt('login', 'mykos-live login: mykos\nPassword: '))

    def test_login_or_echoed_command_is_not_guest_evidence(self):
        self.assertIsNone(probe.guest_result('mykos-live login:\n'))
        self.assertIsNone(probe.guest_result('echo MYKOS_DESKTOP_RESULT={}\n'))

    def test_result_survives_following_shell_prompt(self):
        self.assertEqual(probe.guest_result(
            'noise\nMYKOS_DESKTOP_RESULT={"plasma":false}\nmykos@mykos-live:~$ '),
            {'plasma': False})

    def test_non_object_is_rejected(self):
        with self.assertRaises(ValueError):
            probe.guest_result('MYKOS_DESKTOP_RESULT=[]')

    def test_guest_payload_compiles(self):
        compile(probe.GUEST, 'desktop-guest', 'exec')
