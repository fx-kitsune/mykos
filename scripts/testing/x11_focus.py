"""Verified EWMH window activation in the test guest, independent of desktop stacking."""

CORE = r'''
import ctypes as c,os,time
class MessageData(c.Union):
    _fields_=[('b',c.c_char*20),('s',c.c_short*10),('l',c.c_long*5)]
class ClientMessage(c.Structure):
    _fields_=[('type',c.c_int),('serial',c.c_ulong),('send_event',c.c_int),('display',c.c_void_p),('window',c.c_ulong),('message_type',c.c_ulong),('format',c.c_int),('data',MessageData)]
class Event(c.Union):
    _fields_=[('client',ClientMessage),('padding',c.c_long*24)]
def focus_window(title):
    x=c.CDLL('libX11.so.6')
    x.XOpenDisplay.argtypes=[c.c_char_p];x.XOpenDisplay.restype=c.c_void_p
    x.XDefaultRootWindow.argtypes=[c.c_void_p];x.XDefaultRootWindow.restype=c.c_ulong
    x.XInternAtom.argtypes=[c.c_void_p,c.c_char_p,c.c_int];x.XInternAtom.restype=c.c_ulong
    x.XGetWindowProperty.argtypes=[c.c_void_p,c.c_ulong,c.c_ulong,c.c_long,c.c_long,c.c_int,c.c_ulong,c.POINTER(c.c_ulong),c.POINTER(c.c_int),c.POINTER(c.c_ulong),c.POINTER(c.c_ulong),c.POINTER(c.POINTER(c.c_ubyte))]
    x.XFetchName.argtypes=[c.c_void_p,c.c_ulong,c.POINTER(c.c_void_p)]
    x.XFree.argtypes=[c.c_void_p]
    x.XSendEvent.argtypes=[c.c_void_p,c.c_ulong,c.c_int,c.c_long,c.POINTER(Event)]
    x.XFlush.argtypes=[c.c_void_p];x.XCloseDisplay.argtypes=[c.c_void_p]
    display=x.XOpenDisplay(os.environ.get('DISPLAY','').encode())
    if not display: raise RuntimeError('Cannot connect to the Plasma X11 display.')
    root=x.XDefaultRootWindow(display)
    def atom(name): return x.XInternAtom(display,name.encode(),0)
    def ids(window,name):
        actual=c.c_ulong();fmt=c.c_int();count=c.c_ulong();remaining=c.c_ulong();data=c.POINTER(c.c_ubyte)()
        status=x.XGetWindowProperty(display,window,atom(name),0,4096,0,0,c.byref(actual),c.byref(fmt),c.byref(count),c.byref(remaining),c.byref(data))
        try:
            return list(c.cast(data,c.POINTER(c.c_ulong))[:count.value]) if status==0 and fmt.value==32 and data else []
        finally:
            if data: x.XFree(data)
    def name(window):
        data=c.c_void_p()
        try:
            return c.string_at(data.value).decode(errors='replace') if x.XFetchName(display,window,c.byref(data)) and data.value else ''
        finally:
            if data.value: x.XFree(data)
    def send(window,kind,value):
        event=Event();event.client.type=33;event.client.display=display;event.client.window=window
        event.client.message_type=atom(kind);event.client.format=32;event.client.data.l[0]=value
        if not x.XSendEvent(display,root,0,(1<<19)|(1<<20),c.byref(event)):
            raise RuntimeError('Window manager rejected the EWMH request.')
        x.XFlush(display)
    try:
        deadline=time.monotonic()+15
        while time.monotonic()<deadline:
            windows=[{'id':window,'title':name(window)} for window in ids(root,'_NET_CLIENT_LIST')]
            matches=[window for window in windows if window['title']==title]
            if len(matches)>1: raise RuntimeError('Ambiguous window title: '+title)
            if matches:
                target=matches[0]['id']
                send(root,'_NET_SHOWING_DESKTOP',0)
                send(target,'_NET_ACTIVE_WINDOW',2)
                for attempt in range(25):
                    active=ids(root,'_NET_ACTIVE_WINDOW')
                    if active and active[0]==target and not any(active[1:]):
                        return {'title':title,'window_id':target,'active':True,'windows':windows}
                    time.sleep(.2)
            time.sleep(.2)
        raise RuntimeError('Could not focus '+title+'; active='+repr(ids(root,'_NET_ACTIVE_WINDOW'))+'; windows='+repr(windows))
    finally:
        x.XCloseDisplay(display)
'''


def guest_script(title):
    prefix = r'''
import os,subprocess
from pathlib import Path
pid=subprocess.check_output(['pgrep','-u',str(os.getuid()),'-x','plasmashell'],text=True).split()[0]
for item in Path('/proc/'+pid+'/environ').read_bytes().split(b'\0'):
    if b'=' in item:
        key,value=item.split(b'=',1)
        os.environ[key.decode()]=value.decode(errors='replace')
'''
    return prefix + CORE + '\nresult=focus_window(' + repr(title) + ')\n'
