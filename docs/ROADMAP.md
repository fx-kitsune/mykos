# MyKOS — Lộ trình phát triển

- Trạng thái: Kế hoạch nghiệm thu; M0 đang thực hiện.
- Mục tiêu ban đầu: Bản phân phối x86_64 cài đặt được.
- Tham chiếu: [Tầm nhìn](PRODUCT_VISION.md), [kiến trúc](ARCHITECTURE.md), [trạng thái thực tế](IMPLEMENTATION_STATUS.md).

## Chiến lược bàn giao

Chia công việc thành mốc nhỏ có kết quả chạy hoặc kiểm thử được và tiêu chí nghiệm thu cụ thể. Hoàn thành nền tảng tạo ảnh, cài đặt và kiểm thử trước khi mở rộng việc tự viết giao diện hệ thống. Workspace và bộ nhận diện Fold hiện tại là phần tích hợp giới hạn, chưa hoàn thành M0 hoặc M1.

## M0 — Nền tảng và lần khởi động đầu tiên

**Mục tiêu:** ISO MyKOS đầu tiên có thể tái lập, dùng Ubuntu LTS và KDE Plasma.

Công việc:

- Chốt bản Ubuntu LTS, bộ công cụ tạo ảnh, phiên bản và nguồn gói.
- Tạo danh sách gói tối thiểu, cấu hình KDE và nhận diện MyKOS.
- Tạo ISO x86_64, xuất thông tin bản dựng và mã kiểm tra.
- Khởi động trong QEMU/KVM, cài xuống ổ đĩa ảo sạch và xác nhận lần đăng nhập đầu.
- Ghi hướng dẫn và lỗi đã biết; xác định điều kiện tái lập ảnh.

**Nghiệm thu:** Tạo ảnh lặp lại được từ đầu vào có tài liệu; ISO khởi động; cài đặt thành công; Plasma đăng nhập được; mạng, âm thanh, màn hình, tệp, trình dòng lệnh và quản lý gói đạt kiểm thử cơ bản; có thông tin bản dựng và mã kiểm tra.

## M1 — Trải nghiệm môi trường làm việc

Đã chuẩn bị [bộ thiết kế M1](../design-system/m1/README.md) với bản mẫu năm màn hình và đặc tả. Đây là công việc thiết kế song song; chưa đánh dấu M0 hoặc M1 hoàn thành.

**Mục tiêu:** Thống nhất cấu hình mặc định về hình thức và tương tác.

Công việc:

- Hoàn thiện bộ nhận diện, chủ đề, biểu tượng, phông chữ và hình nền.
- Cấu hình thanh tác vụ, trình mở ứng dụng, thông báo, phím tắt và màn hình ảo.
- Rà soát khả năng tiếp cận và điều hướng bàn phím.
- Tài liệu hóa cấu hình và cách đặt lại mặc định.

**Nghiệm thu:** Nhận diện nhất quán giữa đăng nhập, màn hình làm việc và thiết lập; tác vụ thông thường dễ sử dụng; cấu hình có thể dựng lại từ mã nguồn.

## M2 — Quản lý hệ thống

**Mục tiêu:** Thiết lập thông thường dễ hiểu và đáng tin cậy.

Công việc:

- Đánh giá mô-đun KDE có sẵn trước khi viết thay thế.
- Tích hợp màn hình, mạng, Bluetooth, âm thanh, nguồn điện, lưu trữ và người dùng.
- Bổ sung trợ giúp, trạng thái và chẩn đoán riêng khi trải nghiệm gốc chưa đáp ứng.
- Xác định ranh giới quyền cho thao tác quản trị.

**Nghiệm thu:** Quy trình hoạt động trên ma trận phần cứng hỗ trợ; thao tác đặc quyền dùng cơ chế cấp quyền được hỗ trợ; lỗi rõ ràng và không để hệ thống ở trạng thái không xác định.

## M3 — Trải nghiệm ứng dụng

**Mục tiêu:** Thống nhất tìm kiếm và quản lý ứng dụng.

Công việc:

- Xác định nguồn phần mềm đáng tin và thông tin danh mục.
- Tích hợp Flatpak với trình quản lý gói nền tảng.
- Thiết kế cài đặt, cập nhật, gỡ bỏ và hiển thị quyền truy cập.
- Hiển thị rõ nhà phát hành, nguồn gói và thành phần chịu trách nhiệm cập nhật.

**Nghiệm thu:** Người dùng tìm, cài, mở, cập nhật và gỡ ứng dụng được hỗ trợ; nguồn và quyền hiển thị chính xác; thao tác lỗi đưa ra hướng xử lý.

## M4 — Trải nghiệm nhà phát triển

**Mục tiêu:** Máy trạm phát triển hiệu quả, không áp đặt một bộ công nghệ.

Công việc:

- Tài liệu hóa các cách thiết lập được hỗ trợ.
- Tích hợp trình dòng lệnh, Git, trình soạn thảo, IDE, SDK, môi trường thực thi và container.
- Chỉ cân nhắc trung tâm công cụ phát triển sau khi yêu cầu được xác nhận.
- Thử quy trình phổ biến trên bản cài mới.

**Nghiệm thu:** Chạy được ít nhất một quy trình đại diện có tài liệu; thiết lập lặp lại được; công cụ không làm tổn hại tính toàn vẹn hệ điều hành nền.

## M5 — Độ tin cậy và phục hồi

**Mục tiêu:** Cập nhật và phục hồi dễ hiểu, kiểm thử được.

Công việc:

- Xác định kênh cập nhật, chu kỳ phát hành và ghi chú phiên bản.
- Hiển thị trạng thái cập nhật rõ ràng; thử cập nhật bị gián đoạn hoặc thất bại.
- Đánh giá ảnh chụp trạng thái hệ thống tệp và tích hợp hoàn tác.
- Hướng dẫn sao lưu, phục hồi, chẩn đoán; thiết lập xử lý bản vá bảo mật và lỗ hổng.

**Nghiệm thu:** Cập nhật được thử trên bố cục cài đặt hỗ trợ; quy trình phục hồi đã được thực hành; nếu có hoàn tác bằng ảnh chụp trạng thái thì phải thử toàn bộ quy trình và không mô tả đó là sao lưu dữ liệu.

## M6 — Phát hành công khai 1.0

**Mục tiêu:** Phát hành ổn định, có phạm vi hỗ trợ rõ ràng.

Công việc:

- Chốt ma trận phần cứng và hoàn tất kiểm thử cài đặt, giao diện, cập nhật, phục hồi, bảo mật.
- Công bố ghi chú phiên bản, lỗi đã biết, mã kiểm tra và hướng dẫn cài đặt.
- Công bố kênh hỗ trợ, hướng dẫn đóng góp; gắn thẻ phiên bản và lưu thông tin bản dựng.

**Nghiệm thu:** Không còn lỗi chặn phát hành; cài đặt và cập nhật đạt trên ma trận hỗ trợ; sản phẩm phát hành tái lập và kiểm tra được; tài liệu phản ánh đúng giới hạn.

## Yêu cầu xuyên suốt

Mỗi mốc phải cập nhật tài liệu tiếng Việt, bổ sung kiểm thử tự động khi phù hợp, rà soát khả năng tiếp cận, bảo mật, quyền truy cập, tương thích dự án gốc và có người phụ trách cùng tiêu chí nghiệm thu rõ ràng.

## Hạng mục để sau

Nhân Linux riêng, bản phân nhánh toàn bộ Plasma, định dạng gói riêng, hệ thống khởi tạo riêng, cam kết tương thích mọi ứng dụng Windows, tài khoản đám mây, đồng bộ nhiều thiết bị và chuyển sang hệ điều hành bất biến chỉ được xem xét khi có bằng chứng và nguồn lực bảo trì.

## Việc tiếp theo

Cấu hình nền tảng và công cụ đã được triển khai. Trọng tâm tiếp theo là tạo ISO thật trên máy Ubuntu đủ điều kiện, kiểm thử khởi động, tích hợp Calamares, cài xuống đĩa ảo và xác nhận lần đăng nhập đầu. Chưa mở rộng phạm vi trước khi hoàn thành các tiêu chí M0.
