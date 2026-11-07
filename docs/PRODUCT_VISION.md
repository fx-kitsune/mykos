# MyKOS — Tầm nhìn sản phẩm

> **Mặc định đơn giản. Thiết kế mạnh mẽ.**
> Hệ điều hành Linux dành cho mọi người.

- Trạng thái: Định hướng sản phẩm, phiên bản 1.0.
- Đối tượng: Người dùng phổ thông và nhà phát triển.
- Nền tảng ban đầu: Máy tính để bàn, máy tính xách tay x86_64.
- Chiến lược: Xây dựng bản phân phối độc lập trên nền Linux đã có hệ sinh thái ổn định.

## 1. Tầm nhìn

Xây dựng hệ điều hành mở, hiện đại, dễ tiếp cận trong công việc hằng ngày nhưng vẫn giữ sự linh hoạt, minh bạch và quyền kiểm soát mà người dùng Linux mong đợi.

Người dùng không cần hiểu Linux để sử dụng MyKOS. Người muốn học sâu hơn vẫn có thể tìm hiểu, thay đổi và quản lý máy tính của mình.

## 2. Sứ mệnh

1. Làm Linux dễ cài đặt, dễ học và dễ sử dụng.
2. Giảm trở ngại kỹ thuật trong các tác vụ máy tính thông thường.
3. Giữ quyền kiểm soát của người dùng và giải thích hành vi hệ thống.
4. Thống nhất trải nghiệm quản lý ứng dụng và hệ thống.
5. Ưu tiên độ tin cậy, bảo mật, khả năng tiếp cận và khả năng bảo trì lâu dài.
6. Tích hợp tiêu chuẩn mở và dự án nguồn mở có sẵn khi phù hợp.

## 3. Người dùng mục tiêu

### Người dùng phổ thông

Người duyệt web, liên lạc, học tập, soạn tài liệu và quản lý nội dung đa phương tiện. Họ cần giao diện quen thuộc, thiết lập dễ hiểu, cập nhật đáng tin cậy và quy trình cài đặt ít trở ngại.

### Nhà phát triển và người dùng kỹ thuật

Người cần trình dòng lệnh, Git, trình soạn thảo, IDE, môi trường thực thi, SDK và công cụ container. Họ phải có khả năng kiểm soát môi trường phát triển bằng các công cụ Linux thông dụng.

### Cam kết chung

Một bản cài đặt phục vụ cả hai nhóm. Tính năng nâng cao dễ tìm khi cần nhưng không gây quá tải cho người mới; bề mặt đơn giản đi cùng nền tảng có năng lực.

## 4. Nguyên tắc sản phẩm

- **Dễ tiếp cận:** Tác vụ thông thường không đòi hỏi kiến thức Linux chuyên sâu.
- **Linh hoạt:** Cho phép tùy chỉnh và sử dụng công cụ Linux chuẩn.
- **Minh bạch:** Giải thích thao tác quan trọng, quyền truy cập, cập nhật và lỗi.
- **Đáng tin cậy:** Ưu tiên hành vi dự đoán được và khả năng phục hồi.
- **Mở:** Tôn trọng giấy phép, tiêu chuẩn và quyền sở hữu của người dùng.
- **Bảo mật từ thiết kế:** Áp dụng đặc quyền tối thiểu, nguồn phần mềm đáng tin và ranh giới quyền rõ ràng.
- **Dễ duy trì với dự án gốc:** Ưu tiên cấu hình, đóng gói và bản vá nhỏ thay vì duy trì bản phân nhánh lớn.

## 5. Định vị

MyKOS tham khảo tính quen thuộc của Windows, sự nhất quán của macOS, hệ sinh thái Ubuntu, cách tích hợp Fedora và khả năng tùy biến KDE Plasma. Bản sắc riêng đến từ tích hợp nhất quán, cấu hình mặc định có chủ đích và trải nghiệm đáng tin cậy.

## 6. Phạm vi sản phẩm

| Phạm vi | Nội dung |
|---|---|
| Môi trường làm việc | Màn hình nền, thanh tác vụ, trình mở ứng dụng, thông báo, quản lý cửa sổ và màn hình ảo |
| Khả năng tiếp cận | Điều hướng bàn phím, hỗ trợ tiếp cận và mặc định dễ hiểu |
| Quản lý hệ thống | Màn hình, âm thanh, mạng, Bluetooth, nguồn điện, lưu trữ, người dùng và thiết bị ngoại vi |
| Phần cứng | Trạng thái thiết bị, trình điều khiển và hướng khắc phục lỗi thông thường |
| Ứng dụng | Danh mục đồ họa, cài đặt, cập nhật, gỡ bỏ; thể hiện nguồn, quyền và cơ chế cập nhật |
| Phát triển phần mềm | Trình dòng lệnh, Git, IDE, SDK, môi trường thực thi và container; không ép một bộ công nghệ duy nhất |
| Độ tin cậy | Cập nhật có kiểm soát, nhật ký chẩn đoán, hướng dẫn phục hồi và phương án khôi phục đã kiểm thử |
| Phần sụn | Cập nhật ở những thiết bị và nguồn được công cụ gốc hỗ trợ |
| Hệ sinh thái lâu dài | Đồng bộ cấu hình tùy chọn, tiện ích mở rộng và ứng dụng riêng sau khi lõi ổn định |

## 7. Phiên bản khả dụng tối thiểu

Mốc khả dụng đầu tiên là ảnh MyKOS tái lập được, cài đặt được, khởi động ổn định và cung cấp môi trường KDE cơ bản đầy đủ.

Tiêu chí nghiệm thu:

1. Tạo được ISO x86_64 tái lập từ mã nguồn, cấu hình và hướng dẫn đã công bố.
2. ISO khởi động trong máy ảo và trên tập phần cứng thử nghiệm đã xác định.
3. Cài đặt hoàn tất trên ổ đĩa ảo sạch.
4. Đăng nhập thành công vào KDE Plasma hoạt động bình thường.
5. Mạng, âm thanh, thiết lập màn hình, quản lý tệp, trình dòng lệnh và cài gói cơ bản hoạt động.
6. Quy trình cập nhật hệ thống có tài liệu và đã được thử nghiệm.
7. Giới hạn đã biết và phần cứng hỗ trợ được ghi rõ.
8. Không còn lỗi nghiêm trọng về khởi động, đăng nhập hoặc mất dữ liệu trong ma trận kiểm thử được hỗ trợ.

## 8. Ngoài phạm vi bản đầu tiên

- Viết nhân Linux mới hoặc thay systemd, NetworkManager, PipeWire, Mesa khi chưa có lý do kỹ thuật thuyết phục.
- Viết lại mọi ứng dụng máy tính cá nhân.
- Cam kết tương thích toàn bộ phần mềm Windows hoặc mọi phần cứng.
- Tạo định dạng gói riêng khi chưa có nhu cầu cụ thể.
- Phát hành giao diện hệ thống tự viết trước khi nền tảng ổn định và tái lập được.

## 9. Thước đo thành công

Cài đặt và khởi động thành công trên ma trận hỗ trợ; không còn lỗi chặn phát hành; tạo ảnh tái lập được; kiểm thử cập nhật và phục hồi đạt; người mới hoàn thành tác vụ thông thường thuận tiện; quy trình phát triển dùng công cụ chuẩn và hướng dẫn lặp lại được; mọi thay đổi dự án gốc đều có nguồn gốc rõ và duy trì được.

## 10. Quy tắc quyết định sản phẩm

Trước khi thêm tính năng, đánh giá: tính năng cải thiện tác vụ thực tế nào, thành phần có sẵn có giải quyết tốt không, quyền kiểm soát và bảo mật có được giữ không, đội ngũ có kiểm thử và bảo trì được không, và thay đổi có làm trải nghiệm hệ điều hành nhất quán hơn không.

Tích hợp giải pháp nguồn mở đã đáp ứng tốt yêu cầu. Chỉ phát triển thành phần riêng khi tạo giá trị cụ thể cho người dùng MyKOS.
