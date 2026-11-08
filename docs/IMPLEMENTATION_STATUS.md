# Trạng thái triển khai

Cập nhật ngày 08/11/2026. **M0 đang thực hiện, chưa nghiệm thu.**

## Đã triển khai

- Cấu hình Ubuntu Noble amd64 và nguồn kho có chữ ký.
- Danh sách gói KDE, cấu hình mặc định dựa trên Breeze.
- Lớp thích nghi live-build Ubuntu riêng cho từng bản dựng và kiểm tra điều kiện tạo ISO bằng root.
- Nhật ký, danh sách phiên bản gói, mã băm đầu vào/cấu hình và mã kiểm tra sản phẩm.
- Lệnh chạy QEMU, kiểm tra tự động trong CI, danh sách nghiệm thu máy ảo và phần cứng.
- Workspace Qt 6/QML theo Fold: ghi chú cục bộ, sáng/tối, tập trung và mở ứng dụng KDE.
- Bộ màu MyKOSDark/MyKOSLight, biểu tượng Fold, hình nền và bước đưa ứng dụng vào ảnh.

- Workflow tạo ISO trên GitHub Actions: chạy thủ công hoặc khi sửa chính workflow; lưu sản phẩm và nhật ký riêng trong 7 ngày. Lượt tạo ảnh trên commit `6bfe299` đã hoàn tất và lưu sản phẩm.

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

- Kiểm tra đăng nhập và tác vụ trong môi trường Plasma; mức khởi động BIOS tới môi trường người dùng đã có bằng chứng với bản sao thêm console.
- Tích hợp Calamares, kiểm thử cài đặt và lần đăng nhập đầu trên bản cài.
- Kiểm tra mạng, âm thanh, màn hình, quản lý gói, cập nhật và phục hồi.
- Khóa kho theo thời điểm, khóa bộ công cụ và so sánh bản dựng độc lập.
- Xác định, kiểm thử ma trận phần cứng; xem UEFI/Secure Boot là mục tiêu riêng.

Xem [phạm vi Workspace](../desktop/README.md). Chưa có giao diện hệ thống tự viết, dịch vụ root riêng, hoàn tác tự động, lớp tương thích Windows hoặc bản phát hành công khai. Phần tích hợp Fold chưa hoàn thành M1; ưu tiên nghiệm thu M0 trước khi mở rộng.

## Lỗi Actions đã xác định

- Kiểm thử Qt thiếu `libEGL.so.1` trên runner: đã bổ sung thư viện đồ họa; lượt kiểm tra commit `ff1f4b3` đã đạt trên GitHub.
- Tạo ISO thiếu chủ đề Oneiric/gfxboot: đã thay bước menu BIOS bằng cấu hình văn bản cho Noble, có kiểm thử thiếu thành phần bắt buộc. Chờ xác nhận lượt tạo ISO mới; chưa công bố có ISO hoàn chỉnh.

- Lượt sau sửa menu đã tạo khoảng 2,2 GiB ISO, nhưng thiếu `isohybrid` trong `chroot` ở bước tạo ảnh lai. Đã sửa ánh xạ gói từ `syslinux` sang `syslinux-utils` trong bản sao bộ công cụ; toàn bộ workflow đã thành công ở lượt kế tiếp.

## ISO đầu tiên tạo thành công trên Actions

- [Lượt tạo ảnh 42392072303](https://github.com/fx-kitsune/mykos/actions/runs/42392072303) trên commit `6bfe299` đã thành công ngày 07/11/2026.
- Bước tạo ISO, kiểm tra SHA-256 và ghi cấu trúc khởi động bằng `xorriso` đều hoàn tất.
- [Gói ISO và thông tin bản dựng](https://github.com/fx-kitsune/mykos/actions/runs/42392072303/artifacts/13582690633) có dung lượng khoảng 2,36 GB; lưu đến khoảng ngày 14/11/2026 theo chính sách 7 ngày.
- [Nhật ký chẩn đoán](https://github.com/fx-kitsune/mykos/actions/runs/42392072303/artifacts/13581884776) được lưu riêng.
- CI kiểm tra cấu hình/giao diện của cùng commit cũng đã đạt.

Đây là bản dựng phát triển chưa kiểm thử khởi động. Chưa xác nhận đăng nhập Plasma, cài đặt Calamares, phần cứng hoặc phục hồi; M0 vẫn chưa nghiệm thu. Các bước tạo ảnh không còn bị chặn bởi cấu hình máy cá nhân vì đã chuyển sang máy chạy của GitHub.

## Bước nghiệm thu khởi động tiếp theo

Đã bổ sung workflow QEMU dùng lại Artifacts, kiểm tra mã SHA-256 và khởi động BIOS từ bản sao thêm console nối tiếp. Có nhật ký, ảnh màn hình và kết quả có cấu trúc; chưa thay đổi trạng thái nghiệm thu khởi động trước khi có lượt chạy thực tế. Các kiểm thử công cụ cũng xác nhận thông báo nhân đơn thuần không được xem là thành công và lỗi khởi động phải thắng dấu hiệu thành công cũ trong nhật ký.

## Kết quả kiểm thử BIOS ngày 08/11/2026

- [Lượt QEMU 42435820231](https://github.com/fx-kitsune/mykos/actions/runs/42435820231) trên commit `e3fb762` đã đạt với trạng thái `userspace-ready`.
- ISO nguồn có SHA-256 `4cfe76fce312aa970f7e04540e8d14cd4341e7e1c41b0312f0451f0b57442774`.
- Máy ảo dùng TCG, RAM 4 GiB và hai CPU, không gắn đĩa cài đặt; toàn bộ công cụ kiểm thử ghi nhận khoảng 168 giây.
- Bản sao thêm console có SHA-256 `96321cbbf52584a9c1ce4b26888e8dec35e4a9792773fd948773d74a4842b78a`; nhân, initrd và squashfs giữ nguyên từ ISO nguồn.
- [Bằng chứng gồm kết quả, nhật ký và ảnh màn hình](https://github.com/fx-kitsune/mykos/actions/runs/42435820231/artifacts/13598969791) lưu trong 7 ngày.

Chỉ nghiệm thu mức BIOS → nhân → môi trường người dùng ở bản sao chẩn đoán. Chưa xác nhận đăng nhập Plasma, âm thanh/mạng, khả năng khởi động nguyên trạng trên phần cứng thật hoặc cài đặt. Phần việc tiếp theo là nghiệm thu phiên Plasma và tích hợp Calamares sau đó.

## Bộ thiết kế M1

[Bản thiết kế M1 phiên bản 2.0](../design-system/m1/README.md) thay thế bố cục trang tổng quan cũ. Desktop mặc định chỉ có hình nền và panel; menu, cửa sổ tệp và thiết lập xuất hiện theo thao tác. Đã bỏ câu chào, thẻ nội dung và Workspace tự mở khỏi bản mẫu. Fold chỉ giữ ở màu, biểu tượng và chất liệu. Đồng thời đã thêm gói giao diện Plasma `org.mykos.desktop`, bố cục panel chỉ tạo khi hồ sơ chưa có panel, hình nền tối mới và biểu tượng menu. Đã kiểm thử quy tắc bố cục với API giả lập; chưa tạo ISO mới để kiểm chứng việc áp cấu hình trong Plasma. Không thay giao diện Workspace native.
