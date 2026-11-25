pragma ComponentBehavior: Bound

import qs

ScyStudioSectionBase {
    id: sec
    sectionId: "02-desktop"
    sectionTitle: I18n.tr("DESKTOP EXPERIENCE & CHROME SETTINGS")
    sectionSubtitle: I18n.tr("Configure the status bar, Scy Dynamic Island, workspace switcher pills, launcher search, and desktop icons.")
    deepLinks: [
        {"label": I18n.tr("Bar Module & Join Arranger"), "pageKey": "bar"},
        {"label": I18n.tr("Launcher Modes & Search Sources"), "pageKey": "launcher"},
        {"label": I18n.tr("General Shell Sizing & Density"), "pageKey": "general"}
    ]

    SettingCard {
        title: I18n.tr("STATUS BAR, DYNAMIC ISLAND & WORKSPACE PILLS")
        subtitle: I18n.tr("Unified control over your top/bottom bar geometry, central Dynamic Island capsule, and workspace indicator style.")

        SettingRow {
            title: I18n.tr("Status Bar Silhouette")
            description: I18n.tr("Choose floating islands, carved screen-edge notch, or full-width panel.")

            M3Segmented {
                options: [
                    {"key": "island", "label": I18n.tr("Floating Islands")},
                    {"key": "notch", "label": I18n.tr("Carved Notch")},
                    {"key": "full", "label": I18n.tr("Full Bar")}
                ]
                current: String(ScyBridge.getValue("scy.providers.lucid.prefs.barStyle", "island"))
                onChosen: (k) => ScyBridge.setSetting("scy.providers.lucid.prefs.barStyle", String(k), "instant", "barStyle")
            }
        }

        SettingRow {
            title: I18n.tr("Scy Dynamic Island")
            description: I18n.tr("Adaptive central pill showing active Focus Timer, profile/tier status, media, and 1-click Studio access.")

            M3Switch {
                checked: Boolean(ScyBridge.getValue("scy.island.enabled", true))
                onToggled: (v) => ScyBridge.setSetting("scy.island.enabled", v, "instant", "enabled")
            }
        }

        SettingRow {
            title: I18n.tr("Workspace Indicator Style")
            description: I18n.tr("Visual representation of active, occupied, and empty Hyprland workspaces.")

            M3Dropdown {
                options: [
                    {"key": "morphing-pills", "label": I18n.tr("Morphing Pills")},
                    {"key": "numbered-chips", "label": I18n.tr("Numbered Chips")},
                    {"key": "app-icons", "label": I18n.tr("Active App Icons")},
                    {"key": "dots", "label": I18n.tr("Minimal Dots")},
                    {"key": "roman", "label": I18n.tr("Roman Numerals")},
                    {"key": "kanji", "label": I18n.tr("Kanji")}
                ]
                current: String(ScyBridge.getValue("scy.desktop.workspace_style", "morphing-pills"))
                onChosen: (k) => ScyBridge.setSetting("scy.desktop.workspace_style", String(k), "instant", "workspace_style")
            }
        }
    }
}
