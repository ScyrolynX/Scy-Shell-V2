pragma ComponentBehavior: Bound

import qs

ScyStudioSectionBase {
    id: sec
    sectionId: "07-windows"
    sectionTitle: I18n.tr("HYPRLAND 0.57+ WINDOW & WORKSPACE SETTINGS")
    sectionSubtitle: I18n.tr("Tiling algorithms, inner/outer gaps, border gradients, corner rounding, inactive dimming, overview, and scratchpads.")
    deepLinks: [
        {"label": I18n.tr("Visual Window & Tiling Preview"), "pageKey": "windows"},
        {"label": I18n.tr("Special Scratchpad Workspaces"), "pageKey": "workspaces"}
    ]

    SettingCard {
        title: I18n.tr("SCY WORKSPACE & TILING ENGINE (HYPRLAND 0.57+)")
        subtitle: I18n.tr("Non-destructive modular Hyprland 0.57+ configuration with automatic snapshot backups before every compositor emit.")

        SettingRow {
            title: I18n.tr("Tiling Layout Engine")
            description: I18n.tr("Choose Dwindle spiral tiling or Master + Stack column tiling.")

            M3Segmented {
                options: [
                    {"key": "dwindle", "label": I18n.tr("Dwindle Spiral")},
                    {"key": "master", "label": I18n.tr("Master + Stack")}
                ]
                current: String(ScyBridge.getValue("scy.windows.layout_engine", "dwindle"))
                onChosen: (k) => ScyBridge.setSetting("scy.windows.layout_engine", String(k), "hypr_trial", "general.layout")
            }
        }

        SettingRow {
            title: I18n.tr("Dim Inactive Windows")
            description: I18n.tr("Subtly dim unfocused windows to spotlight active work.")

            M3Switch {
                checked: Boolean(ScyBridge.getValue("scy.windows.dim_inactive", false))
                onToggled: (v) => ScyBridge.setSetting("scy.windows.dim_inactive", v, "hypr_trial", "decoration.dim_inactive")
            }
        }
    }
}
