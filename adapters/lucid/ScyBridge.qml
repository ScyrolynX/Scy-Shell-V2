pragma Singleton

import QtQuick
import Quickshell
import Quickshell.Io

// Scy-Shell Unified Core Bridge for Lucid 2 (Material 3 Expressive Engine)
// Watches ~/.local/state/scy-shell/{runtime-state,live-values}.json written atomically
// by scy-daemon / scy-shell and provides live value loading + immediate shell preview.
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
    property string lastPreviewColor: "#ffb1c4"
    property bool hyprTrialActive: false
    property string hyprTrialKey: ""

    readonly property bool managed: root.state && root.state.scy_gates ? root.state.scy_gates.managed_by_scy_shell === true : false
    readonly property var providers: (root.state && root.state.active_providers) ? root.state.active_providers : ({})
    readonly property var presentations: (root.state && root.state.presentations) ? root.state.presentations : ({})
    readonly property int overrideCount: (root.state && typeof root.state.override_count === "number") ? root.state.override_count : Object.keys(root.liveValues).length

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

    function getValue(scyId, fallbackValue) {
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

    function isModified(scyId, defaultValue) {
        void root.valuesRev;
        if (!root.liveValues || !Object.prototype.hasOwnProperty.call(root.liveValues, scyId))
            return false;
        return JSON.stringify(root.liveValues[scyId]) !== JSON.stringify(defaultValue);
    }

    function owns(domain) {
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
        return p === "lucid" || p === "hybrid";
    }

    function barActiveOn(screenName) {
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

    function dispatch(args) {
        Quickshell.execDetached(["scy-shell-ipc"].concat(args));
    }

    function setProvider(domain, provider) {
        Quickshell.execDetached(["scy-shell", "provider", domain, provider]);
    }

    function setPresentation(domain, val) {
        Quickshell.execDetached(["scy-shell", "presentation", domain, val]);
    }

    function setSetting(scyId, jsonValue, previewKind, origKey) {
        const nextMap = Object.assign({}, root.liveValues);
        nextMap[scyId] = jsonValue;
        root.liveValues = nextMap;
        root.valuesRev = root.valuesRev + 1;
        root.lastPreviewLabel = (origKey || scyId) + " = " + JSON.stringify(jsonValue);

        // Immediate in-memory live preview on Lucid QML shell properties
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

        Quickshell.execDetached(["scy-shell", "config", "set-json", scyId, JSON.stringify(jsonValue)]);
    }

    function resetSetting(scyId, defaultValue, origKey) {
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
