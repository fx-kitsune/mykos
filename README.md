# MyKOS

**Mặc định đơn giản. Thiết kế mạnh mẽ.**

MyKOS là bản phân phối Linux dành cho máy tính cá nhân, phát triển trên Ubuntu và KDE Plasma. Mục tiêu là giúp người dùng phổ thông sử dụng máy thuận tiện, đồng thời giữ quyền tùy biến và công cụ Linux cho người dùng nâng cao.

## Trạng thái dự án

Dự án đang thực hiện **M0 — Nền tảng và lần khởi động đầu tiên**. Chưa có ISO hoặc trình cài đặt được nghiệm thu. Mục tiêu hiện tại là ảnh hệ thống chạy trực tiếp ở chế độ BIOS truyền thống; UEFI, Secure Boot, Calamares và phần cứng thật còn cần kiểm thử.

Đã có cấu hình Ubuntu 24.04 LTS Noble amd64, danh sách gói KDE, công cụ tạo ISO, thông tin bản dựng, mã kiểm tra SHA-256, lệnh chạy QEMU và kiểm thử cấu hình. Nền tảng Noble cung cấp Plasma 5.27.

Bộ thiết kế Fold đã được đưa vào ứng dụng Workspace bằng Qt 6/QML cùng bộ màu, biểu tượng và hình nền KDE. Workspace có ghi chú theo ba không gian, chế độ sáng/tối, đồng hồ tập trung và thao tác mở ứng dụng KDE. Ứng dụng chạy cùng Plasma; ba không gian ghi chú chưa được tích hợp với KDE Activities.

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
