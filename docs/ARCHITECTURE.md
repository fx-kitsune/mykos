# MyKOS — Kiến trúc kỹ thuật

- Trạng thái: Kiến trúc định hướng phiên bản 1.0, đã có một phần triển khai M0.
- Phạm vi: Bản phân phối máy tính cá nhân x86_64.
- Tham chiếu: [Tầm nhìn](PRODUCT_VISION.md), [lộ trình](ROADMAP.md), [trạng thái triển khai](IMPLEMENTATION_STATUS.md).

## 1. Mục tiêu kiến trúc

Lắp ghép thành phần nguồn mở đã trưởng thành, bổ sung lớp tích hợp gọn và trải nghiệm MyKOS nhất quán. Giữ khả năng thay nền Linux khi thực tế cho phép; tách giao diện khỏi thao tác đặc quyền; ưu tiên D-Bus và giao diện dòng lệnh được công bố; hạn chế bản phân nhánh dài hạn; tạo ảnh tái lập được; kiểm thử được bản phát hành và áp dụng đặc quyền tối thiểu.

## 2. Các lớp logic

| Lớp | Thành phần và trách nhiệm |
|---|---|
| Trải nghiệm MyKOS | Môi trường làm việc, thiết lập, danh mục ứng dụng, quản lý tệp, thông báo và công cụ phát triển |
| Nền tảng MyKOS | API hệ thống, tích hợp ứng dụng, cập nhật, thiết bị, cấu hình, chẩn đoán và chính sách |
| Dịch vụ Linux | systemd, D-Bus, Polkit, NetworkManager, PipeWire, UDisks2, fwupd |
| Nền tảng đồ họa | KDE Plasma, KWin, Wayland, Qt/QML, Mesa |
| Hệ điều hành nền và phần cứng | Nhân Linux, GNU và công cụ người dùng, thư viện, phần sụn, thiết bị |

Đây là cách nhóm trách nhiệm, không phải ranh giới tiến trình hoặc gói phần mềm. Plasma, KWin, Wayland, Qt và Mesa có vị trí khác nhau trong hệ thống đồ họa thực tế.

## 3. Công nghệ nền tảng

| Hạng mục | Lựa chọn | Phạm vi và giới hạn |
|---|---|---|
| Hệ điều hành nền | Ubuntu 24.04 LTS Noble | Đã chốt cho thử nghiệm M0; xem ADR 0001 |
| Kiến trúc | amd64 / x86_64 | Kiến trúc khác để sau |
| Môi trường làm việc | KDE Plasma 5.27 của Noble | Tích hợp thành phần gốc, chưa phân nhánh toàn bộ |
| Giao thức hiển thị | Định hướng Wayland | Phải kiểm thử riêng và giữ đường tương thích khi cần |
| Quản lý cửa sổ và tổng hợp hình ảnh | KWin | Thành phần gốc KDE |
| Giao diện riêng MyKOS | Qt 6/QML | Workspace hiện dùng Python/PyQt6; không có nghĩa Plasma nền đã là Qt 6 |
| Dịch vụ mới | Ưu tiên Rust khi phù hợp | Đặc biệt với dịch vụ nền hoặc đặc quyền; chưa triển khai |
| Tích hợp hệ thống | D-Bus | Giao diện có tài liệu, phạm vi yêu cầu hẹp |
| Cấp quyền | Polkit | Cho thao tác đặc quyền cần xác thực |
| Khởi tạo và dịch vụ | systemd | Dùng cơ chế chuẩn |
| Mạng | NetworkManager | Dùng tích hợp hệ thống và giao diện có sẵn |
| Âm thanh | PipeWire | Dùng thành phần gốc |
| Lưu trữ và thiết bị | UDisks2, udev | Tích hợp qua giao diện được hỗ trợ |
| Phần sụn | fwupd | Chỉ ở thiết bị và nguồn được hỗ trợ |
| Gói hệ thống | APT/DEB | Hệ điều hành nền và thành phần tích hợp chặt |
| Ứng dụng đồ họa | Flatpak | Hướng phân phối ưu tiên cần tiếp tục đánh giá |
| Trình cài đặt | Calamares | Chưa cấu hình; phải xác nhận tương thích và kiểm thử |
| Tạo ảnh | Ubuntu live-build `3.0~a57-1ubuntu49.1` | Cấu hình thử nghiệm BIOS, chưa có ISO được nghiệm thu |
| Máy ảo | QEMU/KVM | Dùng TCG khi không có KVM; khởi động thực tế chưa được xác nhận |

Bảng phân biệt công nghệ đã chọn với khả năng đã kiểm chứng. Phiên bản và ràng buộc phải được ghi trong cấu hình bản dựng, không suy ra khả năng hỗ trợ chỉ từ danh sách gói.

## 4. Lớp bản phân phối

Chịu trách nhiệm chọn gói và kho phần mềm, chính sách nhân/phần sụn, mặc định giao diện, nhận diện, cấu hình cài đặt, ứng dụng mặc định, tạo ảnh và xác định phần cứng hỗ trợ.

Ưu tiên cấu hình khai báo. Mỗi lần phát hành phải ghi phiên bản gói, nguồn kho, phiên bản công cụ và thông tin ảnh hệ thống. Kho Ubuntu đang thay đổi theo thời gian nên cấu hình hiện tại chưa bảo đảm tái lập từng bit.

## 5. Lớp trải nghiệm làm việc

Bắt đầu từ Plasma gốc, cấu hình chủ đề, biểu tượng, phông chữ, hình nền, thanh tác vụ, trình mở ứng dụng, lần chạy đầu, thông báo, phím tắt, khả năng tiếp cận và quản lý nguồn. Chỉ bổ sung điểm vào thiết lập riêng khi KDE chưa đáp ứng.

Fold hiện được triển khai thành tài nguyên nhận diện KDE và ứng dụng Workspace không đặc quyền chạy cùng Plasma. Workspace có ba ngữ cảnh ghi chú, không thay thế KDE Activities hoặc trình quản lý cửa sổ. Xem [phạm vi native](../desktop/README.md) và [ADR 0002](ADR/0002-fold-native-integration.md).

Chỉ cân nhắc giao diện hệ thống hoặc trình mở ứng dụng riêng khi có nhu cầu đã xác nhận, phạm vi hẹp và chiến lược tương thích dự án gốc rõ ràng.

## 6. Lớp nền tảng MyKOS

Cung cấp giao diện ổn định, hẹp cho lớp hiển thị; chuyển công việc hệ thống thực sự cho dịch vụ gốc.

| Mô-đun dự kiến | Trách nhiệm | Tích hợp |
|---|---|---|
| `system-info` | Thông tin hệ điều hành, nhân, phần cứng và chẩn đoán | procfs, sysfs, D-Bus, công cụ chuẩn |
| `display-integration` | Trải nghiệm cấu hình màn hình | KWin và giao diện môi trường làm việc |
| `network-integration` | Trạng thái và thao tác mạng | NetworkManager D-Bus |
| `user-integration` | Người dùng và tài khoản | Dịch vụ hệ thống, Polkit |
| `application-manager` | Ứng dụng đã cài và nguồn phần mềm | APT, Flatpak |
| `update-manager` | Phát hiện và hướng dẫn cập nhật | APT, Flatpak |
| `device-integration` | Phát hiện thiết bị và trạng thái | udev, UDisks2, fwupd |
| `power-integration` | Pin và nguồn điện | UPower, dịch vụ môi trường làm việc |
| `diagnostics` | Thu thập nhật ký và sức khỏe hệ thống khi người dùng đồng ý | journalctl, giao diện hệ thống |

Đây là các trách nhiệm dự kiến, không yêu cầu một dịch vụ riêng cho từng tính năng. Ưu tiên ít dịch vụ có trách nhiệm mạch lạc.

### Hợp đồng giao tiếp

- Giao diện có phiên bản, kiểu yêu cầu và kiểu lỗi rõ ràng.
- Ưu tiên D-Bus; kiểm tra mọi đầu vào tại ranh giới dịch vụ.
- Tiến trình giao diện không có đặc quyền; dùng Polkit khi cần cấp quyền.
- Không cung cấp API chạy tùy ý lệnh root cho giao diện.
- Ghi nhật ký thao tác liên quan bảo mật, tránh thu thập thông tin cá nhân không cần thiết.
- Có thời gian chờ, cơ chế hủy và báo cáo trạng thái rõ ràng.

Quy trình minh họa: giao diện gửi yêu cầu có kiểu; dịch vụ kiểm tra đầu vào và quyền; gọi API gốc; trả kết quả có cấu trúc; giao diện giải thích kết quả và bước tiếp theo. Khi triển khai phải dùng giao diện thực sự được thành phần nền hỗ trợ.

## 7. Chiến lược ứng dụng và gói

- **APT/DEB:** Hệ điều hành nền, trình điều khiển, thư viện và thành phần tích hợp chặt.
- **Flatpak:** Nhiều ứng dụng máy tính cá nhân; hiển thị rõ nguồn và quyền.
- **Công cụ phát triển:** Gói chuẩn, bộ cài gốc, trình quản lý phiên bản ngôn ngữ và container theo hướng dẫn bảo mật đã công bố.

Danh mục MyKOS cần thống nhất trải nghiệm và phân biệt chính xác nhà phát hành, nguồn, quyền và cơ chế cập nhật. Không tạo định dạng gói độc quyền trong các mốc đầu.

## 8. Cập nhật, phục hồi và độ tin cậy

Dùng cơ chế cập nhật được bản phân phối nền hỗ trợ. Tách cập nhật hệ điều hành với cập nhật Flatpak cả về xử lý lẫn cách trình bày. Kiểm thử cập nhật gián đoạn, công bố ghi chú phiên bản và giới hạn.

Chỉ đánh giá hoàn tác bằng Btrfs/Snapper sau khi hệ thống tệp, trình cài đặt, bộ nạp khởi động và cập nhật đã được thử cùng nhau. Phương án dựa trên ảnh như bootc là quyết định về sau, không phải điều kiện mặc định của bản tối thiểu.

Ảnh chụp trạng thái không thay thế sao lưu. Bảo vệ dữ liệu người dùng phải có hướng dẫn độc lập với hoàn tác hệ thống.

## 9. Mô hình bảo mật

Phiên người dùng mặc định không đặc quyền; API quản trị hẹp và có cấp quyền; không nhúng thông tin xác thực vào ảnh hoặc repo; ưu tiên gói có chữ ký và nguồn đáng tin; giải thích quyền ứng dụng; duy trì kênh cập nhật được hỗ trợ; giảm dịch vụ nền và giao diện mở ra ngoài. Công bố quy trình báo cáo lỗ hổng trước phát hành công khai.

## 10. Tạo ảnh, kiểm thử và phát hành

Quy trình mục tiêu:

1. Bắt đầu từ bản nền và danh sách gói đã chốt.
2. Giải quyết phụ thuộc từ kho đã khai báo.
3. Áp dụng cấu hình và nhận diện có quản lý phiên bản.
4. Tạo ISO khởi động được.
5. Xuất mã kiểm tra và thông tin bản dựng.
6. Chạy kiểm thử ảnh, khởi động và cài đặt.
7. Lưu nhật ký và sản phẩm của từng lần tạo ảnh.

Các lớp kiểm thử gồm kiểm tra tĩnh, gói/phụ thuộc, khởi động QEMU/KVM, cài đĩa sạch, chức năng môi trường làm việc, cập nhật/phục hồi và phần cứng đại diện. Tạo ISO thành công chưa đủ để nghiệm thu bản phát hành.

## 11. Tổ chức mã nguồn

| Đường dẫn | Vai trò |
|---|---|
| `docs/` | Tầm nhìn, kiến trúc, lộ trình, tạo ảnh và quyết định kiến trúc |
| `design-system/` | Bản mẫu trình duyệt và tài nguyên Fold gốc |
| `distribution/` | Nền tảng, danh sách gói, kho, cài đặt, nhận diện và cấu hình ảnh |
| `desktop/workspace/` | Giao diện Qt/QML và lưu trữ ghi chú |
| `desktop/integration/` | Lệnh mở ứng dụng và mục menu KDE |
| `tests/integration/` | Kiểm thử cấu hình và danh sách nghiệm thu máy ảo |
| `tests/desktop/` | Kiểm thử dữ liệu và giao diện native |
| `tests/hardware/` | Ma trận hỗ trợ thiết bị |
| `scripts/build/` | Tạo cấu hình, ảnh, thông tin bản dựng và xuất tài nguyên thiết kế |
| `scripts/development/` | Công cụ phục vụ phát triển như chạy QEMU |

Khi bắt đầu triển khai mới, có thể bổ sung `platform/`, `applications/`, `services/`, các thành phần giao diện và `scripts/release/` theo trách nhiệm. Không tạo thư mục rỗng để ngụ ý tính năng đã tồn tại.

## 12. Quyết định kiến trúc

Ghi quyết định ảnh hưởng đáng kể đến tương thích, bảo mật, đóng gói hoặc bảo trì trong `docs/ADR/`. Mỗi hồ sơ phải có bối cảnh, vấn đề, các lựa chọn, quyết định, lý do, hệ quả, hướng chuyển đổi, ngày và trạng thái. Xem xét lại khi bằng chứng mới làm thay đổi giả định.
