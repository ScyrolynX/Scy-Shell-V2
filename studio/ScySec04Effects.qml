pragma ComponentBehavior: Bound

import qs

ScyStudioSectionBase {
    id: sec
    sectionId: "04-visual-effects"
    sectionTitle: I18n.tr("GLASS, BLUR, SHADER & ANIMATION SETTINGS")
    sectionSubtitle: I18n.tr("Fine-tune backdrop blur passes, surface translucency, specular borders, drop shadows, shaders, and spring physics.")
    deepLinks: [
        {"label": I18n.tr("Per-Application Window & Terminal Glass"), "pageKey": "glass"}
    ]

    SettingCard {
        title: I18n.tr("SCY GLASS MATERIALS & MOTION PHYSICS")
        subtitle: I18n.tr("Unified material and animation presets synchronized across Hyprland 0.57+ layer rules and shell chrome.")

        SettingRow {
            title: I18n.tr("Shell Material Preset")
            description: I18n.tr("Select frosted Kawase glass, deep refractive Liquid Crystal, opaque Obsidian Matte, Tinted Acrylic, or Crisp Flat.")

            M3Dropdown {
                options: [
                    {"key": "scy-frosted", "label": I18n.tr("Scy Frosted Glass")},
                    {"key": "liquid-crystal", "label": I18n.tr("Liquid Crystal")},
                    {"key": "obsidian-matte", "label": I18n.tr("Obsidian Matte")},
                    {"key": "tinted-acrylic", "label": I18n.tr("Tinted Acrylic")},
                    {"key": "minimal-flat", "label": I18n.tr("Crisp Flat")}
                ]
                current: String(ScyBridge.getValue("scy.effects.material_preset", "scy-frosted"))
                onChosen: (k) => ScyBridge.setSetting("scy.effects.material_preset", String(k), "instant", "material_preset")
            }
        }

        SettingRow {
            title: I18n.tr("Spring & Motion Preset")
            description: I18n.tr("Controls spring stiffness, damping, and transition duration across bars, dock magnification, drawers, and workspaces.")

            M3Dropdown {
                options: [
                    {"key": "expressive-spring", "label": I18n.tr("Expressive Spring")},
                    {"key": "fluid-silk", "label": I18n.tr("Fluid Silk")},
                    {"key": "crisp-snappy", "label": I18n.tr("Crisp Snappy")},
                    {"key": "minimal", "label": I18n.tr("Minimal")},
                    {"key": "instant", "label": I18n.tr("Instant (0ms)")}
                ]
                current: String(ScyBridge.getValue("scy.effects.motion_preset", "expressive-spring"))
                onChosen: (k) => ScyBridge.setSetting("scy.effects.motion_preset", String(k), "instant", "motion_preset")
            }
        }

        SettingRow {
            title: I18n.tr("Post-Processing Shader Tone")
            description: I18n.tr("Optional subtle visual grading without hurting text legibility.")

            M3Dropdown {
                options: [
                    {"key": "none", "label": I18n.tr("None (Native Color)")},
                    {"key": "subtle-grain", "label": I18n.tr("Subtle Film Grain")},
                    {"key": "warm-cinema", "label": I18n.tr("Warm Cinema")},
                    {"key": "high-contrast", "label": I18n.tr("Crisp High Contrast")}
                ]
                current: String(ScyBridge.getValue("scy.effects.shader_preset", "none"))
                onChosen: (k) => ScyBridge.setSetting("scy.effects.shader_preset", String(k), "instant", "shader_preset")
            }
        }
    }
}
