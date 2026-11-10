"""Checks run as the installed test user; package changes stay in its disposable VM."""
import json


NETWORK = r'''
import os, socket, subprocess, urllib.request
from pathlib import Path
def check(args):
    try:
        p=subprocess.run(args,capture_output=True,text=True,timeout=30)
        return {'returncode':p.returncode,'stdout':p.stdout[-8000:],'stderr':p.stderr[-2000:]}
    except (OSError,subprocess.TimeoutExpired) as error:
        return {'error':str(error)}
result={'uid':os.getuid(),
        'network_manager':check(['systemctl','is-active','NetworkManager']),
        'devices':check(['nmcli','-t','-f','DEVICE,TYPE,STATE','device']),
        'dhcp':check(['nmcli','-t','-f','DHCP4.OPTION','device','show']),
        'routes':check(['ip','-j','route']),
        'sudo_without_password':check(['sudo','-n','true'])}
try:
    result['dns']={'addresses':sorted({entry[4][0] for entry in socket.getaddrinfo('deb.debian.org',443)})}
except OSError as error:
    result['dns']={'error':str(error)}
try:
    with urllib.request.urlopen('https://deb.debian.org/debian/dists/trixie/InRelease',timeout=30) as response:
        result['https']={'status':response.status,'signed_release_header':response.read(64).startswith(b'-----BEGIN PGP SIGNED MESSAGE-----')}
except (OSError,ValueError) as error:
    result['https']={'error':str(error)}
try:
    result['resolv_conf']=Path('/etc/resolv.conf').read_text()[-4000:]
except OSError as error:
    result['resolv_conf_error']=str(error)
'''


APT = r'''
import subprocess
def check(args,timeout=300):
    try:
        p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
        return {'returncode':p.returncode,'stdout':p.stdout[-12000:],'stderr':p.stderr[-4000:]}
    except (OSError,subprocess.TimeoutExpired) as error:
        return {'error':str(error)}
result={}
present=check(['dpkg-query','-W','-f=${db:Status-Status}','hello'])
if present.get('stdout') == 'installed':
    raise RuntimeError('Test package hello already exists; refusing to remove a pre-existing package.')
commands=[('update',['sudo','-n','apt-get','-o','APT::Update::Error-Mode=any','update']),
          ('install',['sudo','-n','env','DEBIAN_FRONTEND=noninteractive','apt-get','install','-y','--no-install-recommends','hello']),
          ('run',['hello']),
          ('remove',['sudo','-n','env','DEBIAN_FRONTEND=noninteractive','apt-get','purge','-y','hello'])]
for name,args in commands:
    result[name]=check(args)
    if result[name].get('returncode') != 0:
        break
result['final_package_status']=check(['dpkg-query','-W','-f=${db:Status-Status}','hello'])
'''


DISPLAY = r'''
import subprocess
def check(args):
    try:
        p=subprocess.run(args,capture_output=True,text=True,timeout=30)
        return {'returncode':p.returncode,'stdout':p.stdout[-12000:],'stderr':p.stderr[-2000:]}
    except (OSError,subprocess.TimeoutExpired) as error:
        return {'error':str(error)}
result={'sddm':check(['systemctl','status','sddm','--no-pager','-n','30']),
        'greeter':check(['pgrep','-a','-x','sddm-greeter']),
        'sessions':check(['loginctl','list-sessions','--no-legend','--no-pager']),
        'journal':check(['journalctl','-b','-u','sddm','--no-pager','-n','100','-o','cat'])}
'''


GRAPHICAL_SESSION = r'''
import subprocess
sessions=subprocess.check_output(['loginctl','list-sessions','--no-legend','--no-pager'],text=True)
result={'sessions':sessions,'graphical':{}}
for line in sessions.splitlines():
    parts=line.split()
    if len(parts)>3 and parts[2]=='vmtester' and parts[3]=='seat0':
        output=subprocess.check_output(['loginctl','show-session',parts[0],'-p','Name','-p','Type','-p','State','-p','Class','-p','Remote'],text=True)
        result['graphical']=dict(line.split('=',1) for line in output.splitlines() if '=' in line)
'''


SESSION_SERVICES = r'''
import json, os, subprocess
from pathlib import Path
def check(args,env=None):
    try:
        p=subprocess.run(args,env=env,capture_output=True,text=True,timeout=15)
        return {'returncode':p.returncode,'stdout':p.stdout[-8000:],'stderr':p.stderr[-2000:]}
    except (OSError,subprocess.TimeoutExpired) as error:
        return {'error':str(error)}
result={'agents':{}}
for name in ['openbox','lxpolkit','dunst']:
    result['agents'][name]=check(['pgrep','-u',str(os.getuid()),'-x',name])
shell=check(['pgrep','-u',str(os.getuid()),'-x','mykos-shell'])
if shell.get('returncode')==0:
    pid=shell['stdout'].split()[0]
    env=os.environ.copy()
    for item in Path('/proc/'+pid+'/environ').read_bytes().split(b'\0'):
        if b'=' in item:
            key,value=item.split(b'=',1)
            env[key.decode()]=value.decode(errors='replace')
    result['shell_reply']=check(['mykos-shell','--check'],env)
    result['bus']=check(['dbus-send','--session','--print-reply','--dest=org.freedesktop.DBus',
                         '/org/freedesktop/DBus','org.freedesktop.DBus.GetId'],env)
'''


def network_ready(result):
    try:
        routes = json.loads(result['routes']['stdout'])
        return (result['uid'] > 0 and result['network_manager']['stdout'].strip() == 'active'
                and 'dhcp_server_identifier' in result['dhcp']['stdout']
                and any(route.get('dst') == 'default' for route in routes)
                and bool(result['dns'].get('addresses'))
                and result['https'].get('status') == 200
                and result['https'].get('signed_release_header') is True
                and result['sudo_without_password']['returncode'] == 1
                and 'password is required' in result['sudo_without_password']['stderr'])
    except (KeyError, TypeError, ValueError):
        return False


def apt_ready(result):
    return (all(result.get(name, {}).get('returncode') == 0 for name in ['update', 'install', 'run', 'remove'])
            and result.get('final_package_status', {}).get('stdout', '').strip() in {'', 'not-installed', 'config-files'})


def session_services_ready(result):
    if not all(result.get('agents', {}).get(name, {}).get('returncode') == 0
               for name in ['openbox', 'lxpolkit', 'dunst']):
        return False
    response = result.get('shell_reply', {})
    if response.get('returncode') != 0 or result.get('bus', {}).get('returncode') != 0:
        return False
    try:
        reply = json.loads(response.get('stdout', ''))
        return reply.get('desktop') == 'MyKOS' and reply.get('panel') is True and reply.get('ticks', 0) > 0
    except (ValueError, TypeError, AttributeError):
        return False
