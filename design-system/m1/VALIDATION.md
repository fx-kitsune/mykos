# Kiểm tra bản thiết kế desktop M1

Ngày 08/11/2026. Bản 2.0; Chromium và Playwright trên Linux cloud. Ảnh `previews/` chụp từ bản mẫu, không phải desktop trong ISO.

## Phạm vi kiểm tra

- Desktop ban đầu không có cửa sổ tự mở, Workspace, câu chào hoặc thẻ nội dung; công cụ rà soát F1 mặc định ẩn.
- Mở cửa sổ Tệp, danh sách thư mục, tìm không dấu, vào thư mục và trạng thái rỗng.
- Thu nhỏ và khôi phục cửa sổ, giữ vị trí thư mục trong thao tác này; phóng to/khôi phục và đóng.
- Mở menu ở góc dưới trái, tìm có/không dấu và Enter mở ứng dụng; không có kết quả; Escape đóng.
- Workspace không nằm trong nhóm ghim mặc định.
- Đổi sáng/tối từ cửa sổ thiết lập; trạng thái giảm chuyển động.
- Mở/đóng thông báo rỗng; thay giá trị thanh âm lượng minh họa.
- Màn hình đăng nhập ngăn gửi biểu mẫu và xóa mật khẩu sau thao tác; F1 cho phép quay lại desktop trong bản mẫu.
- 1440×900 và khung 390×844 không tràn trang theo chiều ngang.
- Không có lỗi JavaScript trong các luồng đã kiểm tra.

Các kết quả này chỉ nói về trình duyệt. Bản mẫu dùng một cửa sổ minh họa dùng chung; không thực thi lệnh Terminal, mở web hoặc quản lý tệp thật. Không suy ra hỗ trợ đa ứng dụng, xác thực, bộ gõ hoặc thiết bị từ bản mẫu.

## Tương phản

```sh
python3 design-system/m1/check-contrast.py
```

Kiểm tra các cặp vai trò chữ trên nền/bề mặt và nút nhấn cho Ink/Paper; mức yêu cầu 4,5:1. Khi tích hợp phải kiểm tra lại trong Qt/Plasma, gồm tiêu điểm, độ mờ, chủ đề tương phản cao và tăng chữ. Chưa nghiệm thu trình đọc màn hình hoặc toàn bộ các cặp màu có thể xuất hiện.

## Cần kiểm tra trên KDE

Panel thật, Kickoff/KRunner, Dolphin, KWin, SDDM và màn hình khóa; HiDPI/nhiều màn hình; bộ gõ tiếng Việt; trình đọc màn hình; trạng thái nguồn/mạng/âm lượng thật; lưu và hoàn nguyên cấu hình người dùng. M0 và M1 chưa thay đổi trạng thái nghiệm thu bởi các kiểm tra bản mẫu này.

## Kiểm tra cấu hình Plasma

Đã bổ sung kiểm thử chạy mã bố cục thật trong môi trường API Plasma giả lập bằng Node.js: hồ sơ chưa có panel tạo đúng một panel cạnh dưới cao 48; có các widget KDE dự kiến và chỉ ghim Dolphin; hồ sơ có một hoặc nhiều panel không bị tạo thêm. Tổng bộ kiểm thử tích hợp hiện có 17 kiểm tra đạt.

Kiểm thử API giả lập không xác nhận KPackage, KWin hoặc Plasma chạy đúng trên ISO. Gói giao diện, màu biểu tượng và việc áp hình nền cho hồ sơ mới vẫn cần thử trên KDE thực tế.
