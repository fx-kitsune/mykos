import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

Window {
    id: desktop
    objectName: "mykosDesktop"
    title: "MyKOS Desktop"
    visible: false
    color: dark ? "#171c19" : "#eeefe6"
    property bool dark: workspace.theme === "dark"
    property color ink: dark ? "#edf0e7" : "#293323"
    property color muted: dark ? "#9aa598" : "#6a7761"
    property color surface: dark ? "#202722" : "#f7f8f0"
    property color lime: dark ? "#d7ef83" : "#526a2b"
    property color line: dark ? "#354039" : "#d2d8c9"
    property string clock: Qt.formatTime(new Date(), "hh:mm")
    property string message: ""
    property var apps: [
        {label:"Tệp của bạn", app:"files"}, {label:"Terminal", app:"terminal"},
        {label:"Workspace · Ghi chú", app:"workspace"}, {label:"Soạn thảo", app:"notes"},
        {label:"Hình ảnh", app:"photos"}, {label:"Cài đặt MyKOS", app:"install"}
    ]
    Timer { interval: 1000; repeat: true; running: true; onTriggered: desktop.clock = Qt.formatTime(new Date(), "hh:mm") }
    Connections {
        target: workspace
        function onNotice(text) { desktop.message = text; toast.restart() }
    }
    Timer { id: toast; interval: 6000; onTriggered: desktop.message = "" }
    Column {
        anchors.centerIn: parent; spacing: 20
        Image { anchors.horizontalCenter: parent.horizontalCenter; source: workspace.icon(desktop.dark ? "mark-dark" : "mark-light"); sourceSize.width: 100; sourceSize.height: 100; width: 100; height: 100 }
        Text { anchors.horizontalCenter: parent.horizontalCenter; text: "mykos"; color: desktop.ink; font.family: "Noto Sans"; font.pixelSize: 48; font.letterSpacing: 4 }
        Text { anchors.horizontalCenter: parent.horizontalCenter; text: "CÓ NHỊP CỦA RIÊNG MÌNH"; color: desktop.muted; font.pixelSize: 11; font.letterSpacing: 3 }
    }
    Text { anchors.right: parent.right; anchors.bottom: parent.bottom; anchors.margins: 84; text: "MyKOS Desktop / Phiên phát triển"; color: desktop.muted; font.pixelSize: 11 }

    component FoldButton: Button {
        id: button
        implicitHeight: 38
        hoverEnabled: true
        Accessible.name: text
        contentItem: Text { text: button.text; color: desktop.ink; font.pixelSize: 12; elide: Text.ElideRight; verticalAlignment: Text.AlignVCenter; horizontalAlignment: Text.AlignHCenter }
        background: Rectangle { color: button.down || button.hovered ? desktop.line : desktop.surface; radius: 4; border.color: button.activeFocus ? desktop.lime : desktop.line }
    }

    Window {
        id: panel
        objectName: "mykosPanel"
        title: "MyKOS Panel"
        visible: false
        color: desktop.surface
        function openLauncher() { launcher.settingsMode = false; launcher.show(); launcher.requestActivate(); search.forceActiveFocus() }
        function openSettings() { launcher.settingsMode = true; launcher.show(); launcher.requestActivate() }
        RowLayout {
            anchors.fill: parent; anchors.margins: 8; spacing: 8
            FoldButton { text: "mykos  /  Ứng dụng"; Layout.preferredWidth: 148; onClicked: panel.openLauncher() }
            Repeater {
                model: ["01", "02", "03"]
                FoldButton { text: modelData; Layout.preferredWidth: 36; onClicked: workspace.switchDesktop(index) }
            }
            Rectangle { width: 1; Layout.fillHeight: true; color: desktop.line }
            ListView {
                Layout.fillWidth: true; Layout.fillHeight: true
                orientation: ListView.Horizontal; spacing: 6; clip: true
                model: workspace.windows
                delegate: FoldButton { required property var modelData; text: modelData.title; width: 160; height: 38; onClicked: workspace.activate(modelData.id) }
            }
            FoldButton { text: "Thiết lập"; Layout.preferredWidth: 86; onClicked: panel.openSettings() }
            Text { text: desktop.clock; color: desktop.ink; font.family: "monospace"; font.pixelSize: 15; Layout.leftMargin: 12; Layout.rightMargin: 12 }
        }
    }

    Window {
        id: launcher
        objectName: "mykosLauncher"
        property bool settingsMode: false
        title: settingsMode ? "Thiết lập MyKOS" : "Ứng dụng MyKOS"
        width: 560; height: 500
        x: desktop.x + Math.max(0, (desktop.width - width) / 2)
        y: desktop.y + Math.max(0, desktop.height - height - 72)
        flags: Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        color: desktop.surface
        visible: false
        Shortcut { sequence: "Escape"; onActivated: launcher.hide() }
        ColumnLayout {
            anchors.fill: parent; anchors.margins: 26; spacing: 14
            RowLayout {
                Text { text: launcher.title; color: desktop.ink; font.pixelSize: 24; Layout.fillWidth: true }
                FoldButton { text: "Đóng"; onClicked: launcher.hide() }
            }
            Text { text: "MYKOS DESKTOP"; color: desktop.muted; font.letterSpacing: 2; font.pixelSize: 10 }
            TextField {
                id: search; objectName: "shellSearch"
                visible: !launcher.settingsMode
                Layout.fillWidth: true; placeholderText: "Tìm công cụ…"; color: desktop.ink
                background: Rectangle { color: desktop.dark ? "#171c19" : "#eeefe6"; border.color: desktop.lime; radius: 4 }
                onAccepted: {
                    for (var i = 0; i < desktop.apps.length; i++) {
                        if (desktop.apps[i].label.toLowerCase().indexOf(text.toLowerCase()) >= 0) {
                            workspace.launch(desktop.apps[i].app); launcher.hide(); break
                        }
                    }
                }
            }
            ScrollView {
                id: appScroll
                visible: !launcher.settingsMode
                Layout.fillWidth: true; Layout.fillHeight: true; clip: true
                Column {
                    width: appScroll.availableWidth; spacing: 8
                    Repeater {
                        model: desktop.apps
                        delegate: FoldButton {
                            text: modelData.label; width: appScroll.availableWidth
                            visible: modelData.label.toLowerCase().indexOf(search.text.toLowerCase()) >= 0
                            onClicked: { workspace.launch(modelData.app); launcher.hide() }
                        }
                    }
                }
            }
            ColumnLayout {
                visible: launcher.settingsMode; Layout.fillWidth: true; spacing: 12
                FoldButton { text: desktop.dark ? "Chuyển sang giao diện sáng" : "Chuyển sang giao diện tối"; Layout.fillWidth: true; onClicked: workspace.toggleTheme() }
                Repeater {
                    model: [{label:"Mạng", name:"network"}, {label:"Âm thanh", name:"audio"}, {label:"Màn hình", name:"display"}]
                    FoldButton { text: modelData.label; Layout.fillWidth: true; onClicked: workspace.openSetting(modelData.name) }
                }
                FoldButton { text: "Đăng xuất phiên MyKOS"; Layout.fillWidth: true; onClicked: workspace.logout() }
            }
            Item { Layout.fillHeight: true }
            Text { text: "Super + Space · Ứng dụng     Alt + Tab · Cửa sổ"; color: desktop.muted; font.pixelSize: 10 }
        }
    }
    Window {
        title: "Thông báo MyKOS"; width: 500; height: 70
        x: desktop.x + (desktop.width - width) / 2; y: desktop.y + 30
        visible: desktop.message !== ""
        flags: Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowDoesNotAcceptFocus
        color: desktop.lime
        Text { anchors.fill: parent; anchors.margins: 14; text: desktop.message; color: desktop.dark ? "#171c19" : "white"; wrapMode: Text.Wrap; verticalAlignment: Text.AlignVCenter }
    }
}
