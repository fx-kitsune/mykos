# Danh sách nghiệm thu M0 trên máy ảo

Mỗi mục bắt đầu ở trạng thái **CHƯA CHẠY** hoặc tình trạng bị chặn tương ứng. Khi ghi kết quả, đính kèm SHA-256 của ISO, `build.json`, ngày thử, người thử, phiên bản/lệnh QEMU và nhật ký hoặc ảnh chụp màn hình.

```sh
# Chạy trên máy có màn hình đồ họa và đã cài qemu-system-x86.
scripts/development/run-vm.sh artifacts/m0-001/mykos-0.1.0-dev-amd64.iso
# Chỉ thêm đĩa thử riêng sau khi đã tích hợp trình cài đặt.
qemu-img create -f qcow2 /tmp/mykos-install.qcow2 40G
scripts/development/run-vm.sh artifacts/m0-001/mykos-0.1.0-dev-amd64.iso /tmp/mykos-install.qcow2
```

Công cụ dùng KVM khi truy cập được, ngược lại dùng TCG. Lệnh này không tự xác nhận khởi động thành công. Mặc định không gắn ổ đĩa; đĩa thử được truyền rõ ràng có thể bị ghi. Phiên chạy trực tiếp có thể cho quản trị không mật khẩu; không giữ chính sách đó cho tài khoản trên bản cài.

| Kiểm thử | Kết quả mong đợi | Trạng thái |
|---|---|---|
| Khởi động trực tiếp bằng BIOS | Qua BIOS và nhân tới môi trường người dùng, trên bản sao thêm console | ĐẠT: [42528988768](https://github.com/fx-kitsune/mykos/actions/runs/42528988768), ISO build 42527363919 |
| Đăng nhập và phiên KDE | SDDM/Plasma và ứng dụng hoạt động, dịch vụ phiên ổn định | ĐẠT software/X11: [42529928289](https://github.com/fx-kitsune/mykos/actions/runs/42529928289); PolicyKit/Powerdevil/KScreen active, không restart. OpenGL mặc định chưa nghiệm thu |
| Hình nền mặc định | Logo MyKOS giữa nền tối trong desktop thật | ĐẠT trên bản cài build 42527363919: đã rà soát ảnh `installed-wallpaper.png` của [42529928289](https://github.com/fx-kitsune/mykos/actions/runs/42529928289) |
| Mạng | DHCP, DNS và HTTPS qua NetworkManager | ĐẠT virtio-net/QEMU: [42529928289](https://github.com/fx-kitsune/mykos/actions/runs/42529928289); chưa kiểm tra Wi-Fi/phần cứng thật |
| Âm thanh | Phát âm thanh và điều chỉnh âm lượng bằng PipeWire | ĐẠT HDA ảo: [42529928289](https://github.com/fx-kitsune/mykos/actions/runs/42529928289); PCM chứa 440 Hz, có clip bằng chứng; không bao gồm micro/thiết bị thật |
| Màn hình | Đổi và khôi phục độ phân giải | ĐẠT VGA chuẩn/X11: [42529928289](https://github.com/fx-kitsune/mykos/actions/runs/42529928289), 1280×800 → 1024×768 → 1280×800; Wayland chưa chạy |
| Tệp và trình dòng lệnh | Mở Dolphin/Konsole; tệp giữ được trong phiên đang chạy | ĐẠT: [42529928289](https://github.com/fx-kitsune/mykos/actions/runs/42529928289); Documents đúng nội dung/chủ sở hữu; chưa thử giữ tệp qua reboot |
| Gói phần mềm | APT có xác thực; mở Discover và Flatpak | ĐẠT cơ bản: [42531078658](https://github.com/fx-kitsune/mykos/actions/runs/42531078658), APT update/cài/chạy/gỡ hello, Flatpak CLI và mở/danh mục Discover không lỗi xác thực; chưa thử giao dịch GUI hoặc thêm remote Flatpak |
| Cài vào đĩa ảo trống | Hoàn tất, khởi động lại không cần ISO | ĐẠT BIOS/QCOW2 40 GiB: [42529928289](https://github.com/fx-kitsune/mykos/actions/runs/42529928289), boot GRUB từ đĩa, root ext4/vda1; kiểm tra đã gỡ Casper/Calamares |
| Đăng nhập bản cài | Tài khoản thường; quản trị có cấp quyền rõ ràng | ĐẠT console/SDDM/sudo: [42529928289](https://github.com/fx-kitsune/mykos/actions/runs/42529928289), UID 1000, xác thực mật khẩu. Cấp quyền giao dịch cài/gỡ PackageKit GUI còn kiểm tra riêng |
| Cập nhật và khởi động lại | APT cập nhật, khởi động lại và phiên làm việc bình thường | BỊ CHẶN |
| Phục hồi | Thực hiện hướng dẫn cứu hộ sau cập nhật lỗi | BỊ CHẶN |
| UEFI / Secure Boot | Kiểm chứng riêng theo phần sụn ảo | CHƯA HỖ TRỢ |

Không thử gián đoạn cập nhật trên dữ liệu quan trọng. Chưa cấu hình ảnh chụp trạng thái hoặc hoàn tác; sao lưu là yêu cầu riêng, không phụ thuộc cơ chế hoàn tác tương lai.

## Bằng chứng tự động từ Actions

Workflow `.github/workflows/boot-iso.yml` sử dụng lại ISO đã build và kiểm tra mã SHA-256. Công cụ `scripts/testing/boot_iso.py` khởi động BIOS từ bản sao có bổ sung console nối tiếp, xuất nhật ký và ảnh màn hình. Kết quả `userspace-ready` chỉ xác nhận đã quan sát dấu hiệu môi trường người dùng hoạt động; các dòng đăng nhập Plasma, thiết bị và cài đặt trong bảng vẫn cần kiểm tra độc lập.

Mỗi kết quả ghi SHA-256 của ISO nguồn và bản sao chẩn đoán. Không xem ảnh chụp màn hình đơn lẻ hoặc thông báo nhân Linux là bằng chứng toàn bộ M0 đã đạt. Nếu kiểm thử hết thời gian chờ, xem `serial.log`, `qemu.log` và `screen.png` trước khi chạy lại.

## ISO của lượt kiểm thử mới nhất

Build `42527363919`, SHA-256 `0de50cbd7cc982d083183786f9d33b83b0b1f9aacb8f39522e8da733d63a5751`. Lượt cài `42529928289` dùng KVM, RAM 4 GiB, hai CPU, software rendering; hoàn tất khoảng 413,8 giây. [Bằng chứng](https://github.com/fx-kitsune/mykos/actions/runs/42529928289/artifacts/13637261439) gồm JSON, log, ảnh và clip âm thanh, lưu 7 ngày. Không có đĩa ảo hoặc dữ liệu thử tải lên.

Kiểm tra lại [42531078658](https://github.com/fx-kitsune/mykos/actions/runs/42531078658) trên cùng ISO đạt sau 411,9 giây. [Bằng chứng mới nhất](https://github.com/fx-kitsune/mykos/actions/runs/42531078658/artifacts/13638110433): Discover trong user service manager không còn lỗi xác thực; đã rà soát ảnh danh mục không có hộp thoại lỗi, PCM tiếp tục đạt 440 Hz và ba dịch vụ phiên không restart.
