# Điều kiện tích hợp trình cài đặt

Calamares là lựa chọn kiến trúc, chưa được cấu hình hoặc đưa vào ảnh. Chưa được mô tả ảnh chạy trực tiếp hiện tại là bản đã cài đặt được.

Trước khi bật trình cài đặt:

1. Chốt phiên bản Calamares tương thích với bản Ubuntu đã chọn.
2. Rà soát chuỗi phân vùng, gắn hệ thống tệp, `unpackfs`, tạo người dùng, ngôn ngữ, mạng, bộ nạp khởi động và tháo hệ thống tệp.
3. Trỏ `unpackfs` tới dữ liệu casper thực tế, không giả định đường dẫn.
4. Gỡ gói dành riêng cho phiên trực tiếp, thông tin xác thực và đăng nhập tự động khỏi hệ thống đích.
5. Thử đĩa trống và bảo toàn dữ liệu có sẵn bằng đĩa ảo dùng riêng.
6. Xác nhận đăng nhập, cấp quyền sudo, mạng và cập nhật trên bản cài.
7. Kiểm thử BIOS và UEFI độc lập; chỉ công bố Secure Boot sau khi có kết quả.

Ghi nhật ký, mã kiểm tra ISO chính xác, phần sụn ảo và bố cục đĩa vào [danh sách nghiệm thu máy ảo](../../tests/integration/VM_CHECKLIST.md).
