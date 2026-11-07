# Triển khai giao diện Fold bằng Qt/QML

Nguồn định hướng thị giác nằm trong `design-system/`. Phần này hiện thực thiết kế bằng **ứng dụng đồng hành Qt 6/QML không đặc quyền** và tài nguyên nhận diện KDE. Plasma, KWin và KDE Activities vẫn là thành phần của hệ thống gốc.

## Chạy và kiểm thử

Trên Ubuntu Noble, cài `python3-pyqt6`, `python3-pyqt6.qtquick`, `python3-pyqt6.qtsvg` cùng các gói `qml6-module-*` được liệt kê trong danh sách gói ảnh hệ thống. Sau đó chạy `python3 desktop/workspace/main.py` từ thư mục gốc dự án.

Để phát triển trong môi trường Python riêng trên Linux khác:

```sh
python3 -m venv /tmp/mykos-workspace-venv
/tmp/mykos-workspace-venv/bin/pip install -r desktop/workspace/requirements-dev.txt
/tmp/mykos-workspace-venv/bin/python desktop/workspace/main.py
```

Kiểm thử không cần màn hình:

```sh
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software \
  /tmp/mykos-workspace-venv/bin/python -m unittest discover -s tests/desktop -v
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software \
  MYKOS_WORKSPACE_DATA=/tmp/mykos-smoke \
  MYKOS_SCREENSHOT=/tmp/mykos-workspace.png \
  /tmp/mykos-workspace-venv/bin/python desktop/workspace/main.py --smoke-test
```

Cờ `--smoke-test` thoát sau khi render mẫu giao diện; không xác nhận môi trường làm việc đã cài đặt hoạt động. Các kiểm thử native còn kiểm tra tương tác, ghi chú, hai chế độ màu, kích thước 900×700, báo lỗi và ranh giới mở ứng dụng.

## Tương tác đã hoạt động

- Ba ngữ cảnh ghi chú có tên; lưu Unicode bằng thay thế tệp nguyên tử, chỉ chủ sở hữu có quyền truy cập tệp, trong AppDataLocation của Qt (`MyKOS/Workspace`).
- Đợi 350 ms sau thay đổi trước khi lưu và lưu lần cuối khi thoát; báo lỗi nếu không ghi được.
- Ghi nhớ chế độ sáng/tối riêng của Workspace giữa các lần mở.
- Đồng hồ tập trung 25 phút tính theo thời gian thực; đặt lại khi thoát ứng dụng.
- Ctrl+Space tìm ứng dụng khi Workspace đang được chọn; Escape đóng bảng tìm kiếm.
- Mở Dolphin, Konsole, System Settings, Discover, Kate và Gwenview qua thao tác định sẵn. Báo lỗi nếu thiếu ứng dụng; không nội suy lệnh shell, chạy lệnh root, gửi yêu cầu mạng hoặc giả lập bật/tắt kết nối.

`MYKOS_WORKSPACE_DATA` thay thư mục dữ liệu cục bộ cho phát triển/kiểm thử. Tìm kiếm hiện chỉ bao phủ sáu thao tác mở ứng dụng đã tích hợp, chưa liệt kê mọi ứng dụng cài trên máy. Ba ngữ cảnh chưa phải màn hình ảo, KDE Activities hoặc ba thư mục riêng.

## Tích hợp KDE

`distribution/branding/overlay` cài bộ màu MyKOS Ink/Paper, chủ đề biểu tượng MyKOSFold có Breeze/hicolor dự phòng và hình nền SVG gốc. Hồ sơ KDE mới kế thừa MyKOSDark/MyKOSFold qua `/etc/xdg/kdeglobals`; cấu hình riêng của người dùng được ưu tiên. Hình nền có thể chọn qua trình chọn KDE và không bị ép áp dụng vào màn hình hiện có. Bố cục Plasma, màn hình chờ khởi động và trang trí cửa sổ vẫn dùng Breeze gốc.

Công cụ tạo ảnh đặt ứng dụng ở `/usr/share/mykos/workspace`, lệnh mở ở `/usr/bin/mykos-workspace` và mục ứng dụng trong menu. Không tự khởi chạy Workspace hoặc đăng ký phiên làm việc thay thế.

## Xuất tài nguyên thiết kế

```sh
python3 scripts/build/export-design.py
python3 scripts/build/export-design.py --check
```

Tài nguyên thiết kế gốc không bị thay đổi. Công cụ chuyển các khung SVG lồng nhau thành phép biến đổi tương đương vì Qt SVG Tiny bỏ qua `<svg>` lồng nhau. Biểu tượng đã xuất được lưu trong repo nên bước đưa nhận diện vào ISO không cần Node.js hoặc truy cập mạng. Bí danh ứng dụng KDE bao phủ sáu biểu trưng; biểu tượng thiếu dùng Breeze. Trình sinh gốc ở `design-system/tools/`.

Môi trường đã kiểm thử dùng PyQt 6.7/Qt 6.7 không màn hình. Khả dụng của các mô-đun trong kho Ubuntu được kiểm tra riêng. Giải quyết phụ thuộc toàn ảnh, hiển thị chủ đề Plasma, tích hợp Wayland và phần cứng thật vẫn là điều kiện nghiệm thu M0/M1.
