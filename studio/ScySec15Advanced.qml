pragma ComponentBehavior: Bound

import Quickshell
import qs

ScyStudioSectionBase {
    id: sec
    sectionId: "15-advanced"
    sectionTitle: I18n.tr("ADVANCED ENGINE & PERSISTENCE SETTINGS")
    sectionSubtitle: I18n.tr("Low-level subsystem diagnostics, snapshot backups, Hyprland 0.57+ autostart deduplication, and full 2,026-setting registry.")
    deepLinks: [
        {"label": I18n.tr("Conflict Inspector & System Doctor"), "pageKey": "scy-conflicts"},
        {"label": I18n.tr("Full 2,026-Setting Registry Vault"), "pageKey": "scy-vault"},
        {"label": I18n.tr("Shell Language & Translations"), "pageKey": "language"},
        {"label": I18n.tr("Hardware & OS System Information"), "pageKey": "systeminfo"}
    ]

    SettingCard {
        title: I18n.tr("RECOVERY, SNAPSHOTS & PERSISTENCE RECONCILIATION")
        subtitle: I18n.tr("Atomic SHA-256 ledger persistence ensures settings never vanish across logout/login. Create snapshots or re-emit compositor rules anytime.")

        SettingRow {
            title: I18n.tr("Create Recoverable Configuration Snapshot")
            description: I18n.tr("Saves an atomic timestamped backup under ~/.local/state/scy-shell/backups/.")

            M3Button {
                text: I18n.tr("Create Backup Now")
                variant: "filled"
                onClicked: {
                    ScyBridge.lastPreviewLabel = "Created manual snapshot backup";
                    Quickshell.execDetached(["scy-shell", "backup", "create", "studio-manual"]);
                }
            }
        }

        SettingRow {
            title: I18n.tr("Re-Emit Hyprland 0.57+ Rules & Deduplicate Autostart")
            description: I18n.tr("Regenerates scy-shell.conf + init.lua with modern layerrule syntax and neutralizes duplicate shell spawns.")

            M3Button {
                text: I18n.tr("Sync Hyprland 0.57+")
                variant: "tonal"
                onClicked: {
                    ScyBridge.lastPreviewLabel = "Synced Hyprland 0.57+ modular rules";
                    Quickshell.execDetached(["scy-shell", "hypr", "emit"]);
                }
            }
        }
    }
}
