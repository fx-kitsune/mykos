# Trạng thái triển khai

Cập nhật ngày 08/11/2026. **M0 đang thực hiện, chưa nghiệm thu.**

Tình trạng hiện tại: đã tạo ISO có Calamares; desktop phản hồi trong profile đồ họa phần mềm. Cấu hình installer mới đã mở được đến trang phân vùng trong máy ảo chẩn đoán, nhưng chưa cài xuống đĩa hoặc boot bản cài. Các mục bên dưới lưu lại tiến trình và kết quả theo từng ISO, không phải tất cả đều mô tả bản mới nhất.

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
- Nghiệm thu Calamares đã tích hợp, kiểm thử cài đặt và lần đăng nhập đầu trên bản cài.
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

## ISO cập nhật desktop ngày 08/11/2026

- [Lượt tạo ảnh 42443779141](https://github.com/fx-kitsune/mykos/actions/runs/42443779141) trên commit `6ea43d6` đã thành công. ISO chứa hình nền logo MyKOS và cấu hình desktop hiện tại ở commit này.
- [ISO và thông tin bản dựng](https://github.com/fx-kitsune/mykos/actions/runs/42443779141/artifacts/13603405483) khoảng 2,36 GB; kiểm tra `SHA256SUMS` trong workflow đã đạt. Artifact lưu đến ngày 15/11/2026. Mã băm ZIP của artifact không phải SHA-256 của tệp ISO bên trong.
- Workflow build đã tự kích hoạt [kiểm thử BIOS và phiên Plasma 42444741905](https://github.com/fx-kitsune/mykos/actions/runs/42444741905). Tại thời điểm ghi mục này, kiểm thử còn đang chạy; chưa đánh dấu desktop hoặc M0 đạt.
- Đầu vào ISO thay đổi trên `main` sẽ tự tạo ảnh mới. Sau build thành công, kiểm thử dùng đúng artifact của lượt đó, không dùng mặc định ISO cũ.
- Đã bổ sung kiểm tra console live, tiến trình Plasma/KWin, mở Dolphin/Konsole/Thiết lập và lưu ảnh trước/sau mở ứng dụng. 21 kiểm thử tích hợp cục bộ đã đạt; CI cấu hình/giao diện cũng đã đạt. Đây chưa phải kết quả chạy guest.

Bước tiếp theo: đọc kết quả guest, rà soát ảnh giao diện và giải quyết lỗi nếu có trước khi tích hợp trình cài đặt.

## Chẩn đoán desktop thực tế ngày 08/11/2026

- ISO nguồn từ build `42443779141` có SHA-256 `8e86c37851be57f67c799a514dc0c5c3916987f19affcffbc53b6298e2753033`.
- [Kiểm thử 42447580050](https://github.com/fx-kitsune/mykos/actions/runs/42447580050) xác nhận BIOS/userspace, đăng nhập tài khoản UID 1000, tiến trình Plasma/KWin, mở Dolphin/Konsole/Thiết lập và đọc bộ màu `MyKOSDark`.
- Tuy nhiên ảnh QEMU chỉ thấy splash KDE rồi nền đen; journal ghi `Freeze in OpenGL initialization detected` và KWin crash. Gọi D-Bus tới Plasma hết thời gian chờ. Vì vậy kết quả cũ `desktop-services-ready` không được xem là nghiệm thu giao diện.
- Công cụ kiểm thử mới yêu cầu Plasma trả số panel và desktop hợp lệ, cùng các ứng dụng hoạt động. Profile thử QEMU/TCG thêm `systemd.setenv=KWIN_COMPOSE=N` và `systemd.setenv=QT_QUICK_BACKEND=software` vào bản sao ISO để tránh khởi tạo OpenGL. Đây là cấu hình thử nghiệm cho máy ảo, chưa thay mặc định đồ họa của ISO hoặc chứng minh hỗ trợ phần cứng.
- 25 kiểm thử tích hợp cục bộ đã đạt. Kết quả máy ảo với profile phần mềm và rà soát ảnh vẫn đang chờ; chưa tích hợp Calamares.

Bằng chứng được đọc qua workflow `inspect-boot-evidence.yml` trong repo riêng; không cần thay chính sách mạng cloud để tải ảnh. Không gắn ổ đĩa cài đặt ở các phép thử desktop này.

## Desktop phản hồi và chuẩn bị trình cài đặt

- [Kiểm thử 42481797224](https://github.com/fx-kitsune/mykos/actions/runs/42481797224) trên cùng ISO nguồn đã đạt `desktop-ready` với profile software trong QEMU/TCG. Plasma trả đúng một panel và một desktop; Dolphin, Konsole, Thiết lập mở được. Biến môi trường KWin/Qt Quick đã được xác nhận từ tiến trình guest.
- Ảnh thật đã hiển thị panel và các cửa sổ; hình nền vẫn đen do chưa ghi rõ Image cho desktop mới. Mã khởi tạo đã được sửa chọn đường dẫn SVG logo, chờ xác nhận trong ISO kế tiếp.
- Journal TCG vẫn có lần khởi động Powerdevil/polkit-agent hết thời gian chờ; không xem kết quả desktop là nghiệm thu nguồn điện, thao tác quản trị, mạng hoặc phần cứng.
- Đã bổ sung cấu hình Calamares BIOS, wrapper chỉ chạy live, module tạo bản cài và GRUB. Chưa có kết quả cài xuống đĩa. Bản build kế tiếp sẽ kiểm tra mở Calamares và hình nền đã sửa.

## Calamares mở được trong máy ảo chẩn đoán

- Hai lỗi khởi chạy thực tế đã được sửa: launcher truyền nhầm thư mục dữ liệu bằng `--config`; branding thiếu trường `slideshow` bắt buộc của Calamares 3.3.5. Đã thêm QML slideshow và cấu hình tắt tải log lên máy chủ.
- [Chẩn đoán 42488462653](https://github.com/fx-kitsune/mykos/actions/runs/42488462653) đã đạt `installer-diagnostic-preview`. Đã rà soát ảnh chào, vị trí, bàn phím và phân vùng; Calamares nhận đúng một đĩa `/dev/vda` trống khoảng 40 GiB. Chưa chọn xóa đĩa hoặc ghi phân vùng.
- Phép thử này dùng ISO build `42484136362` và chép overlay installer mới vào phiên live; kết quả ghi mã băm từng tệp overlay. Nó xác nhận cấu hình mới nạp được, **không nghiệm thu launcher hoặc nội dung nguyên trạng của ISO cũ**.
- [Build 42488294820](https://github.com/fx-kitsune/mykos/actions/runs/42488294820) trên commit `730d054` đã thành công, chứa các sửa lỗi này. Kiểm thử khởi động/desktop của chính ISO này đang chạy ở [42489679609](https://github.com/fx-kitsune/mykos/actions/runs/42489679609).
- Công cụ kiểm thử giữ phiên VM hoạt động bằng phím Shift định kỳ để tránh màn hình khóa che bằng chứng; không đổi chính sách khóa màn hình của sản phẩm.

Tiếp theo: rà soát trang tài khoản và tổng kết trên đĩa ảo mới, thực hiện cài đặt, rồi tháo ISO để kiểm tra GRUB và tài khoản bản cài. Mạng, âm thanh, cập nhật, phục hồi và phần cứng vẫn chưa nghiệm thu.
