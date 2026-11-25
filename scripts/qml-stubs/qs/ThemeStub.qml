pragma Singleton
import QtQuick

QtObject {
    property color bg: "#141218"
    property color bgTile: "#1d1b20"
    property color surface0: "#211f26"
    property color surface1: "#2b2930"
    property color surfaceHighest: "#36343b"
    property color text: "#e6e0e9"
    property color subtext: "#cac4d0"
    property color accent: "#ffb1c4"
    property color fgAccent: "#492532"
    property color cPrimary: "#ffb1c4"
    property color cOnPrimary: "#492532"
    property color outline: "#938f99"
    property color error: "#f2b8b5"
    property string fontFamily: "Google Sans"
    property int fontBodyMd: 14
    property int fontBodySm: 12
    property int radiusPill: 999
    property int durQuick: 120
    function dp(v: real): real { return v; }
    function rad(v: real): real { return v; }
    function withBlur(c: color): color { return c; }
}
