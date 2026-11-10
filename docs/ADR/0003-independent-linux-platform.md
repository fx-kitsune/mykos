# ADR 0003 — MyKOS độc lập nền, Debian là cầu nối

Trạng thái: áp dụng cho cấu hình mới; chưa nghiệm thu ISO. Thay thế quyết định Ubuntu tại ADR 0001.

## Mục tiêu

MyKOS có định danh, build pipeline, chính sách cập nhật và dịch vụ riêng. Linux là kernel; “kernel Debian” ở giai đoạn này là Linux được Debian cấu hình, vá và đóng gói, không phải một họ kernel khác. Không coi việc đổi branding hoặc kho gói là đã tạo xong OS độc lập.

## Giai đoạn hiện tại

Bỏ toàn bộ nguồn gói Ubuntu, Casper và adapter live-build cũ. Dùng Debian 13 Trixie, Linux `linux-image-amd64`, Debian live-build và live-boot/live-config. Tách lựa chọn nền trong build.json; giữ Workspace MyKOS tách khỏi nhà cung cấp nền. Chọn Plasma 6 do Trixie cung cấp; các bài kiểm thử hình ảnh Plasma 5 cũ cần nghiệm thu lại.

Userspace vẫn do Debian cung cấp: libc, systemd, APT/dpkg, KDE/Qt, Calamares, initramfs và bootloader. Vì vậy bản hiện tại chưa đạt yêu cầu chỉ phụ thuộc Linux kernel. Không trộn kernel Debian vào rootfs Ubuntu.

## Các mốc tiếp theo để bỏ phụ thuộc distro

1. Khóa nguồn, phiên bản, hash và giấy phép; lưu manifest/SBOM, ký kho MyKOS và thử cập nhật/rollback trên VM.
2. Xây toolchain và rootfs MyKOS từ nguồn upstream, tách kernel provider khỏi nhà cung cấp userspace. Không dùng debootstrap hoặc cài gói Debian trong cấu hình nền độc lập. Mỗi thành phần cần recipe, kiểm tra chữ ký/hash và phụ thuộc build rõ ràng.
3. Sở hữu dịch vụ khởi động, quản lý phiên, mạng, cập nhật, recovery và installer. Thư viện upstream có thể được tự build; phải xác định rõ phạm vi tự phát triển thay vì coi mọi phần mềm ngoài kernel đã được thay thế.
4. Chỉ chuyển mặc định khi rootfs tự build boot được BIOS/UEFI, cài và reboot không ISO, có mạng/âm thanh/desktop, cập nhật có rollback, và không dùng archive/keyring/package database Debian hoặc Ubuntu.

Mỗi mốc phải có bằng chứng VM và kiểm thử phần cứng. Không tuyên bố ổn định chỉ vì thay nhà cung cấp kernel.
