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
    result['dns']={'addresses':sorted({entry[4][0] for entry in socket.getaddrinfo('archive.ubuntu.com',443)})}
except OSError as error:
    result['dns']={'error':str(error)}
try:
    with urllib.request.urlopen('https://archive.ubuntu.com/ubuntu/dists/noble/InRelease',timeout=30) as response:
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
import os, subprocess
from pathlib import Path
def check(args,env=None):
    try:
        p=subprocess.run(args,env=env,capture_output=True,text=True,timeout=30)
        return {'returncode':p.returncode,'stdout':p.stdout[-16000:],'stderr':p.stderr[-2000:]}
    except (OSError,subprocess.TimeoutExpired) as error:
        return {'error':str(error)}
keys=['DBUS_SESSION_BUS_ADDRESS','XDG_RUNTIME_DIR','DISPLAY','XAUTHORITY','XDG_SESSION_ID','XDG_CURRENT_DESKTOP','KWIN_COMPOSE','QT_QUICK_BACKEND']
result={'serial_environment':{key:os.environ.get(key) for key in keys},'processes':[],
        'units':check(['systemctl','--user','show','dbus.service','plasma-polkit-agent.service','plasma-powerdevil.service','plasma-kscreen.service','-p','Id,Type,BusName,MainPID,ActiveState,SubState,Result,NRestarts,TimeoutStartUSec']),
        'unit_definitions':check(['systemctl','--user','cat','dbus.service','plasma-polkit-agent.service','plasma-powerdevil.service']),
        'manager_environment':check(['systemctl','--user','show-environment']),
        'packages':check(['dpkg-query','-W','-f=${binary:Package} ${db:Status-Status} ${Version}\n','dbus-user-session','dbus-x11','dbus-daemon']),
        'session_list':check(['loginctl','list-sessions','--no-legend','--no-pager'])}
# Keep only session/graphics keys; never return the complete process or manager environment.
if 'stdout' in result['manager_environment']:
    result['manager_environment']['stdout']='\n'.join(line for line in result['manager_environment']['stdout'].splitlines() if line.split('=',1)[0] in keys)
for line in subprocess.check_output(['ps','-u',str(os.getuid()),'-o','pid=,ppid=,comm=,args='],text=True).splitlines():
    parts=line.split(None,3)
    if len(parts)<4 or parts[2] not in ['dbus-daemon','plasmashell','systemd','polkit-kde-auth','org_kde_powerde']:
        continue
    pid=parts[0]
    item={'pid':pid,'ppid':parts[1],'command':parts[3]}
    try:
        env=os.environ.copy()
        for entry in Path('/proc/'+pid+'/environ').read_bytes().split(b'\0'):
            if b'=' in entry:
                key,value=entry.split(b'=',1)
                env[key.decode()]=value.decode(errors='replace')
        item['environment']={key:env.get(key) for key in keys}
        if parts[2]=='plasmashell':
            item['bus_id']=check(['dbus-send','--session','--print-reply','--dest=org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus.GetId'],env)
            item['bus_names']=check(['dbus-send','--session','--print-reply','--dest=org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus.ListNames'],env)
    except OSError as error:
        item['error']=str(error)
    result['processes'].append(item)
result['serial_bus_id']=check(['dbus-send','--session','--print-reply','--dest=org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus.GetId'])
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
