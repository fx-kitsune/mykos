# M0 VM acceptance checklist

Every row begins NOT RUN. Attach ISO SHA-256, build.json, test date, tester,
QEMU version/command and logs/screenshots when recording a result.

```sh
# On a machine with a graphical display and qemu-system-x86 installed:
scripts/development/run-vm.sh artifacts/m0-001/mykos-0.1.0-dev-amd64.iso
# Optional disposable disk, after installer integration exists:
qemu-img create -f qcow2 /tmp/mykos-install.qcow2 40G
scripts/development/run-vm.sh artifacts/m0-001/mykos-0.1.0-dev-amd64.iso /tmp/mykos-install.qcow2
```

The launcher uses KVM when accessible and TCG otherwise. It does not automate
or assert successful boot. No disk is attached by default. An explicitly passed
test disk is writable. Live sessions may permit passwordless administration;
never carry that policy into an installed user's account.

| Test | Expected result | Status |
|---|---|---|
| BIOS live boot | Boot menu, kernel, graphical session | NOT RUN |
| KDE login/session | Plasma, launcher, keyboard navigation | NOT RUN |
| Network | DHCP, DNS and HTTPS through NetworkManager | NOT RUN |
| Audio | PipeWire output and volume control | NOT RUN |
| Display | Resolution changes; Wayland session checked separately | NOT RUN |
| Files/terminal | Dolphin and Konsole open, files persist in session | NOT RUN |
| Packages | Signed APT refresh, Discover and Flatpak launch | NOT RUN |
| Install to blank virtual disk | Complete install and reboot without ISO | BLOCKED: installer integration |
| Installed login | Normal account, explicit authorization for admin | BLOCKED |
| Update/reboot | APT update, reboot, working session | BLOCKED |
| Recovery | Documented rescue steps recover a failed update | BLOCKED |
| UEFI / Secure Boot | Separate firmware validation | UNSUPPORTED |

Do not run interrupted-update tests against valuable data. Snapshots/rollback
are not configured; a backup is required independently of any future snapshots.
