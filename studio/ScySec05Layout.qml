pragma ComponentBehavior: Bound

import qs

ScyStudioSectionBase {
    id: sec
    sectionId: "05-layout"
    sectionTitle: I18n.tr("SPATIAL LAYOUT, SCALING & MULTI-MONITOR SETTINGS")
    sectionSubtitle: I18n.tr("Control global UI scale, corner radius scale, spacing rhythm, outer margins, layer Z-order, and multi-monitor distribution.")

    SettingCard {
        title: I18n.tr("SCY LAYOUT COMPOSER")
        subtitle: I18n.tr("Orchestrate how top/bottom bars, Dynamic Island, dock, notifications, OSD, and Control Center anchor across your displays.")

        SettingRow {
            title: I18n.tr("Spatial Desktop Layout Preset")
            description: I18n.tr("Re-anchor bar, Dynamic Island, and dock together in one coordinated layout preset.")

            M3Dropdown {
                options: [
                    {"key": "scy-signature", "label": I18n.tr("Scy Signature (Top Island + Bottom Dock)")},
                    {"key": "unity-left", "label": I18n.tr("Unity Left Rail + Top Strip")},
                    {"key": "bottom-deck", "label": I18n.tr("Unified Bottom Deck")},
                    {"key": "minimal-top", "label": I18n.tr("Minimal Single Top Bar")},
                    {"key": "dual-stage", "label": I18n.tr("Creator Dual-Edge Stage")}
                ]
                current: String(ScyBridge.getValue("scy.layout.active_preset", "scy-signature"))
                onChosen: (k) => ScyBridge.applyLayoutPreset(String(k))
            }
        }

        SettingRow {
            title: I18n.tr("Multi-Monitor Shell Policy")
            description: I18n.tr("Choose whether shell chrome spans all displays, stays on the primary monitor, or follows keyboard focus.")

            M3Segmented {
                options: [
                    {"key": "all-displays", "label": I18n.tr("All Displays")},
                    {"key": "primary-only", "label": I18n.tr("Primary Only")},
                    {"key": "focused-follow", "label": I18n.tr("Follow Focus")}
                ]
                current: String(ScyBridge.getValue("scy.layout.multi_monitor_mode", "all-displays"))
                onChosen: (k) => ScyBridge.setSetting("scy.layout.multi_monitor_mode", String(k), "instant", "multi_monitor_mode")
            }
        }
    }
}
