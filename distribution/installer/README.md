# Installer integration gate

Calamares is the architecture candidate, not yet configured or included.
The current live image must not be advertised as installable.

Before enabling it:

1. Pin the Calamares version compatible with the chosen Ubuntu release.
2. Review partition/mount/unpackfs/user/locale/network/bootloader/unmount sequence.
3. Point unpackfs at the actual casper payload, not an assumed path.
4. Remove live-session packages, credentials and autologin from the target.
5. Test empty disk and preserve-existing-data cases using disposable VM disks.
6. Verify installed user login, sudo authorization, networking and updates.
7. Validate BIOS and UEFI independently; do not claim Secure Boot without testing.

Record logs, exact ISO checksum, virtual firmware and disk layouts in the test matrix.
