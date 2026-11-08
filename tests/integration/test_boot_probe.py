import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('boot_probe', ROOT / 'scripts/testing/boot_iso.py')
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class BootProbeTests(unittest.TestCase):
    def test_kernel_log_alone_does_not_pass(self):
        self.assertEqual(probe.serial_state('Linux version 6.8\nBIOS started'), 'waiting')

    def test_failure_overrides_old_ready_message(self):
        self.assertEqual(probe.serial_state('mykos-live login:\nKernel panic - not syncing'), 'failed')

    def test_userspace_marker_and_ansi_are_recognized(self):
        self.assertEqual(probe.serial_state('\x1b[32m[ OK ]\x1b[0m Reached target Graphical Interface.'), 'userspace-ready')
        self.assertEqual(probe.serial_state('mykos-live login:'), 'userspace-ready')

    def test_only_kernel_arguments_are_changed(self):
        before = 'default mykos\nlabel mykos\n  kernel /casper/vmlinuz-6.8\n  append initrd=/casper/initrd.img-6.8 boot=casper\n'
        after = probe.instrument_menu(before)
        self.assertIn('kernel /casper/vmlinuz-6.8\n', after)
        self.assertIn('append initrd=/casper/initrd.img-6.8 boot=casper console=ttyS0,115200n8', after)
        self.assertEqual(probe.serial_state('Kernel panic'), 'failed')
        with self.assertRaises(ValueError):
            probe.instrument_menu('default mykos\n')
