import QtQuick

Item {
    property string text: ""
    property string placeholder: ""
    property bool enabled: true
    property bool commitOnBlur: true
    property bool password: false
    property bool error: false
    signal accepted(string value)
    signal edited(string value)
}
