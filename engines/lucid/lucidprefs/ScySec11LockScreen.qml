pragma ComponentBehavior: Bound

import qs

ScyStudioSectionBase {
    id: sec
    sectionId: "11-lock-screen"
    sectionTitle: I18n.tr("SESSION LOCK SCREEN SETTINGS (DECOUPLED FROM LOGIN)")
    sectionSubtitle: I18n.tr("Configures ONLY your in-session Wayland lock screen (ext-session-lock-v1). Never overwrites your SDDM/Greetd Login screen.")
    deepLinks: [
        {"label": I18n.tr("Interactive Lock Layout & Widget Slot Editor"), "pageKey": "lockscreen"}
    ]

    SettingCard {
        title: I18n.tr("SCY SESSION LOCK STUDIO (11 — LOCK SCREEN)")
        subtitle: I18n.tr("Authenticated via system PAM with zero stored credentials. Strictly isolated from Section 12 — Login Experience.")

        SettingRow {
            title: I18n.tr("Session Lock Layout Preset")
            description: I18n.tr("Choose among 6 expressive spatial lock compositions.")

            M3Dropdown {
                options: [
                    {"key": "centre", "label": I18n.tr("Centered Focus")},
                    {"key": "split", "label": I18n.tr("Editorial Split")},
                    {"key": "panel", "label": I18n.tr("Side Glass Panel")},
                    {"key": "minimal", "label": I18n.tr("Minimal Pure")},
                    {"key": "bento", "label": I18n.tr("Bento Widget Cards")},
                    {"key": "deck", "label": I18n.tr("Bottom Command Deck")}
                ]
                current: String(ScyBridge.getValue("scy.providers.lucid.prefs.lockPreset", "centre"))
                onChosen: (k) => ScyBridge.setSetting("scy.providers.lucid.prefs.lockPreset", String(k), "instant", "lockPreset")
            }
        }

        SettingRow {
            title: I18n.tr("Lock Screen Clock Typography")
            description: I18n.tr("Expressive stacked digits, bold inline, editorial serif, minimal pill, or orbit analog.")

            M3Dropdown {
                options: [
                    {"key": "stacked-expressive", "label": I18n.tr("Stacked Expressive")},
                    {"key": "inline-bold", "label": I18n.tr("Inline Bold")},
                    {"key": "editorial-serif", "label": I18n.tr("Editorial Serif")},
                    {"key": "minimal-pill", "label": I18n.tr("Minimal Pill")},
                    {"key": "orbit-analog", "label": I18n.tr("Orbit Analog")}
                ]
                current: String(ScyBridge.getValue("scy.lock.clock_style", "stacked-expressive"))
                onChosen: (k) => ScyBridge.setSetting("scy.lock.clock_style", String(k), "instant", "clock_style")
            }
        }

        SettingRow {
            title: I18n.tr("Locked Notification Privacy")
            description: I18n.tr("Control how much notification detail is shown while your session is locked.")

            M3Dropdown {
                options: [
                    {"key": "full", "label": I18n.tr("Full Content")},
                    {"key": "summary-only", "label": I18n.tr("App Name Only")},
                    {"key": "count-only", "label": I18n.tr("Count Pill Only")},
                    {"key": "hidden", "label": I18n.tr("Completely Hidden")}
                ]
                current: String(ScyBridge.getValue("scy.lock.notification_privacy", "summary-only"))
                onChosen: (k) => ScyBridge.setSetting("scy.lock.notification_privacy", String(k), "instant", "notification_privacy")
            }
        }

        SettingRow {
            title: I18n.tr("Test Session Lock Now")
            description: I18n.tr("Immediately lock the active Wayland session using the single configured lock owner.")

            M3Button {
                text: I18n.tr("Lock Session")
                variant: "tonal"
                onClicked: ScyBridge.dispatch(["lock"])
            }
        }
    }
}
