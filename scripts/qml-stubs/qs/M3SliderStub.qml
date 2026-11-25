import QtQuick

Item {
    property real from: 0
    property real to: 100
    property real stepSize: 1
    property real value: 0
    property string suffix: ""
    property bool enabled: true
    signal moved(real v)
}
