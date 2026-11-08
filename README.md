# MyKOS

**Mặc định đơn giản. Thiết kế mạnh mẽ.**

MyKOS là bản phân phối Linux dành cho máy tính cá nhân, phát triển trên Ubuntu và KDE Plasma. Mục tiêu là giúp người dùng phổ thông sử dụng máy thuận tiện, đồng thời giữ quyền tùy biến và công cụ Linux cho người dùng nâng cao.

## Trạng thái dự án

Dự án đang thực hiện **M0 — Nền tảng và lần khởi động đầu tiên**. ISO phát triển đã cài thành công xuống đĩa ảo BIOS, boot không ISO và đăng nhập Plasma X11. Kiểm thử mạng, APT, tệp, đổi độ phân giải và âm thanh ảo đã đạt trên [lượt 42529928289](https://github.com/fx-kitsune/mykos/actions/runs/42529928289). [Lượt kiểm tra lại Discover](https://github.com/fx-kitsune/mykos/actions/runs/42531078658) cũng đã đạt sau khi sửa cách mở ứng dụng trong công cụ thử. Điều kiện tái lập ảnh và toàn bộ M0 chưa nghiệm thu. Chưa có bản phát hành ổn định hoặc hỗ trợ UEFI/Secure Boot được xác nhận.

[Tải ISO phát triển đã kiểm thử](https://github.com/fx-kitsune/mykos/actions/runs/42527363919/artifacts/13635659125) (Artifacts lưu 7 ngày, có thể cần đăng nhập GitHub). Trong QEMU với VGA chuẩn, chọn **MyKOS (do hoa phan mem cho may ao)** ở menu BIOS. Đối chiếu `SHA256SUMS` sau giải nén; xem [bằng chứng và giới hạn](docs/IMPLEMENTATION_STATUS.md).

Đã có cấu hình Ubuntu 24.04 LTS Noble amd64, danh sách gói KDE, công cụ tạo ISO, thông tin bản dựng, mã kiểm tra SHA-256, lệnh chạy QEMU và kiểm thử cấu hình. Nền tảng Noble cung cấp Plasma 5.27.

Bộ thiết kế Fold đã được đưa vào ứng dụng Workspace bằng Qt 6/QML cùng bộ màu, biểu tượng và hình nền KDE. Workspace có ghi chú theo ba không gian, chế độ sáng/tối, đồng hồ tập trung và thao tác mở ứng dụng KDE. Ứng dụng chạy cùng Plasma; ba không gian ghi chú chưa được tích hợp với KDE Activities.

## Tạo ISO khi máy cá nhân không đủ cấu hình

Dùng [workflow Tạo ISO MyKOS](https://github.com/fx-kitsune/mykos/actions/workflows/build-iso.yml): vào **Actions → Tạo ISO MyKOS → Run workflow**. GitHub chạy Ubuntu và lưu ISO/nhật ký để tải xuống trong 7 ngày. Xem [hướng dẫn Actions](docs/BUILD.md#tạo-iso-bằng-github-actions) về tài nguyên, hạn mức và xử lý lỗi.

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
