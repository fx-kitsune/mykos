# ADR 0002 — Tích hợp Fold qua ứng dụng đồng hành và tài nguyên KDE

- Ngày: 07/11/2026.
- Trạng thái: Chấp nhận; chờ kiểm thử trên ảnh đã cài đặt.

## Bối cảnh

Bản mẫu Fold cung cấp định hướng thị giác, biểu tượng gốc và nghiên cứu tương tác trong trình duyệt. Việc cài ảnh M0 chưa được kiểm chứng. Viết giao diện hệ thống hoàn toàn mới sẽ mở rộng gánh nặng bảo trì trước khi nền tảng sẵn sàng.

## Quyết định và lý do

Triển khai Workspace Qt 6/QML tùy chọn cùng bộ màu, biểu tượng và hình nền KDE. Giữ Plasma làm phiên làm việc và KWin làm bộ tổng hợp hình ảnh; không biến bản mẫu trình duyệt thành giao diện hệ điều hành hoặc thêm thực thi lệnh đặc quyền.

Dùng Python/PyQt6 cho phần giao diện không đặc quyền này vì các mô-đun cần thiết có trong kho Ubuntu Noble đã chọn. Đã xem xét PySide6 nhưng tên gói Python tương ứng không có trong chỉ mục kho nền được kiểm tra. Lựa chọn này không thay đổi định hướng ưu tiên Rust cho dịch vụ đặc quyền về sau. Khi phân phối ảnh, tuân thủ giấy phép Qt, PyQt và các gói nền.

Ghi chú có giới hạn kích thước, lưu cục bộ bằng thay thế tệp nguyên tử và chỉ người dùng sở hữu truy cập. Mở ứng dụng qua danh sách lệnh cố định và API tiến trình Qt. Đổi sáng/tối trong ứng dụng không thay giao diện toàn hệ thống. Mặc định màu và biểu tượng KDE chỉ áp dụng nơi chưa có ghi đè của người dùng.

## Hệ quả

Có thể kiểm thử tương tác native và tài nguyên gốc trước khi có ảnh đầy đủ. Chưa triển khai giao diện hệ thống riêng, tích hợp KDE Activities, phím tắt toàn cục, danh mục mọi ứng dụng đã cài, điều khiển trình điều khiển hoặc dịch vụ mạng. Tạo ảnh, khởi động và cài đặt vẫn là điều kiện nghiệm thu M0; tích hợp Fold giới hạn này chưa hoàn thành M1.
