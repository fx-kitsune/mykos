# Trình cài đặt MyKOS với Calamares

Calamares cho Ubuntu Noble và BIOS đã hoàn tất cài xuống QCOW2 mới trong [42492925690](https://github.com/fx-kitsune/mykos/actions/runs/42492925690); kernel/initrd/GRUB và tài khoản đích đã đạt kiểm tra. **Boot và lần đăng nhập đầu của bản cài chưa nghiệm thu** do QEMU lần hai mất quyền KVM trên runner; đang thử lại với fallback TCG. Không xem cấu hình, kiểm thử đơn vị hay việc mở cửa sổ trình cài đặt là bằng chứng cài đặt thành công.

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

1. Build ISO chứa các tệp này và kiểm tra mở Calamares trong Plasma; đọc log nạp module và ảnh thật.
2. Gắn riêng đĩa QCOW2 mới, cài bằng giao diện, ghi kết quả và lỗi nếu có.
3. Tháo ISO, boot GRUB từ đĩa đã cài và đăng nhập tài khoản thường.
4. Kiểm tra tài khoản live/installer đã được gỡ, sudo cần mật khẩu, mạng và cập nhật hoạt động.
5. Thử phục hồi; mở rộng UEFI/Secure Boot và ma trận phần cứng ở mốc riêng.

Ghi SHA-256 ISO, cấu hình máy ảo, bố cục đĩa và bằng chứng vào [danh sách nghiệm thu](../../tests/integration/VM_CHECKLIST.md). Không thử trên đĩa có dữ liệu quan trọng khi phạm vi này chưa được nghiệm thu.

## Kiểm thử tự động trên đĩa dùng riêng

Workflow `install-iso.yml` chạy sau một lượt kiểm thử desktop thành công hoặc được chọn thủ công; chỉ tiếp tục từ kết quả `desktop-ready` có Calamares đang mở. ISO tải xuống phải khớp SHA-256 của kết quả đó trước khi tạo đĩa. Công cụ `scripts/testing/install_iso.py` tạo đúng một QCOW2 mới 40 GiB và kiểm tra guest chỉ thấy đĩa `vda` trống này.

Giai đoạn preview chụp trang chào và các trang kế tiếp bằng phím điều hướng; **không chọn xóa đĩa, không bấm Install**. Kết quả `installer-preview` chỉ cung cấp ảnh để rà soát; không phải bằng chứng cài đặt. Artifact chỉ lưu log/JSON/ảnh, không lưu đĩa ảo. Sau khi rà soát preview mới tiếp tục kiểm thử cài đặt và boot từ đĩa.

Tùy chọn `--prepare-install` đi tiếp từ ảnh phân vùng đã rà soát: chọn xóa trên đúng đĩa ảo mới, nhập tài khoản `vmtester` với mật khẩu ngẫu nhiên dùng một lần, chụp trang tổng kết rồi dừng trước Install. Công cụ kiểm tra lại đĩa vẫn chưa có phân vùng. Mật khẩu không được giữ lại trong báo cáo. Chế độ này vẫn chỉ là chuẩn bị, chưa cài đặt.

Workflow chính thêm `--install --boot-installed`. Trước xác nhận Install, log kế hoạch phải có công việc tạo phân vùng và root ext4; nếu thiếu thì dừng. Sau khi Calamares báo thành công, công cụ gắn đích chỉ đọc để kiểm tra kernel/initrd/GRUB, tài khoản thường, nhóm sudo, mật khẩu đã đặt, root khóa và chính sách live đã gỡ. Đây mới là định nghĩa kiểm tra; trạng thái nghiệm thu phải dựa trên kết quả chạy thực tế.

Để kiểm tra boot, phép thử chỉ bật `serial-getty@ttyS0.service` trong bản cài trên QCOW2, giữ nguyên GRUB và tham số nhân. Sau đó tắt máy live và tạo QEMU mới **không gắn ISO**, boot từ đĩa, đăng nhập console bằng đúng mật khẩu đã nhập trong GUI. `installed-userspace-ready` yêu cầu tài khoản không phải root, hostname đã đặt và `/` là ext4 trên `/dev/vda1`; trạng thái này chưa nghiệm thu đăng nhập đồ họa, mạng/âm thanh hoặc phần cứng. Mật khẩu chỉ tồn tại trong bộ nhớ tiến trình kiểm thử. Artifact chỉ lưu JSON/log/PNG, kể cả thư mục con của lần boot; không tải QCOW2 hoặc ISO lên.

Workflow chẩn đoán có thể dùng `--diagnostic-overlay` để chép cấu hình hiện tại vào phiên live; mỗi tệp được ghi mã SHA-256. Kết quả `installer-diagnostic-preview` không thay thế việc thử lại ISO chứa sẵn cấu hình và launcher chính thức.
