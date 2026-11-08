#!/usr/bin/env python3
"""Collect Plasma user-bus diagnostics from a live VM without attaching an installation disk."""
import argparse
import json
from pathlib import Path
import subprocess
import time

from boot_iso import digest, prepare_menu
from installed_smoke import SESSION_SERVICES
from probe_desktop import SOFTWARE_PARAMETERS
from vm_session import VM


READY = r'''
import json,os,subprocess,time
from pathlib import Path
result={'uid':os.getuid(),'plasma':False}
deadline=time.monotonic()+180
while time.monotonic()<deadline:
    p=subprocess.run(['pgrep','-u',str(os.getuid()),'-x','plasmashell'],capture_output=True,text=True)
    if p.returncode==0:
        result['plasma']=True
        pid=p.stdout.split()[0]
        env=os.environ.copy()
        for item in Path('/proc/'+pid+'/environ').read_bytes().split(b'\0'):
            if b'=' in item:
                key,value=item.split(b'=',1);env[key.decode()]=value.decode(errors='replace')
        env['QT_SELECT']='qt5'
        try:
            q=subprocess.run(['qdbus','org.kde.plasmashell','/PlasmaShell','org.kde.PlasmaShell.evaluateScript','print(JSON.stringify({panels:panels().length,desktops:desktops().length}))'],env=env,capture_output=True,text=True,timeout=15)
            result['containments']={'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr}
            counts=json.loads(q.stdout)
            if counts.get('panels',0)>0 and counts.get('desktops',0)>0: break
        except (OSError,ValueError,subprocess.TimeoutExpired):
            pass
    time.sleep(3)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('iso', type=Path)
    parser.add_argument('--expected-sha', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    iso, output = args.iso.resolve(), args.output.resolve()
    if not iso.is_file() or output.exists() or digest(iso) != args.expected_sha:
        parser.error('Need the exact source ISO and a new output directory.')
    output.mkdir(parents=True)
    report = {'status': 'failed', 'iso_sha256': args.expected_sha,
              'scope': 'Live user-bus diagnostic only; no installation disk attached, not desktop acceptance.'}
    vm = None
    started = time.monotonic()
    try:
        menu = output / 'isolinux.cfg'
        subprocess.run(['xorriso', '-osirrox', 'on', '-indev', str(iso), '-extract', '/isolinux/isolinux.cfg', str(menu)], check=True)
        prepare_menu(menu)
        menu.write_text('\n'.join(line + SOFTWARE_PARAMETERS if line.lstrip().startswith('append ')
                                  else line for line in menu.read_text().splitlines()) + '\n')
        probe = output / 'session-probe.iso'
        subprocess.run(['xorriso', '-indev', str(iso), '-outdev', str(probe), '-boot_image', 'any', 'replay',
                        '-map', str(menu), '/isolinux/isolinux.cfg', '-commit'], check=True)
        command = ['qemu-system-x86_64', '-machine', 'accel=kvm:tcg', '-m', '4096', '-smp', '2',
                   '-boot', 'order=d', '-cdrom', str(probe), '-display', 'none', '-vga', 'std',
                   '-nic', 'user,model=virtio-net-pci',
                   '-serial', 'unix:' + str(output / 'serial.sock') + ',server=on,wait=on',
                   '-qmp', 'unix:' + str(output / 'qmp.sock') + ',server=on,wait=off', '-no-reboot']
        report['command'] = command
        report['probe_iso_sha256'] = digest(probe)
        vm = VM(command, output)
        print('Session diagnostic: waiting for live console', flush=True)
        vm.login()
        report['desktop'] = vm.guest(READY, timeout=240)
        report['services'] = vm.guest(SESSION_SERVICES, timeout=240)
        report['status'] = 'session-diagnostic-collected'
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        report['error'] = str(error)
    finally:
        if vm:
            try:
                vm.capture('session-diagnostic')
            except OSError as error:
                report['screenshot_error'] = str(error)
            vm.close()
        report['elapsed_seconds'] = round(time.monotonic() - started, 1)
        (output / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['status'] == 'session-diagnostic-collected' else 1


if __name__ == '__main__':
    raise SystemExit(main())
