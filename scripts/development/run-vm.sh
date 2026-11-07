#!/bin/bash
set -euo pipefail
if [[ $# -lt 1 || $# -gt 2 ]]; then
    echo "Usage: $0 IMAGE.iso [EXISTING_TEST_DISK.qcow2]" >&2
    exit 2
fi
iso=$(realpath -- "$1")
[[ -f "$iso" ]] || { echo 'ISO not found' >&2; exit 1; }
command -v qemu-system-x86_64 >/dev/null || { echo 'Install qemu-system-x86' >&2; exit 1; }
accel=tcg
[[ -r /dev/kvm && -w /dev/kvm ]] && accel=kvm
args=(-accel "$accel" -m 4096 -smp 2 -boot order=d -cdrom "$iso"
      -nic user,model=virtio-net-pci -device virtio-vga
      -device intel-hda -device hda-duplex -serial stdio)
if [[ $# == 2 ]]; then
    disk=$(realpath -- "$2")
    [[ -f "$disk" && "$disk" == *.qcow2 && "$disk" != *,* ]] || { echo 'Expected an existing qcow2 test disk (path without commas)' >&2; exit 1; }
    args+=(-drive "file=$disk,format=qcow2,if=virtio")
fi
exec qemu-system-x86_64 "${args[@]}"
