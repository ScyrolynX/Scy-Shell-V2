pragma ComponentBehavior: Bound

import QtQuick
import qs

ScyStudioSectionBase {
    id: sec
    sectionId: "01-personalization"
    sectionTitle: I18n.tr("PERSONALIZATION & DESIGN ENGINE SETTINGS")
    sectionSubtitle: I18n.tr("Centralized ScyDesignTokens palette, typography, icon/cursor identity, and wallpaper color extraction.")
    deepLinks: [
        {"label": I18n.tr("Wallpaper & Theme Gallery"), "pageKey": "theme"},
        {"label": I18n.tr("Matugen & Custom Colours"), "pageKey": "colours"},
        {"label": I18n.tr("Base16 / Scheme Palettes"), "pageKey": "palettes"},
        {"label": I18n.tr("Procedural Wallgen (13 Styles)"), "pageKey": "scy-wallgen"},
        {"label": I18n.tr("GTK / Qt / Icons / Cursors"), "pageKey": "environment"}
    ]

    SettingCard {
        title: I18n.tr("SCY DYNAMIC DESIGN ENGINE")
        subtitle: I18n.tr("Harmonize Material 3 Expressive + OKLCH tokens across every bar, dock, widget, notification, lock screen, and 28 desktop apps.")

        SettingRow {
            title: I18n.tr("Architectural Visual Look")
            description: I18n.tr("Select Scy-Shell's signature aesthetic mood while preserving your custom layout and dock preferences.")

            M3Dropdown {
                options: [
                    {"key": "scy-m3-expressive", "label": "Scy Material 3 Expressive (Signature)"},
                    {"key": "corniche-dusk", "label": "Corniche Dusk"},
                    {"key": "pharos-ink", "label": "Pharos Ink"},
                    {"key": "library-desk", "label": "Library Desk"},
                    {"key": "sea-glass", "label": "Sea Glass"},
                    {"key": "phosphor", "label": "Phosphor"},
                    {"key": "night-frame", "label": "Night Frame OLED"},
                    {"key": "zen", "label": "Minimal Zen"}
                ]
                current: String(ScyBridge.presentations["primary_identity"] || "scy-m3-expressive")
                onChosen: (k) => ScyBridge.setPresentation("primary_identity", String(k))
            }
        }

        SettingRow {
            title: I18n.tr("Palette Harmony Rule")
            description: I18n.tr("Controls chroma and secondary accent spread generated from your seed color or wallpaper.")

            M3Dropdown {
                options: [
                    {"key": "expressive", "label": I18n.tr("Expressive")},
                    {"key": "tonal-spot", "label": I18n.tr("Tonal Spot")},
                    {"key": "vibrant", "label": I18n.tr("Vibrant")},
                    {"key": "neutral", "label": I18n.tr("Neutral Studio")},
                    {"key": "monochrome", "label": I18n.tr("Monochrome")}
                ]
                current: String(ScyBridge.getValue("scy.design.palette_harmony", "expressive"))
                onChosen: (k) => ScyBridge.setSetting("scy.design.palette_harmony", String(k), "instant", "palette_harmony")
            }
        }

        SettingRow {
            title: I18n.tr("Quick Accent Seed Swatches")
            description: I18n.tr("Apply a curated OKLCH seed across the entire desktop and 28-app theme ledger.")

            Row {
                spacing: Theme.dp(8)

                Repeater {
                    model: ["#7aa2f7", "#ffb1c4", "#10b981", "#f59e0b", "#cba6f7", "#89dceb", "#f38ba8"]

                    Rectangle {
                        id: seedChip
                        required property string modelData
                        width: Theme.dp(28)
                        height: Theme.dp(28)
                        radius: Theme.dp(14)
                        color: seedChip.modelData
                        border.width: ScyBridge.lastPreviewColor === seedChip.modelData ? 2 : 1
                        border.color: ScyBridge.lastPreviewColor === seedChip.modelData ? Theme.text : Theme.outline

                        MouseArea {
                            anchors.fill: seedChip
                            onClicked: ScyBridge.setSetting("scy.providers.lucid.prefs.themeColour", seedChip.modelData, "theme_accent", "themeColour")
                        }
                    }
                }
            }
        }
    }
}
