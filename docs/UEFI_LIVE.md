# Chạy MyKOS live trên máy chỉ có UEFI

ISO BIOS cũ ở build `42527363919` không có bộ nạp UEFI. Chọn GPT trong công cụ ghi USB không bổ sung bộ nạp còn thiếu. Chuỗi tạo ảnh từ commit `06a84f5` đã thêm GRUB amd64 UEFI, GPT/EFI cho USB và mục boot UEFI từ CD-ROM.

**Trạng thái:** build [42638222263](https://github.com/fx-kitsune/mykos/actions/runs/42638222263) đã tạo ISO, kiểm tra checksum và cấu trúc BIOS/UEFI/GPT, nhưng không tải được lên GitHub vì `Artifact storage quota has been hit`. Vì vậy chưa có file tải xuống từ lượt đó và chưa nghiệm thu boot hệ điều hành đầy đủ. Thử nghiệm ảnh nhỏ đã xác nhận OVMF chạy được bộ nạp/menu từ USB GPT và CD-ROM; tệp nhân trong ảnh nhỏ là dữ liệu giả.

[Lượt 42641747422](https://github.com/fx-kitsune/mykos/actions/runs/42641747422) dùng workflow `build-uefi-live.yml`: tạo ISO, kiểm thử UEFI USB/CD-ROM tới Plasma và BIOS ngay trên cùng runner trước khi upload. Kết quả/ảnh còn được xuất vào log. Nếu Artifacts bị chặn, chỉ sau khi kiểm thử đạt mới tạo release **nháp/prerelease**, với archive 7-Zip chia phần dưới giới hạn 2 GiB/tệp; không tự công bố bản ổn định.

## Phạm vi

- Phiên live trên máy x86_64 UEFI. Bộ nạp hiện chưa ký; cần Secure Boot tắt để chạy bộ nạp này.
- Có các mục đồ họa thường, an toàn và phần mềm như menu BIOS. Với QEMU/VGA chuẩn, chọn `MyKOS (do hoa phan mem cho may ao)`.
- Cài đặt xuống ổ trong ở chế độ UEFI vẫn bị launcher từ chối. Bố cục ESP, GRUB đích và khả năng boot sau cài chưa được hỗ trợ; không xem boot live thành công là cài UEFI đã hoàn tất.
- Chưa có kiểm chứng firmware, Wi-Fi, GPU hoặc thiết bị thật của từng máy.

## Ghi USB sau khi có ISO đạt kiểm thử

1. Tải đúng artifact ISO UEFI đã có bằng chứng nghiệm thu, giải nén ZIP và đối chiếu `SHA256SUMS`. Artifact BIOS cũ không dùng được cho máy chỉ có UEFI.
2. Trong Rufus, chọn đúng USB dùng riêng (nội dung USB sẽ bị ghi lại), rồi chọn ISO mới. Khi được hỏi cách ghi ISOHybrid, chọn **DD Image mode** để giữ nguyên bảng GPT và phân vùng EFI đã kiểm thử. Ở chế độ DD, công cụ lấy bố cục từ ISO; các ô chọn phân vùng có thể bị khóa.
3. Mở Boot Menu của máy và chọn mục **UEFI: tên USB**. Firmware dùng UEFI, Secure Boot tắt đối với bộ nạp chưa ký này.
4. Chọn phiên live trong menu MyKOS. Chỉ trải nghiệm desktop; trình cài hiện chưa hỗ trợ UEFI.

Đường boot USB tự động dùng QEMU `qemu-xhci` + `usb-storage` và bản sao OVMF variables mới. Công cụ chỉ thêm console nối tiếp/cấu hình đồ họa phần mềm vào bản sao menu GRUB để quan sát; không sửa nhân, initrd, squashfs hoặc bộ nạp EFI. Kết quả ghi mã SHA-256 ISO nguồn, bản sao thử và firmware.
