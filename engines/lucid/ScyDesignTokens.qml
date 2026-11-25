pragma Singleton

import QtQuick
import Quickshell
import Quickshell.Io
import qs

// Scy-Shell v2.0 — Centralized Unified Design Token System
// Synchronizes typography, palette harmony, frosted glass materials, spring motion,
// spatial layout scales, Dynamic Island, Dock Studio, Lock Screen, and Login tokens.
Singleton {
    id: root

    readonly property string tokensPath: ScyBridge.stateDir + "/design-tokens.json"
    property var doc: ({})
    property int rev: 0

    readonly property var typography: root.doc && root.doc.typography ? root.doc.typography : ({})
    readonly property var colors: root.doc && root.doc.colors ? root.doc.colors : ({})
    readonly property var materials: root.doc && root.doc.materials ? root.doc.materials : ({})
    readonly property var motion: root.doc && root.doc.motion ? root.doc.motion : ({})
    readonly property var layout: root.doc && root.doc.layout ? root.doc.layout : ({})
    readonly property var dynamicIsland: root.doc && root.doc.dynamic_island ? root.doc.dynamic_island : ({})
    readonly property var dock: root.doc && root.doc.dock ? root.doc.dock : ({})
    readonly property var lockScreen: root.doc && root.doc.lock_screen ? root.doc.lock_screen : ({})
    readonly property var loginExperience: root.doc && root.doc.login_experience ? root.doc.login_experience : ({})

    // Resolved Typography Tokens
    readonly property string displayFont: String(root.typography.display_font || Theme.fontFamily)
    readonly property string uiFont: String(root.typography.ui_font || Theme.fontFamily)
    readonly property string monoFont: String(root.typography.mono_font || "JetBrains Mono")
    readonly property int headingWeight: Number(root.typography.heading_weight || 700)

    // Resolved Material & Glass Tokens
    readonly property string materialPreset: String(root.materials.preset || "scy-frosted")
    readonly property real bgOpacity: root.materials.bg_opacity !== undefined ? Number(root.materials.bg_opacity) : 0.86
    readonly property real surfaceOpacity: root.materials.surface_opacity !== undefined ? Number(root.materials.surface_opacity) : 0.92
    readonly property int blurStrength: root.materials.blur_strength !== undefined ? Number(root.materials.blur_strength) : 3
    readonly property int blurRadius: root.materials.blur_radius !== undefined ? Number(root.materials.blur_radius) : 8
    readonly property int borderThickness: root.materials.border_thickness !== undefined ? Number(root.materials.border_thickness) : 1
    readonly property real borderOpacity: root.materials.border_opacity !== undefined ? Number(root.materials.border_opacity) : 0.28
    readonly property real glowIntensity: root.materials.glow_intensity !== undefined ? Number(root.materials.glow_intensity) : 0.20

    // Resolved Motion & Layout Scale Tokens
    readonly property string motionPreset: String(root.motion.preset || "expressive-spring")
    readonly property real durationScale: root.motion.duration_scale !== undefined ? Number(root.motion.duration_scale) : 1.0
    readonly property real cornerRadiusScale: root.layout.corner_radius_scale !== undefined ? Number(root.layout.corner_radius_scale) : 1.0
    readonly property real spacingScale: root.layout.spacing_scale !== undefined ? Number(root.layout.spacing_scale) : 1.0

    // Dynamic Island Tokens
    readonly property bool islandEnabled: root.dynamicIsland.enabled !== undefined ? Boolean(root.dynamicIsland.enabled) : true
    readonly property string islandMode: String(root.dynamicIsland.mode || "adaptive-pill")
    readonly property int islandWidth: Number(root.dynamicIsland.width || 220)
    readonly property int islandHeight: Number(root.dynamicIsland.height || 34)
    readonly property bool islandShowTimer: root.dynamicIsland.show_timer !== undefined ? Boolean(root.dynamicIsland.show_timer) : true

    function rad(px: real): int {
        return Math.max(4, Math.round(Theme.rad(px) * root.cornerRadiusScale));
    }

    function dur(ms: int): int {
        return Math.max(0, Math.round(ms * root.durationScale));
    }

    function reload() {
        const txt = tokFile.text();
        if (!txt || txt.trim() === "")
            return;
        try {
            root.doc = JSON.parse(txt);
            root.rev = root.rev + 1;
        } catch (e) {
            console.warn("ScyDesignTokens: invalid design-tokens.json:", e);
        }
    }

    FileView {
        id: tokFile
        path: root.tokensPath
        watchChanges: true
        printErrors: false
        onLoaded: root.reload()
        onFileChanged: {
            tokFile.reload();
            root.reload();
        }
    }
}
