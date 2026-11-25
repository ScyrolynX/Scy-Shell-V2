pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import qs

ScyStudioSectionBase {
    id: sec
    sectionId: "13-productivity"
    sectionTitle: I18n.tr("APPLICATIONS, LAUNCHER, AI & PRODUCTIVITY SETTINGS")
    sectionSubtitle: I18n.tr("Calculator & unit converter, ? web search, Focus/Pomodoro timer, Quick Notes, 28-app theming, Local AI, and Game Shelf.")
    deepLinks: [
        {"label": I18n.tr("Screenshots, OCR & Screen Recording"), "pageKey": "capture"},
        {"label": I18n.tr("Local AI Agent & 3D Game Shelf"), "pageKey": "scy-ai"},
        {"label": I18n.tr("89 Built-in & WASM Plugins"), "pageKey": "scy-plugins"},
        {"label": I18n.tr("Startup Apps & Session Env"), "pageKey": "startup"}
    ]

    SettingCard {
        title: I18n.tr("SCY PRODUCTIVITY LAYER")
        subtitle: I18n.tr("Built-in calculator/converter, ? web search, clipboard vault, OCR captures, and Dynamic Island Focus Timer.")

        SettingRow {
            title: I18n.tr("Focus / Pomodoro Timer (Dynamic Island Synced)")
            description: I18n.tr("Start or stop a Focus sprint directly in the top Dynamic Island capsule.")

            Row {
                spacing: Theme.dp(8)

                M3Button {
                    text: I18n.tr("Start 25m Focus")
                    variant: "filled"
                    onClicked: Quickshell.execDetached(["scy-shell", "productivity", "timer-start", "25"])
                }

                M3Button {
                    text: I18n.tr("Stop Timer")
                    variant: "tonal"
                    onClicked: Quickshell.execDetached(["scy-shell", "productivity", "timer-stop"])
                }
            }
        }

        SettingRow {
            title: I18n.tr("Launcher ? Web Search Engine")
            description: I18n.tr("Provider opened when typing '? <query>' in the command launcher.")

            M3Dropdown {
                options: [
                    {"key": "duckduckgo", "label": "DuckDuckGo"},
                    {"key": "brave", "label": "Brave Search"},
                    {"key": "kagi", "label": "Kagi"},
                    {"key": "google", "label": "Google"},
                    {"key": "searxng", "label": "Local SearXNG"}
                ]
                current: String(ScyBridge.getValue("scy.productivity.web_search_provider", "duckduckgo"))
                onChosen: (k) => ScyBridge.setSetting("scy.productivity.web_search_provider", String(k), "instant", "web_search_provider")
            }
        }
    }
}
