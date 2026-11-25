pragma ComponentBehavior: Bound

import qs

ScyStudioSectionBase {
    id: sec
    sectionId: "06-widgets"
    sectionTitle: I18n.tr("AMBIENT WIDGETS & COMPONENT LABORATORY SETTINGS")
    sectionSubtitle: I18n.tr("Customize desktop widget cards (Clock, Weather, Calendar, Media, Telemetry, Notes) and per-component materials.")
    deepLinks: [
        {"label": I18n.tr("Interactive Desktop Widget Canvas"), "pageKey": "widgets"},
        {"label": I18n.tr("89 Built-in & WASM Extensions"), "pageKey": "scy-plugins"}
    ]

    SettingCard {
        title: I18n.tr("SCY COMPONENT LABORATORY & WIDGET BOARDS")
        subtitle: I18n.tr("Apply curated desktop widget arrangements and synchronize frosted glass tokens across every ambient card.")

        SettingRow {
            title: I18n.tr("Desktop Widget Board Preset")
            description: I18n.tr("Switch between Balanced Glance, Minimal Zen Clock, System Telemetry Pro, Productivity Hub, or Clean Slate.")

            M3Dropdown {
                options: [
                    {"key": "balanced-glance", "label": I18n.tr("Balanced Glance (Clock + Weather + Media)")},
                    {"key": "minimal-zen", "label": I18n.tr("Minimal Zen Clock")},
                    {"key": "telemetry-pro", "label": I18n.tr("System Telemetry Pro")},
                    {"key": "productivity-hub", "label": I18n.tr("Agenda + Notes + Pomodoro")},
                    {"key": "clean-slate", "label": I18n.tr("Clean Desktop (No Widgets)")}
                ]
                current: String(ScyBridge.getValue("scy.widgets.board_preset", "balanced-glance"))
                onChosen: (k) => ScyBridge.setSetting("scy.widgets.board_preset", String(k), "instant", "board_preset")
            }
        }

        SettingRow {
            title: I18n.tr("Desktop Widgets Enabled")
            description: I18n.tr("Show or hide ambient desktop widget cards across your wallpaper layer.")

            M3Switch {
                checked: Boolean(ScyBridge.getValue("scy.providers.lucid.prefs.widgetsEnabled", true))
                onToggled: (v) => ScyBridge.setSetting("scy.providers.lucid.prefs.widgetsEnabled", v, "instant", "widgetsEnabled")
            }
        }
    }
}
