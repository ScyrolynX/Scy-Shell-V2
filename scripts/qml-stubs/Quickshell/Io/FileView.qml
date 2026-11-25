import QtQuick

QtObject {
    property string path: ""
    property bool watchChanges: false
    property bool printErrors: true
    property bool blockLoading: false
    property QtObject adapter: null
    signal loaded()
    signal loadFailed()
    signal fileChanged()
    signal adapterUpdated()
    function text(): string { return ""; }
    function setText(t: string) {}
    function reload() {}
    function writeAdapter() {}
}
