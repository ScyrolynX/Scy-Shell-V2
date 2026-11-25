pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import Quickshell.Io
import qs

Column {
    id: page

    spacing: Theme.dp(22)
    property string projectFilter: "all"
    property string categoryFilter: "all"
    property bool modifiedOnly: false
    property string query: ""
    property var scyList: []
    property var lucidList: []
    property var mandaraList: []

    readonly property var accentPresets: ["#ffb1c4", "#7aa2f7", "#10b981", "#f59e0b", "#a855f7", "#ef4444"]

    readonly property var categoryOptions: {
        const seen = {};
        const all = page.scyList.concat(page.lucidList).concat(page.mandaraList);
        for (let i = 0; i < all.length; i++) {
            const cat = (all[i].category || "general").split(".")[0];
            seen[cat] = (seen[cat] || 0) + 1;
        }
        const keys = Object.keys(seen).sort();
        const opts = [{"key": "all", "label": I18n.tr("All Categories (%1)", all.length)}];
        for (let j = 0; j < keys.length; j++) {
            opts.push({"key": keys[j], "label": keys[j] + " (" + seen[keys[j]] + ")"});
        }
        return opts;
    }

    readonly property var combined: {
        void ScyBridge.valuesRev;
        let src = [];
        if (page.projectFilter === "all")
            src = page.scyList.concat(page.lucidList).concat(page.mandaraList);
        else if (page.projectFilter === "scy")
            src = page.scyList;
        else if (page.projectFilter === "lucid")
            src = page.lucidList;
        else
            src = page.mandaraList;

        const cf = page.categoryFilter;
        const modOnly = page.modifiedOnly;
        const q = page.query.trim().toLowerCase();

        return src.filter((item) => {
            if (cf !== "all") {
                const topCat = (item.category || "general").split(".")[0];
                if (topCat !== cf)
                    return false;
            }
            if (modOnly && !ScyBridge.isModified(item.scy_id, item.default_value))
                return false;
            if (q === "")
                return true;
            return item.scy_id.toLowerCase().indexOf(q) !== -1
                || item.original_key.toLowerCase().indexOf(q) !== -1
                || (item.label && item.label.toLowerCase().indexOf(q) !== -1)
                || (item.category && item.category.toLowerCase().indexOf(q) !== -1)
                || (item.storage && item.storage.toLowerCase().indexOf(q) !== -1);
        });
    }

    function isValidHexColor(s) {
        return /^#([0-9a-fA-F]{6}|[0-9a-fA-F]{8})$/.test(String(s).trim());
    }

    function isValidTime24(s) {
        return /^([01][0-9]|2[0-3]):[0-5][0-9]$/.test(String(s).trim());
    }

    FileView {
        id: catFile
        path: Quickshell.shellPath("scy-schema/settings_catalogue.json")
        printErrors: false
        onLoaded: {
            try {
                const parsed = JSON.parse(catFile.text());
                page.scyList = parsed.scy_settings || [];
                page.lucidList = parsed.lucid_settings || [];
                page.mandaraList = parsed.mandara_settings || [];
            } catch (e) {}
        }
    }

    SettingCard {
        title: I18n.tr("TYPE-AWARE 2,026-SETTING UNIFIED STUDIO REGISTRY")
        subtitle: I18n.tr("Loads live values across all Scy-Shell, desktop surface, and subsystem stores with native switches, bounded sliders, enum pickers, color validation, and instant live preview.")

        SettingRow {
            title: I18n.tr("Registry Scope (%1 shown · %2 customized)", page.combined.length, ScyBridge.overrideCount)
            description: I18n.tr("Every setting persists atomically with SHA-256 ledger reconciliation across logins.")

            M3Dropdown {
                options: [
                    {"key": "all", "label": I18n.tr("All Unified Settings (2,026)")},
                    {"key": "scy", "label": I18n.tr("Scy-Native Studio (151)")},
                    {"key": "lucid", "label": I18n.tr("Surface & Desktop Chrome (643)")},
                    {"key": "mandara", "label": I18n.tr("Plugins, Shaders & Subsystems (1,232)")}
                ]
                current: page.projectFilter
                onChosen: (k) => page.projectFilter = String(k)
            }
        }

        SettingRow {
            title: I18n.tr("Subsystem Category")
            description: I18n.tr("Filter by bar, appearance, dock, launcher, lockscreen, hypr, wallgen, greeter or plugins.")

            M3Dropdown {
                options: page.categoryOptions
                current: page.categoryFilter
                onChosen: (k) => page.categoryFilter = String(k)
            }
        }

        SettingRow {
            title: I18n.tr("Show Customized Settings Only")
            description: I18n.tr("Inspect only keys that differ from upstream defaults.")

            M3Switch {
                checked: page.modifiedOnly
                onToggled: (v) => page.modifiedOnly = v
            }
        }

        SettingRow {
            id: searchRow
            title: I18n.tr("Instant Registry Search")
            description: I18n.tr("Search by label, Scy-Shell ID, JSON pointer (/bar/height), Prefs key or target config file.")
            stacked: true

            M3TextField {
                width: searchRow.width
                placeholder: I18n.tr("Search e.g. gaps_in, barStyle, capsule_fill, lockWidget, themeColour, wallgen…")
                onEdited: (v) => page.query = v
            }
        }

        // Live Preview & Hyprland 15s Safety Trial Bar
        SettingRow {
            visible: ScyBridge.lastPreviewLabel !== "" || ScyBridge.hyprTrialActive
            title: ScyBridge.hyprTrialActive
                ? I18n.tr("Hyprland Live Trial Active: %1", ScyBridge.hyprTrialKey)
                : I18n.tr("Live Preview Applied: %1", ScyBridge.lastPreviewLabel)
            description: ScyBridge.hyprTrialActive
                ? I18n.tr("Keep this compositor change or revert immediately to your pre-trial snapshot.")
                : I18n.tr("Synced atomically to Scy-Shell Core and native engine storage.")

            Row {
                spacing: Theme.dp(8)

                Rectangle {
                    width: Theme.dp(28)
                    height: Theme.dp(28)
                    radius: Theme.dp(14)
                    color: page.isValidHexColor(ScyBridge.lastPreviewColor) ? ScyBridge.lastPreviewColor : Theme.accent
                    border.width: 1
                    border.color: Theme.outline
                }

                M3Button {
                    visible: ScyBridge.hyprTrialActive
                    text: I18n.tr("Keep")
                    variant: "filled"
                    onClicked: ScyBridge.confirmHyprTrial()
                }

                M3Button {
                    visible: ScyBridge.hyprTrialActive
                    text: I18n.tr("Revert")
                    variant: "tonal"
                    destructive: true
                    onClicked: ScyBridge.revertHyprTrial()
                }
            }
        }
    }

    // Virtualized ListView rendering type-aware controls for all 1,875 settings
    Rectangle {
        id: vaultBox
        width: page.width
        height: Theme.dp(620)
        radius: Theme.rad(26)
        color: Theme.withBlur(Theme.bgTile)
        clip: true

        ListView {
            id: vaultView
            anchors.fill: vaultBox
            anchors.margins: Theme.dp(12)
            spacing: Theme.dp(8)
            model: page.combined

            delegate: Rectangle {
                id: rowCard
                required property var modelData

                readonly property string widgetKind: rowCard.modelData.ui_widget || "text"
                readonly property string cType: rowCard.modelData.concrete_type || "string"
                readonly property var curVal: ScyBridge.getValue(rowCard.modelData.scy_id, rowCard.modelData.default_value)
                readonly property bool modified: ScyBridge.isModified(rowCard.modelData.scy_id, rowCard.modelData.default_value)
                readonly property bool hasSpecialDefault: rowCard.modelData.special_default !== undefined && rowCard.modelData.special_default !== null
                readonly property real specialSentinel: rowCard.hasSpecialDefault ? Number(rowCard.modelData.special_default.value) : 0
                readonly property string specialLabel: (rowCard.hasSpecialDefault && rowCard.modelData.special_default.label) ? String(rowCard.modelData.special_default.label) : "Auto"
                readonly property real specialManualInitial: (rowCard.hasSpecialDefault && rowCard.modelData.special_default.manual_initial !== undefined) ? Number(rowCard.modelData.special_default.manual_initial) : Number(rowCard.modelData.min || 0)
                readonly property bool isSpecialActive: rowCard.hasSpecialDefault && typeof rowCard.curVal === "number" && !isNaN(rowCard.curVal) && Math.abs(Number(rowCard.curVal) - rowCard.specialSentinel) < 0.000001
                property string validationError: ""

                width: vaultView.width
                height: rowCard.validationError !== "" ? Theme.dp(104) : (rowCard.widgetKind === "color" || rowCard.widgetKind === "spring" ? Theme.dp(92) : Theme.dp(80))
                radius: Theme.dp(16)
                color: Theme.surface0
                border.width: rowCard.modified ? 1 : 0
                border.color: Theme.accent

                Column {
                    id: labelCol
                    anchors.left: rowCard.left
                    anchors.leftMargin: Theme.dp(16)
                    anchors.right: controlArea.left
                    anchors.rightMargin: Theme.dp(14)
                    anchors.verticalCenter: rowCard.verticalCenter
                    spacing: Theme.dp(3)

                    Row {
                        id: titleRow
                        spacing: Theme.dp(6)
                        width: labelCol.width

                        Rectangle {
                            visible: rowCard.modified
                            width: Theme.dp(8)
                            height: Theme.dp(8)
                            radius: Theme.dp(4)
                            color: Theme.accent
                            anchors.verticalCenter: titleRow.verticalCenter
                        }

                        Text {
                            text: "[" + rowCard.modelData.source_project.toUpperCase() + "] " + (rowCard.modelData.label || rowCard.modelData.original_key)
                            color: Theme.text
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontBodyMd
                            font.weight: Font.Medium
                            elide: Text.ElideRight
                        }
                    }

                    Text {
                        width: labelCol.width
                        text: {
                            let rangeTag = "";
                            if (rowCard.modelData.min !== undefined && rowCard.modelData.max !== undefined)
                                rangeTag = " · [" + rowCard.modelData.min + ".." + rowCard.modelData.max + (rowCard.modelData.unit || "") + "]";
                            if (rowCard.hasSpecialDefault)
                                rangeTag = " · " + rowCard.specialLabel + " (" + rowCard.specialSentinel + ")" + rangeTag;
                            return rowCard.modelData.original_key + " · " + rowCard.modelData.category + " (" + rowCard.cType + rangeTag + ") · " + rowCard.modelData.live_preview;
                        }
                        color: Theme.subtext
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontBodySm
                        elide: Text.ElideRight
                    }

                    Text {
                        visible: rowCard.validationError !== ""
                        width: labelCol.width
                        text: rowCard.validationError
                        color: Theme.error
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontBodySm
                        elide: Text.ElideRight
                    }
                }

                Row {
                    id: controlArea
                    anchors.right: rowCard.right
                    anchors.rightMargin: Theme.dp(14)
                    anchors.verticalCenter: rowCard.verticalCenter
                    spacing: Theme.dp(8)

                    // 1. Boolean Switch
                    M3Switch {
                        visible: rowCard.widgetKind === "switch"
                        anchors.verticalCenter: controlArea.verticalCenter
                        checked: Boolean(rowCard.curVal)
                        onToggled: (v) => {
                            rowCard.validationError = "";
                            ScyBridge.setSetting(rowCard.modelData.scy_id, v, rowCard.modelData.live_preview, rowCard.modelData.original_key);
                        }
                    }

                    // 2. Bounded Range Slider (with special sentinel/Auto default support + live readout & unit)
                    Row {
                        id: sliderRow
                        visible: rowCard.widgetKind === "slider"
                        spacing: Theme.dp(8)
                        anchors.verticalCenter: controlArea.verticalCenter

                        Text {
                            visible: rowCard.isSpecialActive
                            anchors.verticalCenter: sliderRow.verticalCenter
                            text: I18n.tr("%1 (%2)", rowCard.specialLabel, rowCard.specialSentinel)
                            color: Theme.accent
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontBodySm
                            font.weight: Font.Medium
                        }

                        M3Slider {
                            width: rowCard.hasSpecialDefault ? Theme.dp(170) : Theme.dp(230)
                            anchors.verticalCenter: sliderRow.verticalCenter
                            enabled: !rowCard.isSpecialActive
                            from: rowCard.modelData.min !== undefined ? Number(rowCard.modelData.min) : 0
                            to: rowCard.modelData.max !== undefined ? Number(rowCard.modelData.max) : 100
                            stepSize: rowCard.modelData.step !== undefined ? Number(rowCard.modelData.step) : 1
                            suffix: rowCard.modelData.unit ? ((rowCard.modelData.unit === "%" || rowCard.modelData.unit === "°") ? rowCard.modelData.unit : (" " + rowCard.modelData.unit)) : ""
                            value: {
                                if (rowCard.isSpecialActive)
                                    return rowCard.specialManualInitial;
                                const fallbackNum = rowCard.hasSpecialDefault ? rowCard.specialManualInitial : Number(rowCard.modelData.default_value || 0);
                                return (typeof rowCard.curVal === "number" && !isNaN(rowCard.curVal)) ? Number(rowCard.curVal) : fallbackNum;
                            }
                            onMoved: (v) => {
                                rowCard.validationError = "";
                                const committed = rowCard.cType === "int" ? Math.round(v) : Number(v.toFixed(4));
                                ScyBridge.setSetting(rowCard.modelData.scy_id, committed, rowCard.modelData.live_preview, rowCard.modelData.original_key);
                            }
                        }

                        M3Button {
                            visible: rowCard.hasSpecialDefault
                            anchors.verticalCenter: sliderRow.verticalCenter
                            text: rowCard.isSpecialActive
                                ? I18n.tr("Manual")
                                : I18n.tr("%1 (%2)", rowCard.specialLabel, rowCard.specialSentinel)
                            variant: rowCard.isSpecialActive ? "tonal" : "filled"
                            onClicked: {
                                rowCard.validationError = "";
                                const nextVal = rowCard.isSpecialActive ? rowCard.specialManualInitial : rowCard.specialSentinel;
                                ScyBridge.setSetting(rowCard.modelData.scy_id, nextVal, rowCard.modelData.live_preview, rowCard.modelData.original_key);
                            }
                        }
                    }

                    // 3. Segmented Choice (<= 3 enum choices)
                    M3Segmented {
                        visible: rowCard.widgetKind === "segmented"
                        anchors.verticalCenter: controlArea.verticalCenter
                        options: rowCard.modelData.choices || []
                        current: rowCard.curVal !== undefined && rowCard.curVal !== null ? rowCard.curVal : ""
                        onChosen: (k) => {
                            rowCard.validationError = "";
                            const v = rowCard.cType === "int" ? parseInt(String(k)) : k;
                            ScyBridge.setSetting(rowCard.modelData.scy_id, v, rowCard.modelData.live_preview, rowCard.modelData.original_key);
                        }
                    }

                    // 4. Exposed Dropdown (> 3 enum choices)
                    M3Dropdown {
                        visible: rowCard.widgetKind === "dropdown"
                        anchors.verticalCenter: controlArea.verticalCenter
                        options: rowCard.modelData.choices || []
                        current: rowCard.curVal !== undefined && rowCard.curVal !== null ? String(rowCard.curVal) : ""
                        onChosen: (k) => {
                            rowCard.validationError = "";
                            const v = rowCard.cType === "int" ? parseInt(k) : k;
                            ScyBridge.setSetting(rowCard.modelData.scy_id, v, rowCard.modelData.live_preview, rowCard.modelData.original_key);
                        }
                    }

                    // 5. Color Swatch + Preset Palette Chips + Validated Hex Input
                    Row {
                        id: colorRow
                        visible: rowCard.widgetKind === "color"
                        spacing: Theme.dp(6)
                        anchors.verticalCenter: controlArea.verticalCenter

                        Rectangle {
                            width: Theme.dp(28)
                            height: Theme.dp(28)
                            radius: Theme.dp(14)
                            anchors.verticalCenter: colorRow.verticalCenter
                            color: page.isValidHexColor(rowCard.curVal) ? String(rowCard.curVal) : "#ffb1c4"
                            border.width: 1
                            border.color: Theme.outline
                        }

                        Repeater {
                            model: page.accentPresets

                            Rectangle {
                                id: swatchDot
                                required property string modelData
                                width: Theme.dp(16)
                                height: Theme.dp(16)
                                radius: Theme.dp(8)
                                anchors.verticalCenter: colorRow.verticalCenter
                                color: swatchDot.modelData

                                MouseArea {
                                    anchors.fill: swatchDot
                                    onClicked: {
                                        rowCard.validationError = "";
                                        ScyBridge.setSetting(rowCard.modelData.scy_id, swatchDot.modelData, rowCard.modelData.live_preview, rowCard.modelData.original_key);
                                    }
                                }
                            }
                        }

                        M3TextField {
                            width: Theme.dp(120)
                            text: String(rowCard.curVal || "#ffb1c4")
                            placeholder: "#RRGGBB"
                            error: rowCard.validationError !== ""
                            onAccepted: (v) => {
                                const trimmed = v.trim();
                                if (!page.isValidHexColor(trimmed)) {
                                    rowCard.validationError = I18n.tr("Expected #RRGGBB or #AARRGGBB hex color");
                                    return;
                                }
                                rowCard.validationError = "";
                                ScyBridge.setSetting(rowCard.modelData.scy_id, trimmed, rowCard.modelData.live_preview, rowCard.modelData.original_key);
                            }
                        }
                    }

                    // 6. Bounded Numeric Field
                    M3TextField {
                        visible: rowCard.widgetKind === "number"
                        width: Theme.dp(150)
                        anchors.verticalCenter: controlArea.verticalCenter
                        text: rowCard.curVal !== undefined && rowCard.curVal !== null ? String(rowCard.curVal) : "0"
                        placeholder: (rowCard.modelData.min !== undefined && rowCard.modelData.max !== undefined) ? (rowCard.modelData.min + ".." + rowCard.modelData.max) : "0"
                        error: rowCard.validationError !== ""
                        onAccepted: (v) => {
                            const num = rowCard.cType === "int" ? Number(v) : parseFloat(v);
                            if (isNaN(num) || !isFinite(num) || (rowCard.cType === "int" && Math.floor(num) !== num)) {
                                rowCard.validationError = I18n.tr("Invalid %1 number", rowCard.cType);
                                return;
                            }
                            if (rowCard.modelData.min !== undefined && num < Number(rowCard.modelData.min)) {
                                rowCard.validationError = I18n.tr("Minimum allowed is %1", rowCard.modelData.min);
                                return;
                            }
                            if (rowCard.modelData.max !== undefined && num > Number(rowCard.modelData.max)) {
                                rowCard.validationError = I18n.tr("Maximum allowed is %1", rowCard.modelData.max);
                                return;
                            }
                            rowCard.validationError = "";
                            ScyBridge.setSetting(rowCard.modelData.scy_id, num, rowCard.modelData.live_preview, rowCard.modelData.original_key);
                        }
                    }

                    // 7. Spring Physics Dual Editor ({stiffness, damping})
                    Row {
                        visible: rowCard.widgetKind === "spring"
                        spacing: Theme.dp(6)
                        anchors.verticalCenter: controlArea.verticalCenter

                        M3TextField {
                            width: Theme.dp(96)
                            text: (rowCard.curVal && rowCard.curVal.stiffness !== undefined) ? String(rowCard.curVal.stiffness) : "320"
                            placeholder: "stiffness"
                            error: rowCard.validationError !== ""
                            onAccepted: (v) => {
                                const st = parseFloat(v);
                                const curDamp = (rowCard.curVal && rowCard.curVal.damping !== undefined) ? Number(rowCard.curVal.damping) : 26;
                                if (isNaN(st) || st < 1 || st > 5000) {
                                    rowCard.validationError = I18n.tr("Stiffness must be 1..5000");
                                    return;
                                }
                                rowCard.validationError = "";
                                ScyBridge.setSetting(rowCard.modelData.scy_id, {"stiffness": st, "damping": curDamp}, rowCard.modelData.live_preview, rowCard.modelData.original_key);
                            }
                        }

                        M3TextField {
                            width: Theme.dp(96)
                            text: (rowCard.curVal && rowCard.curVal.damping !== undefined) ? String(rowCard.curVal.damping) : "26"
                            placeholder: "damping"
                            error: rowCard.validationError !== ""
                            onAccepted: (v) => {
                                const dp = parseFloat(v);
                                const curStiff = (rowCard.curVal && rowCard.curVal.stiffness !== undefined) ? Number(rowCard.curVal.stiffness) : 320;
                                if (isNaN(dp) || dp < 0.1 || dp > 500) {
                                    rowCard.validationError = I18n.tr("Damping must be 0.1..500");
                                    return;
                                }
                                rowCard.validationError = "";
                                ScyBridge.setSetting(rowCard.modelData.scy_id, {"stiffness": curStiff, "damping": dp}, rowCard.modelData.live_preview, rowCard.modelData.original_key);
                            }
                        }
                    }

                    // 8. List / JSON / Text / Time Validated Input
                    M3TextField {
                        visible: rowCard.widgetKind === "text" || rowCard.widgetKind === "list" || rowCard.widgetKind === "json"
                        width: Theme.dp(210)
                        anchors.verticalCenter: controlArea.verticalCenter
                        text: {
                            if (rowCard.curVal === undefined || rowCard.curVal === null)
                                return "";
                            if (rowCard.widgetKind === "list" && Array.isArray(rowCard.curVal))
                                return rowCard.curVal.join(", ");
                            if (typeof rowCard.curVal === "object")
                                return JSON.stringify(rowCard.curVal);
                            return String(rowCard.curVal);
                        }
                        placeholder: rowCard.modelData.placeholder || String(rowCard.cType)
                        error: rowCard.validationError !== ""
                        onAccepted: (v) => {
                            if (rowCard.cType === "time" && !page.isValidTime24(v)) {
                                rowCard.validationError = I18n.tr("Expected 24h time HH:MM");
                                return;
                            }
                            if (rowCard.widgetKind === "json") {
                                try {
                                    const obj = v.trim() === "" ? ({}) : JSON.parse(v);
                                    if (typeof obj !== "object" || Array.isArray(obj) || obj === null) {
                                        rowCard.validationError = I18n.tr("Expected JSON object {...}");
                                        return;
                                    }
                                    rowCard.validationError = "";
                                    ScyBridge.setSetting(rowCard.modelData.scy_id, obj, rowCard.modelData.live_preview, rowCard.modelData.original_key);
                                } catch (e) {
                                    rowCard.validationError = I18n.tr("Invalid JSON syntax");
                                }
                                return;
                            }
                            if (rowCard.widgetKind === "list") {
                                const trimmed = v.trim();
                                if (trimmed.indexOf("[") === 0) {
                                    try {
                                        const arr = JSON.parse(trimmed);
                                        if (!Array.isArray(arr)) {
                                            rowCard.validationError = I18n.tr("Expected JSON array [...]");
                                            return;
                                        }
                                        rowCard.validationError = "";
                                        ScyBridge.setSetting(rowCard.modelData.scy_id, arr, rowCard.modelData.live_preview, rowCard.modelData.original_key);
                                    } catch (e) {
                                        rowCard.validationError = I18n.tr("Invalid JSON array");
                                    }
                                    return;
                                }
                                const parts = trimmed === "" ? [] : trimmed.split(",").map((s) => s.trim()).filter((s) => s !== "");
                                rowCard.validationError = "";
                                ScyBridge.setSetting(rowCard.modelData.scy_id, parts, rowCard.modelData.live_preview, rowCard.modelData.original_key);
                                return;
                            }
                            rowCard.validationError = "";
                            ScyBridge.setSetting(rowCard.modelData.scy_id, v, rowCard.modelData.live_preview, rowCard.modelData.original_key);
                        }
                    }

                    // 9. Read-only TOML Section Header Badge
                    Text {
                        visible: rowCard.widgetKind === "section_table"
                        anchors.verticalCenter: controlArea.verticalCenter
                        text: I18n.tr("Section (%1 keys)", rowCard.modelData.child_count || 0)
                        color: Theme.subtext
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontBodySm
                    }

                    // 10. Per-Row 1-Click Reset-to-Default Button
                    M3Button {
                        visible: rowCard.modified && rowCard.widgetKind !== "section_table"
                        anchors.verticalCenter: controlArea.verticalCenter
                        text: I18n.tr("Reset")
                        variant: "text"
                        onClicked: {
                            rowCard.validationError = "";
                            ScyBridge.resetSetting(rowCard.modelData.scy_id, rowCard.modelData.default_value, rowCard.modelData.original_key);
                        }
                    }
                }
            }
        }
    }
}
