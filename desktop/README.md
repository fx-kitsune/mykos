# Native implementation of the Fold concept

The source of visual direction is `design-system/`. This directory implements
it as an **unprivileged Qt 6/QML companion application**, plus KDE branding
resources. It does not replace Plasma, KWin or KDE Activities.

## Run and test

On an Ubuntu Noble desktop install `python3-pyqt6`, `python3-pyqt6.qtquick`,
`python3-pyqt6.qtsvg` and the `qml6-module-*` packages listed in the image manifest.
Then run `python3 desktop/workspace/main.py` from the checkout.

For isolated development on another Linux system:

```sh
python3 -m venv /tmp/mykos-workspace-venv
/tmp/mykos-workspace-venv/bin/pip install -r desktop/workspace/requirements-dev.txt
/tmp/mykos-workspace-venv/bin/python desktop/workspace/main.py
```

Headless validation:

```sh
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software \
  /tmp/mykos-workspace-venv/bin/python -m unittest discover -s tests/desktop -v
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software \
  MYKOS_WORKSPACE_DATA=/tmp/mykos-smoke \
  MYKOS_SCREENSHOT=/tmp/mykos-workspace.png \
  /tmp/mykos-workspace-venv/bin/python desktop/workspace/main.py --smoke-test
```

The smoke flag exits after rendering; the timer is for a render sample, not an
assertion that the installed desktop works. Native tests also check interaction,
notes, both themes, a 900×700 viewport, error reporting and the launch boundary.

## Working interactions

- Three named note contexts; Unicode notes saved atomically, with owner-only
  file permissions, under Qt's AppDataLocation (`MyKOS/Workspace`).
- A 350 ms save debounce and final save on exit; failed saves are reported.
- Workspace-only dark/light appearance, remembered between launches.
- A 25-minute focus timer based on elapsed wall time, reset on application exit.
- Ctrl+Space application search while Workspace is focused; Escape closes it.
- Explicit launch actions for Dolphin, Konsole, System Settings, Discover, Kate
  and Gwenview. Missing applications report an error. No shell interpolation,
  root commands, network requests or simulated connectivity toggles.

`MYKOS_WORKSPACE_DATA` overrides the local data directory for development/tests.
Search covers the six integrated launch actions, not every installed desktop file.
The three contexts are not virtual desktops, KDE Activities or separate folders.

## KDE integration

`distribution/branding/overlay` installs MyKOS Ink/Paper color schemes, the
MyKOSFold icon theme with Breeze/hicolor fallback and an original SVG wallpaper.
Fresh KDE profiles inherit MyKOSDark/MyKOSFold through `/etc/xdg/kdeglobals`.
Existing per-user settings retain precedence. Wallpaper is selectable through
KDE's wallpaper chooser; it is not forcibly applied to existing desktops.
The upstream Breeze shell layout, splash and window decoration remain in use.

The image builder stages the app in `/usr/share/mykos/workspace`, an executable
`/usr/bin/mykos-workspace` and an application-menu desktop entry. It does not
start Workspace automatically or register a replacement desktop session.

## Design exports

```sh
python3 scripts/build/export-design.py
python3 scripts/build/export-design.py --check
```

Original design assets remain untouched. The exporter flattens nested SVG
viewports into equivalent transforms because Qt SVG Tiny skips nested `<svg>`.
Generated icons are committed so image builds need no Node.js or network access
for branding. Named KDE application aliases cover the six emblems; missing icons
fall back to Breeze. The original generator stays in `design-system/tools/`.

Validation here uses PyQt 6.7/Qt 6.7 offscreen. Ubuntu archive module availability
is checked separately. Full image dependency resolution, Plasma theme rendering,
Wayland integration and physical hardware testing remain M0/M1 release gates.
