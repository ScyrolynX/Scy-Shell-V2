import QtQuick

Item {
    property string text: ""
    property string variant: "tonal"
    property string iconPath: ""
    property bool enabled: true
    property bool destructive: false
    signal clicked()
}
