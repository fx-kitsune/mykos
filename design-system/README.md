# Bộ thiết kế MyKOS

Thư mục chứa bộ biểu tượng MyKOS Fold 1.0 và bản mẫu tương tác MyKOS 0.2. Đây là tài nguyên nghiên cứu thiết kế và bản mẫu trình duyệt. Phần triển khai native sử dụng chúng được mô tả riêng trong [hướng dẫn giao diện](../desktop/README.md).

## Bộ thiết kế M1

[Bản thiết kế M1](m1/README.md) phiên bản 2.0 tập trung vào desktop tối giản, panel, menu và cửa sổ ứng dụng; có hai bảng màu Ink/Paper, ánh xạ KDE và tiêu chí nghiệm thu. Bố cục trang tổng quan M1 cũ đã được thay thế. Đây là bộ bàn giao thiết kế; chưa áp dụng toàn bộ vào ảnh hệ điều hành.

## Xem bản mẫu

Chạy từ thư mục gốc dự án:

```sh
python3 -m http.server 5174 --bind 127.0.0.1 --directory design-system
```

Mở [bản mẫu môi trường làm việc](http://127.0.0.1:5174/) hoặc [danh mục biểu tượng](http://127.0.0.1:5174/icons.html). Không cần cài npm. Nếu chạy ngay trong thư mục này, bỏ `--directory design-system`. Phông chữ lấy từ Google Fonts, có phông không chân cục bộ dự phòng.

## Nội dung

| Đường dẫn | Vai trò |
|---|---|
| `index.html`, `app.js`, `style.css` | Bản mẫu môi trường làm việc theo hoạt động |
| `icons.html`, `icons.css`, `icons.js` | Danh mục, biểu trưng ứng dụng và công cụ hiển thị SVG nội tuyến |
| `assets/icons/` | 40 biểu tượng SVG gốc trên lưới 24 đơn vị, tập biểu tượng có tên và quy chuẩn |
| `assets/app-icons/` | Sáu biểu trưng ứng dụng màu trên lưới 96 đơn vị |
| `tools/build-icons.cjs` | Hình học gốc và trình sinh tài nguyên có thể chạy lại |
| `mykos-fold-icons.zip` | Gói xuất biểu tượng và danh mục để chia sẻ |

Sinh lại tài nguyên bằng Node.js từ thư mục `design-system`:

```sh
node tools/build-icons.cjs
```

Lệnh này không tự cập nhật ZIP. Khi thay tài liệu hoặc trình sinh, cần cập nhật các mục tương ứng trong ZIP để nội dung chia sẻ nhất quán.

## Ngôn ngữ thiết kế

Nền xanh mực lì, điểm nhấn chanh, đường đồng mức và góc gấp nhỏ kết nối bản mẫu với biểu tượng Fold. Biểu tượng hệ thống dùng `viewBox` 24×24, nét 1,6 đơn vị, đầu nét và chỗ nối bo tròn, màu `currentColor`. Biểu trưng ứng dụng dùng chung hình học nhưng có màu chất liệu riêng. Xem [quy chuẩn biểu tượng](assets/icons/README.md).

Bản mẫu có ba không gian theo hoạt động, ghi chú riêng lưu bằng `localStorage`, tìm ứng dụng bằng Ctrl/Meta+Space, chế độ sáng/tối và đồng hồ tập trung 25 phút. Điều khiển kết nối, tệp, trình dòng lệnh và thư viện ảnh chỉ minh họa; không truy cập tệp hoặc thay thiết lập máy. Tìm web mở tab trình duyệt ngoài. Đồng hồ đặt lại khi tải lại trang.

## Kết quả kiểm tra đã ghi nhận

- Cú pháp JavaScript của ứng dụng, trình hiển thị và trình sinh.
- 47 SVG hợp lệ về XML: 40 biểu tượng, sáu biểu trưng và một tập biểu tượng.
- Hiển thị biểu tượng, cửa sổ động, tìm ứng dụng, ghi chú, tập trung và sáng/tối trong trình duyệt.
- Bố cục rộng và hẹp; những kiểm tra này không xác nhận tích hợp hệ điều hành.

## Ảnh tham khảo

![Bộ biểu tượng MyKOS Fold](mykos-fold-preview.jpg)

![Bản mẫu môi trường làm việc trước khi tích hợp Fold](mykos-preview.jpg)

## Triển khai native

[Phần tích hợp KDE](../desktop/README.md) đã sử dụng thiết kế này để tạo Workspace Qt 6/QML, bộ màu, chủ đề biểu tượng Fold có Breeze dự phòng và hình nền. Tệp trình duyệt vẫn là nguồn tham khảo thiết kế.

Từ thư mục gốc repo, chạy `python3 scripts/build/export-design.py` để xuất lại tài nguyên native. Tích hợp này không thay Plasma và không chứng minh ảnh hệ điều hành đã đạt nghiệm thu.
