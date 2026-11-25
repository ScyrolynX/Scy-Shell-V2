pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import qs

Column {
    id: page

    spacing: Theme.dp(26)

    SettingCard {
        title: I18n.tr("DISPLAY MANAGER & PRE-AUTH GREETER")
        subtitle: I18n.tr("Choose between Lucid's per-user synced SDDM theme, Mandara's native Wayland greetd greeter, or preserving your existing login manager.")

        SettingRow {
            title: I18n.tr("Display Manager Strategy")
            description: I18n.tr("Never switches systemd display-manager.service without explicit Polkit confirmation and backup.")

            M3Segmented {
                options: [
                    {"key": "preserve", "label": I18n.tr("Preserve Existing")},
                    {"key": "lucid-sddm", "label": I18n.tr("Lucid SDDM")},
                    {"key": "mandara-greetd", "label": I18n.tr("Mandara greetd")}
                ]
                current: String(ScyBridge.providers["display_manager"] || "preserve")
                onChosen: (k) => ScyBridge.setProvider("display_manager", String(k))
            }
        }

        SettingRow {
            title: I18n.tr("Stage Harmonized Pre-Auth Configs")
            description: I18n.tr("Generates palette-matched SDDM theme.conf and greetd greeter.toml in ~/.local/state/scy-shell/.")

            M3Button {
                text: I18n.tr("Stage Configs")
                variant: "tonal"
                onClicked: Quickshell.execDetached(["scy-shell", "preauth", "stage"])
            }
        }
    }
}
