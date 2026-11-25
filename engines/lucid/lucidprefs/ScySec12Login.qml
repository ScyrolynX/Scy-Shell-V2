pragma ComponentBehavior: Bound

import qs

ScyStudioSectionBase {
    id: sec
    sectionId: "12-login"
    sectionTitle: I18n.tr("PRE-SESSION LOGIN & GREETER SETTINGS (DECOUPLED FROM LOCK)")
    sectionSubtitle: I18n.tr("Configures ONLY pre-session SDDM / Greetd login appearance (~/.local/state/scy-shell/login-greeter.json). Never overwrites Lock Screen.")
    deepLinks: [
        {"label": I18n.tr("System Users & Avatar Accounts"), "pageKey": "users"}
    ]

    SettingCard {
        title: I18n.tr("SCY LOGIN EXPERIENCE STUDIO (12 — LOGIN / GREETER)")
        subtitle: I18n.tr("Harmonized with ScyDesignTokens while maintaining an independent configuration store from Section 11 Lock Screen.")

        SettingRow {
            title: I18n.tr("Display Manager / Greeter Integration")
            description: I18n.tr("Preserve your current system display manager or stage Scy-Shell's SDDM / Greetd pre-auth theme.")

            M3Dropdown {
                options: [
                    {"key": "preserve", "label": I18n.tr("Preserve Existing System DM")},
                    {"key": "scy-sddm", "label": I18n.tr("Scy-Shell SDDM Theme")},
                    {"key": "scy-greetd", "label": I18n.tr("Scy-Shell Greetd Theme")}
                ]
                current: String(ScyBridge.getValue("scy.login.greeter_target", "preserve"))
                onChosen: (k) => ScyBridge.setSetting("scy.login.greeter_target", String(k), "instant", "greeter_target")
            }
        }

        SettingRow {
            title: I18n.tr("Login User Selector Layout")
            description: I18n.tr("Visual presentation of system accounts on the pre-session login screen.")

            M3Segmented {
                options: [
                    {"key": "avatar-cards", "label": I18n.tr("Avatar Cards")},
                    {"key": "carousel", "label": I18n.tr("Carousel")},
                    {"key": "compact-dropdown", "label": I18n.tr("Compact")}
                ]
                current: String(ScyBridge.getValue("scy.login.user_list_style", "avatar-cards"))
                onChosen: (k) => ScyBridge.setSetting("scy.login.user_list_style", String(k), "instant", "user_list_style")
            }
        }

        SettingRow {
            title: I18n.tr("One-Time Backdrop Copy from Lock Screen")
            description: I18n.tr("Copies Lock Screen wallpaper & blur radius once to Login without turning on automatic cross-overwriting.")

            M3Button {
                text: I18n.tr("Copy Backdrop Once")
                variant: "tonal"
                onClicked: ScyBridge.copyLockToLoginOnce()
            }
        }
    }
}
