pragma ComponentBehavior: Bound

import qs

ScyStudioSectionBase {
    id: sec
    sectionId: "08-interactions"
    sectionTitle: I18n.tr("SHORTCUTS, GESTURES, POINTER & HOT CORNERS")
    sectionSubtitle: I18n.tr("Configure hot corners, trackpad swipe gestures, pointer acceleration, keyboard layouts, and global shortcuts.")
    deepLinks: [
        {"label": I18n.tr("Interactive Keybind Recorder & Collision Checker"), "pageKey": "keybinds"},
        {"label": I18n.tr("Keyboard Layouts, Mouse & Touchpad Gestures"), "pageKey": "input"}
    ]

    SettingCard {
        title: I18n.tr("SCY INTERACTION PROFILES & HOT CORNERS")
        subtitle: I18n.tr("Tune desktop responsiveness for mouse precision, laptop multi-finger gestures, or keyboard-driven workflows.")

        SettingRow {
            title: I18n.tr("Interaction Ergonomics Profile")
            description: I18n.tr("Select a preset tuning for pointer focus, scroll behavior, and gesture thresholds.")

            M3Dropdown {
                options: [
                    {"key": "default", "label": I18n.tr("Balanced Desktop")},
                    {"key": "laptop-touch", "label": I18n.tr("Trackpad & Gestures First")},
                    {"key": "vim-keyboard", "label": I18n.tr("Keyboard Driven")},
                    {"key": "creator-mouse", "label": I18n.tr("Mouse Precision")}
                ]
                current: String(ScyBridge.getValue("scy.interactions.profile", "default"))
                onChosen: (k) => ScyBridge.setSetting("scy.interactions.profile", String(k), "instant", "profile")
            }
        }

        SettingRow {
            title: I18n.tr("Top-Left Hot Corner")
            description: I18n.tr("Action triggered when resting the pointer in the top-left screen corner.")

            M3Dropdown {
                options: [
                    {"key": "none", "label": I18n.tr("Disabled")},
                    {"key": "overview", "label": I18n.tr("Workspace Overview")},
                    {"key": "launcher", "label": I18n.tr("App Launcher")},
                    {"key": "control-center", "label": I18n.tr("Control Center")},
                    {"key": "lock", "label": I18n.tr("Lock Screen")}
                ]
                current: String(ScyBridge.getValue("scy.interactions.corner_top_left", "overview"))
                onChosen: (k) => ScyBridge.setSetting("scy.interactions.corner_top_left", String(k), "instant", "corner_top_left")
            }
        }
    }
}
