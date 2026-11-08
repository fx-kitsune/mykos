"""Kiểm tra ranh giới đích cài đặt và cấu hình Calamares bằng dữ liệu thật."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / 'distribution/installer/overlay'
CONFIG = OVERLAY / 'etc/calamares'
spec = importlib.util.spec_from_file_location('installer_target', OVERLAY / 'usr/share/mykos/calamares/modules/mykos-config/main.py')
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class InstallerTests(unittest.TestCase):
    def test_erase_layout_has_an_explicit_ext4_root_without_preselecting_erase(self):
        partition = json.loads((CONFIG / 'modules/partition.conf').read_text())
        roots = [entry for entry in partition['partitionLayout'] if entry.get('mountPoint') == '/']
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0]['filesystem'], 'ext4')
        self.assertEqual(roots[0]['size'], '100%')
        self.assertEqual(partition['initialPartitioningChoice'], 'none')

    def test_branding_has_required_slideshow_and_local_images(self):
        directory = CONFIG / 'branding/mykos'
        branding = json.loads((directory / 'branding.desc').read_text())
        self.assertEqual(branding['componentName'], directory.name)
        self.assertTrue((directory / branding['slideshow']).is_file())
        self.assertEqual(branding['slideshowAPI'], 2)
        for path in branding['images'].values():
            self.assertTrue((directory / path).is_file())
        self.assertEqual(branding['uploadServer']['type'], 'none')
        settings = json.loads((CONFIG / 'settings.conf').read_text())
        self.assertIn('quit-at-end', settings)

    def test_installer_has_grub_and_mounts_needed_for_target_commands(self):
        packages = (ROOT / 'distribution/packages/desktop.list.chroot').read_text().splitlines()
        for package in ['calamares', 'grub-pc-bin', 'grub2-common']:
            self.assertIn(package, packages)
        mounts = json.loads((CONFIG / 'modules/mount.conf').read_text())['extraMounts']
        self.assertTrue({'/proc', '/sys', '/dev', '/run', '/run/udev'} <= {m['mountPoint'] for m in mounts})
        units = json.loads((CONFIG / 'modules/services-systemd.conf').read_text())['units']
        self.assertTrue(all(unit['mandatory'] for unit in units))

    def test_sequence_installs_before_bootloader_and_uses_chroot(self):
        settings = json.loads((CONFIG / 'settings.conf').read_text())
        self.assertFalse(settings['dont-chroot'])
        self.assertTrue(settings['prompt-install'])
        sequence = settings['sequence'][1]['exec']
        for before, after in [('partition', 'mount'), ('mount', 'unpackfs'),
                              ('unpackfs', 'users'), ('packages', 'mykos-config'),
                              ('mykos-config', 'initramfs'), ('initramfs', 'bootloader'),
                              ('bootloader', 'umount')]:
            self.assertLess(sequence.index(before), sequence.index(after))
        source = json.loads((CONFIG / 'modules/unpackfs.conf').read_text())['unpack'][0]
        self.assertEqual(source['source'], '/cdrom/casper/filesystem.squashfs')
        self.assertEqual(source['sourcefs'], 'squashfs')
        self.assertEqual(source['destination'], '')

    def test_installed_account_has_password_and_no_root_or_autologin_default(self):
        users = json.loads((CONFIG / 'modules/users.conf').read_text())
        self.assertFalse(users['setRootPassword'])
        self.assertFalse(users['doAutologin'])
        self.assertEqual(users['sudoersGroup'], '')
        self.assertGreaterEqual(users['passwordRequirements']['minLength'], 8)
        removal = json.loads((CONFIG / 'modules/packages.conf').read_text())
        self.assertFalse(removal['update_db'])
        self.assertIn('casper', removal['operations'][0]['remove'])
        self.assertIn('calamares', removal['operations'][0]['remove'])

    def test_target_cleanup_preserves_user_files_and_only_adds_opted_in_graphics(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for relative in ['usr/bin/mykos-install', 'etc/sudoers.d/casper', 'etc/calamares/settings.conf', 'home/user/notes.txt']:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('retain user data')
            target.configure_target(root)
            self.assertFalse((root / 'usr/bin/mykos-install').exists())
            self.assertFalse((root / 'etc/sudoers.d/casper').exists())
            self.assertFalse((root / 'etc/calamares').exists())
            self.assertEqual((root / 'home/user/notes.txt').read_text(), 'retain user data')
            path = root / 'etc/default/grub.d/60-mykos-software.cfg'
            self.assertFalse(path.exists())
            target.configure_target(root, software=True)
            self.assertIn('systemd.setenv=KWIN_COMPOSE=N', path.read_text())

    def test_cleanup_refuses_live_root_and_missing_targets(self):
        for root in ['/', 'relative-path', '/nonexistent-mykos-install-target']:
            with self.assertRaises(ValueError):
                target.configure_target(root)

    def test_cleanup_does_not_follow_target_symlinks_outside_installation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'target'
            root.mkdir()
            outside = Path(folder) / 'outside'
            outside.mkdir()
            marker = outside / 'mykos-install'
            marker.write_text('keep outside target')
            (root / 'usr').mkdir()
            (root / 'usr/bin').symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                target.configure_target(root)
            self.assertEqual(marker.read_text(), 'keep outside target')
