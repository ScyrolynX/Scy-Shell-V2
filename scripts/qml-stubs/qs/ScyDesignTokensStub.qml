pragma Singleton
import QtQuick

QtObject {
    property string tokensPath: ""
    property var doc: ({})
    property int rev: 0
    property var typography: ({})
    property var colors: ({})
    property var materials: ({})
    property var motion: ({})
    property var layout: ({})
    property var dynamicIsland: ({})
    property var dock: ({})
    property var lockScreen: ({})
    property var loginExperience: ({})
    property string displayFont: "Google Sans"
    property string uiFont: "Google Sans"
    property string monoFont: "JetBrains Mono"
    property int headingWeight: 700
    property string materialPreset: "scy-frosted"
    property real bgOpacity: 0.86
    property real surfaceOpacity: 0.92
    property int blurStrength: 3
    property int blurRadius: 8
    property int borderThickness: 1
    property real borderOpacity: 0.28
    property real glowIntensity: 0.20
    property string motionPreset: "expressive-spring"
    property real durationScale: 1.0
    property real cornerRadiusScale: 1.0
    property real spacingScale: 1.0
    property bool islandEnabled: true
    property string islandMode: "adaptive-pill"
    property int islandWidth: 220
    property int islandHeight: 34
    property bool islandShowTimer: true
    function rad(px: real): int { return Math.round(px); }
    function dur(ms: int): int { return ms; }
}
