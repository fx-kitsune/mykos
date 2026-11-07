# MyKOS Fold 1.0

Bộ 40 biểu tượng SVG gốc cho thiết kế MyKOS. Hình học nguồn nằm trong `design-system/tools/build-icons.cjs`. Từ thư mục `design-system`, chạy `node tools/build-icons.cjs` để sinh lại tài nguyên và danh mục.

## Quy chuẩn hình học

- `viewBox`: `0 0 24 24`; vùng vẽ thông thường từ 2 đến 22.
- Độ dày nét: 1,6 đơn vị; đầu nét và chỗ nối bo tròn.
- Góc vát 2 đơn vị trên hình bao gợi lại dấu MyKOS. Không ép mọi biểu tượng có góc cắt nếu làm giảm khả năng nhận diện.
- Màu đơn dùng `currentColor`; nét cấu trúc phụ có độ đục 40%.
- Kích thước giao diện: 16/20/24/32; biểu trưng ứng dụng: 56/72/96. Co giãn nét cùng SVG; không kéo méo `viewBox` hoặc trộn độ dày nét.
- Màu mặc định, đang chọn và vô hiệu hóa lấy từ giao diện. Trạng thái vô hiệu hóa có độ đục 35%.
- Biểu trưng ứng dụng dùng khung vát góc, màu lì và hình học biểu tượng chung; không nhúng bóng đổ hoặc chuyển sắc.

## Tệp và khả năng tiếp cận

Mỗi biểu tượng nằm trong tệp `name.svg`; `sprite.svg` chứa các biểu tượng có tên. `../../icons.js` hiển thị SVG nội tuyến và `../../icons.html` là danh mục trực quan. Nút phải có nhãn hiển thị hoặc `aria-label`; SVG trang trí dùng `aria-hidden`.

## Dùng trong giao diện web

Sau khi nạp `icons.js`, gọi `icon('files')` để lấy SVG nội tuyến. Với tập biểu tượng:

```html
<svg><use href="assets/icons/sprite.svg#files" /></svg>
```

Ảnh SVG ngoài dùng qua `img` có ngữ cảnh `currentColor` riêng. Dùng SVG nội tuyến hoặc tập biểu tượng để màu thay đổi theo chủ đề giao diện.
