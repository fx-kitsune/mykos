# MyKOS

**Mặc định đơn giản. Thiết kế mạnh mẽ.**

MyKOS là bản phân phối Linux dành cho máy tính cá nhân, đang chuyển sang nền riêng, tạm sử dụng gói Debian 13 và phát triển MyKOS Desktop riêng. Mục tiêu là giúp người dùng phổ thông sử dụng máy thuận tiện, đồng thời giữ quyền tùy biến và công cụ Linux cho người dùng nâng cao.

## Trạng thái dự án

Đã triển khai phiên **MyKOS Desktop** thử nghiệm: shell Qt/QML, desktop, panel, launcher, danh sách cửa sổ, ba desktop ảo và trình quản lý phiên riêng. Openbox tạm đảm nhiệm quản lý cửa sổ X11. Ảnh mặc định đã bỏ Plasma/KWin và tích hợp đăng nhập MyKOS qua SDDM. Workspace giữ ghi chú và đồng hồ tập trung.

Đã chạy kiểm thử phiên thật trên Xvfb/Openbox cùng kiểm thử Qt và cấu hình. **Đã tạo ISO Debian/MyKOS Desktop và boot live thành công trên UEFI USB/CD-ROM; BIOS đã vào userspace. Chưa nghiệm thu cài xuống đĩa.** Không có bản ổn định; compositor Wayland, locking, tray và power management riêng chưa hoàn tất. Xem [phạm vi desktop](desktop/README.md) và [ADR 0004](docs/ADR/0004-own-desktop-environment.md).

[Tải ISO MyKOS Desktop thử nghiệm](https://github.com/fx-kitsune/mykos/releases/tag/untagged-7f6bdfd6a5f5479a1c65) từ release nháp, cần quyền xem repo/draft. Lần này chỉ có **một** tệp `mykos-0.1.0-dev-amd64.7z.001` (~1.57 GB); mở bằng 7-Zip để giải nén ISO. [Build và kiểm thử 42836804675](https://github.com/fx-kitsune/mykos/actions/runs/42836804675), nguồn `904e61d`. Secure Boot chưa hỗ trợ. Trình cài terminal từ repo mới hơn commit ISO và chưa nghiệm thu cài/reboot.

Các ISO/kết quả Ubuntu/Plasma trước đây là bằng chứng lịch sử, không nghiệm thu desktop mới.

## Tạo ISO khi máy cá nhân không đủ cấu hình

Dùng [workflow Tạo ISO MyKOS](https://github.com/fx-kitsune/mykos/actions/workflows/build-iso.yml): vào **Actions → Tạo ISO MyKOS → Run workflow**. GitHub chạy bộ tạo ảnh trong container Debian 13 và lưu ISO/nhật ký để tải xuống trong 7 ngày. Xem [hướng dẫn Actions](docs/BUILD.md#tạo-iso-bằng-github-actions) về tài nguyên, hạn mức và xử lý lỗi.

## Bắt đầu

Chạy từ thư mục gốc dự án:

```sh
python3 -m unittest discover -s tests/integration -v
python3 scripts/build/mykos.py check
```

Lệnh `check` trả về mã thoát khác 0 nếu máy chưa đủ điều kiện tạo ISO. Để chạy giao diện, xem [hướng dẫn Workspace](desktop/README.md). Để tạo ảnh hệ thống, xem [hướng dẫn tạo ISO](docs/BUILD.md).

## Tra cứu tài liệu

Toàn bộ hướng dẫn dự án được viết bằng tiếng Việt. Tên công nghệ, định danh trong mã, đường dẫn và lệnh giữ nguyên để có thể tra cứu và thực thi chính xác.

- [Mục lục tài liệu](docs/README.md).
- [Tầm nhìn sản phẩm](docs/PRODUCT_VISION.md).
- [Kiến trúc kỹ thuật](docs/ARCHITECTURE.md).
- [Lộ trình phát triển](docs/ROADMAP.md).
- [Trạng thái triển khai và giới hạn](docs/IMPLEMENTATION_STATUS.md).
- [Bộ thiết kế giao diện](design-system/README.md).
- [Danh sách kiểm thử máy ảo](tests/integration/VM_CHECKLIST.md).
- [Giải thích giấy phép bằng tiếng Việt](LICENSE.vi.md).

## Hướng độc lập nền

Xem [ADR 0003](docs/ADR/0003-independent-linux-platform.md). Loại bỏ nguồn Ubuntu là bước đầu; hiện vẫn cần userspace, APT, systemd, Qt/KDE và công cụ Debian. Mục tiêu chỉ dựa vào Linux kernel chưa hoàn tất.

## Cài tự động lên NVMe từ USB cứu hộ

Boot bằng USB cứu hộ Linux có Internet, clone repo rồi chạy:

```sh
git clone https://github.com/fx-kitsune/mykos.git
cd mykos
./install
```

Chọn ổ theo model/dung lượng và đặt tài khoản. Wizard tự chuẩn bị công cụ, tạo phân vùng, format, mount, debootstrap và cài bootloader. Không cần GParted, mountpoint hoặc nhập UUID. Một bước xác nhận rõ ổ sẽ bị xóa vẫn bắt buộc; cài tự động dùng toàn bộ ổ được chọn, không giữ dữ liệu/dual boot.

Xem [hướng dẫn](docs/INSTALL_FROM_RESCUE.md). Kiểm thử cài–reboot NVMe ảo đang được bổ sung; chưa tuyên bố nghiệm thu phần cứng thật.
