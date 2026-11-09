# Chạy MyKOS live trên máy chỉ có UEFI

ISO BIOS cũ ở build `42527363919` không có bộ nạp UEFI. Chọn GPT trong công cụ ghi USB không bổ sung bộ nạp còn thiếu. Chuỗi tạo ảnh từ commit `06a84f5` đã thêm GRUB amd64 UEFI, GPT/EFI cho USB và mục boot UEFI từ CD-ROM.

**Đã đạt boot live UEFI trong máy ảo:** [42641747422](https://github.com/fx-kitsune/mykos/actions/runs/42641747422), nguồn `48d2b75`, ISO SHA-256 `136f409837a959f725a0e478fb451a0c8a2a221f83100f183853ef3fda9cb3ba`. USB GPT và CD-ROM đều vào Plasma/KWin với tài khoản UID 1000, một desktop/một panel và mở được Dolphin/Konsole/Thiết lập. Phép thử dùng OVMF, q35, RAM 4 GiB, hai CPU, KVM và đồ họa phần mềm; lần lượt khoảng 111,5 và 115 giây. BIOS tới môi trường người dùng cũng đạt bằng TCG, khoảng 221,3 giây. Đã rà soát ảnh ứng dụng ở cả hai phiên UEFI. Ảnh `desktop.png` sớm vẫn ở splash, không dùng nó để chứng nhận desktop đã vẽ xong.

[Tải gói ISO UEFI trong release nháp](https://github.com/fx-kitsune/mykos/releases/tag/untagged-427026dd49e9e2f8ac7b). Cần đăng nhập tài khoản có quyền xem bản nháp của repo. Tải **cả hai** tệp `mykos-0.1.0-dev-amd64.7z.001` và `.002` vào cùng thư mục, mở `.001` bằng 7-Zip rồi Extract. Kết quả có file ISO, `SHA256SUMS`, danh sách gói và thông tin bản dựng. Có thêm `MYKOS-UEFI-PARTS-SHA256SUMS` để kiểm tra các phần tải.

GitHub đã chặn Artifacts với `Artifact storage quota has been hit` ở build [42638222263](https://github.com/fx-kitsune/mykos/actions/runs/42638222263). Workflow `build-uefi-live.yml` kiểm thử ngay trên runner và xuất JSON/ảnh vào log trước bước lưu. Hai volume 7-Zip được dùng để mỗi release asset dưới giới hạn 2 GiB; đây là bản **nháp/prerelease**, chưa công bố ổn định. [Bản ghi nghiệm thu](../tests/integration/evidence/uefi-live-42641747422.json) giữ mã ISO, trạng thái, tài nguyên VM và mã ảnh đã xem.

## Phạm vi

- Phiên live trên máy x86_64 UEFI. Bộ nạp hiện chưa ký; cần Secure Boot tắt để chạy bộ nạp này.
- Có các mục đồ họa thường, an toàn và phần mềm như menu BIOS. Với QEMU/VGA chuẩn, chọn `MyKOS (do hoa phan mem cho may ao)`.
- Cài đặt xuống ổ trong ở chế độ UEFI vẫn bị launcher từ chối. Bố cục ESP, GRUB đích và khả năng boot sau cài chưa được hỗ trợ; không xem boot live thành công là cài UEFI đã hoàn tất.
- Chưa có kiểm chứng firmware, Wi-Fi, GPU hoặc thiết bị thật của từng máy.

## Ghi USB sau khi có ISO đạt kiểm thử

1. Tải hai phần 7-Zip từ release nháp ở trên, giải nén qua phần `.001` để lấy ISO rồi đối chiếu `SHA256SUMS`. ISO BIOS cũ không dùng được cho máy chỉ có UEFI.
2. Trong Rufus, chọn đúng USB dùng riêng (nội dung USB sẽ bị ghi lại), rồi chọn ISO mới. Khi được hỏi cách ghi ISOHybrid, chọn **DD Image mode** để giữ nguyên bảng GPT và phân vùng EFI đã kiểm thử. Ở chế độ DD, công cụ lấy bố cục từ ISO; các ô chọn phân vùng có thể bị khóa.
3. Mở Boot Menu của máy và chọn mục **UEFI: tên USB**. Firmware dùng UEFI, Secure Boot tắt đối với bộ nạp chưa ký này.
4. Chọn phiên live trong menu MyKOS. Chỉ trải nghiệm desktop; trình cài hiện chưa hỗ trợ UEFI.

Đường boot USB tự động dùng QEMU `qemu-xhci` + `usb-storage` và bản sao OVMF variables mới. Công cụ chỉ thêm console nối tiếp/cấu hình đồ họa phần mềm vào bản sao menu GRUB để quan sát; không sửa nhân, initrd, squashfs hoặc bộ nạp EFI. Kết quả ghi mã SHA-256 ISO nguồn, bản sao thử và firmware.
