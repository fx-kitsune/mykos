# Trình cài đặt MyKOS với Calamares

Calamares cho Ubuntu Noble và BIOS đã hoàn tất cài vào QCOW2 mới, boot GRUB không ISO, đăng nhập tài khoản thường qua SDDM/Plasma X11. [42529928289](https://github.com/fx-kitsune/mykos/actions/runs/42529928289) trên ISO build `42527363919` đạt mạng/HTTPS, sudo, APT, tệp, đổi độ phân giải và âm thanh PipeWire/HDA ảo; ba dịch vụ Plasma dùng deadline mới hoạt động ổn định. [42531078658](https://github.com/fx-kitsune/mykos/actions/runs/42531078658) xác nhận Discover mở/danh mục không còn lỗi xác thực sau khi công cụ thử mở ứng dụng qua user service manager. Chưa nghiệm thu cập nhật/recovery hoặc phần cứng thật.

## Phạm vi hiện tại

- Chuỗi chọn ngôn ngữ, bàn phím, phân vùng, tài khoản, xác nhận; sau đó gắn đích, giải nén `/cdrom/casper/filesystem.squashfs`, tạo tài khoản, thiết lập SDDM/mạng, loại bỏ gói live, tạo initramfs và cài GRUB BIOS.
- Nút **Cài đặt MyKOS** trong menu mở `/usr/bin/mykos-install`. Lệnh chỉ chấp nhận phiên `boot=casper`, cần squashfs của ISO và từ chối UEFI. Sudo của phiên live cấp quyền mở Calamares; không thêm chính sách sudo không mật khẩu cho bản cài.
- Tài khoản thường thuộc nhóm sudo của Ubuntu; root bị khóa, không bật đăng nhập tự động mặc định. Người dùng đặt mật khẩu trong trình cài đặt.
- Không tự làm mới APT hoặc nâng cấp hệ thống khi cài. Các gói và GRUB cần thiết đã có trong ISO.
- Calamares chỉ thao tác sau trang tổng kết và xác nhận. Không tự chọn phương án xóa đĩa. Mục tiêu nghiệm thu đầu tiên là **đĩa ảo trống, dùng riêng, 40 GiB**; chưa công bố dual boot hoặc bảo toàn phân vùng có dữ liệu.

Các tệp `.conf` dùng JSON, là cú pháp hợp lệ của YAML mà Calamares đọc; nhờ vậy kiểm thử cấu hình chỉ cần thư viện chuẩn Python. Cấu hình module đã được đối chiếu các schema có sẵn của gói Calamares 3.3.5 trong kho Noble.

## Ranh giới môi trường live / bản cài

Module `mykos-config` chỉ làm việc trong `rootMountPoint` được Calamares gắn, từ chối `/` và đường dẫn đi qua symlink ra ngoài đích. Nó bỏ launcher/cấu hình installer và sudoers dành riêng cho Casper; không xóa thư mục người dùng. Bước packages gỡ `casper` và `calamares` trước khi tạo lại initramfs.

Nếu người dùng chọn đồ họa phần mềm trong phiên live, module ghi lại đúng hai tham số KWin/Qt Quick đó cho GRUB của bản cài. Phiên không chọn chế độ này giữ mặc định đồ họa bình thường.

## Các bước còn phải kiểm chứng

1. Mở rộng từ kiểm tra mở/danh mục Discover sang giao dịch cài/gỡ và cấp quyền đồ họa PackageKit.
2. Cập nhật đầy đủ, boot lại và kiểm tra phiên làm việc.
3. Thực hành hướng dẫn phục hồi và mở rộng ma trận phần cứng.
4. UEFI/Secure Boot và cài song song là các phạm vi riêng chưa được hỗ trợ.

Ghi SHA-256 ISO, cấu hình máy ảo, bố cục đĩa và bằng chứng vào [danh sách nghiệm thu](../../tests/integration/VM_CHECKLIST.md). Không thử trên đĩa có dữ liệu quan trọng khi phạm vi này chưa được nghiệm thu.

## Kiểm thử tự động trên đĩa dùng riêng

Workflow `install-iso.yml` chạy sau một lượt kiểm thử desktop thành công hoặc được chọn thủ công; chỉ tiếp tục từ kết quả `desktop-ready` có Calamares đang mở. ISO tải xuống phải khớp SHA-256 của kết quả đó trước khi tạo đĩa. Công cụ `scripts/testing/install_iso.py` tạo đúng một QCOW2 mới 40 GiB và kiểm tra guest chỉ thấy đĩa `vda` trống này.

Giai đoạn preview chụp trang chào và các trang kế tiếp bằng phím điều hướng; **không chọn xóa đĩa, không bấm Install**. Kết quả `installer-preview` chỉ cung cấp ảnh để rà soát; không phải bằng chứng cài đặt. Artifact chỉ lưu log/JSON/ảnh, không lưu đĩa ảo. Sau khi rà soát preview mới tiếp tục kiểm thử cài đặt và boot từ đĩa.

Tùy chọn `--prepare-install` đi tiếp từ ảnh phân vùng đã rà soát: chọn xóa trên đúng đĩa ảo mới, nhập tài khoản `vmtester` với mật khẩu ngẫu nhiên dùng một lần, chụp trang tổng kết rồi dừng trước Install. Công cụ kiểm tra lại đĩa vẫn chưa có phân vùng. Mật khẩu không được giữ lại trong báo cáo. Chế độ này vẫn chỉ là chuẩn bị, chưa cài đặt.

Workflow chính thêm `--install --boot-installed`. Trước xác nhận Install, log kế hoạch phải có công việc tạo phân vùng và root ext4; nếu thiếu thì dừng. Sau khi Calamares báo thành công, công cụ gắn đích chỉ đọc để kiểm tra kernel/initrd/GRUB, tài khoản thường, nhóm sudo, mật khẩu đã đặt, root khóa và chính sách live đã gỡ. Đây mới là định nghĩa kiểm tra; trạng thái nghiệm thu phải dựa trên kết quả chạy thực tế.

Để kiểm tra boot, phép thử chỉ bật `serial-getty@ttyS0.service` trong bản cài trên QCOW2, giữ nguyên GRUB và tham số nhân. Sau đó tắt máy live và tạo QEMU mới **không gắn ISO**, boot từ đĩa, đăng nhập console bằng đúng mật khẩu đã nhập trong GUI. `installed-userspace-ready` yêu cầu tài khoản không phải root, hostname đã đặt và `/` là ext4 trên `/dev/vda1`; trạng thái này chưa nghiệm thu đăng nhập đồ họa, mạng/âm thanh hoặc phần cứng. Mật khẩu chỉ tồn tại trong bộ nhớ tiến trình kiểm thử. Artifact chỉ lưu JSON/log/PNG, kể cả thư mục con của lần boot; không tải QCOW2 hoặc ISO lên.

`--smoke-installed` bổ sung kiểm tra NetworkManager/DHCP, tuyến mặc định, DNS và HTTPS bằng kho Ubuntu. Trước xác thực, `sudo -n true` phải bị từ chối vì cần mật khẩu; sau đó công cụ nhập mật khẩu qua prompt sudo riêng khi echo đã tắt. APT làm mới chỉ mục với chế độ lỗi nghiêm ngặt, cài/chạy/gỡ `hello`, giữ nguyên xác thực kho mặc định. Nếu `hello` đã có sẵn, phép thử từ chối gỡ gói đó. Kết quả `installed-cli-smoke-ready` chỉ xác nhận các bước dòng lệnh; trạng thái/journal SDDM và ảnh được lưu riêng để tiếp tục rà soát giao diện. Không dùng kết quả này để nghiệm thu âm thanh hoặc phần cứng.

`--desktop-installed` dùng màn hình SDDM đã rà soát, xác thực một lần bằng bàn phím, kiểm tra logind/Plasma/ứng dụng và màu mặc định. Ba user unit PolicyKit agent, Powerdevil và KScreen phải đăng ký đúng BusName, `active/running`, không restart và có deadline khởi động 60 giây. `--multimedia-installed` tiếp tục ghi/đọc tệp bằng UID thường, đổi rồi phục hồi độ phân giải X11, mở Discover, kiểm tra Flatpak và phát sóng 440 Hz qua PipeWire tới HDA ảo. Bản ghi WAV của QEMU phải thật sự chứa tín hiệu; im lặng hoặc âm khác không đạt. Artifact chỉ giữ một đoạn PCM ngắn đã ghi nhận cùng chỉ số/mã băm, không giữ WAV dài hoặc QCOW2. Các kiểm tra này không nghiệm thu Wayland, phần cứng âm thanh thật hoặc phục hồi.

Workflow chẩn đoán có thể dùng `--diagnostic-overlay` để chép cấu hình hiện tại vào phiên live; mỗi tệp được ghi mã SHA-256. Kết quả `installer-diagnostic-preview` không thay thế việc thử lại ISO chứa sẵn cấu hình và launcher chính thức.
