# ADR 0004 — Desktop environment riêng của MyKOS

Trạng thái: triển khai thử nghiệm, chưa nghiệm thu ISO. Ngày: 2026-11-10. Thay thế hướng tích hợp Plasma của ADR 0002; giữ nền Debian tạm theo ADR 0003.

## Quyết định

MyKOS sở hữu desktop shell, panel, launcher, thiết lập giao diện và trình quản lý phiên. Bỏ Plasma/KWin, Activities, Discover và overlay KDE khỏi ảnh mặc định. Phiên được đăng ký dưới tên MyKOS Desktop, chạy bằng tài khoản thường qua SDDM.

Dùng Openbox làm window manager X11 tạm thời để có di chuyển/resize/maximize cửa sổ, phím tắt và desktop ảo thực sự. Đây không phải compositor riêng; không gọi việc thay panel là đã viết xong toàn bộ graphics stack. Qt/QML và Python hiện thực shell; EWMH kết nối window manager qua xprop/wmctrl. Không đổi tên Openbox thành thành phần tự viết.

Giữ SDDM, Dunst, lxpolkit, NetworkManager/PipeWire và portal GTK như các thành phần độc lập. Các ứng dụng tệp/terminal/soạn thảo/hình ảnh thay bằng Thunar, xfce4-terminal, Mousepad và Ristretto; không cài toàn bộ XFCE. Calamares còn phụ thuộc KDE Frameworks, nhưng phiên desktop không dùng Plasma/KWin.

## Vòng đời và ranh giới

Session manager đặt XDG_CURRENT_DESKTOP=MyKOS, theo dõi tiến trình cốt lõi, kết thúc phiên nếu shell/WM thoát, và dọn process group do nó tạo. D-Bus riêng khi cần cũng được sở hữu và dọn, tránh orphan khi logout. Shell chạy không đặc quyền; IPC chỉ dùng socket trong XDG_RUNTIME_DIR của chính người dùng. Launcher dùng argv cố định. Live autologin và sudo được gỡ khỏi bản cài.

## Kiểm chứng và lộ trình

Đã có kiểm thử phiên thật trên Xvfb/Openbox: desktop/dock EWMH, strut, launcher/settings IPC, ứng dụng, desktop ảo và logout. Chưa nghiệm thu trên ISO, GPU hay phần cứng thật.

Tiếp theo: nghiệm thu ảnh mới, taskbar/launcher đầy đủ và tray, locking/power/accessibility, notification service và settings API riêng. Sau đó đánh giá compositor Wayland dựa trên thư viện như wlroots/Smithay, với kiểm thử đầu vào, đầu ra, clipboard, screencast, XWayland và bảo mật session lock. Không bỏ WM X11 đang dùng trước khi các điều kiện này được kiểm chứng.
