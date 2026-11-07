# Tạo ảnh ISO phát triển M0

## Máy tạo ảnh được hỗ trợ

Dùng **máy ảo Ubuntu 24.04 amd64 riêng cho việc tạo ảnh**, có quyền root, tối thiểu 4 lõi CPU, 8 GiB RAM và 25 GiB đĩa trống. Quá trình tạo ảnh dùng `chroot` và gắn hệ thống tệp; container thông thường không đặc quyền chưa đủ điều kiện. Tránh thực hiện trên máy cá nhân có dữ liệu quan trọng đang được gắn.

Cài phụ thuộc từ kho Ubuntu đã xác thực:

```sh
sudo apt-get update
sudo apt-get install live-build=3.0~a57-1ubuntu49.1 debootstrap ubuntu-keyring \
  squashfs-tools xorriso genisoimage isolinux syslinux syslinux-common \
  syslinux-utils dosfstools mtools cpio rsync python3 git
```

Nếu không có đúng phiên bản đã chốt, dừng và xem lại [quyết định bộ công cụ](ADR/0001-m0-build-baseline.md). Không tự thay bằng Debian live-build vì cách tích hợp Ubuntu/casper khác nhau. APT xác thực gói bằng khóa kho Ubuntu. Cấu hình hiện không thêm kho riêng, khóa bên thứ ba, nguồn Flatpak, thông tin xác thực hoặc PPA.

## Tạo cấu hình và bản dựng

Chạy từ thư mục gốc dự án:

```sh
# Tạo cấu hình không cần root; luôn dùng thư mục chưa tồn tại.
python3 scripts/build/mykos.py configure build/config-review
# Kiểm tra build/config-review/config trước khi tạo ISO đầy đủ.
sudo python3 scripts/build/mykos.py check
sudo python3 scripts/build/mykos.py build build/m0-001 --artifacts artifacts/m0-001
```

Lệnh `build` tự tạo cấu hình mới; không truyền lại thư mục của ví dụ `configure`. Thư mục bản dựng và sản phẩm đã tồn tại không bị tự xóa hoặc tái sử dụng. Khi thất bại, nhật ký vẫn nằm trong thư mục bản dựng.

Nếu lỗi ở bước gắn hệ thống tệp hoặc `chroot`, kiểm tra bằng `findmnt` trước khi xóa tệp. Có thể hủy máy ảo dùng riêng để dọn sạch môi trường.

Lớp thích nghi sao chép bộ công cụ đã cài vào từng thư mục bản dựng và nạp thư viện hàm trong shell hiện tại; không sửa gói hệ thống. `MYKOS_LIVE_BUILD_PREFIX` chỉ hỗ trợ kiểm tra cấu hình với gói Ubuntu đã giải nén. Bản dựng đầy đủ dùng bộ công cụ được cài trên máy.

Workspace Qt 6, biểu tượng, bộ màu, hình nền và mục menu ứng dụng được đưa vào ảnh trong bước tạo cấu hình. Xem [hướng dẫn giao diện](../desktop/README.md) về các gói Qt và giới hạn tích hợp.

## Sản phẩm đầu ra

Khi thành công, thư mục sản phẩm có ISO, danh sách gói đã giải quyết phiên bản, mã commit, trạng thái thay đổi chưa commit, mã băm đầu vào/cấu hình, nhật ký, cấu hình live-build và `SHA256SUMS`.

```sh
cd artifacts/m0-001
sha256sum -c SHA256SUMS
```

Tạo được ảnh chưa chứng minh bản phát hành đạt yêu cầu. Hoàn thành [danh sách kiểm thử máy ảo](../tests/integration/VM_CHECKLIST.md) và ghi bằng chứng trước khi xác nhận khởi động, cài đặt hoặc hỗ trợ thiết bị. Tệp mẫu trong kiểm thử thông tin bản dựng không phải ISO thật.

## Giới hạn tái lập

Đã chốt bản Ubuntu, kiến trúc, nguồn gói và phiên bản live-build. Tuy nhiên `noble`, `noble-updates`, `noble-security` thay đổi theo thời gian; phiên bản gói và toàn bộ công cụ máy tạo ảnh chưa được khóa đầy đủ. Đây là quy trình lặp lại được, **chưa tái lập từng bit**.

Cần kho tại thời điểm cố định, khóa toàn bộ bộ công cụ, chuẩn hóa dấu thời gian và so sánh hai bản dựng độc lập trước khi đạt tiêu chí tái lập nghiêm ngặt.

Giữ `ID` và `VERSION_ID` của Ubuntu để tương thích, đồng thời thêm thông tin biến thể MyKOS. Phiên hệ điều hành nền hiện dùng tiếng Anh; bản địa hóa toàn hệ điều hành và bộ gõ tiếng Việt chưa được tích hợp, kiểm thử. Việc tài liệu và Workspace dùng tiếng Việt không đồng nghĩa toàn bộ bản phân phối đã được Việt hóa.
