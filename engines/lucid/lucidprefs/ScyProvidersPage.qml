pragma ComponentBehavior: Bound

import QtQuick
import qs

Column {
    id: page

    spacing: Theme.dp(26)

    readonly property var surfaceDomains: [
        { "id": "bar", "title": I18n.tr("Status Bar"), "desc": I18n.tr("Lucid M3 Expressive islands/pills (default), Mandara 9 BarStyles, or Hybrid per-display."), "opts": [{"key": "lucid", "label": "Lucid"}, {"key": "mandara", "label": "Mandara"}, {"key": "hybrid", "label": "Hybrid"}] },
        { "id": "dock", "title": I18n.tr("Application Dock"), "desc": I18n.tr("Pinned apps are synchronized two-way across both dock engines."), "opts": [{"key": "lucid", "label": "Lucid"}, {"key": "mandara", "label": "Mandara"}, {"key": "none", "label": "Off"}] },
        { "id": "launcher", "title": I18n.tr("Launcher & Command Palette"), "desc": I18n.tr("Lucid M3 Launcher federates Mandara !ai & @plugins automatically."), "opts": [{"key": "lucid", "label": "Lucid"}, {"key": "mandara", "label": "Mandara"}] },
        { "id": "quick_settings", "title": I18n.tr("Quick Settings / Control Centre"), "desc": I18n.tr("System control tiles, audio mixer, Wi-Fi and Bluetooth sheets."), "opts": [{"key": "lucid", "label": "Lucid"}, {"key": "mandara", "label": "Mandara"}] },
        { "id": "desktop_widgets", "title": I18n.tr("Desktop Widgets Canvas"), "desc": I18n.tr("Run Lucid's 25 M3 widgets, Mandara's 89/WASM widgets, or both side-by-side in Hybrid mode."), "opts": [{"key": "lucid", "label": "Lucid"}, {"key": "mandara", "label": "Mandara"}, {"key": "hybrid", "label": "Hybrid"}] },
        { "id": "wallpaper", "title": I18n.tr("Wallpaper Renderer (LAYER_BACKGROUND)"), "desc": I18n.tr("Lucid awww + LiveShell video/shaders, or Mandara wgpu / low-VRAM CPU shm_canvas."), "opts": [{"key": "lucid", "label": "Lucid"}, {"key": "mandara", "label": "Mandara"}] },
        { "id": "capture", "title": I18n.tr("Screenshots, OCR & Screen Recording"), "desc": I18n.tr("LucidShot vector markup/OCR/GIF+MP4 studio or Mandara region capture."), "opts": [{"key": "lucid", "label": "Lucid"}, {"key": "mandara", "label": "Mandara"}] },
        { "id": "overview", "title": I18n.tr("Workspace Overview"), "desc": I18n.tr("Live window thumbnails and drag-between-workspaces overview."), "opts": [{"key": "lucid", "label": "Lucid"}, {"key": "mandara", "label": "Mandara"}] },
        { "id": "switcher", "title": I18n.tr("Alt-Tab Window Switcher"), "desc": I18n.tr("Keyboard window switcher overlay."), "opts": [{"key": "lucid", "label": "Lucid"}, {"key": "mandara", "label": "Mandara"}] }
    ]

    readonly property var exclusiveDomains: [
        { "id": "notifications", "title": I18n.tr("Notifications Server (org.freedesktop.Notifications)"), "desc": I18n.tr("Exclusive D-Bus owner. Toast rendering can still be chosen independently below.") },
        { "id": "osd", "title": I18n.tr("On-Screen Display (Volume / Brightness / Keys)"), "desc": I18n.tr("Single hardware key listener and HUD overlay.") },
        { "id": "lock_screen", "title": I18n.tr("Session Lock (ext-session-lock-v1)"), "desc": I18n.tr("Strictly one Wayland lock client: Lucid 6 slot presets or Mandara 6 AuthDesigns.") },
        { "id": "polkit", "title": I18n.tr("Polkit Authentication Agent"), "desc": I18n.tr("Session privilege prompt dialog.") },
        { "id": "night_light", "title": I18n.tr("Night Light / Gamma Control"), "desc": I18n.tr("Exclusive zwlr_gamma_control_v1: Lucid hyprsunset or Mandara native gamma.") },
        { "id": "bt_agent", "title": I18n.tr("Bluetooth Pairing Agent (BlueZ)"), "desc": I18n.tr("Handles PIN/passkey confirmations.") },
        { "id": "idle", "title": I18n.tr("Idle & Sleep Coordinator"), "desc": I18n.tr("Dim, lock, DPMS and suspend timers.") },
        { "id": "clipboard", "title": I18n.tr("Clipboard Watcher"), "desc": I18n.tr("Single data-control watcher: cliphist (Lucid) or Mandara clipboard service.") }
    ]

    SettingCard {
        title: I18n.tr("PRESENTATION & CROSS-ENGINE SEPARATION")
        subtitle: I18n.tr("Separate visual presentation from functional backend providers wherever Wayland & D-Bus allow.")

        SettingRow {
            title: I18n.tr("Toast Popup Renderer")
            description: I18n.tr("Choose which visual engine renders notification popups, independent of which notification daemon owns D-Bus.")

            M3Segmented {
                options: [{"key": "lucid", "label": I18n.tr("Lucid M3 Jelly")}, {"key": "mandara", "label": I18n.tr("Mandara GPUI")}]
                current: ScyBridge.presentations["toasts"] || "lucid"
                onChosen: (k) => ScyBridge.setPresentation("toasts", String(k))
            }
        }

        SettingRow {
            title: I18n.tr("Launcher !ai & @Plugin Federation")
            description: I18n.tr("Query Mandara's Local AI Agent (!ai) and 89+WASM Plugins (@) directly inside Lucid's Material 3 Launcher.")

            M3Switch {
                checked: ScyBridge.launcherFederation
                onToggled: (v) => ScyBridge.setPresentation("launcher_federation", v ? "enabled" : "disabled")
            }
        }

        SettingRow {
            title: I18n.tr("Mandara Plugin Pill in Lucid Bar")
            description: I18n.tr("Show an M3 Expressive extension pill inside Lucid's status bar to summon Mandara sidebars & plugins.")

            M3Switch {
                checked: ScyBridge.barPluginPill
                onToggled: (v) => ScyBridge.setPresentation("lucid_bar_plugin_pill", v ? "enabled" : "disabled")
            }
        }
    }

    SettingCard {
        title: I18n.tr("SHELL SURFACE PROVIDERS")
        subtitle: I18n.tr("Inactive provider settings are 100% preserved in the Settings Vault when switching.")

        Repeater {
            model: page.surfaceDomains

            SettingRow {
                id: surfRow
                required property var modelData
                title: surfRow.modelData.title
                description: surfRow.modelData.desc

                M3Segmented {
                    options: surfRow.modelData.opts
                    current: String(ScyBridge.providers[surfRow.modelData.id] || "lucid")
                    onChosen: (k) => ScyBridge.setProvider(surfRow.modelData.id, String(k))
                }
            }
        }
    }

    SettingCard {
        title: I18n.tr("EXCLUSIVE SYSTEM RESOURCE ARBITRATION")
        subtitle: I18n.tr("Pre-flight gated by Scy-Shell Core so two daemons never fight over D-Bus or Wayland protocols.")

        Repeater {
            model: page.exclusiveDomains

            SettingRow {
                id: exclRow
                required property var modelData
                title: exclRow.modelData.title
                description: exclRow.modelData.desc

                M3Segmented {
                    options: [{"key": "lucid", "label": "Lucid"}, {"key": "mandara", "label": "Mandara"}]
                    current: String(ScyBridge.providers[exclRow.modelData.id] || "lucid")
                    onChosen: (k) => ScyBridge.setProvider(exclRow.modelData.id, String(k))
                }
            }
        }
    }
}
