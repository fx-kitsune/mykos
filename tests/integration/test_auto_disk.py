"""Whole-disk safety boundaries; no commands here target a real block device."""
from contextlib import nullcontext
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/install'))
import disk_layout as disks
import bootstrap_tools
spec = importlib.util.spec_from_file_location('auto_installer', ROOT / 'scripts/install/mykos-install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


def drive(path, identifier, **kwargs):
    return dict(path=path, name=path, **{'maj:min':identifier}, type='disk',
                size=40 * 1024**3, model='Test NVMe', serial=identifier, tran='nvme', ro=False, rm=False, **kwargs)


def partition(path, identifier, mounts=None):
    return dict(path=path, **{'maj:min':identifier}, type='part', size=39 * 1024**3,
                mountpoints=mounts or [], fstype='ext4')


class AutoDiskTests(unittest.TestCase):
    def test_running_disk_excluded_and_nvme_target_selected(self):
        host = drive('/dev/nvme0n1', '259:0', children=[partition('/dev/nvme0n1p1','259:1',['/'])])
        target = drive('/dev/nvme1n1', '259:2')
        choices, excluded, *_ = disks.assess([host,target], [{'target':'/','maj:min':'259:1'}], [Path('/source')])
        self.assertEqual([d['path'] for d in choices], ['/dev/nvme1n1'])
        self.assertEqual(excluded[0]['path'], '/dev/nvme0n1')

    def test_loop_backed_iso_protects_rescue_disk_even_if_not_removable(self):
        rescue = drive('/dev/nvme0n1','259:0',children=[partition('/dev/nvme0n1p1','259:1')])
        target = drive('/dev/nvme1n1','259:2')
        loop = dict(path='/dev/loop0', type='loop', **{'maj:min':'7:0'})
        choices, *_ = disks.assess([rescue,target,loop], [{'target':'/','maj:min':'7:0'}], [Path('/source')],
                                   backing_file=lambda key:'/iso/rescue.iso' if key=='7:0' else None,
                                   source_for_path=lambda path:'259:1')
        self.assertEqual([d['path'] for d in choices], ['/dev/nvme1n1'])
        with self.assertRaises(ValueError):
            disks.assess([rescue,target,loop], [{'target':'/','maj:min':'7:0'}], [], backing_file=lambda _:None)

    def test_persistent_overlay_protects_internal_cow_partition(self):
        persistence=drive('/dev/nvme0n1','259:0',children=[partition('/dev/nvme0n1p1','259:1')])
        target=drive('/dev/nvme1n1','259:2')
        mount={'target':'/','maj:min':'0:44','fstype':'overlay',
               'options':'rw,lowerdir=/rofs,upperdir=/cow/upper,workdir=/cow/work'}
        choices,*_=disks.assess([persistence,target],[mount],[],
            source_for_path=lambda path:'259:1')
        self.assertEqual([row['path'] for row in choices],['/dev/nvme1n1'])

    def test_repository_disk_and_usb_are_not_erasable_candidates(self):
        source = drive('/dev/nvme0n1','259:0',children=[partition('/dev/nvme0n1p1','259:1')])
        usb = drive('/dev/sda','8:0'); usb['tran']='usb'
        choices, excluded, *_ = disks.assess([source,usb],
            [{'target':'/mnt/source','maj:min':'259:1'}], [Path('/mnt/source/mykos')])
        self.assertEqual(choices, [])
        self.assertEqual(len(excluded),2)

    def test_active_device_mapper_holders_and_read_only_disks_are_excluded(self):
        holder = dict(path='/dev/mapper/used',type='crypt',**{'maj:min':'253:0'})
        used=drive('/dev/nvme0n1','259:0',children=[dict(partition('/dev/nvme0n1p1','259:1'),children=[holder])])
        readonly=drive('/dev/nvme1n1','259:2');readonly['ro']=True
        self.assertEqual(disks.assess([used,readonly], [], [])[0], [])

    def test_changed_identity_aborts_before_any_write(self):
        original=drive('/dev/nvme0n1','259:0')
        changed=dict(original,serial='DIFFERENT')
        with patch.object(disks,'scan',return_value={'candidates':[changed]}), \
             patch.object(disks,'run') as run:
            with self.assertRaisesRegex(ValueError,'thay đổi'):
                disks.selected('/dev/nvme0n1',[],disks.identity(original))
            run.assert_not_called()

    def test_busy_mount_aborts_before_partitioning(self):
        disk=drive('/dev/nvme0n1','259:0')
        with patch.object(disks,'selected',return_value=(disk,{})), \
             patch.object(disks,'release_mounts',side_effect=RuntimeError('busy')), \
             patch.object(disks,'run') as run:
            with self.assertRaisesRegex(RuntimeError,'busy'):
                disks.prepare(disk,'uefi',[])
            run.assert_not_called()

    def test_layout_handles_nvme_without_constructing_partition_names(self):
        self.assertIn(disks.EFI_TYPE,disks.layout('uefi'))
        self.assertIn(disks.BIOS_TYPE,disks.layout('bios'))
        self.assertNotIn('/dev/',disks.layout('uefi'))
        self.assertIn(disks.ROOT_TYPE,disks.layout('uefi'))

    def test_failed_unmount_never_recursively_deletes_new_system(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'mounted';target.mkdir()
            marker=target/'important.txt';marker.write_text('installed data')
            def fake_run(argv,**kwargs):
                if argv[0]=='umount':raise subprocess.CalledProcessError(1,argv)
            with patch.object(installer.tempfile,'mkdtemp',return_value=str(target)), \
                 patch.object(installer,'run',side_effect=fake_run):
                with self.assertRaisesRegex(RuntimeError,'giữ nguyên'):
                    with installer.mounted_new_system('/dev/fake',None):pass
            self.assertEqual(marker.read_text(),'installed data')

    def test_cancelled_confirmation_never_prepares_disk_or_asks_password(self):
        import argparse
        args=argparse.Namespace(disk='/dev/nvme0n1',disk_identity=None,target=None,mode='bios',
                                username='alice',hostname='mykos',action='install')
        disk=drive('/dev/nvme0n1','259:0')
        with patch.object(installer.os,'geteuid',return_value=0), \
             patch.object(installer.sys.stdin,'isatty',return_value=True), \
             patch.object(installer.bootstrap_tools,'ensure_host_tools'), \
             patch.object(installer.bootstrap_tools,'prepare',return_value=(None,None,{})), \
             patch.object(installer.disk_layout,'selected',return_value=(disk,{})), \
             patch.object(installer.disk_layout,'prepare') as prepare, \
             patch.object(installer,'read_password') as password, \
             patch.object(installer,'disk_lock',return_value=nullcontext()), \
             patch('builtins.input',return_value=''):
            installer.install_automatic(args)
        prepare.assert_not_called()
        password.assert_not_called()

    def test_firmware_check_distinguishes_disabled_enabled_and_unsupported(self):
        with tempfile.TemporaryDirectory() as folder:
            directory=Path(folder)
            with self.assertRaises(ValueError):installer.firmware_secure_boot(directory)
            (directory/'BootOrder-test').write_bytes(b'firmware')
            self.assertFalse(installer.firmware_secure_boot(directory))
            sb=directory/'SecureBoot-8be4df61-93ca-11d2-aa0d-00e098032b8c'
            sb.write_bytes(b'\x06\x00\x00\x00\x00')
            self.assertFalse(installer.firmware_secure_boot(directory))
            sb.write_bytes(b'\x06\x00\x00\x00\x01')
            self.assertTrue(installer.firmware_secure_boot(directory))

    def test_corrupt_bootstrap_payload_is_rejected_before_unpack(self):
        with tempfile.TemporaryDirectory() as folder, \
             patch.object(bootstrap_tools,'download',return_value=b'corrupted'), \
             patch.object(bootstrap_tools,'unpack_deb') as unpack:
            with self.assertRaisesRegex(ValueError,'checksum mismatch'):
                bootstrap_tools.prepare(folder,'trixie')
            unpack.assert_not_called()

    @unittest.skipUnless(shutil.which('sfdisk'),'sfdisk required for real partition-table tests')
    def test_real_gpt_layout_on_sparse_regular_files_for_512_and_4096_sectors(self):
        for mode in ['bios','uefi']:
            for sector in [512,4096]:
                with self.subTest(mode=mode,sector=sector), tempfile.TemporaryDirectory() as folder:
                    image=Path(folder)/'disposable.img'
                    with image.open('wb') as stream:stream.truncate(40*1024**3)
                    subprocess.run(['sfdisk','--sector-size',str(sector),str(image)],input=disks.layout(mode),
                                   text=True,check=True,capture_output=True)
                    table=json.loads(subprocess.check_output(['sfdisk','--sector-size',str(sector),'--json',str(image)],text=True))['partitiontable']
                    self.assertEqual(table['label'],'gpt')
                    self.assertEqual(table['sectorsize'],sector)
                    parts=table['partitions']
                    self.assertEqual(len(parts),2)
                    self.assertEqual(parts[0]['type'].lower(),disks.EFI_TYPE if mode=='uefi' else disks.BIOS_TYPE)
                    self.assertEqual(parts[1]['type'].lower(),disks.ROOT_TYPE)
                    self.assertEqual(parts[0]['start']*sector % 1024**2,0)
