# MyKOS Desktop

MyKOS có phiên desktop riêng, thay Plasma/KWin trong ảnh mặc định. Mã shell, panel và vòng đời phiên nằm trong repo; Openbox hiện là window manager X11 tạm thời. Qt/PyQt6 là bộ công cụ giao diện, không yêu cầu KDE Plasma.

- `session/session.py`: đặt môi trường MyKOS, sở hữu D-Bus riêng khi cần, giám sát Openbox/shell, dừng tiến trình do phiên tạo khi thoát. Không chạy bằng root.
- `shell/`: nền desktop, panel giữ chỗ theo EWMH, launcher cố định, danh sách cửa sổ, ba desktop ảo, đồng hồ, thiết lập sáng/tối và đăng xuất. Giao tiếp local socket chỉ trong runtime directory của người dùng.
- `workspace/`: ghi chú ba ngữ cảnh, tập trung 25 phút, trạng thái cục bộ. Ngữ cảnh ghi chú vẫn độc lập với desktop ảo.
- `integration/`: lệnh `mykos-session`, `mykos-shell`, `mykos-workspace` và mục XSession cho SDDM.
- `session/overlay`: chọn phiên MyKOS trong live SDDM, cấu hình portal GTK và mặc định greeter. Bản cài gỡ quyền sudo live, hook live và phần autologin.

Công cụ ảnh cài cả ba thành phần vào `/usr/share/mykos/`. Phiên đăng nhập có tên **MyKOS Desktop**. Không cần startplasma, plasmashell, KWin, D-Bus KDE Activities hoặc Discover. Installer Calamares vẫn dùng một số thư viện KDE Frameworks; chưa loại bỏ mọi thư viện xuất phát từ KDE.

## Phụ thuộc và chạy thử

Trên Debian 13, dùng các gói trong `distribution/packages/desktop.list.chroot`. Để thử giao diện không màn hình trong môi trường phát triển:

```sh
python3 -m venv work/de-venv
work/de-venv/bin/pip install -r desktop/workspace/requirements-dev.txt
mkdir -p work/runtime
chmod 700 work/runtime
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software \
  XDG_RUNTIME_DIR="$PWD/work/runtime" MYKOS_WORKSPACE_DATA="$PWD/work/state" \
  work/de-venv/bin/python desktop/shell/main.py --smoke-test
```

Để chạy phiên thật sau khi ảnh đã cài, chọn MyKOS Desktop từ SDDM. Không mở `mykos-session` bên trong desktop đang dùng; phiên cần X server riêng. Kiểm thử tự động bên dưới tự tạo Xvfb riêng.

```sh
python3 -m unittest discover -s tests/integration -v
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software \
  work/de-venv/bin/python -m unittest discover -s tests/desktop -v
python3 scripts/build/export-design.py --check
```

Kiểm thử X11 cần Xvfb, Openbox, wmctrl, x11-utils và dbus-daemon; nếu thiếu sẽ được báo skip. CI cài chúng để chạy kiểm thử phiên thật. Kiểm thử xác nhận loại cửa sổ desktop/dock, khoảng panel 56 px, IPC launcher/settings, cửa sổ ứng dụng, chuyển desktop và dừng shell khi đăng xuất.

## Tương tác

Panel mở ứng dụng, chuyển cửa sổ và chọn desktop 01–03. `Super+Space` mở launcher; `Super+Return` mở terminal; `Super+E` mở tệp; `Super+1/2/3` chuyển desktop; `Alt+Tab` chuyển cửa sổ. Các thao tác chạy argv cố định, không nội suy shell.

Thiết lập MyKOS đổi màu của shell/Workspace và mở nm-connection-editor, pavucontrol, arandr. Chúng làm việc với dịch vụ hệ thống thật, không giả lập trạng thái thiết bị. Dunst đảm nhiệm thông báo, lxpolkit đảm nhiệm hộp thoại xác thực và nm-applet cung cấp agent mật khẩu mạng. Chưa có system tray tích hợp trong panel.

`mykos-shell --check` trả JSON từ event loop của shell. `--show-launcher` và `--show-settings` gửi yêu cầu tới shell đang chạy trên cùng DISPLAY. `scripts/testing/probe_desktop.py` đã kiểm tra phản hồi này thay cho Plasma D-Bus.

## Giới hạn hiện tại

Đây là DE thử nghiệm X11 trên một màn hình chính, chưa phải bản ổn định. Đã render Qt và chạy phiên Openbox/Xvfb; chưa tạo, boot hoặc cài ISO mới. Chưa có compositor/Wayland riêng, khóa màn hình, chính sách idle/power, system tray, danh mục mọi ứng dụng `.desktop`, thông báo tự phát triển, khả năng tiếp cận hoàn chỉnh hoặc quản lý nhiều màn hình/hotplug. Các cửa sổ shell theo dõi thay đổi độ phân giải màn hình chính.

Trình quản lý phiên dọn các process group nó khởi tạo; ứng dụng tự daemon hóa hoặc chuyển sang dịch vụ D-Bus cần tích hợp vòng đời bổ sung. Workspace chạy độc lập vẫn cho ứng dụng được mở tiếp tục tồn tại khi đóng Workspace.

Các workflow chẩn đoán tải ISO Ubuntu/Plasma đã chốt và tự động click theo tọa độ cũ là công cụ lịch sử. Không dùng chúng để nghiệm thu desktop mới. Multimedia/Discover và quy trình click SDDM/Calamares cần được hiệu chỉnh theo ảnh mới trước khi công bố nghiệm thu.
