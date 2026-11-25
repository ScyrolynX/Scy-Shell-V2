pragma ComponentBehavior: Bound

import qs

ScyStudioSectionBase {
    id: sec
    sectionId: "03-dock"
    sectionTitle: I18n.tr("ALL DOCK STUDIO SETTINGS")
    sectionSubtitle: I18n.tr("Complete single-owner dock customization: geometry, glass materials, magnification, auto-hide, indicators, groups, and recents.")
    deepLinks: [
        {"label": I18n.tr("Interactive Dock Pin & Module Editor"), "pageKey": "dock"}
    ]

    SettingCard {
        title: I18n.tr("SCY DOCK STUDIO — SINGLE-CLICK MODE & PLACEMENT")
        subtitle: I18n.tr("Guaranteed single-owner dock execution: switching dock style or mode applies in one click, unmaps inactive surfaces immediately, and persists across logins.")

        SettingRow {
            title: I18n.tr("Active Dock Architecture & Style")
            description: I18n.tr("Switch seamlessly between Lucid-inspired floating glass islands, carved notch, split pinned/running islands, compact rail, or off.")

            M3Dropdown {
                options: [
                    {"key": "island", "label": I18n.tr("Scy Floating Island (Lucid Signature)")},
                    {"key": "notch", "label": I18n.tr("Carved Edge Notch")},
                    {"key": "split", "label": I18n.tr("Split Pinned / Running Islands")},
                    {"key": "rail", "label": I18n.tr("Compact GPUI Rail")},
                    {"key": "disabled", "label": I18n.tr("Disabled (No Dock)")}
                ]
                current: ScyBridge.dockMode
                onChosen: (k) => ScyBridge.switchDock(String(k))
            }
        }

        SettingRow {
            title: I18n.tr("Curated Dock Preset")
            description: I18n.tr("Apply coordinated icon sizing, glass material, magnification, and dodge behavior in one click.")

            M3Dropdown {
                options: [
                    {"key": "lucid-signature", "label": I18n.tr("Lucid Signature Island")},
                    {"key": "carved-notch", "label": I18n.tr("Carved Bottom Notch")},
                    {"key": "trinity-split", "label": I18n.tr("Trinity Split Islands")},
                    {"key": "left-studio-rail", "label": I18n.tr("Left Studio Rail")},
                    {"key": "minimal-float", "label": I18n.tr("Minimal Micro-Float")}
                ]
                current: String(ScyBridge.getValue("scy.dock.preset", "lucid-signature"))
                onChosen: (k) => ScyBridge.setSetting("scy.dock.preset", String(k), "instant", "preset")
            }
        }

        SettingRow {
            title: I18n.tr("Screen Edge Placement")
            description: I18n.tr("Anchor the dock along the bottom, left, right, or floating offset.")

            M3Dropdown {
                options: [
                    {"key": "bottom", "label": I18n.tr("Bottom")},
                    {"key": "left", "label": I18n.tr("Left")},
                    {"key": "right", "label": I18n.tr("Right")},
                    {"key": "floating", "label": I18n.tr("Floating")}
                ]
                current: String(ScyBridge.getValue("scy.dock.placement", "bottom"))
                onChosen: (k) => ScyBridge.setSetting("scy.dock.placement", String(k), "instant", "placement")
            }
        }

        SettingRow {
            title: I18n.tr("Intelligent Auto-Hide & Window Dodge")
            description: I18n.tr("Keep the dock visible until overlapped by windows, dodge fullscreen apps, or always hide until edge hover.")

            M3Dropdown {
                options: [
                    {"key": "never", "label": I18n.tr("Always Visible")},
                    {"key": "dodge-windows", "label": I18n.tr("Dodge Overlapping Windows")},
                    {"key": "dodge-maximized", "label": I18n.tr("Dodge Maximized / Fullscreen")},
                    {"key": "always-hide", "label": I18n.tr("Always Auto-Hide")}
                ]
                current: String(ScyBridge.getValue("scy.dock.auto_hide_mode", "dodge-windows"))
                onChosen: (k) => ScyBridge.setSetting("scy.dock.auto_hide_mode", String(k), "instant", "auto_hide_mode")
            }
        }
    }
}
