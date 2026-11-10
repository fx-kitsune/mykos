"""EFI entries must use the same Debian live payload and profiles as the BIOS menu."""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('uefi_builder', ROOT / 'scripts/build/uefi.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
spec = importlib.util.spec_from_file_location('boot_instrumentation', ROOT / 'scripts/testing/boot_iso.py')
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

MENU = ''.join(f'''label {name}
  menu label MyKOS ({name})
  kernel /live/vmlinuz-6.8.0-90-generic
  append initrd=/live/initrd.img-6.8.0-90-generic boot=live username=mykos{extra}
''' for name, extra in [('normal', ''), ('safe', ' nomodeset'), ('software', ' systemd.setenv=KWIN_COMPOSE=N')])


class UefiTests(unittest.TestCase):
    def test_matching_payload_and_software_profile_are_preserved(self):
        menu, entries = builder.menu_from_syslinux(MENU)
        self.assertEqual(len(entries), 3)
        self.assertEqual(menu.count('linux /live/vmlinuz-6.8.0-90-generic'), 3)
        self.assertEqual(menu.count('initrd /live/initrd.img-6.8.0-90-generic'), 3)
        self.assertIn('boot=live username=mykos systemd.setenv=KWIN_COMPOSE=N', menu)
        changed = probe.instrument_grub(menu, software=True)
        self.assertEqual(changed.count('console=ttyS0,115200n8'), 3)
        self.assertEqual([line for line in menu.splitlines() if not line.lstrip().startswith('linux ')],
                         [line for line in changed.splitlines() if not line.lstrip().startswith('linux ')])

    def test_incomplete_or_unsafe_menu_is_rejected(self):
        for text in [MENU.replace('initrd=', 'missing='), MENU.replace('boot=live', 'boot=invalid'),
                     MENU.replace('/live/vmlinuz', '/other/vmlinuz'), MENU.replace('username=mykos', 'username=$unexpected')]:
            with self.assertRaises(ValueError):
                builder.menu_from_syslinux(text)
