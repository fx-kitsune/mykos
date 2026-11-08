# MyKOS M1 — Đặc tả trải nghiệm Fold

- Phiên bản: 1.0 thiết kế, ngày 08/11/2026.
- Trạng thái: Đề xuất để triển khai; chưa nghiệm thu M1, không thay đổi trạng thái M0.
- Đối tượng: Người dùng phổ thông và người dùng Linux nâng cao trên máy tính x86_64.
- Nguồn: [Định hướng sản phẩm](../../docs/PRODUCT_VISION.md), [Fold gốc](../README.md), [Workspace hiện tại](../../desktop/README.md).
- Bàn giao: [Bản mẫu tương tác](index.html), [giá trị thiết kế dùng chung](tokens.json), đặc tả này.

## 1. Kết quả M1 cần tạo ra

Người dùng nhận ra MyKOS từ màn hình đăng nhập đến desktop, mở được ứng dụng quen thuộc, tìm được thiết lập và phân biệt được trạng thái hệ thống. Thao tác bằng chuột và bàn phím có cùng thứ tự, không cần học một mô hình cửa sổ mới.

Phạm vi gồm nhận diện, bảng màu, chữ, biểu tượng, hình nền, thanh tác vụ, trình mở ứng dụng, thông báo, mặc định cửa sổ, khả năng tiếp cận và cách phục hồi cấu hình giao diện. Quản lý gói, trình điều khiển và quy trình cập nhật chuyên sâu thuộc M2/M3/M5; M1 chỉ chuẩn hóa cách hiển thị.

## 2. Quyết định bố cục

### Desktop hệ thống

Dùng Plasma với **một thanh tác vụ cạnh dưới cao 52 đơn vị logic**, trải hết chiều rộng màn hình trong bản triển khai. Bản mẫu đặt khung cách mép 12 px để dễ xem các thành phần; không coi khoảng cách trình bày này là yêu cầu cho panel thật.

Thứ tự từ trái sang phải: biểu tượng MyKOS mở ứng dụng → dấu phân cách → ứng dụng ghim và cửa sổ đang mở → khoảng trống → khay hệ thống, thông báo → ngày giờ → vùng hiện desktop do KDE cung cấp. Bản mẫu rút gọn khay hệ thống để tránh mô phỏng trạng thái phần cứng.

Ghim ban đầu: Workspace, Dolphin, trình duyệt đã được chốt và có trong ảnh, Thiết lập hệ thống. Nếu ảnh chưa có trình duyệt, chưa ghim nút trỏ tới ứng dụng không tồn tại. Trình dòng lệnh nằm trong menu và có thể ghim; không bắt buộc xuất hiện với người mới.

Một chấm hoặc gạch ngắn cho biết ứng dụng đang chạy; viền và nền cho biết cửa sổ được chọn. Không chỉ dùng màu để biểu đạt trạng thái. Nhóm cửa sổ cùng ứng dụng theo hành vi KDE; không tự viết lại trình quản lý cửa sổ.

### Workspace

Thanh công cụ dọc thuộc riêng cửa sổ Workspace. Ba mục Cá nhân/Sáng tạo/Lập trình là ngữ cảnh ghi chú, không làm dịch chuyển cửa sổ hệ thống và không tự tạo thư mục. Không đặt bộ chuyển ngữ cảnh này thành thanh điều hướng toàn hệ điều hành khi chưa tích hợp KDE Activities.

Cửa sổ có thanh tiêu đề hệ thống và nút thu nhỏ, phóng to, đóng theo KDE. Hình vẽ nút trong bản mẫu chỉ minh họa vị trí; không phải điều khiển cửa sổ trình duyệt.

### Màn hình và tỉ lệ

| Môi trường | Yêu cầu thiết kế |
|---|---|
| 1366×768, 100% | Menu và panel không che phần nội dung chính; Workspace có cuộn khi cần |
| 1920×1080, 100% | Khoảng trống tăng, không phóng to chữ chỉ vì màn hình rộng |
| HiDPI 125/150/200% | Dùng đơn vị logic của Qt/Plasma, không nhân tỉ lệ hai lần |
| Cửa sổ Workspace 900×700 | Giới hạn thiết kế native hiện tại; nội dung không tràn ngang |
| Nhiều màn hình | Một panel chính; màn hình mới không tự sao chép panel hoặc đổi vị trí cửa sổ |
| Trang xem thiết kế dưới 640 px | Xếp thẻ dọc để xem trên điện thoại; không phải cam kết hệ điều hành di động |

## 3. Nhận diện và tài nguyên

Giữ dấu gấp Fold, mặt phẳng lì, đường đồng mức nhẹ, màu xanh mực và điểm chanh. Dùng dấu MyKOS từ SVG gốc ở menu, thông tin hệ thống và đăng nhập. Chỉ dùng đường đồng mức trên nền trang hoặc hình nền; không đặt sau văn bản dài, trường nhập hay thông báo lỗi.

Biểu tượng hệ thống theo lưới 24×24, nét 1,6, đầu và chỗ nối bo tròn. Biểu trưng ứng dụng dùng khung gấp, sáu nhóm chất liệu đã có. Dùng tên chuẩn KDE cho ánh xạ ứng dụng; biểu tượng thiếu lấy từ Breeze/hicolor. Không thay biểu tượng bằng emoji vì hình dạng và màu thay đổi theo môi trường.

Bộ thiết kế M1 không tự đổi logo hoặc hình học Fold đã được đưa vào repo. Tài nguyên xuất cho Qt phải qua trình chuyển SVG hiện có vì Qt SVG Tiny không hỗ trợ SVG lồng nhau như trình duyệt.

## 4. Màu, chữ và kích thước

Giá trị chuẩn nằm trong `tokens.json`. Màu mang vai trò: nền, bề mặt, bề mặt nổi, chữ chính, chữ phụ, điểm nhấn, chữ trên điểm nhấn, đường viền, lỗi và thành công. Không dùng tên màu để suy ra tác dụng.

| Vai trò | Ink | Paper |
|---|---|---|
| Nền | `#171c19` | `#eeefe6` |
| Bề mặt | `#202722` | `#f7f8f0` |
| Chữ chính | `#edf0e7` | `#293323` |
| Chữ phụ | `#9aa598` | `#5e6d57` |
| Điểm nhấn | `#d7ef83` | `#526a2b` |
| Chữ trên điểm nhấn | `#20271c` | `#ffffff` |

Dùng Noto Sans từ gói nền để có tiếng Việt và hoạt động ngoại tuyến. Noto Sans Mono cho mã và số liệu khi cần căn cột. Không phụ thuộc Google Fonts hoặc tải phông trong phiên hệ điều hành.

Chữ nội dung 14, phụ 12, tiêu đề mục 18, tiêu đề trang 28 và câu chào lớn 40 đơn vị logic. Giãn dòng nội dung 1,5; không dùng chữ 10 cho nội dung quyết định hoặc thông báo lỗi. Chữ 10 trong bản mẫu dành cho nhãn trang trí, không làm chuẩn thu nhỏ mọi thành phần KDE.

Nhịp khoảng cách: 4/8/12/16/24/32/48/64. Bo góc nút 4, thẻ và cửa sổ 8. Nút tối thiểu cao 36, vùng bấm hỗ trợ cảm ứng hướng tới 44; biểu tượng thao tác 24, viền tiêu điểm 2 và khoảng cách tiêu điểm 3.

## 5. Hành vi thành phần

| Thành phần | Mặc định | Tương tác | Không khả dụng / lỗi |
|---|---|---|---|
| Nút chính | Nền nhấn, chữ tương phản | Một hành động chính trong vùng; Enter/Space kích hoạt | Có lý do bằng chữ; không chỉ làm mờ |
| Nút thường | Bề mặt, nhãn rõ | Nền đổi khi trỏ; tiêu điểm thấy rõ | Không điều hướng tới ứng dụng chưa cài |
| Tab/ngữ cảnh | Có nhãn và số thứ tự | Viền, nền và trạng thái được chọn; không mất nội dung | Trạng thái lưu ghi chú lỗi hiển thị gần nội dung |
| Trường nhập | Nhãn luôn hiện ngoài giá trị | Tiêu điểm rõ, hỗ trợ chọn/dán và bộ gõ | Lỗi bằng chữ, giữ dữ liệu đang nhập |
| Menu ứng dụng | Tìm kiếm ở đầu | Có thể tìm không dấu; Enter mở kết quả; Escape đóng | “Chưa tìm thấy ứng dụng phù hợp.” và giữ truy vấn |
| Thông báo | Tên nguồn, nội dung, hành động liên quan | Dùng trung tâm KDE để xem lại | Lỗi cần hành động không biến mất cùng hạn ngắn như thông báo thông thường |
| Thanh tiến độ | Mô tả việc đang làm | Có thể hủy khi cơ chế nền thực sự hỗ trợ | Không hiện phần trăm giả hoặc nút hủy không hoạt động |

Chuyển động: đổi trạng thái trỏ khoảng 120 ms, mở bảng khoảng 160 ms. Khi người dùng yêu cầu giảm chuyển động, tắt chuyển cảnh không cần thiết; không dùng ảnh động để truyền thông tin duy nhất.

## 6. Năm màn hình bàn giao

### A. Màn hình làm việc

Hình nền Ink nhẹ, panel cố định cạnh dưới, một cửa sổ Workspace thể hiện ba ngữ cảnh, dự án/tệp, ghi chú và tập trung. Không tự mở Workspace mỗi lần đăng nhập trong M1 nếu chưa có quyết định về lần chạy đầu. Hồ sơ mới có một cấu hình ban đầu; người dùng vẫn được tùy biến.

### B. Trình mở ứng dụng

Dùng Kickoff của Plasma; KRunner tiếp tục phục vụ tìm lệnh nhanh. Bản mẫu dùng danh mục sáu ứng dụng để xem cấu trúc, không phải nguồn danh sách ứng dụng thật. Bản triển khai phải đọc mục ứng dụng đã cài, tìm theo tên tiếng Việt/tên gốc và trình bày trạng thái không có kết quả. Mở menu đặt tiêu điểm vào ô tìm; đóng trả tiêu điểm về nút gọi. Menu không được chặn Alt+Tab hoặc phím tắt hệ thống.

### C. Thông báo và lỗi

Dùng thông báo và khay hệ thống KDE. Trạng thái thành công ngắn gọn, có thể mở vị trí liên quan. Trạng thái lỗi mô tả việc chưa làm được, nguyên nhân đã biết và bước tiếp theo, ví dụ: “Chưa tải được danh sách ứng dụng. Không có kết nối mạng. Kiểm tra kết nối rồi thử lại.” Không hiển thị thông tin kỹ thuật nội bộ trừ khi người dùng mở chi tiết.

Không mô phỏng Wi-Fi, pin hoặc cập nhật như thể lấy trạng thái thật. Không tự xóa thông báo quan trọng khi bật Không làm phiền; giữ chúng trong lịch sử theo chính sách KDE. Không làm gián đoạn công việc bằng hộp thoại nếu chưa cần quyết định.

### D. Thiết lập giao diện

Dùng các trang KDE có sẵn để chọn màu, biểu tượng, hình nền, chữ, tỉ lệ và khả năng tiếp cận. Áp dụng giao diện toàn hệ thống là thao tác có chủ đích tại đây. Nút sáng/tối trong Workspace hiện chỉ đổi riêng ứng dụng, chưa được mô tả là đổi toàn hệ thống.

Mỗi thay đổi có phản hồi; thay đổi màn hình cần cơ chế tự hoàn nguyên có thời gian xác nhận từ KDE. Không tự viết lại trang mạng, âm thanh hoặc người dùng trong M1.

### E. Đăng nhập và khóa máy

Tích hợp SDDM cho đăng nhập và màn hình khóa của Plasma cho khóa máy; đây là hai thành phần khác nhau. Bản M1 đầu ưu tiên cấu hình/chủ đề Breeze tương thích thay vì viết bộ xác thực mới.

Luồng: chọn tài khoản → nhập mật khẩu → đang xác thực → phiên làm việc hoặc lỗi có thể thử lại. Không hiển thị mật khẩu, không ghi nội dung trường vào nhật ký. Thông báo lỗi không phân biệt tài khoản có tồn tại hay không. Có đường truy cập bàn phím, bố cục bàn phím, tùy chọn hỗ trợ và lựa chọn phiên thực sự có sẵn. Tắt nguồn/khởi động lại dùng cơ chế cấp quyền gốc, không chạy lệnh root từ giao diện.

Bản mẫu không xác thực, không gửi và không lưu mật khẩu; ô nhập được xóa khi bấm nút. Chưa có màn hình đăng nhập M1 tích hợp trong ảnh hệ điều hành.

## 7. Bàn phím và khả năng tiếp cận

| Phím | Hành vi mục tiêu |
|---|---|
| Meta | Mở menu ứng dụng KDE |
| Alt+Space | KRunner theo cấu hình KDE đã kiểm thử |
| Alt+Tab | Chuyển cửa sổ theo KWin |
| Meta+E | Mở trình quản lý tệp nếu phím tắt này được xác nhận trong hồ sơ |
| Meta+L | Khóa phiên bằng cơ chế KDE |
| Escape | Đóng bảng hiện tại, không xóa dữ liệu nhập |
| Tab / Shift+Tab | Đi qua điều khiển theo thứ tự thị giác |
| Enter / Space | Kích hoạt điều khiển có tiêu điểm theo loại điều khiển |

Ctrl+Space hiện là phím cục bộ Workspace/bản mẫu; không chiếm nó trên toàn hệ thống vì có thể xung đột bộ gõ. Cho phép tùy chỉnh hoặc đổi phím cục bộ ở giai đoạn triển khai.

Chữ thông thường đạt tương phản tối thiểu 4,5:1 trên bề mặt sử dụng; tiêu điểm và dấu chọn đạt tối thiểu 3:1. Không dùng màu làm tín hiệu duy nhất; biểu tượng thao tác có tên đọc được, trang trí không đi vào cây tiếp cận. Hỗ trợ tăng chữ, tương phản cao của KDE, giảm chuyển động, bộ gõ và nội dung tiếng Việt dài. Không chặn chủ đề hỗ trợ tiếp cận của người dùng bằng màu cố định.

Bản mẫu là tài liệu xem thiết kế, chưa được nghiệm thu trình đọc màn hình cho toàn desktop. Bản triển khai cần thử bằng công cụ tiếp cận thực tế và bàn phím, không suy ra từ việc HTML có nhãn.

## 8. Ánh xạ triển khai và khoảng trống

| Thiết kế | Thành phần đích | Hiện có | Việc cần làm M1 |
|---|---|---|---|
| Ink/Paper | Bộ màu KDE, `kdeglobals` | Có bộ màu thử nghiệm | Đồng bộ giá trị ngữ nghĩa, kiểm tra tương phản trên KCM và ứng dụng |
| Fold | Chủ đề MyKOSFold | Có SVG và bí danh | Bổ sung ánh xạ cần thiết, thử chọn/không khả dụng và chủ đề tương phản cao |
| Hình nền | Trình chọn hình nền Plasma | Có SVG | Kiểm tra HiDPI, màn hình ngoài và cách chọn mặc định cho hồ sơ mới |
| Panel cạnh dưới | Plasma Panel, Task Manager, System Tray, Digital Clock | Đang dùng cấu hình Breeze gốc | Tạo bố cục khai báo chỉ áp dụng cho hồ sơ mới; kiểm thử không trùng panel |
| Menu ứng dụng | Kickoff và KRunner | Thành phần gốc có sẵn | Chốt ghim, vị trí, tìm kiếm và phím tắt |
| Thông báo | Plasma Notifications | Thành phần gốc | Đồng bộ màu, khoảng cách, thời gian và Không làm phiền |
| Đăng nhập | SDDM/Breeze | Mới chọn dịch vụ SDDM | Thử đăng nhập trước, cấu hình nhận diện sau; không sửa cơ chế xác thực |
| Khóa máy | Plasma Screen Locker | Chưa nghiệm thu | Kiểm tra khóa/mở và khác biệt với SDDM |
| Workspace | Qt 6/QML | Có bản native | Căn lại chữ/khoảng cách và trạng thái lỗi theo đặc tả |

Ưu tiên cấu hình, tài nguyên và phần mở rộng nhỏ. Không phân nhánh toàn bộ Plasma, viết lại KWin hoặc cài chủ đề không rõ nguồn. Các giá trị trong `tokens.json` là nguồn thiết kế; **chưa có cơ chế tự động đồng bộ chúng vào toàn bộ tài nguyên KDE**.

## 9. Áp dụng và phục hồi cấu hình

Hồ sơ mới nhận mặc định MyKOS theo cấu hình hệ thống. Hồ sơ đã tùy biến không bị ghi đè tự động sau cập nhật. Cần nút hoặc hướng dẫn “Khôi phục giao diện MyKOS” có xem trước phạm vi: màu, biểu tượng, panel và phím tắt liên quan.

Trước khi áp dụng, lưu các giá trị giao diện bị thay đổi để có thể hoàn nguyên. Không xóa toàn bộ `~/.config`, ghi chú, tài liệu, ứng dụng hoặc cấu hình không liên quan. Không khởi động lại SDDM trong phiên đang dùng. Thay đổi ảnh hưởng phiên phải được giải thích và chỉ thực hiện sau lựa chọn của người dùng. Bản mẫu “Đặt lại” chỉ đổi trạng thái trang xem thiết kế.

## 10. Thứ tự thực hiện

1. Chốt tài nguyên và giá trị dùng chung; rà soát khả năng tiếp cận.
2. Kiểm chứng phiên Plasma M0 rồi áp bộ màu/biểu tượng/hình nền trên hồ sơ thử mới.
3. Cấu hình panel, Kickoff và phím tắt; kiểm tra hồ sơ hiện có không bị thay đổi.
4. Đồng bộ Workspace; thử trạng thái rỗng, lỗi lưu, thiếu ứng dụng, tăng chữ.
5. Kiểm tra thông báo, khóa máy và nhận diện SDDM sau khi đăng nhập nền hoạt động.
6. Thử toàn bộ ma trận, sửa lỗi và ghi bằng chứng nghiệm thu.

## 11. Tiêu chí nghiệm thu M1

| Nhóm | Điều kiện đạt | Trạng thái |
|---|---|---|
| Nhận diện | Đăng nhập, khóa, desktop và thiết lập nhất quán; biểu tượng thiếu có dự phòng | CHƯA THỬ TRÊN KDE |
| Panel/menu | Mở/ghim/chuyển ứng dụng bằng chuột và bàn phím; không trùng panel | CHƯA THỬ TRÊN KDE |
| Cửa sổ | Di chuyển, thay cỡ, thu nhỏ, khôi phục, phóng to và Alt+Tab hoạt động | CHƯA THỬ TRÊN KDE |
| Tiếp cận | Hai bảng màu, tăng chữ, tiêu điểm, tương phản cao, giảm chuyển động và tiếng Việt | CHƯA NGHIỆM THU |
| Màn hình | 1366×768, 1920×1080, HiDPI và nhiều màn hình không mất điều khiển | CHƯA THỬ TRÊN KDE |
| Thông báo | Nguồn rõ, lỗi có hướng xử lý, Không làm phiền và lịch sử hoạt động | CHƯA THỬ TRÊN KDE |
| Cấu hình | Dựng lại từ repo, chỉ áp mặc định cho hồ sơ mới; khôi phục không mất dữ liệu | CHƯA THỬ TRÊN KDE |
| Độ ổn định | Không có lỗi chặn tác vụ, đăng nhập hoặc mất dữ liệu trong ma trận | CHƯA NGHIỆM THU |

Bản mẫu chỉ là bằng chứng về hướng thiết kế và tương tác trình duyệt. Hoàn thành đặc tả không có nghĩa hoàn thành M1 hoặc bỏ qua các tiêu chí M0 còn thiếu.
