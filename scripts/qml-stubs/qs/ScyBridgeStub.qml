pragma Singleton
import QtQuick

QtObject {
    property string stateDir: "/tmp/scy-shell"
    property bool managed: true
    property var providers: ({})
    property var presentations: ({})
    property var liveValues: ({})
    property int valuesRev: 0
    property int overrideCount: 0
    property string activeProfile: "balanced"
    property string performanceTier: "balanced"
    property string dockOwner: "lucid"
    property string dockMode: "island"
    property bool previewActive: false
    property int previewChangeCount: 0
    property bool lazyStudioTabs: true
    property bool livePreviewStagingMode: false
    property string lastPreviewLabel: ""
    property string lastPreviewColor: "#7aa2f7"
    property bool hyprTrialActive: false
    property string hyprTrialKey: ""
    property bool ownsToastRender: true
    property bool launcherFederation: true
    property bool barPluginPill: true
    function getValue(scyId: string, fallbackValue: var): var { return fallbackValue; }
    function isModified(scyId: string, defaultValue: var): bool { return false; }
    function owns(domain: string): bool { return true; }
    function barActiveOn(screenName: string): bool { return true; }
    function dispatch(args: var) {}
    function openStudioSection(sectionKey: string) {}
    function switchDock(targetModeOrEngine: string) {}
    function setProvider(domain: string, provider: string) {}
    function setPresentation(domain: string, val: string) {}
    function setSetting(scyId: string, jsonValue: var, previewKind: string, origKey: string) {}
    function resetSetting(scyId: string, defaultValue: var, origKey: string) {}
    function resetSection(sectionId: string) {}
    function applyProfile(profileId: string) {}
    function saveCustomProfile(profileId: string, profileName: string) {}
    function applyLayoutPreset(layoutId: string) {}
    function applyPerformanceTier(tierId: string) {}
    function commitPreview() {}
    function revertPreview() {}
    function copyLockToLoginOnce() {}
    function confirmHyprTrial() {}
    function revertHyprTrial() {}
}
