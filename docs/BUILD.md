# Tạo ảnh MyKOS — nền tạm Debian 13

Quyết định hiện hành: [ADR 0003](ADR/0003-independent-linux-platform.md), thay thế ADR 0001.

Dùng VM Debian 13 amd64 riêng, quyền root, ít nhất 25 GiB trống. Container cần đặc quyền chroot/mount; CI dùng `debian:13` với `--privileged`. Nhãn runner Ubuntu của GitHub chỉ cung cấp hạ tầng container, không cung cấp gói cho ảnh MyKOS.

```sh
sudo apt-get update
sudo apt-get install live-build debootstrap debian-archive-keyring squashfs-tools \
  xorriso genisoimage isolinux syslinux syslinux-common syslinux-utils \
  dosfstools mtools grub-efi-amd64-bin grub-common cpio rsync python3 git
python3 -m unittest discover -s tests/integration -v
python3 scripts/build/export-design.py --check
sudo python3 scripts/build/mykos.py check
sudo python3 scripts/build/mykos.py build build/debian-13 --artifacts artifacts/debian-13
```

Thư mục build và artifacts phải mới. Không tái sử dụng cây có mount. Build giữ log khi thất bại và ghi cấu hình, hash đầu vào, manifest gói và SHA256SUMS sau thành công.

`distribution/base/build.json` khai báo nguồn Debian, suite, flavour kernel và initramfs. Kernel dùng `linux-image-amd64`; live dùng `live-boot`, `live-config`, `live-config-systemd`. Không dùng Casper, PPA, Ubuntu keyring hoặc kho Ubuntu. APT giữ xác thực chữ ký. Kho cập nhật/bảo mật do Debian live-build quản lý.

Bộ công cụ Debian được sao chép nguyên trạng vào cây build; không còn các bản vá live-build Ubuntu cũ. Hook chroot đặt `ID=mykos`, `ID_LIKE=debian`, giữ định danh nền gói ở build metadata. Hook binary tạo ba menu BIOS; UEFI sử dụng cùng kernel/initrd trong `/live`. Live UEFI chưa có Secure Boot; trình cài vẫn chỉ hỗ trợ BIOS.

## Tạo ISO bằng GitHub Actions

Chạy workflow `build-iso.yml` hoặc `build-uefi-live.yml`. Chúng cài công cụ từ Debian trong container Debian 13. Workflow thứ hai chạy các probe BIOS/UEFI trước khi lưu ISO. Chưa chạy các workflow mới trong lần refactor này.

## Giới hạn kiểm chứng

Đã chạy kiểm thử cấu hình, đối chiếu tên gói với chỉ mục Debian 13 main và thử `lb config` bằng gói Debian giải nén. Phép thử giải nén chỉ sửa đường dẫn đọc VERSION trong thư mục work để dùng gói chưa cài; không sửa mã công cụ được phân phối.

Chưa tạo ISO hoặc boot/cài Debian trong lần refactor: workspace chỉ có khoảng 7.5 GiB trống, dưới ngưỡng build 25 GiB, và thiếu bộ công cụ mount/chroot. Phải nghiệm thu lại MyKOS Desktop/Openbox, Calamares, BIOS/UEFI, mạng, âm thanh và bản cài không còn quyền live. Các kết quả Ubuntu trước đây không xác nhận ảnh Debian. Kho và container tag còn thay đổi; chưa tái lập từng bit.

Cập nhật 2026-11-10: đã cài PyQt6 trong venv và chạy 8 bài desktop, gồm phiên Xvfb/Openbox thật. Chưa nghiệm thu ISO.

Ảnh mặc định cài shell/session MyKOS và XSession `mykos.desktop`, không cài Plasma/KWin. Xem [ADR 0004](ADR/0004-own-desktop-environment.md).
