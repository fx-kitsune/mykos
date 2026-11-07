# MyKOS

**Simple by default. Powerful by design.**

An Ubuntu-based desktop distribution integrating upstream KDE Plasma. Product
requirements live in [docs/PRODUCT_VISION.md](docs/PRODUCT_VISION.md).

## Current implementation

Native Fold design integration includes an optional Qt 6/QML Workspace, local
notes, focus timer, fixed KDE app launch actions, color schemes, icon theme and
wallpaper. See [desktop implementation](desktop/README.md).

M0 foundation: declarative Ubuntu 24.04 (Noble) amd64 package selection, live-build
configuration, upstream Breeze defaults, image build tooling, package inventory,
SHA-256 metadata, QEMU launcher and automated configuration tests.

**No validated ISO or installer is available yet.** M0 acceptance is incomplete.
The first image target is a development live session using legacy BIOS. UEFI,
Secure Boot, Calamares installation and hardware support remain release gates.
Noble supplies Plasma 5.27; Qt 6/QML is a future MyKOS application choice.

## Development

```sh
python3 -m unittest discover -s tests/integration -v
python3 scripts/build/mykos.py check
```

The second command intentionally exits nonzero when build prerequisites are
missing. See [build instructions](docs/BUILD.md), [VM test matrix](tests/integration/VM_CHECKLIST.md)
and [implementation status](docs/IMPLEMENTATION_STATUS.md).
