pragma ComponentBehavior: Bound

import QtQuick
import qs

ScyStudioSectionBase {
    id: sec
    sectionId: "14-profiles"
    sectionTitle: I18n.tr("PROFILE & SNAPSHOT OPTIONS")
    sectionSubtitle: I18n.tr("Switch complete desktop profiles in one click, or capture your current desktop into a reusable custom profile.")

    property string customProfileName: ""

    readonly property var builtinProfiles: [
        {"id": "balanced", "name": I18n.tr("Balanced (Scy Default)"), "desc": I18n.tr("Top floating island bar, bottom Lucid glass dock, Dynamic Island, frosted Kawase glass, and balanced spring physics.")},
        {"id": "minimal", "name": I18n.tr("Minimal Zen"), "desc": I18n.tr("Compact top bar, auto-hidden dock, Clean Slate desktop, tight tiling gaps, and calm minimal motion.")},
        {"id": "productivity", "name": I18n.tr("Productivity Focus"), "desc": I18n.tr("Left vertical rail dock, top status strip, active Focus Timer in Dynamic Island, and agenda/notes widgets.")},
        {"id": "immersive", "name": I18n.tr("Immersive Liquid Glass"), "desc": I18n.tr("Liquid Crystal deep blur, split floating dock with magnification wave, generous gaps, and fluid silk animations.")},
        {"id": "gaming", "name": I18n.tr("Gaming Low-Latency"), "desc": I18n.tr("Fullscreen VRR enabled, auto-dodging chrome, 1-pass fast blur, crisp 0-lag transitions, and DND ready.")},
        {"id": "creative", "name": I18n.tr("Creative Studio"), "desc": I18n.tr("Neutral color-accurate surfaces, carved bottom notch dock, and System Telemetry Pro cards.")},
        {"id": "cinema", "name": I18n.tr("Cinema OLED"), "desc": I18n.tr("Deep OLED dark surfaces, auto-hiding bar & dock, warm cinema shader tone, and dimmed inactive windows.")}
    ]

    SettingCard {
        title: I18n.tr("SCY COMPLETE DESKTOP PROFILES (8 MODES)")
        subtitle: I18n.tr("Each profile orchestrates layout, bar, dock, materials, animations, tiling gaps, widgets, and performance together — never just colors.")

        Repeater {
            model: sec.builtinProfiles

            SettingRow {
                id: profRow
                required property var modelData
                title: profRow.modelData.name
                description: profRow.modelData.desc

                M3Button {
                    text: ScyBridge.activeProfile === profRow.modelData.id ? I18n.tr("Active ✓") : I18n.tr("Apply Profile")
                    variant: ScyBridge.activeProfile === profRow.modelData.id ? "filled" : "tonal"
                    onClicked: ScyBridge.applyProfile(String(profRow.modelData.id))
                }
            }
        }

        SettingRow {
            id: saveRow
            title: I18n.tr("Save Current Desktop as Custom Profile")
            description: I18n.tr("Stores a portable .scyprofile.json in ~/.config/scy-shell/profiles/ ready for export or sharing.")
            stacked: true

            Row {
                spacing: Theme.dp(10)

                M3TextField {
                    width: Math.max(Theme.dp(240), saveRow.width - Theme.dp(180))
                    placeholder: I18n.tr("e.g. Ultrawide Coding Setup")
                    onEdited: (v) => sec.customProfileName = v
                }

                M3Button {
                    text: I18n.tr("Save Custom")
                    variant: "filled"
                    onClicked: {
                        const nm = sec.customProfileName.trim() !== "" ? sec.customProfileName.trim() : "custom-desktop";
                        const slug = nm.toLowerCase().replace(/[^a-z0-9_-]+/g, "-");
                        ScyBridge.saveCustomProfile(slug, nm);
                    }
                }
            }
        }
    }
}
