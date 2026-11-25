pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import Quickshell.Io
import qs

Column {
    id: page

    spacing: Theme.dp(26)
    property string filterText: ""
    property var allPlugins: []
    readonly property var filteredPlugins: {
        const q = page.filterText.trim().toLowerCase();
        if (q === "")
            return page.allPlugins;
        return page.allPlugins.filter((p) => {
            return p.id.toLowerCase().indexOf(q) !== -1 || p.name.toLowerCase().indexOf(q) !== -1;
        });
    }

    FileView {
        id: plugFile
        path: Quickshell.shellPath("scy-schema/plugins_catalogue.json")
        printErrors: false
        onLoaded: {
            try {
                page.allPlugins = JSON.parse(plugFile.text());
            } catch (e) {}
        }
    }

    SettingCard {
        title: I18n.tr("MANDARA 89 BUILT-IN & WASM PLUGINS")
        subtitle: I18n.tr("Sandboxed wasm32-wasip2 Wasmtime host + 89 built-in desktop, bar and launcher plugins.")

        SettingRow {
            id: filterRow
            title: I18n.tr("Filter Plugins (%1 loaded)", page.allPlugins.length)
            description: I18n.tr("Also accessible anytime from Lucid's Launcher by typing @<plugin-name>.")
            stacked: true

            M3TextField {
                width: filterRow.width
                placeholder: I18n.tr("Search Docker, Tailscale, Pomodoro, Prayer, Weather, Ports, Git…")
                onEdited: (v) => page.filterText = v
            }
        }

        Repeater {
            model: page.filteredPlugins.slice(0, 45)

            SettingRow {
                id: plugRow
                required property var modelData
                title: plugRow.modelData.name + " (" + plugRow.modelData.id + ")"
                description: plugRow.modelData.description || plugRow.modelData.kind

                M3Button {
                    text: I18n.tr("Toggle Panel")
                    variant: "tonal"
                    onClicked: Quickshell.execDetached(["mandara", "msg", "panel", "toggle", plugRow.modelData.id])
                }
            }
        }
    }
}
