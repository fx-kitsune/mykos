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

## Tạo ISO bằng GitHub Actions

Không cần máy cá nhân chạy Linux hoặc đủ tài nguyên. Workflow [Tạo ISO MyKOS](https://github.com/fx-kitsune/mykos/actions/workflows/build-iso.yml) dùng máy tạm `ubuntu-24.04` của GitHub để chạy cùng công cụ trong repo.

### Cách chạy

1. Mở repo → **Actions** → **Tạo ISO MyKOS**.
2. Chọn **Run workflow**, chọn nhánh `main` và xác nhận chạy.
3. Theo dõi các bước cài công cụ, kiểm tra tài nguyên, tạo ảnh và kiểm tra sản phẩm.
4. Khi thành công, mở phần **Artifacts** của lần chạy, tải `mykos-iso-amd64-…` và giải nén trên máy cá nhân.
5. Kiểm tra `SHA256SUMS` trong thư mục giải nén bằng `sha256sum -c SHA256SUMS` trên Linux. Trên Windows có thể dùng `Get-FileHash -Algorithm SHA256` trong PowerShell để đối chiếu mã của ISO với dòng tương ứng trong tệp.

Các nhãn **Actions**, **Run workflow**, **Artifacts** là tên nút trên GitHub. Cần đăng nhập tài khoản có quyền chạy workflow. Nếu Actions đang tắt hoặc hạn mức không còn, bật lại/kiểm tra trong thiết lập repo và tài khoản; workflow không tự mua thêm tài nguyên.

### Thời gian chạy và lưu trữ

- Chạy thủ công; chỉ tự kích hoạt trên `main` khi chính tệp `build-iso.yml` thay đổi để thử cấu hình tạo ảnh mới. Sửa tài liệu hoặc giao diện không tự tạo ISO.
- Mỗi nhánh chỉ có một lượt tạo ảnh đang chạy; lượt sau chờ, không tự hủy lượt trước.
- Job tối đa 180 phút, bước tạo ISO tối đa khoảng 150 phút để còn thời gian thu thập nhật ký.
- ISO, mã SHA-256, danh sách gói và thông tin bản dựng lưu trong một gói tải xuống. Nhật ký chẩn đoán lưu riêng trong `mykos-build-logs-…`, kể cả khi tạo ảnh thất bại.
- Hai gói có thời hạn lưu 7 ngày và dùng dung lượng Actions của tài khoản. ISO đã nén được tải lên không nén thêm. Không tự đăng lên GitHub Releases.

### Tài nguyên và xử lý lỗi

Workflow dọn các SDK Android, .NET và GHC cài sẵn trên máy tạm do GitHub cấp. Không dọn máy cá nhân hoặc mã nguồn. Sau khi cài công cụ, kiểm tra lại yêu cầu tối thiểu 25 GiB đĩa trống; không hạ yêu cầu để bỏ qua thiếu dung lượng. Runner có thể ít lõi hoặc RAM hơn cấu hình khuyến nghị cho máy tự quản, vì vậy thời gian tạo ảnh cần được đo từ lần chạy thực tế.

Nếu lỗi, tải nhật ký riêng; xem `preflight.log`, `build.log`, `toolchain.txt` và thông tin đĩa. Thiếu dung lượng, hết thời gian, thiếu đúng phiên bản gói hoặc lỗi tích hợp live-build đều phải được xử lý theo thông báo thực tế. Nếu bị hủy cưỡng bức, runner dừng hoặc hết hạn job, GitHub có thể không thực hiện được bước lưu nhật ký cuối.

Tạo ảnh và xác minh SHA-256 chưa phải kiểm thử khởi động. Workflow build ghi cấu trúc khởi động bằng `xorriso`; sau khi thành công, workflow kiểm thử BIOS chạy QEMU tự động. Chưa xác nhận màn hình Plasma và chưa thử cài đặt. Tiếp tục theo [danh sách nghiệm thu máy ảo](../tests/integration/VM_CHECKLIST.md).

## Kiểm thử khởi động bằng Actions

Workflow **Kiểm thử khởi động ISO** dùng lại Artifacts của lượt tạo ảnh, không tạo lại ISO. Vào Actions, chọn workflow này và **Run workflow**; nhập mã lượt build và tên gói ISO còn hạn. Giá trị mặc định ban đầu trỏ tới lượt tạo ảnh `42392072303`.

Workflow kiểm tra toàn bộ `SHA256SUMS`, tạo bản sao ISO có thêm tham số `console=ttyS0,115200n8 systemd.show_status=1`, rồi khởi động qua BIOS của QEMU. Nhân, initrd và dữ liệu squashfs giữ nguyên. Thay menu trên bản sao giúp quan sát nhật ký mà không sửa bản ISO tải xuống của người dùng; kết quả ghi mã SHA-256 của cả hai ảnh.

QEMU dùng KVM nếu có quyền truy cập, nếu không dùng TCG; RAM 4 GiB, hai CPU ảo, không gắn đĩa cài đặt. Giới hạn chờ khởi động là 20 phút. Chỉ thấy thông báo nhân Linux chưa đủ để đạt: phải có dấu hiệu vào môi trường người dùng, như đích systemd phù hợp hoặc lời nhắc đăng nhập của máy trực tiếp. Lỗi nhân hoặc không tìm thấy hệ thống tệp trực tiếp khiến kiểm thử thất bại.

Kết quả lưu trong `mykos-boot-evidence-…` trong 7 ngày: `result.json`, nhật ký nối tiếp, nhật ký QEMU, menu chẩn đoán và ảnh màn hình. Không lưu thêm bản sao ISO lớn. Xem ảnh thủ công để xác nhận giao diện thực tế; đạt kiểm thử này chưa chứng minh đăng nhập Plasma, mạng/âm thanh, Calamares hoặc phục hồi. Sau mỗi lượt tạo ISO thành công trên `main`, workflow kiểm thử tự động nhận đúng mã lượt build và tên artifact của lượt đó. Có thể chạy thủ công để kiểm tra lại một artifact cụ thể.

### Khi nào ISO được tạo lại?

Push lên `main` thay đổi `distribution/**`, `desktop/workspace/**`, `scripts/build/**` hoặc workflow build sẽ tạo ISO mới. Thay đổi tài liệu hay bản mẫu web không kích hoạt tạo ảnh. Có thể chạy thủ công bằng **Run workflow**. Kết quả kiểm thử BIOS phải khớp lượt build và SHA-256; không dùng kết quả của ISO cũ để nghiệm thu mã mới.

### Bằng chứng phiên Plasma

Sau kiểm thử BIOS, workflow chạy `scripts/testing/probe_desktop.py` trên một máy ảo mới với cùng ISO nguồn. Công cụ chỉ bổ sung console nối tiếp vào bản sao, đăng nhập tài khoản live `mykos`, đợi Plasma và kiểm tra tiến trình KWin; sau đó mở Dolphin, Konsole và Thiết lập bằng môi trường của phiên Plasma. Không dùng sudo, không thay cấu hình hệ thống guest và không gắn ổ đĩa cài đặt.

Kết quả `desktop-services-ready` xác nhận tiến trình và thao tác mở ứng dụng, chưa thay thế rà soát giao diện, bàn phím, mạng, âm thanh hoặc cài đặt. Nếu không đăng nhập được hoặc desktop không chạy, bước kiểm thử thất bại và giữ console cùng ảnh màn hình. Bằng chứng nằm trong `desktop-test/` của artifact kiểm thử; JSON ghi SHA-256 ISO nguồn và bản sao. Cần xem ảnh và ghi kết quả riêng trong danh sách nghiệm thu trước khi đánh dấu phiên Plasma đạt.
