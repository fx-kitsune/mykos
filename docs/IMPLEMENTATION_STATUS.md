# Implementation status

Updated 2026-11-07. M0 is **in progress**, not accepted.

Implemented:
- Ubuntu Noble amd64 release configuration and declared signed archive sources.
- KDE baseline package manifest and upstream Breeze defaults.
- Isolated Ubuntu live-build adapter, configuration and root-build preflight.
- Build log, resolved package inventory, source/config hashes and checksums.
- QEMU launcher, static CI, tests and VM/hardware acceptance checklists.
- Fold-native Qt 6/QML Workspace with local notes, theme, focus and KDE launch actions.
- MyKOSDark/MyKOSLight KDE schemes, Fold icon exports, wallpaper and image staging.

Verified in this cloud environment:
- Seven build/configuration tests and seven native desktop/storage tests.
- Native offscreen launch, dark/light rendering, note editing/context switching,
  focus start/stop, app-search popup and a 900×700 viewport; no QML warnings.
- Shell syntax checks and deterministic native design export checks.
- The original 39 baseline package names exist in the Ubuntu Noble amd64 archive indexes
  (availability check only; dependency installation is not yet exercised).
- All eight Qt/PyQt module package names exist in the Noble universe index.
- Configuration generation with an extracted pinned Ubuntu live-build package
  and debootstrap (no root/chroot/image build performed).

Blocked here: host is Debian 13, has no root/sudo or KVM device, and only about
7.5 GiB free against a 25 GiB build requirement. Build preflight reports these
limitations before attempting changes.

Remaining M0 acceptance work:
- Produce the full ISO on the documented Ubuntu build VM.
- Boot and validate the live desktop.
- Integrate Calamares and test installation plus installed first login.
- Exercise network/audio/display/package/update and recovery workflows.
- Lock package snapshots/toolchain and compare independent builds.
- Define and validate hardware support; add UEFI/Secure Boot as separate targets.

See `desktop/README.md` for the exact scope of the optional native companion.
No custom shell, root daemon, automatic rollback, Windows compatibility layer or
public release is claimed. Continue M0 before expanding M1–M6.
