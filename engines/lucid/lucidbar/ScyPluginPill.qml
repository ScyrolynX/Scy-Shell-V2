pragma ComponentBehavior: Bound

import QtQuick
import qs
import qs.lucidui

// Scy-Shell Cross-Engine Bar Pill for Lucid 2 Status Bar:
// Opens Mandara's 88+WASM Plugin Drawer (left click), Local AI Command Agent
// (middle click), or Scy-Shell Studio -> Plugins (right click) while keeping
// Lucid's authentic Material 3 Expressive pill geometry & hover state layer.
Item {
    id: pill

    visible: ScyBridge.barPluginPill
    implicitWidth: visible ? Theme.dp(36) : 0
    implicitHeight: visible ? Theme.dp(32) : 0

    Rectangle {
        id: pillBg
        anchors.fill: pill
        radius: pillBg.height / 2
        color: Theme.withBlur(Theme.bgTile)
        border.width: 1
        border.color: hover.hovered ? Theme.accent : Theme.outline

        Icon {
            anchors.centerIn: pillBg
            name: "extension"
            size: Theme.dp(18)
            color: hover.hovered ? Theme.accent : Theme.text
        }

        HoverHandler {
            id: hover
        }

        TapHandler {
            acceptedButtons: Qt.LeftButton | Qt.MiddleButton | Qt.RightButton
            onTapped: (eventPoint, button) => {
                if (button === Qt.MiddleButton)
                    ScyBridge.dispatch(["agent", "toggle"]);
                else if (button === Qt.RightButton)
                    ScyBridge.dispatch(["studio", "13-productivity"]);
                else
                    ScyBridge.dispatch(["sidebar", "toggle"]);
            }
        }
    }
}
