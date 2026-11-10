## ISO Debian + MyKOS Desktop đã build/boot (2026-11-10)

[Build 42836804675](https://github.com/fx-kitsune/mykos/actions/runs/42836804675), nguồn `904e61d60549d00a3d5b0642e7d436e70a40d705`, ISO SHA-256 `dd6df477d885b180231708aff16acde049c461338cbbe61adc411a6f436d2b13`, đã qua build, checksum và cấu trúc BIOS/UEFI. OVMF USB đạt `desktop-ready` sau 56,1 giây, CD-ROM sau 55,6 giây; guest UID 1000, MyKOS Shell/Openbox, Thunar và xfce4-terminal hoạt động, shell IPC trả panel/ticks. BIOS đạt `userspace-ready` sau 60 giây. Đã xem ảnh UEFI USB cuối, thấy panel/taskbar MyKOS, nền desktop và hai ứng dụng. Không dùng các kết quả này để nghiệm thu cài xuống đĩa.

Artifacts vẫn bị chặn bởi quota; [release nháp](https://github.com/fx-kitsune/mykos/releases/tag/untagged-7f6bdfd6a5f5479a1c65) có một archive `.7z.001` 1.568.963.045 byte và checksum. Không có phần `.002` ở build này. Bằng chứng có cấu trúc: `tests/integration/evidence/debian-own-de-42836804675.json`. Profile boot phần mềm đã được chọn nhưng `QT_QUICK_BACKEND` trong môi trường guest là null; chưa xác nhận override đã truyền tới shell.

## Trình cài terminal từ repo

Đã có `scripts/install/mykos-install.py`: wizard tương tác, plan không ghi, debootstrap xác thực kho, root ext4 đã mount, kiểm tra ESP/bios_grub, xác nhận UUID và mật khẩu mới. Không tự phân vùng/format, không cài gói live/Calamares vào đích. Bản repo có 62 integration tests và 8 native desktop tests đã qua CI; cài đĩa/reboot bằng trình cài terminal vẫn chưa được nghiệm thu. Xem `docs/INSTALL_FROM_RESCUE.md`.

## MyKOS Desktop riêng (2026-11-10)

Đã bỏ gói và overlay Plasma/KWin khỏi ảnh mặc định; shell, panel, launcher, desktop và session manager là mã MyKOS. Openbox quản lý cửa sổ X11 tạm thời, SDDM chọn phiên MyKOS; Calamares đã chuyển session mặc định và dọn live autologin/sudoers. Qt/PyQt6 đã cài trong venv để chạy kiểm thử trong lần này.

Đã chạy 50 bài integration và 8 bài desktop, trong đó có phiên Xvfb/Openbox thật: loại cửa sổ, strut 56 px, IPC launcher/settings, cửa sổ ứng dụng, desktop ảo và dừng phiên. Chưa tạo hoặc nghiệm thu ISO mới, compositor Wayland/locking/tray/power management riêng chưa hoàn tất. Các bài chẩn đoán dùng tọa độ và ISO Ubuntu cũ không chứng minh DE mới. Xem ADR 0004 và desktop/README.md.

## Refactor nền mới (2026-11-09)

Đã chuyển cấu hình nguồn, kernel, live initramfs, menu boot, đường dẫn installer và CI tạo ISO sang Debian 13; đặt ID MyKOS. Đã kiểm tra 48 bài integration, xuất thiết kế và tên gói Debian main. `lb config` được thử với gói Debian giải nén. Kiểm thử giao diện desktop chưa chạy được vì thiếu PyQt6 trong môi trường; bốn bài state thuần Python đã qua. Chưa build/boot ISO Debian; userspace Debian và KDE còn là phụ thuộc tạm thời.

> Cấu hình hiện hành đã chuyển sang Debian 13; xem [ADR 0003](ADR/0003-independent-linux-platform.md). Nội dung Ubuntu và kết quả ISO bên dưới là lịch sử, không nghiệm thu nền mới. Mục tiêu nền riêng chỉ dùng Linux kernel còn đang triển khai.

# Trạng thái triển khai

Cập nhật ngày 09/11/2026 (giờ Việt Nam). **M0 đang thực hiện, chưa nghiệm thu.**

Live UEFI/GPT đã đạt trên máy ảo ở [42641747422](https://github.com/fx-kitsune/mykos/actions/runs/42641747422); [gói ISO nháp](https://github.com/fx-kitsune/mykos/releases/tag/untagged-427026dd49e9e2f8ac7b) đã có đủ hai volume 7-Zip. USB GPT và CD-ROM đều vào Plasma bằng đồ họa phần mềm; BIOS tới môi trường người dùng cũng đạt. Secure Boot, cài đặt UEFI và phần cứng thật chưa hỗ trợ/nghiệm thu. [Phạm vi, checksum và cách ghi USB](UEFI_LIVE.md). Các bằng chứng cài đặt BIOS bên dưới thuộc ISO cũ, không được suy rộng sang cài UEFI.

Tình trạng hiện tại: ISO mới đã đạt cài đặt BIOS, boot không ISO, đăng nhập SDDM/Plasma X11, mạng/APT, tệp, độ phân giải và âm thanh ảo. Discover đã mở và hiển thị danh mục không còn lỗi xác thực sau khi sửa ngữ cảnh phiên trong công cụ thử. Các phần lịch sử bên dưới mô tả từng ISO, không phải tất cả là trạng thái bản mới nhất.

## Bản dựng đã kiểm thử cài đặt BIOS

- [Build 42527363919](https://github.com/fx-kitsune/mykos/actions/runs/42527363919), nguồn `187042d`; [ISO và thông tin bản dựng](https://github.com/fx-kitsune/mykos/actions/runs/42527363919/artifacts/13635659125), lưu 7 ngày từ 08/11/2026 UTC.
- SHA-256 ISO: `0de50cbd7cc982d083183786f9d33b83b0b1f9aacb8f39522e8da733d63a5751`.
- [Boot/live desktop 42528988768](https://github.com/fx-kitsune/mykos/actions/runs/42528988768) đạt trên đúng ISO; desktop phần mềm còn được quan sát trên TCG.
- [Cài đặt 42529928289](https://github.com/fx-kitsune/mykos/actions/runs/42529928289), công cụ `7147161`, đạt `installed-multimedia-ready` sau khoảng 413,8 giây. Hai VM dùng KVM, RAM 4 GiB, hai CPU; cài vào QCOW2 mới 40 GiB rồi bỏ ISO, boot GRUB và đăng nhập SDDM bằng tài khoản thường.
- DHCP/DNS/HTTPS, sudo yêu cầu mật khẩu, APT có chữ ký và vòng cài/chạy/gỡ `hello` đạt. Dolphin/Konsole/Thiết lập mở; tệp trong Documents đúng nội dung và chủ sở hữu. XRandR đổi 1280×800 → 1024×768 → 1280×800 thành công.
- PipeWire/WirePlumber hoạt động, thay/khôi phục âm lượng và phát 440 Hz thành công. PCM từ HDA ảo thực sự chứa tần số yêu cầu ở 44,1 kHz; clip `audio-tone-evidence.wav` có SHA-256 `076135f37d6e6071eeb546591b539ad830c52114d2a07544bd8d4ff2801b71fc`.
- Ba unit PolicyKit/Powerdevil/KScreen giữ `Type=dbus`, đúng BusName, deadline 60 giây, `active/running`, `NRestarts=0` cả trước và sau tác vụ màn hình/Discover. Đã rà soát ảnh hình nền logo của bản cài và ảnh ứng dụng.
- **Quản lý gói còn một phần:** Flatpak CLI chạy, chưa cấu hình remote; Discover mở và hiển thị danh mục nhưng có hộp thoại “Failed to obtain authentication”. Kết quả tự động cũ chỉ yêu cầu tiến trình mở, không nghiệm thu giao dịch PackageKit. Công cụ đã siết điều kiện lỗi này và đổi cách mở Discover qua user service manager để kiểm tra tác động của phiên console nối tiếp.
- [Bằng chứng JSON/log/ảnh/clip âm thanh](https://github.com/fx-kitsune/mykos/actions/runs/42529928289/artifacts/13637261439). Serial-getty và phần cứng âm thanh ảo chỉ là thiết lập kiểm thử; không xem là nghiệm thu phần cứng thật.
- Với VGA chuẩn của QEMU, chọn **MyKOS (do hoa phan mem cho may ao)**. Mặc định OpenGL, Wayland, KScreen OSD/KSplash trên TCG chậm, cập nhật/recovery và thiết bị thật còn cần kiểm tra. Plasma tự fallback sang tài nguyên Breeze theo mã nguồn 5.27; chưa có bằng chứng lỗi do thiếu tài nguyên fallback của chủ đề MyKOS.

## Kiểm tra lại Discover trên cùng ISO

[Lượt 42531078658](https://github.com/fx-kitsune/mykos/actions/runs/42531078658), công cụ `49ded1d`, đạt lại toàn bộ bộ thử sau 411,9 giây trên chính SHA-256 ISO ở trên, hai VM đều KVM. Discover được mở bằng user service manager thay vì là tiến trình con của console nối tiếp; PolicyKit xác định phiên theo tiến trình/systemd, không chỉ biến DISPLAY. ControlGroup của Discover nằm trong `user@1000.service/app.slice/mykos-discover-smoke.service`.

Log không còn “Failed to obtain authentication” hoặc lỗi giao dịch PackageKit, ảnh `installed-multimedia.png` đã được rà soát: danh mục hiển thị, không còn hộp thoại lỗi. Không cần thay chính sách cấp quyền hoặc sửa ISO cho vấn đề do công cụ thử này. Điều kiện kiểm thử hiện từ chối lỗi giao dịch kể cả khi tiến trình Discover còn chạy. Cả ba dịch vụ phiên vẫn ổn định sau tác vụ.

[Bằng chứng mới nhất](https://github.com/fx-kitsune/mykos/actions/runs/42531078658/artifacts/13638110433) chứa JSON/log/ảnh và clip 440 Hz SHA-256 `d912922c8ce7743de0d9d2f784522cdee40c53a1191178fe519c85cfee1bcac5`. APT đã thử cài/chạy/gỡ; Discover mới nghiệm thu mở/danh mục/không có lỗi khởi đầu, chưa thử cài/gỡ qua giao diện. Flatpak chưa thêm remote. M0 còn thiếu khóa đầu vào và so sánh bản dựng độc lập; cập nhật/recovery/phần cứng chưa nghiệm thu.

Trang tĩnh đã cập nhật tiến độ ở commit `f576a51`; [kiểm tra 42531247253](https://github.com/fx-kitsune/mykos-static-web/actions/runs/42531247253) và [Pages 42531247148](https://github.com/fx-kitsune/mykos-static-web/actions/runs/42531247148) đều thành công. Các ảnh trên web vẫn có nhãn bản thiết kế M1, không được đổi thành ảnh chứng nhận ISO.

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

- Kiểm tra quản lý gói cơ bản đã có APT và mở Discover; giao dịch cài/gỡ/cập nhật bằng giao diện và nguồn Flatpak đầy đủ thuộc phạm vi ứng dụng còn phải mở rộng.
- Khóa kho theo thời điểm, khóa bộ công cụ và so sánh bản dựng độc lập; hiện nguồn gói vẫn thay đổi theo thời gian.
- Chốt phạm vi đồ họa được hỗ trợ và ghi đầy đủ lỗi còn lại; không suy rộng kết quả software/X11 sang OpenGL hoặc Wayland.

Trước phát hành công khai còn phải kiểm thử cập nhật/reboot, phục hồi, giấy phép và thời gian hỗ trợ nền KDE 5; xác định ma trận phần cứng. UEFI/Secure Boot là phạm vi riêng chưa hỗ trợ.
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

## Cài đặt thực tế và hình nền đã xác nhận

- [Build 42490508466](https://github.com/fx-kitsune/mykos/actions/runs/42490508466) trên commit `be895b2` thành công; ISO SHA-256 `caadce0d0a2ba2734057045f2b81f5dbc709cabc25d054f32e1874509cb5492c`. Bố cục xóa đĩa đã khai báo rõ một phân vùng gốc ext4, thay cho kế hoạch mặc định từng chỉ tạo bảng phân vùng trống.
- [Kiểm thử 42491888587](https://github.com/fx-kitsune/mykos/actions/runs/42491888587) đạt BIOS, desktop software và Calamares nạp xong module/kiểm tra điều kiện. Công cụ hiện yêu cầu các dấu hiệu sẵn sàng này, không chỉ tiến trình đang chạy.
- [Kiểm thử cài đặt 42492925690](https://github.com/fx-kitsune/mykos/actions/runs/42492925690) đã thực hiện xác nhận Install trên QCOW2 mới 40 GiB. Calamares hoàn tất, tạo kernel/initrd và GRUB BIOS; kiểm tra đích chỉ đọc xác nhận root ext4, tài khoản `vmtester` có mật khẩu/nhóm sudo, root khóa, Casper/Calamares và sudoers live đã gỡ. Ảnh `live-wallpaper.png` đã được rà soát, hiển thị logo MyKOS giữa nền tối.
- Toàn bộ lượt cài đặt vẫn mang kết quả **failed**: QEMU thứ hai không mở được KVM (`Permission denied`), nên chưa boot bản cài. Đã thêm fallback KVM → TCG và kiểm tra bằng QEMU cục bộ; lượt tiếp theo phải xác nhận boot không ISO và đăng nhập thật trước khi nâng trạng thái nghiệm thu.

## Boot bản cài không ISO đã đạt

[Kiểm thử 42521038587](https://github.com/fx-kitsune/mykos/actions/runs/42521038587) trên cùng ISO SHA-256 `caadce0d0a2ba2734057045f2b81f5dbc709cabc25d054f32e1874509cb5492c` đã đạt `installed-userspace-ready`. Sau khi cài, công cụ tháo ISO, mở QEMU mới, boot GRUB từ QCOW2 và đăng nhập console bằng đúng mật khẩu đã nhập ở Calamares. Guest xác nhận UID 1000, hostname `mykos-installed`, `/` là ext4 trên `/dev/vda1`; dòng lệnh nhân không có `boot=casper`. Lần boot này dùng TCG sau khi KVM của runner mất quyền truy cập. Tổng thời gian công cụ ghi nhận khoảng 427,5 giây.

Phép thử chỉ bật serial-getty trong bản cài dùng riêng để quan sát đăng nhập, không sửa GRUB hoặc tham số nhân. Ảnh đăng nhập đồ họa lúc này còn đen với con trỏ, nên **chưa nghiệm thu SDDM/Plasma của bản cài**. Lượt tiếp theo thu trạng thái/journal SDDM, kiểm tra DHCP/DNS/HTTPS, yêu cầu mật khẩu sudo và vòng làm mới APT có xác thực → cài/chạy/gỡ `hello`.

## Mạng và APT của bản cài đã đạt

[42522062087](https://github.com/fx-kitsune/mykos/actions/runs/42522062087) đã đạt `installed-cli-smoke-ready` trên cùng ISO. NetworkManager có lease DHCP và tuyến mặc định, DNS phân giải được kho Ubuntu, HTTPS trả 200 với đầu tệp InRelease đúng định dạng. `sudo -n true` bị từ chối vì cần mật khẩu; xác thực bằng mật khẩu tài khoản đã nhập trong Calamares thành công. APT làm mới chỉ mục theo xác thực mặc định, cài/chạy/gỡ `hello` đều trả mã 0, gói thử không còn được cài sau phép thử.

SDDM và greeter hoạt động; ảnh sau các kiểm tra CLI đã hiện màn hình đăng nhập với phiên Plasma (X11). Ảnh đen trước đó được chụp quá sớm trong lần boot TCG. Chưa xem việc greeter hiển thị là bằng chứng đăng nhập Plasma; phép thử tiếp theo nhập tài khoản/mật khẩu qua SDDM và kiểm tra session cùng ứng dụng.

## Đăng nhập Plasma và sửa deadline dịch vụ

- [42523552134](https://github.com/fx-kitsune/mykos/actions/runs/42523552134) đã đạt `installed-desktop-ready`: nhập tài khoản/mật khẩu qua SDDM, logind xác nhận phiên X11 `active`, `Class=user`, `Remote=no` trên seat0. Plasma phản hồi, Dolphin/Konsole/Thiết lập hoạt động và bộ màu là MyKOSDark. Đã rà soát ảnh ứng dụng và hình nền logo trong bản cài.
- Journal vẫn ghi PolicyKit agent/Powerdevil lặp khởi động và KScreen không trả lời. [Chẩn đoán 42525892264](https://github.com/fx-kitsune/mykos/actions/runs/42525892264) xác nhận D-Bus của phiên live có tăng tốc là thống nhất, ba unit hoạt động với deadline mặc định 5 giây.
- [So sánh TCG 42526372487](https://github.com/fx-kitsune/mykos/actions/runs/42526372487) tái hiện hai unit restart 17 lần và KScreen `failed`. Thử override người dùng `TimeoutStartSec=60s` rồi khởi động lại unit: cả ba chuyển sang `active/running`, D-Bus đăng ký đúng tên và `NRestarts=0`.
- Commit `187042d` đưa deadline 60 giây vào drop-in toàn hệ thống cho đúng ba user unit. [Build 42527363919](https://github.com/fx-kitsune/mykos/actions/runs/42527363919) đang tạo ISO chứa sửa đổi. Phép thử bản cài tiếp theo yêu cầu unit vẫn là `Type=dbus`, đúng BusName, hoạt động và không restart, kể cả sau đổi độ phân giải/mở Discover. Chưa nghiệm thu sửa đổi trong ISO trước kết quả khởi động lạnh.

## Bằng chứng live UEFI ngày 09/11/2026

Nguồn `48d2b75`, ISO SHA-256 `136f409837a959f725a0e478fb451a0c8a2a221f83100f183853ef3fda9cb3ba`. [42641747422](https://github.com/fx-kitsune/mykos/actions/runs/42641747422) hoàn tất build, checksum, cấu trúc boot, kiểm thử trực tiếp và tải release nháp. USB/KVM đạt `desktop-ready` sau 111,5 giây; CD-ROM/KVM sau 115 giây, guest đều xác nhận `/sys/firmware/efi`, UID 1000, Plasma/KWin, một desktop/một panel, ba ứng dụng và MyKOSDark. BIOS/TCG đạt `userspace-ready` sau 221,3 giây. Đã xem ảnh ứng dụng UEFI cuối; ảnh chụp sớm vẫn ở splash nên không dùng để nghiệm thu render desktop.

[Bản ghi có cấu trúc](../tests/integration/evidence/uefi-live-42641747422.json) giữ nguồn, mã ISO, tài nguyên, trạng thái và mã ảnh đã xem. Hạn mức Actions Artifacts vẫn chưa được giải quyết; đường tải lần này là release nháp với hai phần archive dưới 2 GiB mỗi tệp. Không tự công bố bản ổn định. Các phép thử mạng/âm thanh/cài đặt trong UEFI và giao diện mặc định OpenGL chưa được thực hiện ở lượt này.
