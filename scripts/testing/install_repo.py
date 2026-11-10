#!/usr/bin/env python3
"""Run the real automatic installer against a fresh QEMU NVMe, then boot without ISO.

Only a freshly created local QCOW2 is attached as a writable disk. The existing
verified live ISO is read-only rescue media. No host block device is exposed.
"""
import argparse
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import time

from boot_iso import digest, instrument_grub
from vm_session import VM

RESCUE_SHA = 'dd6df477d885b180231708aff16acde049c461338cbbe61adc411a6f436d2b13'
ROOT = Path(__file__).resolve().parents[2]


def wait_installer(vm, predicate, timeout, start):
    def state(text):
        if re.search(r'(?m)^mykos-install: ', text):
            raise RuntimeError('Installer stopped before completing: ' + text[-2500:])
        return predicate(text)
    return vm.wait(state, timeout=timeout, start=start)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('iso', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    iso, out = args.iso.resolve(), args.output.resolve()
    if not iso.is_file() or digest(iso) != RESCUE_SHA or out.exists():
        parser.error('Require the verified rescue ISO and a fresh output directory.')
    if any(',' in str(p) for p in [iso, out, ROOT]):
        parser.error('QEMU paths must not contain commas.')
    out.mkdir(parents=True)
    report = {'status':'failed', 'rescue_iso_sha256':RESCUE_SHA,
              'target':'fresh emulated NVMe QCOW2, 40 GiB',
              'scope':'Automatic disk preparation/install and installed-user console boot without rescue media',
              'instrumentation':'Read-only 9p source share; serial console added to rescue copy; serial getty enabled on installed disk after installation.'}
    vm = None
    started = time.monotonic()
    try:
        disk = out / 'fresh-nvme.qcow2'
        subprocess.run(['qemu-img','create','-f','qcow2',str(disk),'40G'],check=True)
        menu=out/'grub.cfg'
        subprocess.run(['xorriso','-osirrox','on','-indev',str(iso),'-extract','/boot/grub/grub.cfg',str(menu)],check=True)
        menu.chmod(0o600)
        menu.write_text(instrument_grub(menu.read_text(), software=True))
        rescue=out/'rescue-serial.iso'
        subprocess.run(['xorriso','-indev',str(iso),'-outdev',str(rescue),'-boot_image','any','replay',
                        '-map',str(menu),'/boot/grub/grub.cfg','-commit'],check=True)
        def command(directory, live):
            variables=directory/'OVMF_VARS.fd'
            shutil.copy2('/usr/share/OVMF/OVMF_VARS_4M.fd',variables)
            result=['qemu-system-x86_64','-machine','q35,accel=kvm:tcg','-m','6144','-smp','2',
                    '-drive','if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE_4M.fd',
                    '-drive','if=pflash,format=raw,file='+str(variables),
                    '-drive','if=none,id=target,format=qcow2,file='+str(disk),
                    '-device','nvme,drive=target,serial=MYKOS-VM-TEST,bootindex='+('2' if live else '1'),
                    '-display','none','-vga','std','-nic','user,model=virtio-net-pci',
                    '-serial','unix:'+str(directory/'serial.sock')+',server=on,wait=on',
                    '-qmp','unix:'+str(directory/'qmp.sock')+',server=on,wait=off','-no-reboot']
            if live:
                result += ['-drive','if=none,id=live,format=raw,readonly=on,file='+str(rescue),
                           '-device','ide-cd,drive=live,bootindex=1',
                           '-virtfs','local,path='+str(ROOT)+',mount_tag=mykos-source,security_model=none,readonly=on']
            return result
        live=out/'live';live.mkdir()
        vm=VM(command(live, True),live)
        vm.login()
        inventory=vm.guest("import json,subprocess\nresult=json.loads(subprocess.check_output(['lsblk','--json','--bytes','-o','NAME,TYPE,SIZE,SERIAL']))")
        targets=[d for d in inventory['blockdevices'] if d['type']=='disk']
        if len(targets)!=1 or targets[0]['name']!='nvme0n1' or int(targets[0]['size'])!=40*1024**3 or targets[0].get('children'):
            raise RuntimeError('Refuse anything except exactly one fresh 40 GiB emulated NVMe.')
        report['inventory']=inventory
        vm.guest("import subprocess\nsubprocess.run(['sudo','mkdir','-p','/mnt/mykos-source'],check=True)\nsubprocess.run(['sudo','mount','-t','9p','-o','trans=virtio,version=9p2000.L,ro','mykos-source','/mnt/mykos-source'],check=True)\nresult={'source_ready':True}")
        start=len(vm.transcript)
        vm.serial.sendall(b'sudo /mnt/mykos-source/install --hostname mykos-installed\r')
        wait_installer(vm,lambda text:'Chọn ổ cài' in text or '[1]:' in text,300,start)
        vm.serial.sendall(b'1\r')
        start=len(vm.transcript)
        wait_installer(vm,lambda text:'[mykos]:' in text,60,start)
        vm.serial.sendall(b'vmtester\r')
        start=len(vm.transcript)
        wait_installer(vm,lambda text:'Confirm: ' in text,300,start)
        vm.serial.sendall(b'XOA VA CAI MYKOS\r')
        password='Mykos-'+secrets.token_hex(12)
        start=len(vm.transcript)
        wait_installer(vm,lambda text:' / Password: ' in text,60,start)
        vm.serial.sendall((password+'\r').encode())
        start=len(vm.transcript)
        wait_installer(vm,lambda text:' / Repeat password: ' in text,60,start)
        vm.serial.sendall((password+'\r').encode())
        start=len(vm.transcript)
        wait_installer(vm,lambda text:re.search(r'(?m)^MYKOS_INSTALL_COMPLETE\s*$',text),2400,start)
        report['automatic_install']='complete'
        vm.capture('installed-from-rescue')
        # Read the installed tree and enable console observation only. Do not alter
        # fstab, bootloader, credentials or the production installer result.
        report['target_checks']=vm.guest(r'''
import json,subprocess
from pathlib import Path
def run(argv):return subprocess.run(['sudo',*argv],check=True,text=True,capture_output=True).stdout
run(['mkdir','-p','/mnt/installed-check'])
run(['mount','/dev/nvme0n1p2','/mnt/installed-check'])
try:
    text=run(['cat','/mnt/installed-check/etc/os-release'])
    config=json.loads(run(['cat','/mnt/installed-check/etc/mykos-install.json']))
    fstab=run(['cat','/mnt/installed-check/etc/fstab'])
    run(['systemctl','--root=/mnt/installed-check','enable','serial-getty@ttyS0.service'])
    result={'os_release':text,'install_record':config,'fstab':fstab}
finally:run(['umount','/mnt/installed-check'])
''')
        if 'ID=mykos' not in report['target_checks']['os_release']:
            raise RuntimeError('Target identity is not MyKOS.')
        vm.close();vm=None
        installed=out/'installed';installed.mkdir()
        vm=VM(command(installed, False),installed)
        vm.login(username='vmtester',hostname='mykos-installed',password=password)
        report['booted_without_iso']=vm.guest(r'''
import json,os,socket,subprocess
from pathlib import Path
result={'uid':os.getuid(),'hostname':socket.gethostname(),'cmdline':Path('/proc/cmdline').read_text(),
 'root':json.loads(subprocess.check_output(['findmnt','--json','--mountpoint','/','-o','SOURCE,FSTYPE'])),
 'sddm':subprocess.run(['systemctl','is-active','sddm'],capture_output=True,text=True).stdout.strip(),
 'network':subprocess.run(['systemctl','is-active','NetworkManager'],capture_output=True,text=True).stdout.strip(),
 'session_present':Path('/usr/share/xsessions/mykos.desktop').is_file(),
 'passwordless_sudo':subprocess.run(['sudo','-n','true'],capture_output=True,text=True).returncode}
''')
        check=report['booted_without_iso']
        if not (check['uid']==1000 and check['hostname']=='mykos-installed' and 'boot=live' not in check['cmdline']
                and check['root']['filesystems'][0]['fstype']=='ext4' and check['session_present']
                and check['sddm']=='active' and check['network']=='active' and check['passwordless_sudo']!=0):
            raise RuntimeError('Installed-user boot checks did not pass.')
        vm.authenticate_sudo(password)
        vm.capture('installed-boot')
        report['status']='installed-cli-ready'
    except (OSError,ValueError,RuntimeError,TimeoutError,subprocess.SubprocessError) as error:
        report['error']=str(error)
    finally:
        if vm is not None:
            try:vm.capture('final-screen')
            except OSError:pass
            vm.close()
        report['elapsed_seconds']=round(time.monotonic()-started,1)
        (out/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report['status']=='installed-cli-ready' else 1


if __name__=='__main__':
    raise SystemExit(main())
