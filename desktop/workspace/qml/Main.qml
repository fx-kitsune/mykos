import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: root
    width: 1240; height: 820
    minimumWidth: 900; minimumHeight: 700
    visible: true
    title: "MyKOS Workspace"
    property bool dark: workspace.theme === "dark"
    property color paper: dark ? "#171c19" : "#eeefe6"
    property color surface: dark ? "#202722" : "#f7f8f0"
    property color ink: dark ? "#edf0e7" : "#293323"
    property color muted: dark ? "#9aa598" : "#6a7761"
    property color lime: dark ? "#d7ef83" : "#526a2b"
    property color line: dark ? "#354039" : "#d2d8c9"
    property int spaceIndex: 0
    property var spaces: ["personal", "creative", "development"]
    property var names: ["Cá nhân", "Sáng tạo", "Lập trình"]
    property var headings: ["Chừa chỗ cho", "Để ý tưởng", "Từ dòng đầu tiên"]
    property var subheadings: ["điều bạn muốn làm.", "tìm thấy hình hài.", "đến điều tiếp theo."]
    property var projects: ["Một ý tưởng mới", "Xưởng ý tưởng", "Dự án tiếp theo"]
    property double focusEnd: 0
    property int remaining: 0
    property string clock: Qt.formatTime(new Date(), "hh:mm")
    property string message: ""
    color: paper
    font.family: "Noto Sans"
    font.pixelSize: 13

    function switchSpace(index) {
        spaceIndex = index
        note.text = workspace.note(spaces[index])
    }
    function focusLabel() {
        return ("0" + Math.floor(remaining / 60)).slice(-2) + ":" + ("0" + remaining % 60).slice(-2)
    }
    Component.onCompleted: note.text = workspace.note(spaces[0])
    Connections {
        target: workspace
        function onNotice(text) { root.message = text; toastTimer.restart() }
    }
    Timer { id: toastTimer; interval: 5000; onTriggered: root.message = "" }
    Timer {
        interval: 1000; running: true; repeat: true
        onTriggered: {
            root.clock = Qt.formatTime(new Date(), "hh:mm")
            if (root.focusEnd > 0) {
                root.remaining = Math.max(0, Math.ceil((root.focusEnd - Date.now()) / 1000))
                if (root.remaining === 0) {
                    root.focusEnd = 0
                    root.message = "Đã hoàn thành một nhịp. Nghỉ một chút nhé."
                    toastTimer.restart()
                }
            }
        }
    }
    Shortcut { sequence: "Ctrl+Space"; onActivated: { searchPopup.open(); search.forceActiveFocus() } }
    Shortcut { sequence: "Escape"; onActivated: searchPopup.close() }

    component FoldButton: Button {
        id: control
        property string asset: ""
        implicitHeight: 48
        hoverEnabled: true
        Accessible.name: text
        contentItem: RowLayout {
            spacing: 12
            Image { visible: control.asset !== ""; source: workspace.icon(control.asset); sourceSize.width: 32; sourceSize.height: 32; Layout.preferredWidth: 32; Layout.preferredHeight: 32 }
            Text { text: control.text; color: root.ink; font: control.font; Layout.fillWidth: true }
        }
        background: Rectangle { color: control.down ? root.line : root.surface; radius: 5; border.width: control.activeFocus || control.hovered ? 2 : 1; border.color: control.activeFocus || control.hovered ? root.lime : root.line }
        leftPadding: 15; rightPadding: 15
    }

    Rectangle {
        id: rail
        width: 78; anchors.top: parent.top; anchors.bottom: parent.bottom
        color: root.dark ? "#111713" : "#e2e6d8"
        ColumnLayout {
            anchors.fill: parent; anchors.margins: 12; spacing: 16
            Image { source: workspace.icon(root.dark ? "mark-dark" : "mark-light"); Layout.preferredWidth: 36; Layout.preferredHeight: 36; Layout.alignment: Qt.AlignHCenter; Layout.topMargin: 12 }
            Rectangle { color: root.line; Layout.fillWidth: true; height: 1; Layout.topMargin: 10; Layout.bottomMargin: 10 }
            Repeater {
                model: [{label:"Tệp", app:"files"}, {label:"Terminal", app:"terminal"}, {label:"Thiết lập", app:"settings"}]
                delegate: Button {
                    Layout.fillWidth: true; implicitHeight: 48
                    Accessible.name: modelData.label
                    ToolTip.visible: hovered; ToolTip.text: modelData.label
                    contentItem: Image { source: workspace.icon(modelData.app); fillMode: Image.PreserveAspectFit; sourceSize.width: 32; sourceSize.height: 32 }
                    background: Rectangle { radius: 4; color: parent.hovered || parent.activeFocus ? root.line : "transparent"; border.color: parent.activeFocus ? root.lime : "transparent" }
                    onClicked: workspace.launch(modelData.app)
                }
            }
            Item { Layout.fillHeight: true }
            FoldButton { leftPadding: 5; rightPadding: 5; text: root.dark ? "Sáng" : "Tối"; Accessible.name: "Đổi sáng / tối trong Workspace"; Layout.fillWidth: true; onClicked: workspace.toggleTheme() }
        }
    }

    ColumnLayout {
        anchors.left: rail.right; anchors.right: parent.right; anchors.top: parent.top; anchors.bottom: parent.bottom
        anchors.leftMargin: 42; anchors.rightMargin: 42; anchors.topMargin: 24; anchors.bottomMargin: 22; spacing: 20
        RowLayout {
            Layout.fillWidth: true
            Text { text: "mykos<span style='color:" + root.muted + "'> / workspace</span>"; textFormat: Text.RichText; color: root.ink; font.pixelSize: 19 }
            Item { Layout.fillWidth: true }
            Text { text: "CÙNG MỘT NHỊP CỦA BẠN"; color: root.muted; font.pixelSize: 10; font.letterSpacing: 1.5 }
            Text { text: root.clock; color: root.ink; font.family: "monospace"; Layout.leftMargin: 24 }
        }
        Rectangle { Layout.fillWidth: true; height: 1; color: root.line }
        RowLayout {
            spacing: 10
            Repeater {
                model: root.names
                delegate: FoldButton { text: "0" + (index + 1) + "   " + modelData; onClicked: root.switchSpace(index); background: Rectangle { color: root.spaceIndex === index ? root.surface : "transparent"; radius: 4; border.color: root.spaceIndex === index ? root.lime : root.line; border.width: 1 } }
            }
            Item { Layout.fillWidth: true }
        }
        RowLayout {
            Layout.fillWidth: true; Layout.topMargin: 12; Layout.bottomMargin: 8
            ColumnLayout {
                spacing: 6
                Text { text: "KHÔNG GIAN / 0" + (root.spaceIndex + 1); color: root.muted; font.pixelSize: 10; font.letterSpacing: 2; bottomPadding: 12 }
                Text { text: root.headings[root.spaceIndex]; color: root.ink; font.pixelSize: 38; font.weight: Font.Medium }
                Text { text: root.subheadings[root.spaceIndex]; color: root.lime; font.pixelSize: 38; font.weight: Font.Medium }
                Text { text: "Tệp, ý tưởng và công cụ. Cùng một nhịp của bạn."; color: root.muted; topPadding: 10 }
            }
            Item { Layout.fillWidth: true }
            FoldButton { text: "Tìm ứng dụng   Ctrl + Space"; Layout.preferredWidth: 260; onClicked: { searchPopup.open(); search.forceActiveFocus() } }
        }
        Text { text: "Tiếp nối điều đang làm"; color: root.ink; font.pixelSize: 14 }
        RowLayout {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 18
            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true; Layout.preferredWidth: 520
                color: root.dark ? "#273025" : "#dce5cd"; radius: 6; border.color: root.line
                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 24; spacing: 10
                    Text { text: "DÀNH CHO ĐIỀU TIẾP THEO  ↗"; color: root.lime; font.pixelSize: 10; font.letterSpacing: 1.5 }
                    Item {
                        Layout.fillWidth: true; Layout.fillHeight: true; implicitHeight: 110
                        Repeater {
                            model: 4
                            Rectangle { x: parent.width / 2 - 82 + index * 28; y: parent.height / 2 - 40; width: 80; height: 80; rotation: -27; color: Qt.rgba(0.6, 0.75, 0.4, index * 0.04); border.color: root.lime; opacity: 0.35 + index * 0.12 }
                        }
                        Text { anchors.centerIn: parent; text: "0" + (root.spaceIndex + 1); color: root.lime; font.pixelSize: 54; font.weight: Font.DemiBold }
                    }
                    Text { text: root.projects[root.spaceIndex]; color: root.ink; font.pixelSize: 20 }
                    FoldButton { text: "Mở tệp của bạn"; asset: "files"; Layout.fillWidth: true; onClicked: workspace.launch("files") }
                }
            }
            ColumnLayout {
                Layout.fillWidth: true; Layout.fillHeight: true; Layout.preferredWidth: 420; spacing: 14
                Rectangle {
                    Layout.fillWidth: true; Layout.fillHeight: true; color: "#d9dfc5"; radius: 6
                    ColumnLayout {
                        anchors.fill: parent; anchors.margins: 20
                        Text { text: "GHI CHÚ NHANH / " + root.names[root.spaceIndex].toUpperCase(); color: "#35402c"; font.pixelSize: 10; font.letterSpacing: 1 }
                        ScrollView {
                            Layout.fillWidth: true; Layout.fillHeight: true; clip: true
                            TextArea {
                                id: note; objectName: "quickNote"; color: "#35402c"; font.pixelSize: 16; wrapMode: TextEdit.Wrap
                                placeholderText: "Ý tưởng vừa thoáng qua…"; placeholderTextColor: "#67735c"
                                background: Item {}
                                Accessible.name: "Ghi chú cho không gian " + root.names[root.spaceIndex]
                                onTextChanged: if (activeFocus) workspace.saveNote(root.spaces[root.spaceIndex], text)
                            }
                        }
                        Text { text: "Lưu tự động trên máy · Không đồng bộ đám mây"; color: "#526046"; font.pixelSize: 10 }
                    }
                }
                FoldButton {
                    Layout.fillWidth: true; implicitHeight: 72
                    objectName: "focusButton"
                    text: root.focusEnd ? root.focusLabel() + " · Nhấn để kết thúc" : "Một nhịp tập trung   /   25 phút"
                    onClicked: { root.focusEnd = root.focusEnd ? 0 : Date.now() + 25 * 60 * 1000; root.remaining = root.focusEnd ? 1500 : 0 }
                }
            }
        }
        Text { text: "Công cụ quen thuộc"; color: root.ink; font.pixelSize: 14 }
        RowLayout {
            Layout.fillWidth: true; spacing: 14
            Repeater {
                model: [{label:"Tệp của bạn", app:"files"}, {label:"Terminal", app:"terminal"}, {label:"Thiết lập", app:"settings"}]
                delegate: FoldButton { text: modelData.label; asset: modelData.app; Layout.fillWidth: true; implicitHeight: 64; onClicked: workspace.launch(modelData.app) }
            }
        }
        RowLayout {
            Text { text: "MYKOS / CÓ NHỊP CỦA RIÊNG MÌNH"; color: root.muted; font.pixelSize: 9; font.letterSpacing: 1.5 }
            Item { Layout.fillWidth: true }
            Text { text: "Workspace · Ba không gian ghi chú"; color: root.muted; font.pixelSize: 10 }
        }
    }
    Popup {
        id: searchPopup; objectName: "appSearchPopup"
        anchors.centerIn: parent; width: 520; padding: 24; modal: true; focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        background: Rectangle { color: root.surface; border.color: root.line; radius: 8 }
        contentItem: ColumnLayout {
            spacing: 14
            TextField { id: search; objectName: "appSearch"; Layout.fillWidth: true; placeholderText: "Tìm ứng dụng…"; Accessible.name: "Tìm ứng dụng"; color: root.ink; background: Rectangle { color: root.paper; border.color: root.lime; radius: 4 } onAccepted: { for (var i = 0; i < results.count; i++) { var button = results.itemAt(i); if (button.visible) { workspace.launch(button.app); searchPopup.close(); break; } } } }
            Repeater {
                id: results
                model: [{label:"Tệp · Files", app:"files"}, {label:"Terminal", app:"terminal"}, {label:"Thiết lập · Settings", app:"settings"}, {label:"Ứng dụng · Discover", app:"apps"}, {label:"Soạn thảo · Kate", app:"notes"}, {label:"Hình ảnh · Gwenview", app:"photos"}]
                delegate: FoldButton { property string app: modelData.app; text: modelData.label; asset: app === "apps" ? "settings" : app; visible: text.toLowerCase().indexOf(search.text.toLowerCase()) >= 0; Layout.fillWidth: true; onClicked: { workspace.launch(app); searchPopup.close() } }
            }
            FoldButton { text: "Đóng · Esc"; Layout.fillWidth: true; onClicked: searchPopup.close() }
        }
        onOpened: { search.text = ""; search.forceActiveFocus() }
    }
    Rectangle {
        visible: root.message !== ""; anchors.horizontalCenter: parent.horizontalCenter; anchors.bottom: parent.bottom; anchors.bottomMargin: 24
        width: Math.min(parent.width - 60, messageText.implicitWidth + 40); height: messageText.implicitHeight + 28; radius: 5; color: root.lime
        Text { id: messageText; anchors.centerIn: parent; width: parent.width - 32; text: root.message; wrapMode: Text.Wrap; color: root.dark ? "#20271c" : "white"; horizontalAlignment: Text.AlignHCenter }
    }
}
