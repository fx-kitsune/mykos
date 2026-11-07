# Trạng thái triển khai

Cập nhật ngày 07/11/2026. **M0 đang thực hiện, chưa nghiệm thu.**

## Đã triển khai

- Cấu hình Ubuntu Noble amd64 và nguồn kho có chữ ký.
- Danh sách gói KDE, cấu hình mặc định dựa trên Breeze.
- Lớp thích nghi live-build Ubuntu riêng cho từng bản dựng và kiểm tra điều kiện tạo ISO bằng root.
- Nhật ký, danh sách phiên bản gói, mã băm đầu vào/cấu hình và mã kiểm tra sản phẩm.
- Lệnh chạy QEMU, kiểm tra tự động trong CI, danh sách nghiệm thu máy ảo và phần cứng.
- Workspace Qt 6/QML theo Fold: ghi chú cục bộ, sáng/tối, tập trung và mở ứng dụng KDE.
- Bộ màu MyKOSDark/MyKOSLight, biểu tượng Fold, hình nền và bước đưa ứng dụng vào ảnh.

- Workflow tạo ISO trên GitHub Actions: chạy thủ công hoặc khi sửa chính workflow; lưu sản phẩm và nhật ký riêng trong 7 ngày. Chưa có kết quả build đầy đủ được xác nhận tại thời điểm cấu hình.

## Đã kiểm chứng trong môi trường cloud

- Mười kiểm thử tạo ảnh/cấu hình/menu khởi động và bảy kiểm thử giao diện/lưu trữ đã đạt ở các lần kiểm tra tương ứng.
- Khởi chạy native không màn hình; render sáng/tối; sửa ghi chú; chuyển ngữ cảnh; bật/tắt tập trung; mở tìm ứng dụng; kích thước 900×700; không có cảnh báo QML.
- Cú pháp shell và tính nhất quán của tài nguyên thiết kế sinh tự động.
- 39 tên gói nền ban đầu tồn tại trong chỉ mục Ubuntu Noble amd64; đây mới là kiểm tra khả dụng, chưa cài và giải quyết phụ thuộc toàn bộ ảnh.
- Tám tên gói mô-đun Qt/PyQt có trong chỉ mục `universe` của Noble.
- Tạo cấu hình với gói Ubuntu live-build đã chốt và debootstrap đã giải nén; chưa thực hiện `chroot` hoặc tạo ISO đầy đủ.

## Giới hạn môi trường ghi nhận khi kiểm thử

Máy chạy Debian 13, không có root/sudo hoặc thiết bị KVM; dung lượng trống ghi nhận khoảng 7,5 GiB, thấp hơn yêu cầu 25 GiB. Công cụ kiểm tra điều kiện sẽ báo các giới hạn trước khi tạo ảnh. Đây là trạng thái ghi nhận của môi trường kiểm thử, không phải cấu hình bắt buộc cho mọi lần chạy sau.

## Còn thiếu để nghiệm thu M0

- Tạo ISO đầy đủ trên máy ảo Ubuntu đúng điều kiện.
- Khởi động và kiểm tra môi trường làm việc trực tiếp.
- Tích hợp Calamares, kiểm thử cài đặt và lần đăng nhập đầu trên bản cài.
- Kiểm tra mạng, âm thanh, màn hình, quản lý gói, cập nhật và phục hồi.
- Khóa kho theo thời điểm, khóa bộ công cụ và so sánh bản dựng độc lập.
- Xác định, kiểm thử ma trận phần cứng; xem UEFI/Secure Boot là mục tiêu riêng.

Xem [phạm vi Workspace](../desktop/README.md). Chưa có giao diện hệ thống tự viết, dịch vụ root riêng, hoàn tác tự động, lớp tương thích Windows hoặc bản phát hành công khai. Phần tích hợp Fold chưa hoàn thành M1; ưu tiên nghiệm thu M0 trước khi mở rộng.

## Lỗi Actions đã xác định

- Kiểm thử Qt thiếu `libEGL.so.1` trên runner: đã bổ sung thư viện đồ họa; lượt kiểm tra commit `ff1f4b3` đã đạt trên GitHub.
- Tạo ISO thiếu chủ đề Oneiric/gfxboot: đã thay bước menu BIOS bằng cấu hình văn bản cho Noble, có kiểm thử thiếu thành phần bắt buộc. Chờ xác nhận lượt tạo ISO mới; chưa công bố có ISO hoàn chỉnh.

- Lượt sau sửa menu đã tạo khoảng 2,2 GiB ISO, nhưng thiếu `isohybrid` trong `chroot` ở bước tạo ảnh lai. Đã sửa ánh xạ gói từ `syslinux` sang `syslinux-utils` trong bản sao bộ công cụ; chờ xác nhận lại toàn bộ workflow.
