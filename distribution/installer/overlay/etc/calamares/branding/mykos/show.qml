import QtQuick 2.0
import calamares.slideshow 1.0

Presentation {
    id: presentation
    Slide {
        Rectangle { anchors.fill: parent; color: "#171c19" }
        Column {
            anchors.centerIn: parent
            spacing: 24
            Image {
                source: "logo.svg"
                width: 112; height: 112
                fillMode: Image.PreserveAspectFit
                anchors.horizontalCenter: parent.horizontalCenter
            }
            Text {
                text: "Đang cài đặt MyKOS"
                color: "#edf0e7"
                font.pixelSize: 22
            }
        }
    }
    function onActivate() { presentation.currentSlide = 0 }
    function onLeave() {}
}
