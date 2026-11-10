# Cài MyKOS từ terminal của USB cứu hộ khác

Trình cài thử nghiệm dùng `debootstrap` để tạo MyKOS trực tiếp lên phân vùng đích. Không cần boot ISO MyKOS, không cần Calamares hoặc môi trường live của MyKOS. Có thể chạy từ Debian/Ubuntu live hoặc Linux rescue khác đã cài đủ công cụ host.

**Chưa nghiệm thu cài đĩa và reboot bằng trình cài này.** Hiện đã kiểm thử kế hoạch, guard phân vùng, xác nhận UUID, triển khai tệp và dọn mount. Không coi các kiểm thử đó là bằng chứng một máy đã cài thành công.

## Phạm vi đầu tiên

Host/target amd64; root là một phân vùng ext4 rỗng trên một ổ thường; BIOS hoặc UEFI. UEFI cần ESP FAT32 rỗng trên cùng ổ và Secure Boot tắt; loader dùng đường fallback `EFI/BOOT`, không sửa firmware NVRAM. BIOS cần chọn rõ whole disk cho GRUB; GPT cần phân vùng `bios_grub` đúng chuẩn trước đó. Chưa hỗ trợ dual boot, giữ dữ liệu trên root cũ, LVM, RAID, LUKS, Btrfs, phân vùng tự động hoặc resume sau lỗi.

Trình cài không có lệnh format/chia ổ. Người dùng chuẩn bị phân vùng bằng công cụ cứu hộ rồi mount root tại `/mnt/mykos`; với UEFI mount ESP tại `/mnt/mykos/boot/efi`. Root chỉ được chứa `lost+found` và thư mục `boot/efi` cần cho ESP. Không chọn phân vùng đang có dữ liệu muốn giữ. Plan liệt kê cả thao tác ghi bootloader.

## Chuẩn bị và lấy mã

Ví dụ trên Debian/Ubuntu live:

```sh
sudo apt-get update
sudo apt-get install debootstrap debian-archive-keyring gpgv git python3 util-linux

git clone https://github.com/fx-kitsune/mykos.git
cd mykos
```

Trên rescue Linux khác, cài các công cụ tương ứng bằng package manager của host. `debootstrap` phải hỗ trợ Trixie và archive keyring phải chứa khóa phát hành Debian 13. Một số USB cứu hộ cũ cung cấp keyring quá cũ; khi đó dùng `--keyring /path/to/current/debian-archive-keyring.gpg` từ nguồn tin cậy, không tắt kiểm tra chữ ký. `debootstrap` và Debian archive keyring phải đến từ nguồn tin cậy; script không tự cài phần mềm lên host, không bỏ kiểm tra chữ ký và không dùng `curl | sudo sh`. Host cần quyền root, mạng, mount/chroot, đủ RAM và ít nhất khoảng 10 GiB trống trên phân vùng đích (khuyến nghị 25 GiB trở lên cho desktop/cập nhật). Kiểm tra dung lượng đích trước khi chạy; APT có thể cần thêm chỗ tùy phiên bản gói.

## Xem kế hoạch trước

Sau khi phân vùng đã mount đúng:

```sh
python3 scripts/install/mykos-install.py plan \
  --target /mnt/mykos --mode uefi \
  --username alice --hostname mykos

findmnt --mountpoint /mnt/mykos -o TARGET,SOURCE,FSTYPE,UUID
```

`plan` không ghi tệp hoặc chạy công cụ hệ thống. Nó hiển thị gói và bước dự kiến; kiểm tra mount/device thật diễn ra khi gọi `install`, trước bất kỳ ghi dữ liệu nào. Lấy UUID của root từ `findmnt`; không dùng UUID của USB cứu hộ hoặc ESP.

## Cài UEFI

Thay `UUID_ROOT_DA_KIEM_TRA` bằng UUID ext4 đích vừa kiểm tra:

```sh
sudo python3 scripts/install/mykos-install.py install \
  --target /mnt/mykos --mode uefi \
  --username alice --hostname mykos \
  --confirm-uuid UUID_ROOT_DA_KIEM_TRA
```

Trình cài kiểm tra root rỗng, ESP rỗng và cùng ổ, từ chối root filesystem đang chạy, rồi yêu cầu nhập hai lần mật khẩu tài khoản mới. Mật khẩu tối thiểu 12 ký tự, không nhận qua tham số CLI, không ghi vào metadata hoặc log. Tài khoản mới thuộc nhóm sudo và phải dùng mật khẩu; root bị khóa. Không có tài khoản/mật khẩu live trong bản cài.

## Cài BIOS

```sh
sudo python3 scripts/install/mykos-install.py install \
  --target /mnt/mykos --mode bios --boot-disk /dev/WHOLE_DISK \
  --username alice --hostname mykos \
  --confirm-uuid UUID_ROOT_DA_KIEM_TRA
```

`/dev/WHOLE_DISK` phải là ổ cha của phân vùng root đích, không phải tên phân vùng. Đây là thao tác ghi vùng boot của ổ đó; kiểm tra lại thông tin in ra trước khi xác nhận UUID. Script không chuẩn bị `bios_grub` hoặc thay bảng phân vùng.

## Sau khi chạy

Hệ thống được bootstrap từ kho Debian có chữ ký, cài Linux kernel Debian và MyKOS Desktop riêng. Shell/session lấy từ checkout Git này; chưa có kho APT MyKOS được ký riêng. `fstab` dùng UUID, DNS giao cho NetworkManager, máy có machine-id mới khi boot. Policy chặn khởi động dịch vụ được dùng trong giai đoạn cài rồi gỡ sau thành công.

Các mount `/dev`, `/sys`, `/proc`, `/run` do trình cài tạo được dọn ở cuối; root và ESP do người dùng mount vẫn giữ nguyên để kiểm tra. Thông tin cài nằm trong `/etc/mykos-install.json` của đích. Sau kiểm tra, người dùng tự unmount ESP/root, tháo USB cứu hộ và reboot. Không tự reboot máy từ script.

Nếu lỗi giữa chừng, root có thể đã được ghi một phần. Script giữ `.mykos-install.lock` và từ chối xem đây là root rỗng để tránh ghi đè khi chạy lại. Đọc lỗi và kiểm tra mount trước khi sửa; không xóa root hoặc khóa rồi chạy lại một cách mù quáng. Việc mất điện/kill cưỡng bức có thể để lại mount cần dọn thủ công.
