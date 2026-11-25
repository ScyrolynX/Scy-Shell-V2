pragma Singleton

import QtQuick
import Quickshell
import Quickshell.Io
import qs

// Scy-Shell v2.0 — Unified Core Bridge & Single-Owner Surface Orchestrator
// Watches ~/.local/state/scy-shell/{runtime-state,live-values}.json written atomically
// by scy-daemon / scy-shell and provides single-click dock switching, live preview,
// profile switching, layout presets, performance tiers, and all 2,026 unified settings.
Singleton {
    id: root

    readonly property string stateDir: {
        const xdgState = Quickshell.env("XDG_STATE_HOME");
        const base = (xdgState && xdgState !== "") ? xdgState : (Quickshell.env("HOME") + "/.local/state");
        return base + "/scy-shell";
    }
    readonly property string statePath: root.stateDir + "/runtime-state.json"
    readonly property string valuesPath: root.stateDir + "/live-values.json"

    property var state: ({})
    property var liveValues: ({})
    property int valuesRev: 0
    property string lastPreviewLabel: ""
    property string lastPreviewColor: "#7aa2f7"
    property bool hyprTrialActive: false
    property string hyprTrialKey: ""
    property bool livePreviewStagingMode: false

    readonly property bool managed: root.state && root.state.scy_gates ? root.state.scy_gates.managed_by_scy_shell === true : false
    readonly property var providers: (root.state && root.state.active_providers) ? root.state.active_providers : ({})
    readonly property var presentations: (root.state && root.state.presentations) ? root.state.presentations : ({})
    readonly property int overrideCount: (root.state && typeof root.state.override_count === "number") ? root.state.override_count : Object.keys(root.liveValues).length
    readonly property string activeProfile: (root.state && root.state.active_profile) ? String(root.state.active_profile) : String(root.getValue("scy.profiles.active", "balanced"))
    readonly property string performanceTier: (root.state && root.state.performance_tier) ? String(root.state.performance_tier) : String(root.getValue("scy.performance.tier", "balanced"))
    readonly property string dockOwner: (root.state && root.state.dock_owner) ? String(root.state.dock_owner) : String(root.providers["dock"] || "lucid")
    readonly property string dockMode: (root.state && root.state.dock_mode) ? String(root.state.dock_mode) : String(root.getValue("scy.dock.mode", "island"))
    readonly property bool previewActive: Boolean(root.state && root.state.preview_active)
    readonly property int previewChangeCount: (root.state && typeof root.state.preview_change_count === "number") ? root.state.preview_change_count : 0
    readonly property bool lazyStudioTabs: Boolean(root.getValue("scy.performance.lazy_studio_tabs", true))

    function reloadState() {
        const txt = stateFile.text();
        if (!txt || txt.trim() === "") {
            root.state = ({});
            return;
        }
        try {
            root.state = JSON.parse(txt);
            if (root.state.identity && root.state.identity.accent_seed)
                root.lastPreviewColor = String(root.state.identity.accent_seed);
        } catch (e) {
            console.warn("ScyBridge: invalid runtime-state.json:", e);
        }
    }

    function reloadValues() {
        const txt = valuesFile.text();
        if (!txt || txt.trim() === "") {
            root.liveValues = ({});
            root.valuesRev = root.valuesRev + 1;
            return;
        }
        try {
            const parsed = JSON.parse(txt);
            root.liveValues = (parsed && parsed.values) ? parsed.values : ({});
            root.valuesRev = root.valuesRev + 1;
        } catch (e) {
            console.warn("ScyBridge: invalid live-values.json:", e);
        }
    }

    function getValue(scyId: string, fallbackValue: var): var {
        void root.valuesRev;
        if (root.liveValues && Object.prototype.hasOwnProperty.call(root.liveValues, scyId))
            return root.liveValues[scyId];
        if (scyId.indexOf("scy.providers.lucid.prefs.") === 0 && typeof Prefs !== "undefined") {
            const prop = scyId.slice("scy.providers.lucid.prefs.".length);
            if (Prefs[prop] !== undefined)
                return Prefs[prop];
        }
        return fallbackValue;
    }

    function isModified(scyId: string, defaultValue: var): bool {
        void root.valuesRev;
        if (!root.liveValues || !Object.prototype.hasOwnProperty.call(root.liveValues, scyId))
            return false;
        return JSON.stringify(root.liveValues[scyId]) !== JSON.stringify(defaultValue);
    }

    function owns(domain: string): bool {
        if (!root.managed)
            return true;
        const p = root.providers[domain];
        if (p === undefined || p === null)
            return true;
        if (typeof p === "object") {
            for (const k in p) {
                if (p[k] === "lucid")
                    return true;
            }
            return false;
        }
        if (domain === "dock")
            return p === "lucid";
        return p === "lucid" || p === "hybrid";
    }

    function barActiveOn(screenName: string): bool {
        if (!root.managed)
            return true;
        const p = root.providers["bar"];
        if (p === undefined || p === null)
            return true;
        if (typeof p === "object" && screenName !== "")
            return p[screenName] === undefined ? true : (p[screenName] === "lucid");
        return p === "lucid" || p === "hybrid";
    }

    readonly property bool ownsToastRender: !root.managed || (root.presentations["toasts"] || "lucid") === "lucid"
    readonly property bool launcherFederation: !root.managed || (root.presentations["launcher_federation"] || "enabled") === "enabled"
    readonly property bool barPluginPill: root.managed && (root.presentations["lucid_bar_plugin_pill"] || "enabled") === "enabled"

    function dispatch(args: var) {
        Quickshell.execDetached(["scy-shell-ipc"].concat(args));
    }

    function openStudioSection(sectionKey: string) {
        Quickshell.execDetached(["qs", "ipc", "call", "settings", "show", sectionKey]);
    }

    // Single-click, zero-duplicate dock switching!
    function switchDock(targetModeOrEngine: string) {
        const nextState = Object.assign({}, root.state);
        const nextProv = Object.assign({}, root.providers);
        if (targetModeOrEngine === "off" || targetModeOrEngine === "none" || targetModeOrEngine === "disabled") {
            nextProv["dock"] = "none";
            nextState["dock_owner"] = "none";
            nextState["dock_mode"] = "disabled";
            if (typeof Prefs !== "undefined")
                Prefs.dockEnabled = false;
            Quickshell.execDetached(["scy-shell", "dock", "switch", "off"]);
        } else if (targetModeOrEngine === "mandara" || targetModeOrEngine === "rail") {
            nextProv["dock"] = "mandara";
            nextState["dock_owner"] = "mandara";
            nextState["dock_mode"] = "rail";
            if (typeof Prefs !== "undefined")
                Prefs.dockEnabled = false;
            Quickshell.execDetached(["scy-shell", "dock", "switch", "mandara"]);
        } else {
            nextProv["dock"] = "lucid";
            nextState["dock_owner"] = "lucid";
            nextState["dock_mode"] = targetModeOrEngine === "lucid" ? "island" : targetModeOrEngine;
            if (typeof Prefs !== "undefined") {
                Prefs.dockEnabled = true;
                if (targetModeOrEngine === "island" || targetModeOrEngine === "notch" || targetModeOrEngine === "split")
                    Prefs.dockStyle = targetModeOrEngine;
            }
            if (targetModeOrEngine === "island" || targetModeOrEngine === "notch" || targetModeOrEngine === "split")
                Quickshell.execDetached(["scy-shell", "config", "set", "scy.dock.mode", targetModeOrEngine]);
            else
                Quickshell.execDetached(["scy-shell", "dock", "switch", "lucid"]);
        }
        nextState["active_providers"] = nextProv;
        root.state = nextState;
        root.lastPreviewLabel = "Dock -> " + targetModeOrEngine;
    }

    function setProvider(domain: string, provider: string) {
        if (domain === "dock") {
            root.switchDock(provider);
            return;
        }
        const nextState = Object.assign({}, root.state);
        const nextProv = Object.assign({}, root.providers);
        nextProv[domain] = provider;
        nextState["active_providers"] = nextProv;
        root.state = nextState;
        Quickshell.execDetached(["scy-shell", "provider", domain, provider]);
    }

    function setPresentation(domain: string, val: string) {
        Quickshell.execDetached(["scy-shell", "presentation", domain, val]);
    }

    function setSetting(scyId: string, jsonValue: var, previewKind: string, origKey: string) {
        const nextMap = Object.assign({}, root.liveValues);
        nextMap[scyId] = jsonValue;
        root.liveValues = nextMap;
        root.valuesRev = root.valuesRev + 1;
        root.lastPreviewLabel = (origKey || scyId) + " = " + JSON.stringify(jsonValue);

        if (scyId === "scy.dock.mode") {
            root.switchDock(String(jsonValue));
            return;
        }

        if (scyId.indexOf("scy.providers.lucid.prefs.") === 0 && typeof Prefs !== "undefined") {
            const prop = origKey || scyId.slice("scy.providers.lucid.prefs.".length);
            if (Prefs[prop] !== undefined) {
                try {
                    Prefs[prop] = jsonValue;
                } catch (e) {}
            }
        }
        if (previewKind === "theme_accent" && typeof jsonValue === "string" && jsonValue.indexOf("#") === 0) {
            root.lastPreviewColor = jsonValue;
            if (origKey === "themeColour")
                Quickshell.execDetached(["scy-shell", "theme", "apply", "--seed", jsonValue]);
        } else if (previewKind === "hypr_trial") {
            root.hyprTrialActive = true;
            root.hyprTrialKey = origKey || scyId;
        }

        if (root.livePreviewStagingMode) {
            const patch = ({});
            patch[scyId] = jsonValue;
            Quickshell.execDetached(["scy-shell", "preview", "stage", "--changes", JSON.stringify(patch)]);
        } else {
            Quickshell.execDetached(["scy-shell", "config", "set-json", scyId, JSON.stringify(jsonValue)]);
        }
    }

    function resetSetting(scyId: string, defaultValue: var, origKey: string) {
        const nextMap = Object.assign({}, root.liveValues);
        delete nextMap[scyId];
        root.liveValues = nextMap;
        root.valuesRev = root.valuesRev + 1;
        root.lastPreviewLabel = (origKey || scyId) + " (reset)";

        if (scyId.indexOf("scy.providers.lucid.prefs.") === 0 && typeof Prefs !== "undefined") {
            const prop = origKey || scyId.slice("scy.providers.lucid.prefs.".length);
            if (Prefs[prop] !== undefined && defaultValue !== undefined) {
                try {
                    Prefs[prop] = defaultValue;
                } catch (e) {}
            }
        }
        Quickshell.execDetached(["scy-shell", "config", "reset", scyId]);
    }

    function resetSection(sectionId: string) {
        root.lastPreviewLabel = "Reset section " + sectionId;
        Quickshell.execDetached(["scy-shell", "config", "reset-section", sectionId]);
    }

    function applyProfile(profileId: string) {
        root.lastPreviewLabel = "Profile -> " + profileId;
        Quickshell.execDetached(["scy-shell", "profile", "apply", profileId]);
    }

    function saveCustomProfile(profileId: string, profileName: string) {
        root.lastPreviewLabel = "Saved profile: " + profileName;
        Quickshell.execDetached(["scy-shell", "profile", "create", profileId, "--name", profileName]);
    }

    function applyLayoutPreset(layoutId: string) {
        root.lastPreviewLabel = "Layout -> " + layoutId;
        Quickshell.execDetached(["scy-shell", "layout", "apply", layoutId]);
    }

    function applyPerformanceTier(tierId: string) {
        root.lastPreviewLabel = "Performance -> " + tierId;
        Quickshell.execDetached(["scy-shell", "performance", "apply", tierId]);
    }

    function commitPreview() {
        root.livePreviewStagingMode = false;
        root.lastPreviewLabel = "Committed staged preview";
        Quickshell.execDetached(["scy-shell", "preview", "commit"]);
    }

    function revertPreview() {
        root.livePreviewStagingMode = false;
        root.lastPreviewLabel = "Reverted staged preview";
        Quickshell.execDetached(["scy-shell", "preview", "revert"]);
    }

    function copyLockToLoginOnce() {
        root.lastPreviewLabel = "Copied Lock visual style to Login Greeter (one-time)";
        Quickshell.execDetached(["scy-shell", "preauth", "copy-lock-to-login-once"]);
    }

    function confirmHyprTrial() {
        root.hyprTrialActive = false;
        Quickshell.execDetached(["scy-shell", "hypr", "trial-confirm"]);
    }

    function revertHyprTrial() {
        root.hyprTrialActive = false;
        Quickshell.execDetached(["scy-shell", "hypr", "trial-revert"]);
    }

    FileView {
        id: stateFile
        path: root.statePath
        watchChanges: true
        printErrors: false
        onLoaded: root.reloadState()
        onFileChanged: {
            stateFile.reload();
            root.reloadState();
        }
    }

    FileView {
        id: valuesFile
        path: root.valuesPath
        watchChanges: true
        printErrors: false
        onLoaded: root.reloadValues()
        onFileChanged: {
            valuesFile.reload();
            root.reloadValues();
        }
    }

    IpcHandler {
        target: "scy"

        function reload(): void {
            stateFile.reload();
            valuesFile.reload();
            root.reloadState();
            root.reloadValues();
        }

        function status(): string {
            return root.managed ? "managed" : "standalone";
        }
    }
}
