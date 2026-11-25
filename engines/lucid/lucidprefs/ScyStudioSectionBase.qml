pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import Quickshell.Io
import qs

// Scy-Shell v2.0 — Unified Intent-Driven Studio Section Base
// Combines bespoke interactive feature decks at the top of each Studio section with
// complete, schema-validated, live-bound controls for every setting in that section,
// transactional Live Preview (Stage / Apply / Revert), and 1-click Section Reset.
Column {
    id: base

    property string sectionId: "01-personalization"
    property string sectionTitle: ""
    property string sectionSubtitle: ""
    property var deepLinks: []
    default property alias featureDeck: featureCol.data

    spacing: Theme.dp(20)
    property string categoryFilter: "all"
    property bool modifiedOnly: false
    property string query: ""
    property var allSectionItems: []

    readonly property var accentPresets: ["#7aa2f7", "#ffb1c4", "#10b981", "#f59e0b", "#a855f7", "#ef4444"]

    readonly property var categoryOptions: {
        const seen = {};
        for (let i = 0; i < base.allSectionItems.length; i++) {
            const cat = (base.allSectionItems[i].category || "general").split(".")[0];
            seen[cat] = (seen[cat] || 0) + 1;
        }
        const keys = Object.keys(seen).sort();
        const opts = [{"key": "all", "label": I18n.tr("All (%1)", base.allSectionItems.length)}];
        for (let j = 0; j < keys.length; j++) {
            opts.push({"key": keys[j], "label": keys[j] + " (" + seen[keys[j]] + ")"});
        }
        return opts;
    }

    readonly property var filteredItems: {
        void ScyBridge.valuesRev;
        const cf = base.categoryFilter;
        const modOnly = base.modifiedOnly;
        const q = base.query.trim().toLowerCase();

        return base.allSectionItems.filter((item) => {
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
                || (item.help_text && item.help_text.toLowerCase().indexOf(q) !== -1)
                || (item.category && item.category.toLowerCase().indexOf(q) !== -1);
        });
    }

    function isValidHexColor(s: var): bool {
        return /^#([0-9a-fA-F]{6}|[0-9a-fA-F]{8})$/.test(String(s).trim());
    }

    function isValidTime24(s: var): bool {
        return /^([01][0-9]|2[0-3]):[0-5][0-9]$/.test(String(s).trim());
    }

    FileView {
        id: catFile
        path: Quickshell.shellPath("scy-schema/settings_catalogue.json")
        printErrors: false
        onLoaded: {
            try {
                const parsed = JSON.parse(catFile.text());
                const scyArr = parsed.scy_settings || [];
                const lucArr = parsed.lucid_settings || [];
                const manArr = parsed.mandara_settings || [];
                const merged = scyArr.concat(lucArr).concat(manArr);
                base.allSectionItems = merged.filter((it) => it.studio_section === base.sectionId);
            } catch (e) {}
        }
    }

    // 1. Bespoke Section Feature Deck (interactive presets, composer cards, hardware advisor, etc.)
    Column {
        id: featureCol
        width: base.width
        spacing: Theme.dp(18)
    }

    // 2. Specialized Deep-Dive Tool Sheets (preserving 100% rich interactive editors)
    SettingCard {
        id: toolsCard
        visible: base.deepLinks && base.deepLinks.length > 0
        title: I18n.tr("INTERACTIVE WORKBENCHES & SPECIALIZED TOOLS")
        subtitle: I18n.tr("Open dedicated interactive visual editors within Scy-Shell Studio (use the top-left Back arrow to return here).")

        Flow {
            width: Math.max(Theme.dp(320), base.width - Theme.dp(40))
            spacing: Theme.dp(10)

            Repeater {
                model: base.deepLinks

                M3Button {
                    id: linkBtn
                    required property var modelData
                    text: String(linkBtn.modelData.label || "")
                    variant: "tonal"
                    onClicked: ScyBridge.openStudioSection(String(linkBtn.modelData.pageKey || ""))
                }
            }
        }
    }

    // 3. Scy Live Preview Bar + Section Reset + Fine-Grained Controls Header
    SettingCard {
        title: base.sectionTitle !== "" ? base.sectionTitle : I18n.tr("FINE-GRAINED SECTION SETTINGS (%1)", base.allSectionItems.length)
        subtitle: base.sectionSubtitle !== "" ? base.sectionSubtitle : I18n.tr("Every control below binds directly to the unified Scy-Shell persistence & live-preview engine.")

        SettingRow {
            title: I18n.tr("Transactional Live Preview Mode")
            description: ScyBridge.previewActive
                ? I18n.tr("%1 staged change(s) active — Commit to persist permanently or Revert to restore.", ScyBridge.previewChangeCount)
                : I18n.tr("Stage changes non-destructively to compare Before / After before saving.")

            Row {
                spacing: Theme.dp(8)

                M3Switch {
                    checked: ScyBridge.livePreviewStagingMode
                    onToggled: (v) => ScyBridge.livePreviewStagingMode = v
                }

                M3Button {
                    visible: ScyBridge.previewActive || ScyBridge.livePreviewStagingMode
                    text: I18n.tr("Apply & Save")
                    variant: "filled"
                    onClicked: ScyBridge.commitPreview()
                }

                M3Button {
                    visible: ScyBridge.previewActive || ScyBridge.livePreviewStagingMode
                    text: I18n.tr("Revert")
                    variant: "tonal"
                    destructive: true
                    onClicked: ScyBridge.revertPreview()
                }
            }
        }

        SettingRow {
            visible: ScyBridge.hyprTrialActive
            title: I18n.tr("Hyprland 0.57+ Safety Trial: %1", ScyBridge.hyprTrialKey)
            description: I18n.tr("Confirm compositor geometry/rule update or revert immediately to pre-trial backup.")

            Row {
                spacing: Theme.dp(8)

                M3Button {
                    text: I18n.tr("Keep")
                    variant: "filled"
                    onClicked: ScyBridge.confirmHyprTrial()
                }

                M3Button {
                    text: I18n.tr("Revert")
                    variant: "tonal"
                    destructive: true
                    onClicked: ScyBridge.revertHyprTrial()
                }
            }
        }

        SettingRow {
            title: I18n.tr("Filter & Section Reset (%1 of %2 shown)", base.filteredItems.length, base.allSectionItems.length)
            description: I18n.tr("Narrow by subsystem, inspect customized values only, or reset this Studio section to defaults.")

            Row {
                spacing: Theme.dp(10)

                M3Dropdown {
                    options: base.categoryOptions
                    current: base.categoryFilter
                    onChosen: (k) => base.categoryFilter = String(k)
                }

                M3Button {
                    text: base.modifiedOnly ? I18n.tr("Modified Only ✓") : I18n.tr("Modified Only")
                    variant: base.modifiedOnly ? "filled" : "tonal"
                    onClicked: base.modifiedOnly = !base.modifiedOnly
                }

                M3Button {
                    text: I18n.tr("Reset Section")
                    variant: "text"
                    destructive: true
                    onClicked: ScyBridge.resetSection(base.sectionId)
                }
            }
        }

        SettingRow {
            id: secSearchRow
            title: I18n.tr("Search This Section")
            description: I18n.tr("Instant filter across all controls in this Studio section.")
            stacked: true

            M3TextField {
                width: secSearchRow.width
                placeholder: I18n.tr("Filter settings in this section…")
                onEdited: (v) => base.query = v
            }
        }
    }

    // 4. Virtualized Type-Aware Section Settings List
    Rectangle {
        id: secListBox
        width: base.width
        height: Math.min(Theme.dp(560), Math.max(Theme.dp(220), base.filteredItems.length * Theme.dp(86) + Theme.dp(24)))
        radius: ScyDesignTokens.rad(24)
        color: Theme.withBlur(Theme.bgTile)
        clip: true

        ListView {
            id: secListView
            anchors.fill: secListBox
            anchors.margins: Theme.dp(12)
            spacing: Theme.dp(8)
            model: base.filteredItems

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

                width: secListView.width
                height: rowCard.validationError !== "" ? Theme.dp(104) : (rowCard.widgetKind === "color" || rowCard.widgetKind === "spring" ? Theme.dp(92) : Theme.dp(80))
                radius: ScyDesignTokens.rad(16)
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
                            text: rowCard.modelData.label || rowCard.modelData.original_key
                            color: Theme.text
                            font.family: ScyDesignTokens.uiFont
                            font.pixelSize: Theme.fontBodyMd
                            font.weight: Font.Medium
                            elide: Text.ElideRight
                        }
                    }

                    Text {
                        width: labelCol.width
                        text: {
                            const help = rowCard.modelData.help_text ? (rowCard.modelData.help_text + " · ") : "";
                            let rangeTag = "";
                            if (rowCard.modelData.min !== undefined && rowCard.modelData.max !== undefined && rowCard.modelData.min !== null && rowCard.modelData.max !== null)
                                rangeTag = " [" + rowCard.modelData.min + ".." + rowCard.modelData.max + (rowCard.modelData.unit || "") + "]";
                            return help + rowCard.modelData.category + rangeTag;
                        }
                        color: Theme.subtext
                        font.family: ScyDesignTokens.uiFont
                        font.pixelSize: Theme.fontBodySm
                        elide: Text.ElideRight
                    }

                    Text {
                        visible: rowCard.validationError !== ""
                        width: labelCol.width
                        text: rowCard.validationError
                        color: Theme.error
                        font.family: ScyDesignTokens.uiFont
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

                    M3Switch {
                        visible: rowCard.widgetKind === "switch"
                        anchors.verticalCenter: controlArea.verticalCenter
                        checked: Boolean(rowCard.curVal)
                        onToggled: (v) => {
                            rowCard.validationError = "";
                            ScyBridge.setSetting(rowCard.modelData.scy_id, v, rowCard.modelData.live_preview, rowCard.modelData.original_key);
                        }
                    }

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
                            font.family: ScyDesignTokens.uiFont
                            font.pixelSize: Theme.fontBodySm
                            font.weight: Font.Medium
                        }

                        M3Slider {
                            width: rowCard.hasSpecialDefault ? Theme.dp(170) : Theme.dp(220)
                            anchors.verticalCenter: sliderRow.verticalCenter
                            enabled: !rowCard.isSpecialActive
                            from: rowCard.modelData.min !== undefined && rowCard.modelData.min !== null ? Number(rowCard.modelData.min) : 0
                            to: rowCard.modelData.max !== undefined && rowCard.modelData.max !== null ? Number(rowCard.modelData.max) : 100
                            stepSize: rowCard.modelData.step !== undefined && rowCard.modelData.step !== null ? Number(rowCard.modelData.step) : 1
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

                    Row {
                        id: colorRow
                        visible: rowCard.widgetKind === "color"
                        spacing: Theme.dp(6)
                        anchors.verticalCenter: controlArea.verticalCenter

                        Rectangle {
                            width: Theme.dp(26)
                            height: Theme.dp(26)
                            radius: Theme.dp(13)
                            anchors.verticalCenter: colorRow.verticalCenter
                            color: base.isValidHexColor(rowCard.curVal) ? String(rowCard.curVal) : "#7aa2f7"
                            border.width: 1
                            border.color: Theme.outline
                        }

                        Repeater {
                            model: base.accentPresets

                            Rectangle {
                                id: swatchDot
                                required property string modelData
                                width: Theme.dp(15)
                                height: Theme.dp(15)
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
                            width: Theme.dp(116)
                            text: String(rowCard.curVal || "#7aa2f7")
                            placeholder: "#RRGGBB"
                            error: rowCard.validationError !== ""
                            onAccepted: (v) => {
                                const trimmed = v.trim();
                                if (!base.isValidHexColor(trimmed)) {
                                    rowCard.validationError = I18n.tr("Expected #RRGGBB or #AARRGGBB hex color");
                                    return;
                                }
                                rowCard.validationError = "";
                                ScyBridge.setSetting(rowCard.modelData.scy_id, trimmed, rowCard.modelData.live_preview, rowCard.modelData.original_key);
                            }
                        }
                    }

                    M3TextField {
                        visible: rowCard.widgetKind === "number"
                        width: Theme.dp(140)
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
                            if (rowCard.modelData.min !== undefined && rowCard.modelData.min !== null && num < Number(rowCard.modelData.min)) {
                                rowCard.validationError = I18n.tr("Minimum allowed is %1", rowCard.modelData.min);
                                return;
                            }
                            if (rowCard.modelData.max !== undefined && rowCard.modelData.max !== null && num > Number(rowCard.modelData.max)) {
                                rowCard.validationError = I18n.tr("Maximum allowed is %1", rowCard.modelData.max);
                                return;
                            }
                            rowCard.validationError = "";
                            ScyBridge.setSetting(rowCard.modelData.scy_id, num, rowCard.modelData.live_preview, rowCard.modelData.original_key);
                        }
                    }

                    Row {
                        visible: rowCard.widgetKind === "spring"
                        spacing: Theme.dp(6)
                        anchors.verticalCenter: controlArea.verticalCenter

                        M3TextField {
                            width: Theme.dp(92)
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
                            width: Theme.dp(92)
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

                    M3TextField {
                        visible: rowCard.widgetKind === "text" || rowCard.widgetKind === "list" || rowCard.widgetKind === "json"
                        width: Theme.dp(200)
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
                            if (rowCard.cType === "time" && !base.isValidTime24(v)) {
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

                    Text {
                        visible: rowCard.widgetKind === "section_table"
                        anchors.verticalCenter: controlArea.verticalCenter
                        text: I18n.tr("Group (%1)", rowCard.modelData.child_count || 0)
                        color: Theme.subtext
                        font.family: ScyDesignTokens.uiFont
                        font.pixelSize: Theme.fontBodySm
                    }

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
