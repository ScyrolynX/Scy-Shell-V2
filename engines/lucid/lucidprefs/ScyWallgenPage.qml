pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import qs

Column {
    id: page

    spacing: Theme.dp(26)
    property string chosenStyle: "aurora"

    readonly property var styles: [
        {"key": "aurora", "label": "Aurora"},
        {"key": "topographic", "label": "Topographic"},
        {"key": "bauhaus", "label": "Bauhaus"},
        {"key": "voronoi", "label": "Voronoi"},
        {"key": "flow-field", "label": "Flow Field"},
        {"key": "iso-cubes", "label": "Iso Cubes"},
        {"key": "halftone", "label": "Halftone"},
        {"key": "waves", "label": "Waves"},
        {"key": "mesh-gradient", "label": "Mesh Gradient"},
        {"key": "brutalist-grid", "label": "Brutalist Grid"},
        {"key": "starfield", "label": "Starfield"},
        {"key": "chladni", "label": "Chladni Cymatics"},
        {"key": "ripples", "label": "Ripples"}
    ]

    SettingCard {
        title: I18n.tr("PROCEDURAL WALLGEN STUDIO (13 GENERATIVE STYLES)")
        subtitle: I18n.tr("Generates palette-harmonized wallpapers using Mandara Wallgen and applies them to your active wallpaper renderer (Lucid awww/LiveShell or Mandara).")

        SettingRow {
            title: I18n.tr("Generative Algorithm")
            description: I18n.tr("Seeded automatically from your current Material 3 Expressive accent palette.")

            M3Dropdown {
                options: page.styles
                current: page.chosenStyle
                onChosen: (k) => page.chosenStyle = k
            }
        }

        SettingRow {
            title: I18n.tr("Generate & Apply Wallpaper")
            description: I18n.tr("Renders high-resolution artwork and updates Matugen + OKLCH tokens across both engines.")

            M3Button {
                text: I18n.tr("Generate Now")
                variant: "filled"
                iconPath: "auto_awesome"
                onClicked: Quickshell.execDetached(["scy-shell", "wallgen", page.chosenStyle])
            }
        }
    }
}
