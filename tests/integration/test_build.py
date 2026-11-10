import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("mykos", ROOT / "scripts/build/mykos.py")
mykos = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mykos)


class ImageToolTests(unittest.TestCase):
    def test_configuration_preserves_trust_and_debian_boot(self):
        args = mykos.config_args(mykos.settings())
        flags = dict(zip(args[::2], args[1::2]))
        self.assertEqual(flags["--initramfs"], "live-boot")
        self.assertEqual(flags["--mode"], "debian")
        self.assertEqual(flags["--apt-secure"], "true")
        self.assertEqual(flags["--distribution"], "trixie")
        self.assertIn("boot=live", flags["--bootappend-live"])

    def test_no_existing_tree_is_modified(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            marker = path / "user-data"
            marker.write_text("retain")
            with self.assertRaises(ValueError):
                mykos.configure(path)
            self.assertEqual(marker.read_text(), "retain")

    def test_failed_live_build_configuration_propagates(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(mykos, "prepare_toolchain", return_value={}), \
                    patch.object(mykos, "run", side_effect=OSError("missing lb")):
                with self.assertRaises(OSError):
                    mykos.configure(Path(folder) / "new")

    def test_staged_desktop_is_readable_and_executable_by_session_user(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / "build"
            def fake_config(args, **kwargs):
                (kwargs["cwd"] / "config").mkdir()
            with patch.object(mykos, "prepare_toolchain", return_value={}), \
                    patch.object(mykos, "run", side_effect=fake_config):
                mykos.configure(destination)
            prerequisite = destination / "config/hooks/normal/005-mykos-prerequisites.hook.chroot"
            self.assertTrue(prerequisite.stat().st_mode & 0o111)
            hooks = destination / "config/hooks/live"
            self.assertTrue((hooks / "010-mykos.hook.chroot").is_file())
            self.assertTrue((hooks / "090-mykos-menu.hook.binary").stat().st_mode & 0o111)
            installed = destination / "config/includes.chroot"
            self.assertEqual((installed / "usr/bin/mykos-session").stat().st_mode & 0o777, 0o755)
            self.assertEqual((installed / "usr/bin/mykos-shell").stat().st_mode & 0o777, 0o755)
            self.assertTrue((installed / "usr/share/xsessions/mykos.desktop").is_file())
            self.assertTrue((installed / "usr/share/mykos/shell/Shell.qml").is_file())
            self.assertTrue((installed / "usr/lib/live/config/0099-mykos-session").stat().st_mode & 0o111)
            self.assertEqual((installed / "usr/bin/mykos-workspace").stat().st_mode & 0o777, 0o755)
            self.assertEqual((installed / "usr/share/mykos/workspace/main.py").stat().st_mode & 0o777, 0o644)
            self.assertEqual((installed / "usr/share/mykos/workspace/qml").stat().st_mode & 0o777, 0o755)
            self.assertTrue((installed / "usr/share/applications/mykos-workspace.desktop").exists())
            self.assertTrue((installed / "usr/share/icons/MyKOSFold/index.theme").exists())
            self.assertEqual((installed / "usr/bin/mykos-install").stat().st_mode & 0o777, 0o755)
            self.assertEqual((installed / "etc/calamares/settings.conf").stat().st_mode & 0o777, 0o644)
            self.assertTrue((installed / "usr/share/mykos/calamares/modules/mykos-config/main.py").exists())

    def test_relocated_debian_toolchain_preserves_source_layout_and_templates(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            prefix = base / "usr"
            for relative, content in {
                "share/live/build/functions/common.sh": "# original library\n",
                "share/live/build/bootloaders/grub-pc/grub.cfg": "# original template\n",
                "share/live/build/bootloaders/isolinux/isolinux.cfg": "# BIOS template\n",
                "lib/live/build.sh": "# bootstrap\n",
                "lib/live/build/binary_grub_cfg": "# original stage\n",
                "bin/lb": "#!/bin/sh\n"}.items():
                path = prefix / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            target = base / "toolchain"
            with patch.dict(mykos.os.environ, {"MYKOS_LIVE_BUILD_PREFIX": str(prefix)}):
                mykos.prepare_toolchain(target)
            self.assertEqual((target / "share/bootloaders/grub-pc/grub.cfg").read_text(), "# original template\n")
            self.assertTrue((target / "share/bootloaders/isolinux/isolinux.cfg").is_file())
            self.assertEqual((target / "functions/common.sh").read_bytes(),
                             (prefix / "share/live/build/functions/common.sh").read_bytes())
            self.assertEqual((target / "scripts/build/binary_grub_cfg").read_text(), "# original stage\n")

    def test_no_ubuntu_packages_or_archives_are_selected(self):
        self.assertTrue({"live-boot", "live-config", "live-config-systemd", "debian-archive-keyring"} <= set(mykos.packages()))
        self.assertFalse({"casper", "linux-generic", "ubuntu-keyring"} & set(mykos.packages()))
        cfg = mykos.settings()
        self.assertEqual(cfg["kernel_flavour"], "amd64")
        self.assertIn("deb.debian.org", cfg["mirror"])
        self.assertIn("debian-security", cfg["security_mirror"])

    def test_artifact_checksums_match_and_do_not_claim_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            iso, manifest = base / "input.iso", base / "packages"
            iso.write_bytes(b"fixture, not a bootable image")
            manifest.write_text("linux-image-amd64 0-test\n")
            output = base / "output"
            mykos.metadata(iso, output, manifest)
            for line in (output / "SHA256SUMS").read_text().splitlines():
                digest, filename = line.split("  ")
                self.assertEqual(digest, mykos.sha256(output / filename))
            record = json.loads((output / "build.json").read_text())
            self.assertIn("unvalidated", record["validation"])
            self.assertEqual(record["package_manifest_sha256"], mykos.sha256(manifest))
            with self.assertRaises(ValueError):
                mykos.metadata(iso, output, manifest)

    def test_packages_are_unique_and_cover_desktop_basics(self):
        packages = mykos.packages()
        self.assertEqual(len(packages), len(set(packages)))
        for name in ["live-boot", "linux-image-amd64", "sddm", "openbox", "pipewire-audio", "network-manager"]:
            self.assertIn(name, packages)


if __name__ == "__main__":
    unittest.main()
