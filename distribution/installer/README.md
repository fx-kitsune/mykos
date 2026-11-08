# Trình cài đặt MyKOS với Calamares

Đã chuẩn bị cấu hình Calamares cho Ubuntu Noble và BIOS truyền thống. **Chưa nghiệm thu cài xuống đĩa hoặc lần đăng nhập đầu của bản cài.** Không xem cấu hình, kiểm thử đơn vị hay việc mở cửa sổ trình cài đặt là bằng chứng cài đặt thành công.

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
