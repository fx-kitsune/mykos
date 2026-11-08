# Tài liệu dự án MyKOS

## Đọc theo nhu cầu

| Nhu cầu | Tài liệu |
|---|---|
| Hiểu mục tiêu và đối tượng sử dụng | [Tầm nhìn sản phẩm](PRODUCT_VISION.md) |
| Hiểu cấu trúc và lựa chọn công nghệ | [Kiến trúc kỹ thuật](ARCHITECTURE.md) |
| Theo dõi các mốc nghiệm thu | [Lộ trình phát triển](ROADMAP.md) |
| Phân biệt phần đã làm, đã kiểm tra và còn thiếu | [Trạng thái triển khai](IMPLEMENTATION_STATUS.md) |
| Chuẩn bị máy và tạo ISO | [Hướng dẫn tạo ISO](BUILD.md) |
| Chạy và phát triển giao diện native | [Workspace và tích hợp KDE](../desktop/README.md) |
| Triển khai thiết kế trải nghiệm M1 | [Đặc tả và bản mẫu M1](../design-system/m1/README.md) |
| Tra cứu phong cách giao diện | [Bộ thiết kế](../design-system/README.md) |
| Dựng biểu tượng đúng quy chuẩn | [Quy chuẩn biểu tượng Fold](../design-system/assets/icons/README.md) |
| Kiểm thử khởi động và cài đặt | [Danh sách kiểm thử máy ảo](../tests/integration/VM_CHECKLIST.md) |
| Ghi nhận phần cứng được hỗ trợ | [Ma trận phần cứng](../tests/hardware/README.md) |
| Chuẩn bị tích hợp Calamares | [Điều kiện tích hợp trình cài đặt](../distribution/installer/README.md) |
| Hiểu lý do chọn nền tảng M0 | [Quyết định kiến trúc 0001](ADR/0001-m0-build-baseline.md) |
| Hiểu phạm vi triển khai Fold | [Quyết định kiến trúc 0002](ADR/0002-fold-native-integration.md) |
| Hiểu giấy phép dự án | [Giải thích giấy phép](../LICENSE.vi.md) |

## Quy ước biên soạn

1. Viết tiêu đề, nội dung, bảng, chú thích lệnh, mô tả ảnh và tài liệu được sinh tự động bằng tiếng Việt có dấu.
2. Giữ nguyên tên sản phẩm, tên gói, API, khóa cấu hình, tên tệp, đường dẫn, biến môi trường và câu lệnh. Không dịch định danh khiến hướng dẫn không còn chạy đúng.
3. Dùng “tạo ISO” hoặc “tạo bản dựng” cho thao tác xây dựng ảnh hệ thống; “nghiệm thu” cho việc xác nhận đủ tiêu chí; “kho gói” cho nguồn phần mềm; “ảnh hệ thống” cho sản phẩm đóng gói hệ điều hành.
4. Phân biệt mục tiêu thiết kế, phần đã triển khai và kết quả đã kiểm chứng. Tạo được cấu hình hoặc render được giao diện chưa chứng minh ISO khởi động hay cài đặt thành công.
5. Cập nhật tài liệu nguồn khi sửa nội dung được sinh tự động. Với Fold, phải sửa cả mẫu trong `design-system/tools/build-icons.cjs`; bản ZIP cũng phải chứa nội dung tiếng Việt tương ứng.
6. Giữ liên kết tương đối trong repo. Tên tệp hiện tại được giữ để không làm hỏng liên kết đã chia sẻ.
7. Giữ bản gốc giấy phép pháp lý trong `LICENSE`; bản giải thích tiếng Việt nằm tại `LICENSE.vi.md`. Tài liệu hướng dẫn không được tự ý thay đổi điều khoản cấp phép.

## Thuật ngữ dùng trong dự án

| Thuật ngữ | Cách hiểu |
|---|---|
| Bản phân phối | Hệ điều hành được lắp ghép từ nhân Linux, gói phần mềm và cấu hình |
| Ảnh hệ thống / ISO | Tệp chứa môi trường khởi động và nội dung hệ điều hành |
| Phiên chạy trực tiếp | Môi trường chạy từ ISO mà chưa cài xuống ổ đĩa |
| Bản dựng | Kết quả của một lần tạo ảnh hệ thống từ cấu hình và mã nguồn |
| Bộ công cụ tạo ảnh | Các công cụ và phiên bản dùng để tạo bản dựng |
| Kho gói | Nguồn cung cấp gói phần mềm và thông tin xác thực |
| Bộ kiểm thử cơ bản | Các kiểm tra ngắn để phát hiện lỗi chức năng chính |
| Tái lập từng bit | Hai lần tạo ảnh cho kết quả giống hệt nhau ở mức byte |
| Thành phần gốc | Thành phần được phát triển, duy trì bởi dự án nguồn như KDE hoặc Ubuntu |
| ADR | Hồ sơ quyết định kiến trúc, ghi bối cảnh, lựa chọn và hệ quả |
| Workspace | Tên ứng dụng MyKOS quản lý ba ngữ cảnh ghi chú và công cụ liên quan |
