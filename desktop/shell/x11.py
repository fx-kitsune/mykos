"""Small EWMH adapter. Fixed argv only; no shell or user-provided commands."""
import subprocess


def command(args):
    return subprocess.run(args, check=True, text=True, capture_output=True, timeout=2).stdout


def describe_window(window, kind, geometry=None):
    identifier = str(int(window))
    command(['xprop', '-id', identifier, '-f', '_NET_WM_WINDOW_TYPE', '32a',
             '-set', '_NET_WM_WINDOW_TYPE', '_NET_WM_WINDOW_TYPE_' + kind])
    command(['xprop', '-id', identifier, '-f', '_NET_WM_DESKTOP', '32c',
             '-set', '_NET_WM_DESKTOP', '4294967295'])
    if kind == 'DOCK' and geometry:
        x, y, width, height, root_height = geometry
        bottom = root_height - y
        values = [0, 0, 0, bottom, 0, 0, 0, 0, 0, 0, x, x + width - 1]
        command(['xprop', '-id', identifier, '-f', '_NET_WM_STRUT_PARTIAL', '32c',
                 '-set', '_NET_WM_STRUT_PARTIAL', ','.join(map(str, values))])
        command(['xprop', '-id', identifier, '-f', '_NET_WM_STRUT', '32c',
                 '-set', '_NET_WM_STRUT', f'0,0,0,{bottom}'])


def list_windows(exclude):
    rows = []
    for line in command(['wmctrl', '-l']).splitlines():
        fields = line.split(None, 3)
        if len(fields) == 4:
            try:
                identifier, desktop = int(fields[0], 16), int(fields[1])
            except ValueError:
                continue
            if identifier not in exclude and desktop >= 0:
                rows.append({'id': hex(identifier), 'title': fields[3], 'desktop': desktop})
    return rows
