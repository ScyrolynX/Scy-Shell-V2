import QtQuick

Item {
    property var options: []
    property var current: ""
    property bool enabled: true
    signal chosen(var key)
}
