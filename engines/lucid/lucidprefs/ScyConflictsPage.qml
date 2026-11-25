pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import Quickshell.Io
import qs

Column {
    id: page

    spacing: Theme.dp(26)
    property var report: ({ "conflict_count": 0, "critical_count": 0, "items": [] })
    property string doctorOutput: ""

    function refreshScan() {
        scanProc.running = true;
    }

    Component.onCompleted: page.refreshScan()

    Process {
        id: scanProc
        command: ["scy-shell", "conflicts", "--json"]
        stdout: StdioCollector {
            id: scanOut
            onStreamFinished: {
                try {
                    page.report = JSON.parse(scanOut.text);
                } catch (e) {}
            }
        }
    }

    Process {
        id: docProc
        command: ["scy-shell", "doctor"]
        stdout: StdioCollector {
            id: docOut
            onStreamFinished: page.doctorOutput = docOut.text.trim()
        }
    }

    SettingCard {
        title: I18n.tr("CONFLICT & HEALTH INSPECTOR")
        subtitle: I18n.tr("Scans D-Bus owners, /proc daemons, Wayland layer namespaces, Display Managers and Hyprland keybinds.")

        SettingRow {
            title: page.report.conflict_count === 0 ? I18n.tr("Zero active resource conflicts detected") : I18n.tr("%1 resource conflicts require attention", page.report.conflict_count)
            description: I18n.tr("Scy-Shell never kills user daemons or overwrites autostart files without explicit consent.")

            M3Button {
                text: I18n.tr("Re-scan Now")
                variant: "filled"
                iconPath: "refresh"
                onClicked: page.refreshScan()
            }
        }

        Repeater {
            model: page.report.items || []

            SettingRow {
                id: cfRow
                required property var modelData
                title: cfRow.modelData.domain + " — " + cfRow.modelData.owner
                description: cfRow.modelData.summary
                warning: cfRow.modelData.severity === "critical" ? I18n.tr("Critical exclusive protocol collision") : ""

                M3Button {
                    text: I18n.tr("Sync Gates")
                    variant: "tonal"
                    onClicked: {
                        Quickshell.execDetached(["scy-shell", "conflicts", "--resync"]);
                        page.refreshScan();
                    }
                }
            }
        }
    }

    SettingCard {
        title: I18n.tr("SYSTEM DOCTOR & BACKUP TIME-MACHINE")
        subtitle: I18n.tr("Verify CachyOS / Hyprland dependencies, GPU backend, portals and configuration backups.")

        SettingRow {
            title: I18n.tr("Run Scy-Shell Doctor")
            description: page.doctorOutput !== "" ? page.doctorOutput : I18n.tr("Checks Quickshell, Mandara, Hyprland, portals, fonts and config ledger integrity.")
            stacked: page.doctorOutput !== ""

            M3Button {
                text: I18n.tr("Run Diagnostics")
                variant: "tonal"
                iconPath: "health_and_safety"
                onClicked: docProc.running = true
            }
        }

        SettingRow {
            title: I18n.tr("Create Timestamped Snapshot Backup")
            description: I18n.tr("Saves Scy-Shell, Lucid, Mandara and Hyprland configs into ~/.local/share/scy-shell/backups/.")

            M3Button {
                text: I18n.tr("Backup Now")
                variant: "outlined"
                iconPath: "save"
                onClicked: Quickshell.execDetached(["scy-shell", "backup", "create", "studio-manual"])
            }
        }
    }
}
