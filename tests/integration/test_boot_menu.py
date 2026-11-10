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
        modules = self.base / "lib/syslinux/modules/bios"
        modules.mkdir(parents=True)
        (self.base / "lib/ISOLINUX").mkdir()
        (self.base / "lib/ISOLINUX/isolinux.bin").write_bytes(b"fixture")
        for name in ["menu.c32", "ldlinux.c32", "libcom32.c32", "libutil.c32"]:
            (modules / name).write_bytes(b"fixture")
        payload = self.base / "binary/live"
        payload.mkdir(parents=True)
        for name in ["vmlinuz-6.12.10-amd64", "initrd.img-6.12.10-amd64",
                     "vmlinuz-6.12.20-amd64", "initrd.img-6.12.20-amd64"]:
            (payload / name).write_bytes(b"fixture")
        (self.base / "config").mkdir()
        (self.base / "config/binary").write_text('LB_BOOTAPPEND_LIVE="boot=live components username=mykos"\n')
        self.env = dict(os.environ, MYKOS_SYSLINUX_ROOT=str(self.base / "lib"))

    def tearDown(self):
        self.temp.cleanup()

    def run_stage(self):
        return subprocess.run(["sh", str(STAGE)], cwd=self.base / "binary", env=self.env,
                              capture_output=True, text=True)

    def test_menu_uses_matching_latest_kernel_and_required_syslinux_modules(self):
        result = self.run_stage()
        self.assertEqual(result.returncode, 0, result.stderr)
        target = self.base / "binary/isolinux"
        menu = (target / "isolinux.cfg").read_text()
        self.assertIn("kernel /live/vmlinuz-6.12.20-amd64", menu)
        self.assertIn("initrd=/live/initrd.img-6.12.20-amd64 boot=live", menu)
        self.assertNotIn("/casper/", menu)
        for module in ["isolinux.bin", "menu.c32", "ldlinux.c32", "libcom32.c32", "libutil.c32"]:
            self.assertTrue((target / module).is_file())

    def test_missing_initrd_fails(self):
        (self.base / "binary/live/initrd.img-6.12.20-amd64").unlink()
        self.assertNotEqual(self.run_stage().returncode, 0)

    def test_missing_module_fails(self):
        (self.base / "lib/syslinux/modules/bios/ldlinux.c32").unlink()
        self.assertNotEqual(self.run_stage().returncode, 0)
