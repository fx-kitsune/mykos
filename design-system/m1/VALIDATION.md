# Kiểm tra bộ thiết kế M1

Ngày kiểm tra: 08/11/2026. Công cụ: Chromium và Playwright trên môi trường Linux cloud. Đây là kiểm tra bản mẫu trình duyệt, không phải kiểm thử KDE, SDDM hoặc ISO.

## Đã kiểm tra

| Hạng mục | Kết quả |
|---|---|
| Năm màn hình xem thiết kế | Mở được desktop, menu ứng dụng, thông báo, thiết lập và đăng nhập |
| Sáng/tối | Đổi màu toàn bản mẫu; có ảnh Ink và Paper |
| Ghi chú | Tách ba ngữ cảnh và giữ nội dung khi chuyển qua lại trong phiên |
| Tập trung | Bắt đầu ở 25:00, dừng và trở về trạng thái ban đầu |
| Tìm ứng dụng | Truy vấn không dấu `thiet lap` trả đúng mục; Enter mở màn hình liên quan |
| Không có kết quả | Có thông báo rõ và giữ ô tìm |
| Đóng menu | Escape đóng hộp thoại theo hành vi trình duyệt |
| Giảm chuyển động | Tùy chọn cập nhật trạng thái của bản mẫu |
| Thông báo minh họa | Hành động có phản hồi và không gửi yêu cầu mạng |
| Đăng nhập minh họa | Ngăn gửi biểu mẫu, xóa giá trị sau khi chọn đăng nhập; không lưu mật khẩu |
| Khung xem | Kiểm tra ở 1440×1120 và 390×844; không tràn trang theo chiều ngang ở khung hẹp |
| JavaScript | Không có lỗi thực thi được ghi nhận trong các luồng đã thử |
| Tài nguyên | SVG Fold tải từ repo, không phụ thuộc phông hoặc thư viện mạng |

## Tương phản chữ

Chạy từ thư mục gốc:

```sh
python3 design-system/m1/check-contrast.py
```

Đã kiểm tra bảy cặp vai trò cho mỗi bảng màu: chữ chính/nền, chữ chính/bề mặt, chữ phụ/nền, chữ phụ/bề mặt, điểm nhấn/nền, chữ trên nhấn/nền nhấn và chữ lỗi/bề mặt. Tất cả đạt ít nhất 4,5:1. Giá trị thấp nhất trong các cặp đã kiểm tra là khoảng 4,77:1 ở chữ phụ trên nền Paper.

Các số đo không chứng minh mọi cặp màu, trạng thái không khả dụng, cấu hình tương phản cao hoặc bề mặt ứng dụng bên thứ ba đều đạt. Khi triển khai phải kiểm tra lại trong Qt/Plasma với độ mờ, hình nền, chủ đề và tỉ lệ thực tế.

## Chưa nghiệm thu

Đăng nhập SDDM, mở khóa, trình đọc màn hình, IME/bộ gõ tiếng Việt trong KDE, HiDPI và nhiều màn hình, panel thật, danh sách ứng dụng cài đặt, thông báo hệ thống, phục hồi cấu hình và hiệu năng đồ họa. Không dùng kết quả của bản mẫu để đánh dấu hoàn thành các mục này.

Ảnh `previews/` là ảnh chụp bản mẫu trình duyệt với phông có sẵn trong môi trường kiểm tra; không phải ảnh desktop từ ISO.
