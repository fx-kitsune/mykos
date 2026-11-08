// Chỉ tạo bố cục khi hồ sơ chưa có panel. Không tạo cửa sổ hay chạy ứng dụng.
if (panels().length === 0) {
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
