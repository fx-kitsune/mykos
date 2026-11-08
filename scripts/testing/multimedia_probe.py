"""Exercise the installed X11 display and PipeWire output; inspect QEMU's PCM capture."""
from array import array
import math
import sys
import wave


GUEST = r'''
import math, os, re, subprocess, time, wave
from array import array
from pathlib import Path
pid=subprocess.check_output(['pgrep','-u',str(os.getuid()),'-x','plasmashell'],text=True).split()[0]
env=os.environ.copy()
for item in Path('/proc/'+pid+'/environ').read_bytes().split(b'\0'):
    if b'=' in item:
        key,value=item.split(b'=',1)
        env[key.decode()]=value.decode(errors='replace')
def command(args):
    try:
        p=subprocess.run(args,env=env,capture_output=True,text=True,timeout=45)
        return {'returncode':p.returncode,'stdout':p.stdout[-12000:],'stderr':p.stderr[-2000:]}
    except (OSError,subprocess.TimeoutExpired) as error:
        return {'error':str(error)}
result={'uid':os.getuid()}
note=Path.home()/'Documents/mykos-smoke.txt'
note.parent.mkdir(exist_ok=True)
text='MyKOS installed-user file check\n'
note.write_text(text)
result['file']={'path':str(note),'content_matches':note.read_text()==text,'owner_uid':note.stat().st_uid}
query=command(['xrandr','--query'])
result['display_query']=query
match=re.search(r'(?m)^(\S+) connected(?: primary)? (\d+x\d+)\+',query.get('stdout',''))
if match:
    output,original=match.groups()
    alternate='1024x768' if original!='1024x768' else '800x600'
    result['display']={'output':output,'original':original,'alternate':alternate}
    try:
        result['display']['change']=command(['xrandr','--output',output,'--mode',alternate])
        time.sleep(2)
        result['display']['changed']=command(['xrandr','--query'])
    finally:
        result['display']['restore']=command(['xrandr','--output',output,'--mode',original])
        time.sleep(2)
        result['display']['restored']=command(['xrandr','--query'])
result['pipewire_before']=command(['systemctl','--user','is-active','pipewire','wireplumber'])
result['audio_status']=command(['wpctl','status','-n'])
volume=command(['wpctl','get-volume','@DEFAULT_AUDIO_SINK@'])
result['audio']={'original':volume}
match=re.search(r'Volume:\s*([0-9.]+)',volume.get('stdout',''))
if match:
    original=match.group(1)
    muted='[MUTED]' in volume['stdout']
    tone=Path('/tmp/mykos-audio-tone.wav')
    samples=array('h')
    for frame in range(48000*2):
        value=round(6000*math.sin(2*math.pi*440*frame/48000))
        samples.extend([value,value])
    with wave.open(str(tone),'wb') as output:
        output.setnchannels(2); output.setsampwidth(2); output.setframerate(48000)
        output.writeframes(samples.tobytes())
    try:
        result['audio']['set_volume']=command(['wpctl','set-volume','@DEFAULT_AUDIO_SINK@','0.5'])
        result['audio']['unmute']=command(['wpctl','set-mute','@DEFAULT_AUDIO_SINK@','0'])
        result['audio']['play']=command(['pw-play',str(tone)])
    finally:
        result['audio']['restore_volume']=command(['wpctl','set-volume','@DEFAULT_AUDIO_SINK@',original])
        result['audio']['restore_mute']=command(['wpctl','set-mute','@DEFAULT_AUDIO_SINK@','1' if muted else '0'])
result['pipewire']=command(['systemctl','--user','is-active','pipewire','wireplumber'])
result['file']['content_matches']=note.read_text()==text
result['flatpak_version']=command(['flatpak','--version'])
result['flatpak_remotes']=command(['flatpak','remotes','--columns=name,url'])
with open('/tmp/mykos-discover-smoke.log','w') as log:
    subprocess.Popen(['plasma-discover'],env=env,stdout=log,stderr=subprocess.STDOUT)
time.sleep(30)
result['discover']=command(['pgrep','-u',str(os.getuid()),'-x','plasma-discover'])
result['discover_log']=Path('/tmp/mykos-discover-smoke.log').read_text(errors='replace')[-5000:]
'''


def guest_ready(result):
    import re
    try:
        display = result['display']
        output = re.escape(display['output'])
        for key, mode in [('changed', display['alternate']), ('restored', display['original'])]:
            if re.search(r'(?m)^' + output + r' connected(?: primary)? ' + re.escape(mode) + r'\+', display[key]['stdout']) is None:
                return False
        return (result['uid'] > 0 and result['file']['content_matches'] is True
                and result['file']['owner_uid'] == result['uid']
                and result['pipewire']['returncode'] == 0
                and all(result[key]['returncode'] == 0 for key in ['flatpak_version', 'flatpak_remotes', 'discover'])
                and all(result['audio'][key]['returncode'] == 0 for key in
                        ['original', 'set_volume', 'unmute', 'play', 'restore_volume', 'restore_mute']))
    except (KeyError, TypeError):
        return False


def _power(samples, rate, frequency):
    coefficient = 2 * math.cos(2 * math.pi * frequency / rate)
    previous = before_previous = 0.0
    for sample in samples:
        current = sample + coefficient * previous - before_previous
        before_previous, previous = previous, current
    return previous**2 + before_previous**2 - coefficient * previous * before_previous


def analyze_wave(path, start_bytes=0, evidence_path=None):
    result = {'tone_detected': False, 'max_rms': 0.0, 'max_tone_ratio': 0.0}
    with wave.open(str(path), 'rb') as source:
        channels, width, rate, frames = source.getnchannels(), source.getsampwidth(), source.getframerate(), source.getnframes()
        result.update(channels=channels, sample_width=width, sample_rate=rate, frames=frames,
                      duration_seconds=round(frames / rate, 2))
        if width != 2 or channels < 1 or rate < 8000:
            return result
        source.setpos(min(frames, start_bytes // (channels * width)))
        while data := source.readframes(rate // 4):
            samples = array('h')
            samples.frombytes(data)
            if sys.byteorder != 'little':
                samples.byteswap()
            mono = samples[::channels]
            rms = math.sqrt(sum(value**2 for value in mono) / len(mono)) / 32768
            result['max_rms'] = max(result['max_rms'], rms)
            if rms < .001:
                continue
            ratio = _power(mono, rate, 440) / max(1.0, _power(mono, rate, 400), _power(mono, rate, 480))
            result['max_tone_ratio'] = max(result['max_tone_ratio'], ratio)
            if ratio > 10:
                if not result['tone_detected'] and evidence_path is not None:
                    with wave.open(str(evidence_path), 'wb') as evidence:
                        evidence.setnchannels(channels)
                        evidence.setsampwidth(width)
                        evidence.setframerate(rate)
                        evidence.writeframes(data)
                result['tone_detected'] = True
    return result
