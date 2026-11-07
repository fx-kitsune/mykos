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
    def test_configuration_preserves_trust_and_ubuntu_boot(self):
        args = mykos.config_args(mykos.settings())
        flags = dict(zip(args[::2], args[1::2]))
        self.assertEqual(flags["--initramfs"], "casper")
        self.assertEqual(flags["--mode"], "ubuntu")
        self.assertEqual(flags["--apt-secure"], "true")
        self.assertEqual(flags["--distribution"], "noble")
        self.assertIn("boot=casper", flags["--bootappend-live"])

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
            installed = destination / "config/includes.chroot"
            self.assertEqual((installed / "usr/bin/mykos-workspace").stat().st_mode & 0o777, 0o755)
            self.assertEqual((installed / "usr/share/mykos/workspace/main.py").stat().st_mode & 0o777, 0o644)
            self.assertEqual((installed / "usr/share/mykos/workspace/qml").stat().st_mode & 0o777, 0o755)
            self.assertTrue((installed / "usr/share/applications/mykos-workspace.desktop").exists())
            self.assertTrue((installed / "usr/share/icons/MyKOSFold/index.theme").exists())

    def test_toolchain_adapter_sources_library_without_modifying_original(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            prefix = base / "usr"
            share = prefix / "share/live/build"
            share.mkdir(parents=True)
            (share / "functions").mkdir()
            (share / "functions/echo.sh").write_text("Echo () { echo test; }\n")
            (share / "VERSION").write_text("3.0~a57\n")
            (share / "boot-link").symlink_to("/nonexistent-config-only")
            lib = prefix / "lib/live/build"
            lib.mkdir(parents=True)
            (prefix / "lib/live/build.sh").write_text("# common\n")
            binary = prefix / "bin"
            binary.mkdir()
            original = '( . "${LIVE_BUILD}/scripts/build.sh" > /dev/null 2>&1 || true ) || . /usr/lib/live/build.sh'
            (binary / "lb").write_text("#!/bin/sh\n" + original + "\n")
            (lib / "lb_config").write_text("#!/bin/sh\n" + original + "\n")
            with patch.dict(mykos.os.environ, {"MYKOS_LIVE_BUILD_PREFIX": str(prefix)}):
                env = mykos.prepare_toolchain(base / "relocated")
            adapted = (base / "relocated/bin/lb").read_text()
            self.assertNotIn("|| true", adapted)
            self.assertIn('. "${LIVE_BUILD}/scripts/build.sh"', adapted)
            self.assertIn(original, (binary / "lb").read_text())
            self.assertEqual(env["LIVE_BUILD"], str(base / "relocated"))
            self.assertTrue((base / "relocated/boot-link").is_symlink())

    def test_artifact_checksums_match_and_do_not_claim_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            iso, manifest = base / "input.iso", base / "packages"
            iso.write_bytes(b"fixture, not a bootable image")
            manifest.write_text("linux-image-generic 0-test\n")
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
        for name in ["casper", "linux-generic", "sddm", "plasma-desktop", "pipewire-audio", "network-manager"]:
            self.assertIn(name, packages)


if __name__ == "__main__":
    unittest.main()
