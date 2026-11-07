# ADR 0002: Fold integration through a native companion and KDE resources

- Date: 2026-11-07
- Status: Accepted; installed-image validation pending

## Context

The Fold concept supplies visual direction, original icons and a browser
interaction study. M0 image installation is still unvalidated. A complete custom
shell would expand the maintenance surface before the base OS is ready.

## Decision

Implement an optional Qt 6/QML Workspace companion and upstream KDE color/icon/
wallpaper resources. Keep Plasma as the session and compositor. Do not convert
the browser prototype into the OS shell or add privileged command execution.

Use Python/PyQt6 for this small unprivileged UI integration: the relevant modules
are available in the selected Ubuntu Noble archive. PySide6 was evaluated but
its Python module package names were not available in that base archive. This
choice does not change the Rust preference for future privileged services.
Respect Qt/PyQt and distribution package licenses when redistributing the image.

Local context notes are atomically stored, bounded and private to the user.
Launching applications uses a fixed command allowlist and Qt process APIs.
The app does not alter system appearance when toggling its own light/dark theme.
KDE global color/icon defaults apply only where user settings do not override them.

## Consequences

We can exercise native interaction and original design assets before a full
image is available. No custom shell, KDE Activities integration, global shortcut,
app inventory, driver control or networking service is claimed. Build/boot/install
acceptance still blocks M0; this focused design integration does not complete M1.
