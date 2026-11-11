#!/usr/bin/env bash
# Repair Debian Trixie MyKOS firmware from a networked Linux Live USB.
# Usage: sudo bash scripts/recovery/repair-surface-wifi-chroot.sh [root-device]
# Defaults to /dev/nvme0n1p2; never formats or partitions disks.
set -Eeuo pipefail
export DEBIAN_FRONTEND=noninteractive
if [[ ${EUID} -ne 0 ]]; then echo "Run as root (sudo)." >&2; exit 1; fi
ROOT_ARG="${1:-/dev/nvme0n1p2}"
if [[ $# -gt 1 || ! -b $ROOT_ARG ]]; then
  echo "Usage: sudo bash $0 [/dev/nvme0n1p2]" >&2
  lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINTS
  exit 2
fi
ROOT_DEV=$(readlink -f -- "$ROOT_ARG")
if [[ $(findmnt -nro SOURCE / 2>/dev/null) == "$ROOT_DEV" ]]; then
  echo "Refusing to operate on the running root filesystem." >&2; exit 1
fi
TARGET=$(mktemp -d /mnt/mykos-repair.XXXXXX)
MOUNTED=()
RESOLV_BACKUP=""
cleanup() {
  set +e
  if [[ -n $RESOLV_BACKUP ]]; then
    rm -f "$TARGET/etc/resolv.conf"
    mv "$RESOLV_BACKUP" "$TARGET/etc/resolv.conf"
  fi
  for ((i=${#MOUNTED[@]}-1;i>=0;i--)); do umount -R "${MOUNTED[i]}" 2>/dev/null || echo "Unmount manually: ${MOUNTED[i]}" >&2; done
  rmdir "$TARGET" 2>/dev/null || true
}
trap cleanup EXIT
echo "Selected installed root: $ROOT_DEV"
lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINTS "$ROOT_DEV"
read -r -p "Type REPAIR to mount and modify this installation: " confirm
[[ $confirm == REPAIR ]] || { echo "Cancelled."; exit 1; }
mount "$ROOT_DEV" "$TARGET"
MOUNTED+=("$TARGET")
if [[ ! -f "$TARGET/etc/os-release" || ! -x "$TARGET/usr/bin/apt-get" ]]; then
  echo "Partition $ROOT_DEV is not recognized as an installed Linux root." >&2
  echo "Root directory listing:" >&2
  ls -la "$TARGET" >&2
  echo "os-release and apt-get:" >&2
  ls -l "$TARGET/etc/os-release" "$TARGET/usr/bin/apt-get" 2>&1 || true
  echo "Stopping without modifying the installation." >&2
  exit 1
fi
# MyKOS may brand ID differently; check its Debian ancestry instead.
(
  . "$TARGET/etc/os-release"
  case " ${ID:-} ${ID_LIKE:-} " in
    *debian*) ;;
    *) echo "Unsupported OS: ID=${ID:-unknown} ID_LIKE=${ID_LIKE:-none}" >&2; exit 1 ;;
  esac
  if [[ "${VERSION_CODENAME:-}" != trixie ]]; then
    echo "Expected Debian Trixie, got ${VERSION_CODENAME:-unknown}." >&2; exit 1
  fi
) || exit 1
if [[ ! -d "$TARGET/etc/apt" ]]; then echo "Missing apt configuration." >&2; exit 1; fi
# Ensure the Debian firmware component is available. Leave existing sources intact.
mkdir -p "$TARGET/etc/apt/sources.list.d"
cat > "$TARGET/etc/apt/sources.list.d/mykos-firmware-repair.sources" <<'SOURCES'
Types: deb
URIs: https://deb.debian.org/debian
Suites: trixie trixie-updates
Components: main contrib non-free non-free-firmware
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg

Types: deb
URIs: https://security.debian.org/debian-security
Suites: trixie-security
Components: main contrib non-free non-free-firmware
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg
SOURCES
for dir in dev proc sys run; do
  mkdir -p "$TARGET/$dir"
  mount --rbind "/$dir" "$TARGET/$dir"
  mount --make-rslave "$TARGET/$dir"
  MOUNTED+=("$TARGET/$dir")
done
# resolv.conf may be a broken link to NetworkManager inside the chroot.
if [[ -e "$TARGET/etc/resolv.conf" || -L "$TARGET/etc/resolv.conf" ]]; then
  RESOLV_BACKUP="$TARGET/etc/resolv.conf.mykos-repair.$$"
  mv "$TARGET/etc/resolv.conf" "$RESOLV_BACKUP"
fi
cp -L /etc/resolv.conf "$TARGET/etc/resolv.conf"
echo "Updating APT indexes and installing firmware into the installed OS..."
chroot "$TARGET" /usr/bin/apt-get update
chroot "$TARGET" /usr/bin/apt-get install -y \
  linux-image-amd64 initramfs-tools network-manager \
  firmware-libertas firmware-misc-nonfree firmware-realtek \
  firmware-atheros firmware-iwlwifi firmware-mediatek
# Surface Pro 5 uses the mwifiex_pcie driver for its onboard Marvell Wi-Fi.
# module availability varies with the installed kernel.
chroot "$TARGET" /usr/sbin/update-initramfs -u -k all
chroot "$TARGET" /usr/bin/systemctl enable NetworkManager.service
echo "Firmware and initramfs repair complete. Reboot without the Live USB."
echo "After boot, inspect: lspci -nnk; lsusb; nmcli device; dmesg | grep -Ei 'mwifiex|firmware|wifi|wlan'"
