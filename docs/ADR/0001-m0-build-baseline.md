# ADR 0001 — Nền tảng ảnh Ubuntu/KDE cho M0

- Ngày: 07/11/2026.
- Trạng thái: Chấp nhận cho phát triển; chờ kiểm chứng ảnh đầy đủ.

## Bối cảnh

Tại thời điểm bắt đầu triển khai, repo chỉ có tầm nhìn, kiến trúc và lộ trình, chưa có công cụ tạo ảnh. Cần hoàn thành M0 trước khi mở rộng giao diện hệ thống hoặc dịch vụ đặc quyền riêng.

## Quyết định và lựa chọn đã cân nhắc

Dùng Ubuntu 24.04 LTS Noble amd64 và Plasma 5.27 từ kho gốc cho thử nghiệm đầu tiên. Ubuntu 26.04 và Plasma 6 là phương án chuyển nền về sau, sau khi đánh giá tích hợp cài đặt và phần cứng. Qt 6/QML cho thành phần MyKOS không đồng nghĩa Plasma trong Noble dùng Qt 6.

Dùng Ubuntu live-build `3.0~a57-1ubuntu49.1`, casper và ISO lai Syslinux, trước hết cho BIOS truyền thống. Đã cân nhắc Debian live-build có cách tích hợp Ubuntu khác; chỉnh sửa ISO Kubuntu với đầu vào lớn, khó truy nguyên đầy đủ; và tích hợp trực tiếp livecd-rootfs cần thêm hạ tầng phát hành.

Sao chép bộ công cụ đã cài vào từng thư mục tạo ảnh. Gói Ubuntu được kiểm tra có bước dò thư viện hàm trong shell con, khiến cách gọi sau di chuyển mất các hàm như `Echo`. Lớp thích nghi nhỏ thay bước dò bằng nạp trực tiếp thư viện đã sao chép vào shell hiện tại. Không vá hành vi khác hoặc sửa gói hệ thống. Ghi nhận lớp này trong đầu vào và xem lại khi thay bộ công cụ cũ.

Dùng các kho Ubuntu có chữ ký `main`, `restricted`, `universe`, `multiverse` cùng bản vá bảo mật và cập nhật. Phần mềm `restricted`/`multiverse` chịu ràng buộc giấy phép và hỗ trợ của nguồn; phải rà soát trước khi phân phối công khai. Giữ định danh nền tương thích Ubuntu và bổ sung nhận diện biến thể MyKOS.

## Hệ quả và hướng chuyển đổi

Mục tiêu đầu tiên là phiên chạy trực tiếp chưa nghiệm thu, chưa phải bản cài đặt được xác nhận. Calamares cần chuỗi mô-đun, dữ liệu cài ngoại tuyến, phân vùng, bộ nạp khởi động và dọn tài khoản phiên trực tiếp được rà soát riêng. Chỉ đưa trình cài đặt ra sử dụng sau khi kiểm thử.

UEFI, Secure Boot và chuyển sang Plasma mới là điều kiện cần xác nhận riêng. Kho gói thay đổi theo thời gian nên chưa tạo lại ảnh giống từng byte; cần khóa kho theo thời điểm và toàn bộ công cụ máy tạo ảnh. Phải đánh giá thời gian hỗ trợ còn lại của KDE 5 trước khi chọn Noble cho phát hành công khai.
