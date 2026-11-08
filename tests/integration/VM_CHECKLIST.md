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
| Khởi động trực tiếp bằng BIOS | Qua BIOS và nhân tới môi trường người dùng, trên bản sao thêm console | ĐẠT: [QEMU/TCG 42435820231](https://github.com/fx-kitsune/mykos/actions/runs/42435820231), 08/11/2026 |
| Đăng nhập và phiên KDE | Plasma, trình mở ứng dụng và điều hướng bàn phím hoạt động | MỘT PHẦN: [42481797224](https://github.com/fx-kitsune/mykos/actions/runs/42481797224) đạt desktop phản hồi và mở ứng dụng với profile software; mặc định OpenGL và cảnh báo Powerdevil/polkit chưa nghiệm thu |
| Hình nền mặc định | Logo MyKOS giữa nền tối trong desktop thật | ĐẠT trên ISO build 42490508466: đã rà soát `live-wallpaper.png` của [42492925690](https://github.com/fx-kitsune/mykos/actions/runs/42492925690) |
| Mạng | DHCP, DNS và HTTPS qua NetworkManager | ĐẠT trên virtio-net/QEMU: [42522062087](https://github.com/fx-kitsune/mykos/actions/runs/42522062087); chưa kiểm tra Wi-Fi/phần cứng thật |
| Âm thanh | Phát âm thanh và điều chỉnh âm lượng bằng PipeWire | CHƯA CHẠY |
| Màn hình | Đổi độ phân giải; kiểm tra phiên Wayland riêng | CHƯA CHẠY |
| Tệp và trình dòng lệnh | Mở Dolphin/Konsole; tệp giữ được trong phiên đang chạy | CHƯA CHẠY |
| Gói phần mềm | Làm mới APT có xác thực; mở Discover và Flatpak | MỘT PHẦN: [42522062087](https://github.com/fx-kitsune/mykos/actions/runs/42522062087) đạt APT update/cài/chạy/gỡ hello; Discover/Flatpak còn chờ |
| Cài vào đĩa ảo trống | Hoàn tất, khởi động lại không cần ISO | ĐẠT BIOS/QCOW2: [42521038587](https://github.com/fx-kitsune/mykos/actions/runs/42521038587) cài xong, tháo ISO, boot GRUB từ đĩa; console xác nhận root ext4 trên vda1 |
| Đăng nhập bản cài | Tài khoản thường; quản trị có cấp quyền rõ ràng | MỘT PHẦN: console UID 1000 đạt; [42522062087](https://github.com/fx-kitsune/mykos/actions/runs/42522062087) xác nhận sudo yêu cầu và chấp nhận đúng mật khẩu; đăng nhập GUI còn chờ |
| Cập nhật và khởi động lại | APT cập nhật, khởi động lại và phiên làm việc bình thường | BỊ CHẶN |
| Phục hồi | Thực hiện hướng dẫn cứu hộ sau cập nhật lỗi | BỊ CHẶN |
| UEFI / Secure Boot | Kiểm chứng riêng theo phần sụn ảo | CHƯA HỖ TRỢ |

Không thử gián đoạn cập nhật trên dữ liệu quan trọng. Chưa cấu hình ảnh chụp trạng thái hoặc hoàn tác; sao lưu là yêu cầu riêng, không phụ thuộc cơ chế hoàn tác tương lai.

## Bằng chứng tự động từ Actions

Workflow `.github/workflows/boot-iso.yml` sử dụng lại ISO đã build và kiểm tra mã SHA-256. Công cụ `scripts/testing/boot_iso.py` khởi động BIOS từ bản sao có bổ sung console nối tiếp, xuất nhật ký và ảnh màn hình. Kết quả `userspace-ready` chỉ xác nhận đã quan sát dấu hiệu môi trường người dùng hoạt động; các dòng đăng nhập Plasma, thiết bị và cài đặt trong bảng vẫn cần kiểm tra độc lập.

Mỗi kết quả ghi SHA-256 của ISO nguồn và bản sao chẩn đoán. Không xem ảnh chụp màn hình đơn lẻ hoặc thông báo nhân Linux là bằng chứng toàn bộ M0 đã đạt. Nếu kiểm thử hết thời gian chờ, xem `serial.log`, `qemu.log` và `screen.png` trước khi chạy lại.
