#!/usr/bin/env python3
"""Own the lifetime of an unprivileged MyKOS X11 session."""
import os
from pathlib import Path
import signal
import select
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def session_environment(source):
    env = dict(source)
    if not env.get('DISPLAY'):
        raise ValueError('MyKOS Desktop currently requires an X11 display.')
    env.update(XDG_CURRENT_DESKTOP='MyKOS', XDG_SESSION_DESKTOP='mykos',
               XDG_SESSION_TYPE='x11', MYKOS_SESSION='1', QT_QPA_PLATFORM='xcb')
    return env


def stop_children(children):
    # Processes are private process groups; never kill by executable name or UID.
    for child in reversed(children):
        if child.poll() is None:
            try:
                os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
    deadline = time.monotonic() + 3
    for child in reversed(children):
        try:
            child.wait(timeout=max(0, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            child.wait()


def supervise(commands, env, auxiliaries=(), popen=subprocess.Popen, pause=time.sleep, owned=()):
    children = list(owned)
    stopping = False

    def request_stop(*_):
        nonlocal stopping
        stopping = True

    previous = {sig: signal.signal(sig, request_stop) for sig in (signal.SIGTERM, signal.SIGINT)}
    try:
        for command in commands:
            children.append(popen(command, env=env, start_new_session=True))
        required = list(children)
        for command in auxiliaries:
            try:
                children.append(popen(command, env=env, start_new_session=True))
            except OSError as error:
                print(f'MyKOS: optional agent unavailable: {error}', file=sys.stderr)
        while not stopping:
            for child in required:
                code = child.poll()
                if code is not None:
                    return code if code >= 0 else 1
            pause(0.1)
        return 0
    finally:
        stop_children(children)
        for sig, handler in previous.items():
            signal.signal(sig, handler)


def main():
    if os.geteuid() == 0:
        raise ValueError('Run the desktop as a regular user, never as root.')
    env = session_environment(os.environ)
    owned = []
    if not env.get('DBUS_SESSION_BUS_ADDRESS'):
        bus = subprocess.Popen(['dbus-daemon', '--session', '--nofork', '--print-address=1'],
                               stdout=subprocess.PIPE, text=True, start_new_session=True)
        owned.append(bus)
        if not select.select([bus.stdout], [], [], 5)[0]:
            stop_children(owned)
            raise ValueError('Session D-Bus startup timed out.')
        address = bus.stdout.readline().strip()
        bus.stdout.close()
        if not address:
            stop_children(owned)
            raise ValueError('Session D-Bus did not publish an address.')
        env['DBUS_SESSION_BUS_ADDRESS'] = address
    try:
        variables = ['DISPLAY', 'XDG_CURRENT_DESKTOP', 'XDG_SESSION_DESKTOP', 'XDG_SESSION_TYPE']
        if env.get('XAUTHORITY'):
            variables.append('XAUTHORITY')
        subprocess.run(['dbus-update-activation-environment', *variables], env=env,
                       check=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        stop_children(owned)
        raise ValueError('Could not initialize desktop D-Bus activation environment.')
    commands = [['openbox', '--config-file', str(ROOT / 'session/openbox.xml')],
                [sys.executable, str(ROOT / 'shell/main.py')]]
    agents = [['lxpolkit'], ['dunst'], ['nm-applet']]
    return supervise(commands, env, agents, owned=owned)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError) as error:
        print(f'MyKOS session: {error}', file=sys.stderr)
        sys.exit(1)
