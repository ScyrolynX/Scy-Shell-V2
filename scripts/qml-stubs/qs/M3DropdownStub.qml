import QtQuick

Item {
    property var options: []
    property string current: ""
    signal chosen(string key)
}
