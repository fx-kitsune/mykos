"""No disk writes: test installer plans, target guards, deployment and mount cleanup."""
import argparse
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('terminal_installer', ROOT / 'scripts/install/mykos-install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


def options(**updates):
    values = dict(action='install', target='/mnt/mykos', mode='uefi', boot_disk=None, username='alice', hostname='mykos',
                  keyring='/usr/share/keyrings/debian-archive-keyring.gpg', confirm_uuid=None, disk=None)
    values.update(updates)
    return argparse.Namespace(**values)


class TerminalInstallerTests(unittest.TestCase):
    def test_wizard_selects_nvme_without_asking_for_mount_or_uuid(self):
        args = options(action='wizard', target=None)
        disk = {'path':'/dev/nvme0n1', 'maj:min':'259:0', 'type':'disk',
                'size':500 * 1024**3, 'serial':'NVME-TEST', 'model':'Demo NVMe', 'tran':'nvme'}
        with patch.object(installer.sys.stdin, 'isatty', return_value=True), \
             patch('builtins.input', side_effect=['1', 'alice']) as prompt, \
             patch.object(installer.disk_layout, 'scan', return_value={'candidates':[disk], 'excluded':[]}), \
             patch.object(installer, 'run') as run:
            installer.wizard_options(args)
        self.assertEqual(args.disk, '/dev/nvme0n1')
        self.assertIsNone(args.target)
        self.assertEqual(args.username, 'alice')
        self.assertEqual(prompt.call_count, 2)
        run.assert_not_called()

    def test_plan_is_read_only_and_excludes_live_credentials_and_live_packages(self):
        with patch.object(installer, 'run', side_effect=AssertionError('plan executed a process')):
            result = installer.plan(options())
        self.assertFalse(result['formats_disks'])
        self.assertFalse(result['partitions_disks'])
        self.assertIn('linux-image-amd64', result['packages'])
        self.assertIn('grub-efi-amd64-bin', result['packages'])
        self.assertFalse(installer.LIVE_ONLY.intersection(result['packages']) - {'grub2-common'})
        self.assertNotIn('calamares', result['packages'])
        self.assertNotIn('plasma-desktop', result['packages'])
        bios = installer.plan(options(mode='bios', boot_disk='/dev/sdz'))
        self.assertIn('grub-pc-bin', bios['packages'])

    def test_rejects_host_paths_root_user_and_missing_bios_boot_disk(self):
        for changes in [dict(target='/'), dict(target='/home'), dict(target='/mnt/../usr'),
                        dict(username='root'), dict(username='alice;sh'), dict(hostname='bad\nname'),
                        dict(mode='bios'), dict(mode='bios', boot_disk='/dev/sda;wipe')]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                installer.plan(options(**changes))

    def test_nonroot_install_cannot_write_or_prompt(self):
        with patch.object(installer.os, 'geteuid', return_value=1000), \
             patch.object(installer, 'run') as run, patch.object(installer.getpass, 'getpass') as password:
            with self.assertRaises(ValueError):
                installer.install(options())
            run.assert_not_called()
            password.assert_not_called()

    def test_rejects_running_root_and_boot_disk_mismatch(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            args = options(target=str(target), mode='bios', boot_disk='/dev/sdz')
            root = dict(target=str(target), source='/dev/sda2', fstype='ext4', uuid='aaaa-bbbb')
            host = dict(target='/', source='/dev/sda2', fstype='ext4', uuid='aaaa-bbbb')
            with patch.object(installer, 'validate_options', return_value=target), \
                 patch.object(installer, 'mount_record', side_effect=[root, host]):
                with self.assertRaisesRegex(ValueError, 'currently running'):
                    installer.inspect_target(args)
            host.update(source='overlay', uuid=None)
            with patch.object(installer, 'validate_options', return_value=target), \
                 patch.object(installer, 'mount_record', side_effect=[root, host]), \
                 patch.object(installer, 'disk_ancestors', return_value={'/dev/sda'}):
                with self.assertRaisesRegex(ValueError, 'parent disk'):
                    installer.inspect_target(args)

    def test_nonempty_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            (target / 'important.txt').write_text('keep')
            with self.assertRaises(ValueError):
                installer.require_empty(target)
            self.assertEqual((target / 'important.txt').read_text(), 'keep')

    def test_uuid_confirmation_is_required_before_password_or_disk_writes(self):
        root = dict(source='/dev/sdz2', uuid='target-uuid', fstype='ext4')
        with tempfile.TemporaryDirectory() as folder, \
             patch.object(installer.os, 'geteuid', return_value=0), \
             patch.object(installer.shutil, 'which', return_value='/usr/bin/tool'), \
             patch.object(installer, 'inspect_target', return_value=(Path(folder), root, None, '/dev/sdz')), \
             patch.object(installer, 'run') as run, \
             patch.object(installer.getpass, 'getpass') as password:
            # The real Debian keyring is present on the test host.
            keyring = Path(folder) / 'archive.gpg'
            keyring.write_bytes(b'not used; no bootstrap should run')
            with self.assertRaisesRegex(ValueError, '--confirm-uuid target-uuid'):
                installer.install(options(keyring=str(keyring), confirm_uuid='wrong-uuid'))
            run.assert_not_called()
            password.assert_not_called()
            self.assertFalse((Path(folder) / '.mykos-install.lock').exists())

    def test_cleanup_only_unmounts_created_mounts_in_reverse_order_on_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            calls = []
            with patch.object(installer, 'run', side_effect=lambda argv, **kw: calls.append(argv)):
                with self.assertRaisesRegex(RuntimeError, 'simulated package failure'):
                    with installer.target_mounts(target):
                        raise RuntimeError('simulated package failure')
            unmounts = [argv[-1] for argv in calls if argv[0] == 'umount']
            self.assertEqual(unmounts, [str(target / name) for name in ['run', 'proc', 'sys', 'dev']])
            self.assertNotIn(str(target), unmounts)
            self.assertNotIn(str(target / 'boot/efi'), unmounts)

    def test_deployment_installs_own_session_without_live_autologin_hook(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            (target / 'etc').mkdir()
            installer.deploy_desktop(target)
            self.assertEqual((target / 'usr/bin/mykos-session').stat().st_mode & 0o777, 0o755)
            self.assertTrue((target / 'usr/share/mykos/shell/Shell.qml').is_file())
            self.assertIn('ID=mykos', (target / 'etc/os-release').read_text())
            self.assertFalse((target / 'usr/lib/live/config/0099-mykos-session').exists())
            self.assertNotIn('User=', (target / 'etc/sddm.conf.d/10-mykos.conf').read_text())
            self.assertFalse((target / 'usr/share/calamares').exists())

    def test_boot_layout_checks_reject_data_fat_partition_and_missing_bios_grub(self):
        with patch.object(installer, 'output', return_value='basic-data-guid'):
            with self.assertRaisesRegex(ValueError, 'EFI System Partition'):
                installer.validate_boot_layout('uefi', '/dev/sdz', {'source':'/dev/sdz1'})
        with patch.object(installer, 'output', side_effect=['gpt', '{"blockdevices":[{"children":[]}]}']):
            with self.assertRaisesRegex(ValueError, 'bios_grub'):
                installer.validate_boot_layout('bios', '/dev/sdz', None)
        with patch.object(installer, 'output', return_value='c12a7328-f81f-11d2-ba4b-00a0c93ec93b'):
            installer.validate_boot_layout('uefi', '/dev/sdz', {'source':'/dev/sdz1'})

    def test_target_write_cannot_escape_through_symlink(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            target = base / 'target'
            outside = base / 'outside'
            target.mkdir(); outside.mkdir()
            (target / 'etc').symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                installer.write(target, 'etc/fstab', 'should not escape')
            self.assertFalse((outside / 'fstab').exists())
