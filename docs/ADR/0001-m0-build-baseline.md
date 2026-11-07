# ADR 0001: M0 Ubuntu/KDE live-image baseline

- Date: 2026-11-07
- Status: Accepted for development; full image validation pending

## Context

The repository contains product/architecture/roadmap documents, with no existing
image implementation. M0 must precede custom shell and privileged-service work.

## Decision

Use Ubuntu 24.04 LTS Noble amd64 and its upstream Plasma 5.27 packages for the
first live-image experiment. Ubuntu 26.04 and Plasma 6 are alternatives for a
later rebase, after testing installer and hardware integration. Qt 6/QML remains
appropriate for future first-party components, not a claim about Noble Plasma.

Use Ubuntu live-build `3.0~a57-1ubuntu49.1`, casper and Syslinux ISO hybrid output
for legacy BIOS first. Alternatives considered: Debian live-build (different
Ubuntu integration), remastering a Kubuntu ISO (large opaque starting artifact),
and direct livecd-rootfs integration (additional release infrastructure).

Relocate the installed toolchain into each build directory. The inspected Ubuntu
package probes its common function library in a subshell; a relocated invocation
otherwise loses functions such as Echo. The small repository adapter replaces
that probe with direct sourcing of the relocated library. No other behavior or
system package is patched. Record this adapter with the source inputs and revisit
it when replacing the old Ubuntu toolchain.

Use Ubuntu signed main/restricted/universe/multiverse, security and updates.
Multiverse/restricted software has licensing/support constraints inherited from
Ubuntu; package selection must be reviewed before public redistribution.
Keep source identity compatible with Ubuntu and add MyKOS variant branding.

## Consequences

The first target is an unvalidated live session, not an installable release.
Calamares requires a separately reviewed module sequence and offline payload,
partition, bootloader and live-user cleanup configuration. Do not expose an
installer launcher until those paths are tested. UEFI/Secure Boot and modern
Plasma migration remain explicit gates, not implied support.

Rolling archives prevent bit-identical rebuilding. A package snapshot and full
host toolchain lock must replace this development recipe before satisfying the
strict reproducibility goal. The limited remaining KDE 5 support window must be
reviewed before planning a public release on Noble.
