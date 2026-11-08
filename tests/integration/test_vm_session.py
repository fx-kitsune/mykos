"""Ranh giới dữ liệu console và đĩa dùng cho kiểm thử installer."""
import importlib.util
from pathlib import Path
import sys
import shlex
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[2] / 'scripts/testing'
spec = importlib.util.spec_from_file_location('vm_session_tested', SCRIPTS / 'vm_session.py')
vm = importlib.util.module_from_spec(spec)
with patch.object(sys, 'path', [str(SCRIPTS), *sys.path]):
    spec.loader.exec_module(vm)


class VMSessionTests(unittest.TestCase):
    def test_kvm_permissions_are_not_changed_outside_github_hosted_runners(self):
        with patch.dict(vm.os.environ, {'RUNNER_ENVIRONMENT': 'self-hosted'}), patch.object(vm.subprocess, 'run') as command:
            self.assertEqual(vm.refresh_kvm_access(), {'attempted': False, 'reason': 'not-github-hosted'})
            command.assert_not_called()

    def test_startup_failure_keeps_the_actual_process_error(self):
        with tempfile.TemporaryDirectory() as output:
            command = [sys.executable, '-c', "import sys;sys.stderr.write('fixture disk is locked');sys.exit(2)"]
            with self.assertRaisesRegex(RuntimeError, 'fixture disk is locked'):
                vm.VM(command, output)

    def test_guest_command_round_trip_preserves_quoted_data(self):
        command = vm.command_for_guest('result={"text":\'a "quoted" value\',"ready":True}', 'TAG=')
        self.assertLess(len(command), 4096)
        result = subprocess.run(shlex.split(command), capture_output=True, text=True, check=True)
        self.assertEqual(vm.frame(result.stdout, 'TAG='), {'text': 'a "quoted" value', 'ready': True})

    def test_only_one_unpartitioned_disk_of_exact_size_is_accepted(self):
        disk = {'name': 'vda', 'type': 'disk', 'size': 40 * 1024**3}
        self.assertTrue(vm.empty_test_disk({'blockdevices': [disk, {'name': 'sr0', 'type': 'rom'}]}))
        self.assertFalse(vm.empty_test_disk({'blockdevices': [dict(disk, children=[{'name': 'vda1'}])]}))
        self.assertFalse(vm.empty_test_disk({'blockdevices': [disk, dict(disk, name='vdb')]}))
        self.assertFalse(vm.empty_test_disk({'blockdevices': [dict(disk, size=20 * 1024**3)]}))
        self.assertFalse(vm.empty_test_disk({'blockdevices': []}))
        self.assertTrue(vm.empty_test_disk({'blockdevices': [disk, {'name': 'fd0', 'type': 'disk', 'size': 4096}]}))
        self.assertFalse(vm.empty_test_disk({'blockdevices': [disk, dict(disk, name='fd0')]}))

    def test_guest_exception_returns_a_complete_frame_instead_of_timing_out(self):
        command = vm.command_for_guest("raise RuntimeError('target mount failed')", 'TAG=')
        process = subprocess.run(shlex.split(command), capture_output=True, text=True, check=True)
        self.assertEqual(vm.frame(process.stdout, 'TAG='),
                         {'__mykos_guest_error__': 'RuntimeError: target mount failed'})

    def test_fragmented_result_is_not_decoded_until_newline(self):
        self.assertIsNone(vm.frame('TAG={"ready":', 'TAG='))
        self.assertIsNone(vm.frame('echo TAG={}\n', 'TAG='))
        self.assertEqual(vm.frame('TAG={"ready":true}\n', 'TAG='), {'ready': True})
        self.assertEqual(vm.frame('\x1b[?2004lTAG={"ready":true}\n\x1b[?2004huser@host:~$ ', 'TAG='), {'ready': True})

    def test_keyboard_test_data_rejects_unhandled_characters(self):
        self.assertEqual(vm.key_sequence('Vm 1-'), [['shift', 'v'], ['m'], ['spc'], ['1'], ['minus']])
        with self.assertRaises(ValueError):
            vm.key_sequence('unsupported\n')
