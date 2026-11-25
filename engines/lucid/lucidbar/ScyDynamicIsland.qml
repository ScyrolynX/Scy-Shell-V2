pragma ComponentBehavior: Bound

import QtQuick
import Quickshell.Io
import qs
import qs.lucidui

// Scy-Shell v2.0 — Universal Dynamic Island Capsule
// Adaptive top-center pill displaying active Focus Timer, profile/performance state,
// and quick 1-click access to Unified Studio & Control Center.
Rectangle {
    id: island

    property bool hovered: false
    property bool timerRunning: false
    property int timerRemainingSec: 1500
    property string timerPhase: "focus"

    visible: ScyDesignTokens.islandEnabled
    width: island.hovered ? ScyDesignTokens.islandWidth + Theme.dp(76) : ScyDesignTokens.islandWidth
    height: ScyDesignTokens.islandHeight
    radius: ScyDesignTokens.rad(18)
    color: Qt.rgba(0.06, 0.07, 0.10, ScyDesignTokens.surfaceOpacity)
    border.width: ScyDesignTokens.borderThickness
    border.color: island.hovered ? Theme.accent : Qt.rgba(1, 1, 1, ScyDesignTokens.borderOpacity * 0.65)

    Behavior on width {
        NumberAnimation {
            duration: ScyDesignTokens.dur(220)
            easing.type: Easing.OutCubic
        }
    }

    function formatTimer(sec: int): string {
        const m = Math.floor(Math.max(0, sec) / 60);
        const s = Math.max(0, sec) % 60;
        return (m < 10 ? "0" + m : String(m)) + ":" + (s < 10 ? "0" + s : String(s));
    }

    function reloadTimer() {
        const txt = timerFile.text();
        if (!txt || txt.trim() === "")
            return;
        try {
            const doc = JSON.parse(txt);
            island.timerRunning = Boolean(doc.running);
            island.timerPhase = String(doc.phase || "focus");
            if (doc.ends_at && doc.running) {
                const nowSec = Math.floor(Date.now() / 1000);
                island.timerRemainingSec = Math.max(0, Number(doc.ends_at) - nowSec);
            } else {
                island.timerRemainingSec = Number(doc.remaining_seconds || 1500);
            }
        } catch (e) {}
    }

    FileView {
        id: timerFile
        path: ScyBridge.stateDir + "/focus-timer.json"
        watchChanges: true
        printErrors: false
        onLoaded: island.reloadTimer()
        onFileChanged: {
            timerFile.reload();
            island.reloadTimer();
        }
    }

    Timer {
        interval: 1000
        running: island.visible && island.timerRunning
        repeat: true
        onTriggered: {
            if (island.timerRemainingSec > 0)
                island.timerRemainingSec = island.timerRemainingSec - 1;
            else
                island.timerRunning = false;
        }
    }

    Row {
        id: rowContent
        anchors.centerIn: island
        spacing: Theme.dp(8)

        Rectangle {
            width: Theme.dp(8)
            height: Theme.dp(8)
            radius: Theme.dp(4)
            color: island.timerRunning ? "#10b981" : Theme.accent
            anchors.verticalCenter: rowContent.verticalCenter
        }

        Icon {
            name: island.timerRunning ? "timer" : "auto_awesome"
            size: Theme.dp(15)
            color: Theme.accent
            anchors.verticalCenter: rowContent.verticalCenter
        }

        Text {
            text: {
                if (island.timerRunning && ScyDesignTokens.islandShowTimer)
                    return I18n.tr("Focus %1", island.formatTimer(island.timerRemainingSec));
                if (island.hovered)
                    return I18n.tr("Scy · %1 · %2", ScyBridge.activeProfile, ScyBridge.performanceTier);
                return I18n.tr("Scy · %1", ScyBridge.activeProfile);
            }
            color: Theme.text
            font.family: ScyDesignTokens.uiFont
            font.pixelSize: Theme.fontBodySm
            font.weight: Font.Medium
            anchors.verticalCenter: rowContent.verticalCenter
        }
    }

    MouseArea {
        anchors.fill: island
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        onEntered: island.hovered = true
        onExited: island.hovered = false
        onClicked: (mouse) => {
            if (mouse.button === Qt.RightButton)
                ScyBridge.dispatch(["quick", "toggle"]);
            else
                ScyBridge.openStudioSection("01-personalization");
        }
    }
}
