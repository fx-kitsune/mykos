# Cài MyKOS bằng một script từ USB cứu hộ

Boot USB Linux cứu hộ có Internet. Lấy repo rồi chạy:

```sh
git clone https://github.com/fx-kitsune/mykos.git
cd mykos
./install
```

Script tự xin quyền sudo khi cần. Bạn không phải chia phân vùng, format, mount hoặc nhập UUID.

## Bạn sẽ thấy gì

1. Danh sách ổ trong, ưu tiên NVMe, hiển thị model và dung lượng. Chọn bằng số; nếu chỉ có một ổ hợp lệ có thể nhấn Enter.
2. Nhập tên tài khoản (mặc định `mykos`; tên máy tự đặt `mykos`).
3. Xem lại đúng ổ đích, serial, các phân vùng đang có và thông báo **toàn bộ dữ liệu trên ổ này sẽ bị xóa**. Gõ `XOA VA CAI MYKOS` để xác nhận; Enter để hủy.
4. Đặt mật khẩu tài khoản mới hai lần, tối thiểu 12 ký tự.
5. Chờ script cài đặt, sau đó tắt máy/reboot và tháo USB cứu hộ.

Chỉ bước xác nhận xóa ổ được giữ lại để tránh mất dữ liệu nhầm ổ; các bước kỹ thuật được tự động hóa.

## Script tự làm những việc gì

- Chuẩn bị công cụ còn thiếu trên rescue Debian/Ubuntu (APT), Fedora (DNF) hoặc Arch (pacman); không yêu cầu người dùng cài debootstrap riêng. Host khác dùng được khi đã có đủ các công cụ cần thiết.
- Tải debootstrap và archive keyring Debian 13 với phiên bản/SHA-256 ghim trong repo; giải nén riêng, không thay kho gói của host. Xác thực InRelease trước khi ghi ổ.
- Tự nhận biết phiên cứu hộ đang boot UEFI hay BIOS; có thể ghi đè bằng `--mode` khi có nhu cầu nâng cao.
- Tạo GPT: UEFI có ESP FAT32 512 MiB; BIOS có phân vùng BIOS boot 2 MiB. Phần dung lượng còn lại là root ext4.
- Format và mount các phân vùng mới, bootstrap Debian, cài Linux kernel và MyKOS Desktop, cấu hình fstab, mạng, tài khoản và GRUB.
- Dùng UUID nội bộ để tạo fstab và kiểm tra đích. Không bắt người dùng tìm/copy UUID.
- Tháo các mount do trình cài tạo. Không tự reboot, để người dùng đọc kết quả trước.

Mật khẩu không nhận qua argv và không ghi vào log/metadata. Root bị khóa; tài khoản mới thuộc nhóm sudo và phải dùng mật khẩu. Không cài tài khoản live, gói live-boot hoặc Calamares vào hệ thống đích.

## Bảo vệ chọn nhầm ổ

Ổ đang chứa hệ thống/USB cứu hộ, mã nguồn trình cài hoặc dữ liệu đang được chính trình cài sử dụng không được đưa vào danh sách có thể xóa. Có kiểm tra ảnh ISO cứu hộ được loop-mount từ một phân vùng, ổ chỉ đọc/USB, device mapper đang hoạt động và nhận diện ổ thay đổi sau xác nhận.

Các phân vùng của ổ đích được tự unmount sau xác nhận; nếu đang bận, trình cài dừng trước khi ghi bảng phân vùng. Không dùng force/lazy unmount, không tự kill tiến trình. Khi unmount thất bại sau cài, giữ nguyên dữ liệu và mountpoint để chẩn đoán, không xóa đệ quy thư mục đang mount.

## Xem trước mà không ghi

```sh
./install plan
./install plan --disk /dev/nvme0n1 --mode uefi
```

`plan` chỉ đọc thiết bị và in kế hoạch. Ví dụ tên thiết bị không thay thế bước chọn ổ thật. `./install install --disk /dev/nvme0n1` có thể chọn trước ổ nhưng vẫn yêu cầu xem và xác nhận xóa trong terminal.

## Giới hạn

Hiện là cài mới dùng **toàn bộ ổ**, không dual boot hoặc giữ dữ liệu cũ. Cần host/target amd64, ổ trong ít nhất 25 GiB và Internet; NVMe có nhận diện ổ ổn định được hỗ trợ. Ổ USB rời và các volume LVM/RAID/LUKS đang hoạt động bị loại trừ. Secure Boot chưa hỗ trợ; nếu phát hiện đang bật thì dừng trước khi xóa ổ.

Đã kiểm thử guard thiết bị, hủy trước khi ghi, thay ổ, lỗi unmount, hash bootstrap, và tạo GPT thật trên tệp thưa với sector 512/4096 byte. [Lượt 42851532511](https://github.com/fx-kitsune/mykos/actions/runs/42851532511) đã tự cài lên NVMe ảo UEFI 40 GiB và reboot không ISO thành công trong 244,3 giây. Tài khoản mới đăng nhập console được, root là ext4 trên NVMe, SDDM và NetworkManager hoạt động. Bằng chứng: `tests/integration/evidence/auto-nvme-install-42851532511.json`. Chưa nghiệm thu đăng nhập đồ họa bản cài, cài BIOS đầy đủ hoặc phần cứng NVMe thật.

Sau khi đã xác nhận xóa và bắt đầu chia ổ, lỗi mạng/phần cứng hoặc mất điện có thể để lại hệ thống chưa hoàn chỉnh; không có khả năng khôi phục dữ liệu cũ tự động. Script báo lỗi thay vì thông báo cài thành công.

Chế độ nâng cao `install --target ... --confirm-uuid ...` vẫn giữ cho phát triển trên phân vùng chuẩn bị sẵn; nó không thuộc luồng wizard mặc định.
