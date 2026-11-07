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
| Khởi động trực tiếp bằng BIOS | Có menu khởi động, nhân và phiên đồ họa | CHƯA CHẠY |
| Đăng nhập và phiên KDE | Plasma, trình mở ứng dụng và điều hướng bàn phím hoạt động | CHƯA CHẠY |
| Mạng | DHCP, DNS và HTTPS qua NetworkManager | CHƯA CHẠY |
| Âm thanh | Phát âm thanh và điều chỉnh âm lượng bằng PipeWire | CHƯA CHẠY |
| Màn hình | Đổi độ phân giải; kiểm tra phiên Wayland riêng | CHƯA CHẠY |
| Tệp và trình dòng lệnh | Mở Dolphin/Konsole; tệp giữ được trong phiên đang chạy | CHƯA CHẠY |
| Gói phần mềm | Làm mới APT có xác thực; mở Discover và Flatpak | CHƯA CHẠY |
| Cài vào đĩa ảo trống | Hoàn tất, khởi động lại không cần ISO | BỊ CHẶN: chưa tích hợp trình cài đặt |
| Đăng nhập bản cài | Tài khoản thường; quản trị có cấp quyền rõ ràng | BỊ CHẶN |
| Cập nhật và khởi động lại | APT cập nhật, khởi động lại và phiên làm việc bình thường | BỊ CHẶN |
| Phục hồi | Thực hiện hướng dẫn cứu hộ sau cập nhật lỗi | BỊ CHẶN |
| UEFI / Secure Boot | Kiểm chứng riêng theo phần sụn ảo | CHƯA HỖ TRỢ |

Không thử gián đoạn cập nhật trên dữ liệu quan trọng. Chưa cấu hình ảnh chụp trạng thái hoặc hoàn tác; sao lưu là yêu cầu riêng, không phụ thuộc cơ chế hoàn tác tương lai.
