"""Kiểm tra bước tạo menu thật bằng tệp nhân/mô-đun giả lập, không giả lập boot."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / "distribution/image-build/lb_binary_syslinux"


class BootMenuTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        library = self.base / "toolchain/scripts"
        library.mkdir(parents=True)
        (library / "build.sh").write_text('''
Read_conffiles () { :; }
Set_defaults () { :; }
Require_stagefile () { for file in "$@"; do test -f "$file" || exit 1; done; }
Check_stagefile () { test ! -f "$1" || exit 0; }
Check_lockfile () { :; }
Create_lockfile () { :; }
Create_stagefile () { touch "$1"; }
''')
        modules = self.base / "lib/syslinux/modules/bios"
        modules.mkdir(parents=True)
        (self.base / "lib/ISOLINUX").mkdir()
        (self.base / "lib/ISOLINUX/isolinux.bin").write_bytes(b"fixture")
        for name in ["menu.c32", "ldlinux.c32", "libcom32.c32", "libutil.c32"]:
            (modules / name).write_bytes(b"fixture")
        (self.base / ".build").mkdir()
        for name in ["config", "bootstrap", "binary_linux-image"]:
            (self.base / ".build" / name).touch()
        payload = self.base / "binary/casper"
        payload.mkdir(parents=True)
        for name in ["vmlinuz-6.8.0-9-generic", "initrd.img-6.8.0-9-generic",
                     "vmlinuz-6.8.0-10-generic", "initrd.img-6.8.0-10-generic"]:
            (payload / name).write_bytes(b"fixture")
        self.env = dict(os.environ, LIVE_BUILD=str(self.base / "toolchain"),
                        MYKOS_SYSLINUX_ROOT=str(self.base / "lib"), LB_BOOTLOADER="syslinux",
                        LB_ARCHITECTURES="amd64", LB_INITRAMFS="casper", LB_BINARY_IMAGES="iso-hybrid",
                        LB_BOOTAPPEND_LIVE="boot=casper username=mykos")

    def tearDown(self):
        self.temp.cleanup()

    def run_stage(self):
        return subprocess.run(["sh", str(STAGE)], cwd=self.base, env=self.env,
                              capture_output=True, text=True)

    def test_menu_uses_matching_latest_kernel_and_required_syslinux_modules(self):
        result = self.run_stage()
        self.assertEqual(result.returncode, 0, result.stderr)
        target = self.base / "binary/isolinux"
        menu = (target / "isolinux.cfg").read_text()
        self.assertIn("kernel /casper/vmlinuz-6.8.0-10-generic", menu)
        self.assertIn("initrd=/casper/initrd.img-6.8.0-10-generic boot=casper", menu)
        self.assertNotIn("/live/", menu)
        for module in ["isolinux.bin", "menu.c32", "ldlinux.c32", "libcom32.c32", "libutil.c32"]:
            self.assertTrue((target / module).is_file())
        self.assertTrue((self.base / ".build/binary_syslinux").is_file())

    def test_missing_initrd_fails_without_success_marker(self):
        (self.base / "binary/casper/initrd.img-6.8.0-10-generic").unlink()
        self.assertNotEqual(self.run_stage().returncode, 0)
        self.assertFalse((self.base / ".build/binary_syslinux").exists())

    def test_missing_module_fails_without_success_marker(self):
        (self.base / "lib/syslinux/modules/bios/ldlinux.c32").unlink()
        self.assertNotEqual(self.run_stage().returncode, 0)
        self.assertFalse((self.base / ".build/binary_syslinux").exists())
