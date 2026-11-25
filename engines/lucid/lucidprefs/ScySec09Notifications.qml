pragma ComponentBehavior: Bound

import qs

ScyStudioSectionBase {
    id: sec
    sectionId: "09-notifications"
    sectionTitle: I18n.tr("NOTIFICATIONS, OSD & CONTROL CENTER SETTINGS")
    sectionSubtitle: I18n.tr("Quick Settings tile grid, Do Not Disturb, quiet hours, toast popups, volume/brightness OSD, and history.")
    deepLinks: [
        {"label": I18n.tr("Per-App Notification Rules & Quiet Hours"), "pageKey": "notifications"}
    ]

    SettingCard {
        title: I18n.tr("SCY CONTROL CENTER & NOTIFICATION ENGINE")
        subtitle: I18n.tr("Configure Quick Settings grid density, system toggles, and single-owner D-Bus notification popups.")

        SettingRow {
            title: I18n.tr("Control Center Tile Grid")
            description: I18n.tr("Number of quick-toggle columns in the slide-out Control Center.")

            M3Segmented {
                options: [
                    {"key": 2, "label": I18n.tr("2 Columns")},
                    {"key": 3, "label": I18n.tr("3 Columns")},
                    {"key": 4, "label": I18n.tr("4 Compact")}
                ]
                current: Number(ScyBridge.getValue("scy.control_center.columns", 2))
                onChosen: (k) => ScyBridge.setSetting("scy.control_center.columns", Number(k), "instant", "columns")
            }
        }

        SettingRow {
            title: I18n.tr("Toast Popup Style")
            description: I18n.tr("Choose between Expressive Material 3 Jelly cards or crisp GPUI toasts.")

            M3Segmented {
                options: [
                    {"key": "lucid", "label": I18n.tr("Expressive Glass")},
                    {"key": "mandara", "label": I18n.tr("Compact GPUI")}
                ]
                current: String(ScyBridge.presentations["toasts"] || "lucid")
                onChosen: (k) => ScyBridge.setPresentation("toasts", String(k))
            }
        }
    }
}
