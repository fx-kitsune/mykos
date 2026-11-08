// Chỉ tạo bố cục khi hồ sơ chưa có panel. Không tạo cửa sổ hay chạy ứng dụng.
if (panels().length === 0) {
    var workspaceDesktops = desktopsForActivity(currentActivity());
    for (var i = 0; i < workspaceDesktops.length; i++) {
        var desktop = workspaceDesktops[i];
        desktop.wallpaperPlugin = "org.kde.image";
        desktop.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
        desktop.writeConfig("Image", "file:///usr/share/wallpapers/MyKOS/contents/images/1920x1080.svg");
    }
    var panel = new Panel;
    panel.location = 'bottom';
    panel.height = 48;
    var launcher = panel.addWidget('org.kde.plasma.kickoff');
    launcher.currentConfigGroup = ['General'];
    launcher.writeConfig('icon', 'start-here-mykos');
    var tasks = panel.addWidget('org.kde.plasma.icontasks');
    tasks.currentConfigGroup = ['General'];
    // Chỉ ghim ứng dụng đã có trong danh sách gói, không ghim trình duyệt chưa cài.
    tasks.writeConfig('launchers', ['applications:org.kde.dolphin.desktop']);
    panel.addWidget('org.kde.plasma.systemtray');
    panel.addWidget('org.kde.plasma.digitalclock');
    panel.addWidget('org.kde.plasma.showdesktop');
}
