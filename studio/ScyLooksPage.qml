pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import qs

Column {
    id: page

    spacing: Theme.dp(26)

    readonly property var allLooks: [
        {"key": "scy-m3-expressive", "label": "Scy-Shell · Material 3 Expressive (Default)"},
        {"key": "corniche-dusk", "label": "Corniche Dusk — Rose evening glass"},
        {"key": "pharos-ink", "label": "Pharos Ink — High-contrast monochrome"},
        {"key": "montaza-crimson", "label": "Montaza Crimson — Botanical crimson"},
        {"key": "qaitbay-forest", "label": "Qaitbay Forest — Stone & cedar matte"},
        {"key": "anfushi-wave", "label": "Anfushi Wave — Mediterranean cyan"},
        {"key": "night-frame", "label": "Night Frame — Framed obsidian"},
        {"key": "redmond", "label": "Redmond — Fluent acrylic"},
        {"key": "cupertino", "label": "Cupertino — Translucent menu bar & dock"},
        {"key": "corniche-frame", "label": "Corniche Frame — Screen-framing bezel"},
        {"key": "raml-line", "label": "Raml Line — Swiss hairline grid"},
        {"key": "lighthouse-rail", "label": "Lighthouse Rail — Vertical workstation rail"},
        {"key": "phosphor", "label": "Phosphor — Retro CRT terminal"},
        {"key": "pharos-lantern", "label": "Pharos Lantern — Warm amber low-glare"},
        {"key": "stanley-arches", "label": "Stanley Arches — Pill & arch geometry"},
        {"key": "souk-tiles", "label": "Souk Tiles — Geometric mosaic"},
        {"key": "sea-glass", "label": "Sea Glass — Deep frosted translucency"},
        {"key": "library-desk", "label": "Library Desk — Paper grain editorial"},
        {"key": "ink-rush", "label": "Ink Rush — Sumi-e comic borders"},
        {"key": "zen", "label": "Zen — Chromeless minimal pill"}
    ]

    SettingCard {
        title: I18n.tr("ARCHITECTURAL VISUAL IDENTITY (20 LOOKS)")
        subtitle: I18n.tr("Material 3 Expressive is Scy-Shell's primary design language; all 19 Mandara Looks remain selectable.")

        SettingRow {
            title: I18n.tr("Active Shell & Mandara Surface Look")
            description: I18n.tr("Harmonizes HCT/OKLCH palettes, Google Sans typography, corner radii and spring motion.")

            M3Dropdown {
                options: page.allLooks
                current: ScyBridge.presentations["primary_identity"] || "scy-m3-expressive"
                onChosen: (k) => ScyBridge.setPresentation("primary_identity", k)
            }
        }

        SettingRow {
            title: I18n.tr("Sync 28 External App Themes (SHA-256 Tamper-Safe)")
            description: I18n.tr("Updates GTK3/4, Qt5/6, Kitty, Ghostty, Foot, Alacritty, Zed, Helix, Neovim, Yazi, Btop, Cava & Vesktop without overwriting hand-edited files.")

            M3Button {
                text: I18n.tr("Sync App Themes")
                variant: "filled"
                iconPath: "palette"
                onClicked: Quickshell.execDetached(["scy-shell", "theme", "apply"])
            }
        }
    }
}
