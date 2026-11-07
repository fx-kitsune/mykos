# M0 development image builds

## Supported build machine

Use a disposable **Ubuntu 24.04 amd64 VM**, root access, at least 4 CPU cores,
8 GiB RAM and 25 GiB free disk. A full build uses chroot and filesystem mounts;
an ordinary unprivileged container is insufficient. Do not build on a personal
workstation containing valuable mounted filesystems.

Install dependencies from authenticated Ubuntu repositories:

```sh
sudo apt-get update
sudo apt-get install live-build=3.0~a57-1ubuntu49.1 debootstrap ubuntu-keyring \
  squashfs-tools xorriso genisoimage isolinux syslinux syslinux-common \
  syslinux-utils dosfstools mtools cpio rsync python3 git
```

If the pinned tool version is unavailable, stop and review the toolchain ADR.
Do not silently substitute Debian live-build: its Ubuntu/casper support differs.
APT authenticates packages using Ubuntu archive keys. No private repository,
third-party signing key, Flatpak remote, credential or PPA is configured.

## Configure and build

From the repository root:

```sh
# Configure without root; always choose a fresh directory.
python3 scripts/build/mykos.py configure build/config-review
# Examine build/config-review/config before a full build.
sudo python3 scripts/build/mykos.py check
sudo python3 scripts/build/mykos.py build build/m0-001 --artifacts artifacts/m0-001
```

The build command creates its own new configuration; do not pass the directory
from the separate configure example. Existing build/artifact directories are
never removed or reused automatically. Failed build logs stay in the build tree.
After a failed mount/chroot stage, inspect `findmnt` in the disposable VM before
removing files; destroying the disposable VM is the simplest cleanup procedure.

The local toolchain adapter copies the installed pinned toolchain into each build
tree and sources its function library in the current shell. It does not modify
system packages. `MYKOS_LIVE_BUILD_PREFIX` supports an extracted Ubuntu package
prefix for configuration inspection only; full builds use the installed toolchain.

## Outputs

On successful completion, artifacts contain the ISO, resolved package manifest,
source revision and dirty-tree status, configuration/input hashes, build log,
live-build generated configuration and SHA256SUMS. Verify the artifact directory:

```sh
cd artifacts/m0-001
sha256sum -c SHA256SUMS
```

Image building does not mean release validation. Follow the VM checklist and
record evidence before claiming first boot, installation or hardware support.
The fixture used in metadata unit tests is not a real ISO.

## Reproducibility boundary

The Ubuntu release, architecture, sources and live-build version are pinned.
Ubuntu noble, noble-updates and noble-security remain rolling authenticated
archives. Package versions and the rest of the host toolchain are recorded or
controlled by the build host, not fully locked. This is a repeatable recipe,
**not a bit-for-bit reproducible build**. Snapshot repositories, complete tool
locks, normalized timestamps and a two-build comparison remain necessary before
meeting the product's strict reproducibility criterion.

The builder retains Ubuntu ID and VERSION_ID for compatibility and adds MyKOS
variant metadata. The initial session uses English; Vietnamese localization and
input methods have not been integrated or tested.
