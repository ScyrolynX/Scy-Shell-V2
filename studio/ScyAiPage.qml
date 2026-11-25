pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import qs

Column {
    id: page

    spacing: Theme.dp(26)
    property string promptText: ""

    SettingCard {
        title: I18n.tr("LOCAL AI COMMAND AGENT & CLOUD PRODUCTIVITY")
        subtitle: I18n.tr("100% on-device natural language control (FunctionGemma-270M / Qwen3-0.6B), Whisper STT, CalDAV sync & 3D Game Shelf.")

        SettingRow {
            id: aiRow
            title: I18n.tr("Run Natural-Language Shell Command (!ai)")
            description: I18n.tr("Model weights are strictly opt-in user downloads (Qwen3-0.6B Apache-2.0 / FunctionGemma Gemma Terms). Deterministic offline command router works immediately.")
            stacked: true

            M3TextField {
                width: aiRow.width
                placeholder: I18n.tr("e.g. switch bar to mandara and set gaps to 12")
                onAccepted: (v) => Quickshell.execDetached(["scy-shell", "ai", v])
            }
        }

        SettingRow {
            title: I18n.tr("3D Steam / Lutris / Heroic Game Shelf")
            description: I18n.tr("Open Mandara's hardware-accelerated cover-art game launcher (Super + Shift + G).")

            M3Button {
                text: I18n.tr("Open Game Shelf")
                variant: "tonal"
                iconPath: "sports_esports"
                onClicked: ScyBridge.dispatch(["games"])
            }
        }
    }
}
