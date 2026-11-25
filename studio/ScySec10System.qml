pragma ComponentBehavior: Bound

import qs

ScyStudioSectionBase {
    id: sec
    sectionId: "10-system-hardware"
    sectionTitle: I18n.tr("SYSTEM, DISPLAYS, AUDIO, POWER & PERFORMANCE SETTINGS")
    sectionSubtitle: I18n.tr("Hardware-aware performance tiers, display arrangement & refresh rate, PipeWire audio, Wi-Fi, Bluetooth, idle, and storage.")
    deepLinks: [
        {"label": I18n.tr("Displays, Refresh Rate & Arrangement"), "pageKey": "displays"},
        {"label": I18n.tr("PipeWire Audio & App Mixer"), "pageKey": "sound"},
        {"label": I18n.tr("Wi-Fi, Ethernet & VPN"), "pageKey": "network"},
        {"label": I18n.tr("Bluetooth Devices"), "pageKey": "bluetooth"},
        {"label": I18n.tr("KDE Connect Phone Bridge"), "pageKey": "kdeconnect"},
        {"label": I18n.tr("Idle, Sleep & Caffeine"), "pageKey": "idle"},
        {"label": I18n.tr("Date, Time & World Clocks"), "pageKey": "datetime"},
        {"label": I18n.tr("Storage & Drive Health"), "pageKey": "storage"}
    ]

    readonly property string tierTradeoff: {
        const t = ScyBridge.performanceTier;
        if (t === "max-quality")
            return I18n.tr("4-pass Kawase blur (radius 10), full multi-layer shadows, specular glow, and spring physics (~3–5% GPU).");
        if (t === "performance")
            return I18n.tr("1-pass fast blur (radius 4), 0 outer shadows/glow, crisp snappy curves, and fullscreen VRR for high-Hz displays.");
        if (t === "battery")
            return I18n.tr("Opaque Obsidian Matte surfaces (0 blur passes), reduced motion, and minimal background wakeups for laptop battery life.");
        return I18n.tr("3-pass frosted glass (radius 8), medium shadows, expressive springs, and lazy offscreen Studio tab unloading.");
    }

    SettingCard {
        title: I18n.tr("SCY INTELLIGENT PERFORMANCE ADVISOR")
        subtitle: sec.tierTradeoff

        SettingRow {
            title: I18n.tr("Active Performance & Efficiency Tier")
            description: I18n.tr("Every visual/GPU trade-off is transparent above and can still be overridden individually below.")

            M3Dropdown {
                options: [
                    {"key": "max-quality", "label": I18n.tr("Maximum Visual Quality")},
                    {"key": "balanced", "label": I18n.tr("Balanced (Recommended)")},
                    {"key": "performance", "label": I18n.tr("Performance (High-Hz / Gaming)")},
                    {"key": "battery", "label": I18n.tr("Battery Efficiency")}
                ]
                current: ScyBridge.performanceTier
                onChosen: (k) => ScyBridge.applyPerformanceTier(String(k))
            }
        }

        SettingRow {
            title: I18n.tr("Variable Refresh Rate (VRR / Adaptive Sync)")
            description: I18n.tr("Synchronizes Hyprland 0.57+ misc:vrr policy.")

            M3Segmented {
                options: [
                    {"key": "off", "label": I18n.tr("Off")},
                    {"key": "fullscreen-only", "label": I18n.tr("Fullscreen / Games")},
                    {"key": "on", "label": I18n.tr("Always On")}
                ]
                current: String(ScyBridge.getValue("scy.performance.vrr_policy", "fullscreen-only"))
                onChosen: (k) => ScyBridge.setSetting("scy.performance.vrr_policy", String(k), "instant", "vrr_policy")
            }
        }
    }
}
