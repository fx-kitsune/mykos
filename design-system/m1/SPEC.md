# MyKOS M1 — Desktop và thao tác hệ thống

- Phiên bản thiết kế: 2.0, ngày 08/11/2026.
- Trạng thái: Đề xuất triển khai KDE; chưa nghiệm thu M1.
- Nguồn: [Tầm nhìn sản phẩm](../../docs/PRODUCT_VISION.md), bộ biểu tượng Fold và KDE Plasma.
- Thay thế: Bản M1 đặt Workspace, câu chào và thẻ nội dung ở trung tâm desktop.

## 1. Nguyên tắc

Desktop là nơi mở ứng dụng và quản lý cửa sổ. Mặc định chỉ có hình nền và thanh tác vụ. Không có khẩu hiệu, nội dung giới thiệu, thẻ dự án, bảng điều khiển hoặc ứng dụng tự mở chỉ để lấp chỗ trống.

Fold chỉ xác định màu, biểu tượng, hình học và chất liệu. Không sao chép bố cục bản concept thành bố cục hệ điều hành. Chữ chỉ xuất hiện để đặt tên điều khiển, nội dung, trạng thái hoặc lỗi liên quan tới thao tác hiện tại.

Workspace là ứng dụng tùy chọn, không tự khởi chạy, không đại diện cho desktop và không thay KDE Activities hoặc màn hình ảo. Bản native hiện có của Workspace chưa được thiết kế lại trong thay đổi này.

## 2. Desktop mặc định

Hình nền xanh mực hoặc nền sáng trung tính, hình học gấp nhẹ, không chữ. Một panel cạnh dưới cao 48 đơn vị logic, sát mép màn hình, không tạo khung nổi giống thanh điều hướng website.

Thứ tự panel: mở ứng dụng → ứng dụng ghim/đang chạy → khoảng trống → khay hệ thống → ngày giờ → hiện desktop. Ghim Tệp, trình duyệt đã có trong ảnh và Thiết lập. Nếu chưa có trình duyệt trong ảnh, không ghim một nút hỏng.

Ứng dụng đang chạy có gạch nhỏ; cửa sổ được chọn có cả nền và gạch nhấn. Không hiển thị “đang kết nối”, phần trăm pin hoặc cập nhật nếu chưa có dữ liệu thật. Nút khay hệ thống có tên đọc được, không cần nhãn chữ luôn hiện.

Không đặt icon tệp hoặc tiện ích lên desktop theo mặc định. Người dùng có thể thêm qua công cụ KDE.

## 3. Menu ứng dụng

Mở từ biểu tượng MyKOS ở góc trái dưới. Menu neo ngay trên panel, ô tìm kiếm ở đầu, ứng dụng ghim hoặc danh sách đầy đủ ở giữa, tài khoản và thao tác phiên ở cuối. Không có câu chào, thẻ giới thiệu hoặc gợi ý quảng bá.

Nhập để tìm theo tên tiếng Việt/tên gốc, có hoặc không dấu. Enter mở kết quả đầu; Escape đóng và trả tiêu điểm về vị trí gọi menu. Không có kết quả thì giữ truy vấn và hiện “Không tìm thấy ứng dụng”. Bản triển khai dùng Kickoff/KRunner và danh sách ứng dụng thực sự đã cài.

Các nút nguồn, khóa và đăng xuất phải đi qua cơ chế phiên/cấp quyền của KDE. Không thực thi lệnh quản trị tùy ý từ giao diện.

## 4. Cửa sổ và trình quản lý tệp

Giữ trang trí cửa sổ KWin: tiêu đề nhỏ, thu nhỏ, phóng to/khôi phục và đóng. Nội dung chính chiếm phần lớn diện tích. Không đặt câu chào hoặc dấu thương hiệu lớn bên trong ứng dụng.

Trình quản lý tệp dùng Dolphin. Bố cục tham chiếu: thanh công cụ và đường dẫn ở trên; vị trí ở trái; danh sách hoặc lưới tệp ở giữa; số mục ở thanh trạng thái. Tên, loại và kích thước là dữ liệu hữu ích. Trạng thái rỗng chỉ ghi “Thư mục trống”; tìm không có kết quả dùng thông báo tương ứng.

Mật độ mặc định vừa phải: nội dung 14, nhãn phụ 12; hàng tệp khoảng 40 đơn vị logic. Không mở rộng chữ hoặc khoảng cách kiểu trang giới thiệu. Người dùng được đổi chế độ danh sách/lưới qua Dolphin.

Alt+Tab, kéo cửa sổ, thay kích thước, thu nhỏ và khôi phục tuân theo KWin. Bản mẫu hỗ trợ kéo, thay cỡ, thu nhỏ và phóng to một cửa sổ minh họa; không phải trình quản lý đa cửa sổ thật.

## 5. Thiết lập

Dùng các trang KDE hiện có. Trang giao diện chỉ chứa lựa chọn đang cần: sáng/tối, biểu tượng, chữ và giảm chuyển động. Nhóm thiết lập ở trái, giá trị và điều khiển ở phải. Không đặt nội dung giới thiệu hoặc lặp lại thông tin đã có trong nhãn.

Áp dụng màu toàn desktop phải là lựa chọn rõ ràng ở thiết lập KDE. Chế độ sáng/tối của Workspace hiện chỉ tác động riêng ứng dụng và không được mô tả là thay giao diện toàn hệ thống.

## 6. Khay hệ thống, thông báo và đăng nhập

Thông báo mặc định rỗng: “Không có thông báo”. Chỉ tạo mục khi có sự kiện thực tế. Thông báo lỗi gồm việc chưa hoàn tất và hướng xử lý, không dùng thẻ minh họa để lấp bảng. Dùng Plasma Notifications và System Tray.

Điều khiển âm lượng nằm trong bảng nhỏ mở từ biểu tượng loa. Mạng, pin và Bluetooth chỉ xuất hiện theo thiết bị/dịch vụ có thật. Các phần trăm trong bản mẫu là giá trị minh họa, không đọc hoặc thay đổi máy.

Đăng nhập: tài khoản, trường mật khẩu, hành động đăng nhập và lỗi khi cần. Không có khẩu hiệu. Dùng SDDM/Breeze cho đăng nhập, Plasma Screen Locker cho khóa máy; không tự viết bộ xác thực. Mật khẩu không xuất hiện trong nhật ký. Bản mẫu không xác thực, không gửi và xóa trường sau thao tác đăng nhập.

## 7. Màu, chữ và khả năng tiếp cận

Giữ bảng Ink/Paper trong [tokens.json](tokens.json), dùng Noto Sans ngoại tuyến. Màu nhấn dùng cho tiêu điểm/chọn và hành động, không phủ mọi bề mặt. Thứ bậc chữ chính/phụ đủ rõ, không ép người dùng đọc nhãn trang trí cỡ nhỏ.

- Chữ thông thường đạt tương phản tối thiểu 4,5:1 trên bề mặt sử dụng.
- Dấu tiêu điểm nhìn thấy rõ, không chỉ biểu đạt bằng màu.
- Tab/Shift+Tab theo thứ tự thao tác; Enter/Space kích hoạt theo loại điều khiển.
- Meta mở menu, Alt+Space mở KRunner, Alt+Tab chuyển cửa sổ, Meta+L khóa theo cấu hình KDE được kiểm thử.
- Không chiếm Ctrl+Space toàn hệ thống vì có thể xung đột bộ gõ. Trong bản mẫu, phím này chỉ mở menu khi trang có tiêu điểm.
- Tôn trọng tăng chữ, giảm chuyển động và chủ đề tương phản cao của KDE.
- HiDPI dùng đơn vị logic; kiểm tra 1366×768, 1920×1080, 125/150/200% và nhiều màn hình.

Khung xem hẹp của bản mẫu chỉ phục vụ rà soát; không cam kết hệ điều hành cho điện thoại.

## 8. Ánh xạ triển khai

| Phần | Thành phần KDE | Hướng thực hiện |
|---|---|---|
| Panel | Plasma Panel, Task Manager, System Tray, Digital Clock | Một panel dưới, 48 đơn vị logic, hồ sơ mới |
| Menu | Kickoff/KRunner | Danh sách ứng dụng thật, ghim gọn, phím tắt chuẩn |
| Cửa sổ | KWin/Breeze | Giữ thao tác và trang trí gốc, chỉnh nhận diện vừa đủ |
| Tệp | Dolphin | Cấu hình mặc định có mật độ phù hợp, không viết trình quản lý tệp mới |
| Thiết lập | Các KCM gốc | Bộ màu, icon và chữ thống nhất |
| Thông báo/âm lượng | Plasma và dịch vụ hệ thống | Dữ liệu thật, không mô phỏng trạng thái thiết bị |
| Đăng nhập/khóa | SDDM và Plasma Screen Locker | Nhận diện tối giản, giữ xác thực gốc |
| Workspace | Ứng dụng Qt/QML riêng | Tùy chọn, không tự mở cùng phiên |

Gói `org.mykos.desktop` đã được thêm vào lớp cấu hình ảnh, đặt panel cạnh dưới và chỉ chạy nhánh tạo bố cục khi chưa có panel. Tài nguyên KDE hiện chỉ ghim Dolphin; trình duyệt và Thiết lập trong ảnh tham chiếu chưa được ghim vào cấu hình thật khi chưa đối chiếu định danh ứng dụng. Hình nền tối đã thay bằng hình học gấp không chữ. Chưa tạo ISO mới để kiểm chứng bố cục; đây vẫn là thay đổi cấu hình chờ nghiệm thu. Bản mẫu trình duyệt không thay Dolphin hoặc SDDM bằng ứng dụng web.

## 9. Áp dụng, phục hồi và nghiệm thu

Mặc định chỉ áp cho hồ sơ mới; không ghi đè tùy biến của hồ sơ hiện có sau cập nhật. Khi có thao tác khôi phục giao diện MyKOS, giải thích phạm vi và lưu giá trị cần hoàn nguyên. Không xóa toàn bộ `~/.config`, tài liệu hoặc ghi chú. Không khởi động lại SDDM trong phiên đang dùng.

M1 chỉ đạt khi bản KDE thực tế có nhận diện nhất quán, menu/panel/cửa sổ hoạt động bằng chuột và bàn phím, đủ tương phản và khả năng tiếp cận, không lỗi ở ma trận màn hình, cấu hình dựng lại được và hoàn nguyên không mất dữ liệu.

Hiện mới có thiết kế, bản mẫu và kiểm tra trình duyệt. Chưa nghiệm thu M1; các điều kiện M0 còn thiếu vẫn giữ nguyên. Thứ tự tiếp theo: xác nhận phiên Plasma → cấu hình hồ sơ KDE thử → kiểm tra panel/menu/Dolphin → đồng bộ nhận diện → đăng nhập/khóa → nghiệm thu.
