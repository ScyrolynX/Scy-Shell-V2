"""Scy-Shell v2.0 — Unified 15-Section Studio Taxonomy & Native Scy-Shell Settings Definitions.

Eliminates any user-facing 'Lucid vs Mandara' engine split by organizing every setting around
what the user wants to customize (Sections 01 through 15), while preserving 100% of underlying
Lucid and Mandara capabilities and strictly separating Lock Screen (11) from Login Experience (12).
"""
from __future__ import annotations

from typing import Any

UNIFIED_STUDIO_15_SECTIONS: tuple[dict[str, Any], ...] = (
    {
        "id": "01-personalization",
        "num": "01",
        "key": "scy-01-personalization",
        "group": "Appearance & Identity",
        "label": "Personalization",
        "title": "01 — Personalization",
        "icon": "palette",
        "blurb": "Themes, 20 unified Looks, procedural & live wallpapers, OKLCH dynamic colors, typography, icons, cursors and 28-app theming",
    },
    {
        "id": "02-desktop",
        "num": "02",
        "key": "scy-02-desktop",
        "group": "Appearance & Identity",
        "label": "Desktop Experience",
        "title": "02 — Desktop Experience",
        "icon": "desktop_windows",
        "blurb": "Top & edge panels, Dynamic Island, desktop icons, workspace presentation, floating elements and live desktop editing",
    },
    {
        "id": "03-dock-studio",
        "num": "03",
        "key": "scy-03-dock-studio",
        "group": "Appearance & Identity",
        "label": "Dock Studio",
        "title": "03 — Dock Studio",
        "icon": "dock_to_bottom",
        "blurb": "Dedicated dock customization laboratory: single-owner lifecycle, placement, magnification, groups, glass, indicators and presets",
    },
    {
        "id": "04-visual-effects",
        "num": "04",
        "key": "scy-04-visual-effects",
        "group": "Appearance & Identity",
        "label": "Visual Effects",
        "title": "04 — Visual Effects",
        "icon": "blur_on",
        "blurb": "Blur, glassmorphism, surface transparency, shadows, gradients, shaders, lighting, spring physics and per-component motion",
    },
    {
        "id": "05-layout",
        "num": "05",
        "key": "scy-05-layout",
        "group": "Workspace & Surfaces",
        "label": "Layout & Composition",
        "title": "05 — Layout & Composition",
        "icon": "dashboard_customize",
        "blurb": "Scy Layout Composer, panel positioning, component dimensions, alignment, spacing, radii, layer priority and multi-monitor layouts",
    },
    {
        "id": "06-widgets",
        "num": "06",
        "key": "scy-06-widgets",
        "group": "Workspace & Surfaces",
        "label": "Widgets & Components",
        "title": "06 — Widgets & Components",
        "icon": "widgets",
        "blurb": "Scy Component Laboratory, desktop widget library, per-component materials, visibility, positioning and live previews",
    },
    {
        "id": "07-windows",
        "num": "07",
        "key": "scy-07-windows",
        "group": "Workspace & Surfaces",
        "label": "Window Management",
        "title": "07 — Window Management",
        "icon": "grid_view",
        "blurb": "Hyprland 0.57+ layouts, window rules, workspaces, gaps, borders, focus behaviour, floating rules and safe 15s compositor trials",
    },
    {
        "id": "08-interactions",
        "num": "08",
        "key": "scy-08-interactions",
        "group": "Workspace & Surfaces",
        "label": "Interactions",
        "title": "08 — Interactions",
        "icon": "touch_app",
        "blurb": "Keyboard shortcuts, mouse & touchpad gestures, hot corners, hover & click actions, workspace navigation and interaction profiles",
    },
    {
        "id": "09-notifications",
        "num": "09",
        "key": "scy-09-notifications",
        "group": "System & Security",
        "label": "Notifications & Control",
        "title": "09 — Notifications & Control Center",
        "icon": "notifications_active",
        "blurb": "Notification appearance & history, Scy Control Center layout, quick toggles, OSD styling and system status indicators",
    },
    {
        "id": "10-system",
        "num": "10",
        "key": "scy-10-system",
        "group": "System & Security",
        "label": "System & Hardware",
        "title": "10 — System & Hardware",
        "icon": "display_settings",
        "blurb": "Displays, refresh rate, scaling, HDR/VRR, audio, Wi-Fi, Bluetooth, power profiles, battery and hardware-aware performance tiers",
    },
    {
        "id": "11-lock-screen",
        "num": "11",
        "key": "scy-11-lock-screen",
        "group": "System & Security",
        "label": "Lock Screen",
        "title": "11 — Lock Screen",
        "icon": "lock",
        "blurb": "Dedicated session lock Studio: clock layouts, weather, media, privacy, independent wallpaper/blur/glass, widgets and multi-monitor",
    },
    {
        "id": "12-login",
        "num": "12",
        "key": "scy-12-login",
        "group": "System & Security",
        "label": "Login Experience",
        "title": "12 — Login Experience",
        "icon": "badge",
        "blurb": "Dedicated pre-login greeter Studio: user cards, avatar styling, session picker, power actions, background, accessibility and accounts",
    },
    {
        "id": "13-productivity",
        "num": "13",
        "key": "scy-13-productivity",
        "group": "Workflow & Architecture",
        "label": "Apps & Productivity",
        "title": "13 — Applications & Productivity",
        "icon": "rocket_launch",
        "blurb": "Intelligent launcher, clipboard history, calculator & unit converter, calendar, quick notes, timers, capture, AI and extensions",
    },
    {
        "id": "14-profiles",
        "num": "14",
        "key": "scy-14-profiles",
        "group": "Workflow & Architecture",
        "label": "Profiles & Presets",
        "title": "14 — Profiles & Presets",
        "icon": "style",
        "blurb": "Complete desktop profiles (Minimal, Productivity, Immersive, Gaming, Creative, Cinema, Balanced), import/export, backups & restore",
    },
    {
        "id": "15-advanced",
        "num": "15",
        "key": "scy-15-advanced",
        "group": "Workflow & Architecture",
        "label": "Advanced Configuration",
        "title": "15 — Advanced Configuration",
        "icon": "tune",
        "blurb": "Complete searchable settings inspector, Hyprland fine-tuning, configuration files, process ownership diagnostics and system doctor",
    },
)

SECTION_BY_ID: dict[str, dict[str, Any]] = {s["id"]: s for s in UNIFIED_STUDIO_15_SECTIONS}


def classify_studio_section(scy_id: str, category: str, original_key: str) -> str:
    """Deterministically assigns every setting (Lucid, Mandara, and Scy-Shell native) to one of the
    15 unified Studio sections without exposing engine origins."""
    sid = scy_id.lower()
    cat = (category or "").lower()
    key = (original_key or "").lower()

    # Explicit Scy-Shell v2 native namespaces
    if sid.startswith("scy.design.effects.") or sid.startswith("scy.effects."):
        return "04-visual-effects"
    if sid.startswith("scy.design."):
        return "01-personalization"
    if sid.startswith("scy.desktop.") or sid.startswith("scy.island."):
        return "02-desktop"
    if sid.startswith("scy.dock."):
        return "03-dock-studio"
    if sid.startswith("scy.layout."):
        return "05-layout"
    if sid.startswith("scy.widgets."):
        return "06-widgets"
    if sid.startswith("scy.windows."):
        return "07-windows"
    if sid.startswith("scy.interactions."):
        return "08-interactions"
    if sid.startswith("scy.control_center."):
        return "09-notifications"
    if sid.startswith("scy.performance."):
        return "10-system"
    if sid.startswith("scy.lock."):
        return "11-lock-screen"
    if sid.startswith("scy.login."):
        return "12-login"
    if sid.startswith("scy.productivity."):
        return "13-productivity"
    if sid.startswith("scy.profiles."):
        return "14-profiles"

    # Strict separation of Login (12) vs Lock Screen (11)
    if ".sddm." in sid or ".greeter." in sid or "preauth" in cat or key.startswith(("greeter", "login", "sddm")) or key in ("lockloginsync", "lockloginweather"):
        return "12-login"
    if ".lock_widgets." in sid or key.startswith("lock") or "/lock" in key or cat in ("lock", "lockscreen", "lock_screen"):
        return "11-lock-screen"

    # Dock Studio (03)
    if key.startswith("dock") or "/dock/" in key or key == "/dock" or cat == "dock":
        return "03-dock-studio"

    # Personalization (01): Themes, Wallpapers, Wallgen, Fonts, Icons, Cursors, Looks
    if (
        ".wallgen." in sid
        or any(tok in key for tok in ("theme", "palette", "colour", "color", "wallpaper", "font", "typography", "cursor", "icon_theme", "icontheme", "/looks"))
        or cat in ("theme", "themes", "wallpaper", "typography", "looks", "colours", "palettes")
    ):
        if any(tok in key for tok in ("blur", "shadow", "shader", "glass", "opacity", "darkness", "tint")) and "wallpaper" not in key:
            return "04-visual-effects"
        return "01-personalization"

    # Visual Effects (04): Glass, Blur, Animations, Motion, Shadows, Shaders
    if (
        ".glass." in sid
        or any(tok in key for tok in ("blur", "glass", "shadow", "shader", "motion", "anim", "spring", "surfacetint", "surfacedarkness", "opacity", "dim"))
        or cat in ("glass", "motion", "animations", "effects")
    ):
        return "04-visual-effects"

    # Widgets & Components (06)
    if ".widget_opts." in sid or "widget" in key or "widget" in cat:
        return "06-widgets"

    # Desktop Experience (02): Bar, Panels, Sidebars, Desktop Icons, Workspaces
    if any(tok in key for tok in ("bar", "sidebar", "side_bar", "desktopicon", "desktop_icon", "island", "notch")):
        return "02-desktop"

    # Layout & Composition (05)
    if any(tok in key for tok in ("margin", "padding", "spacing", "radius", "anchor", "placement", "zone")):
        return "05-layout"

    # Window Management (07): Hyprland, Switcher, Overview, Tiling, Gaps, Borders
    if (
        ".hypr." in sid
        or any(tok in key for tok in ("hypr", "gaps_", "rounding", "window", "switcher", "overview", "tiling", "dwindle", "master", "compositor"))
        or cat in ("hyprland", "windows", "compositor", "window_switcher")
    ):
        return "07-windows"

    # Interactions (08): Input, Keybinds, Shortcuts, Gestures, Corners, Pointer
    if (
        ".keys." in sid
        or any(tok in key for tok in ("keybind", "shortcut", "touchpad", "mouse", "pointer", "gesture", "corner", "swipe", "keyboard", "xkb"))
        or cat in ("input", "keybinds", "shortcuts", "corners")
    ):
        return "08-interactions"

    # Notifications & Control Center (09)
    if any(tok in key for tok in ("notif", "toast", "osd", "control_center", "controlcentre", "quick_settings", "alert", "dnd")):
        return "09-notifications"

    # System & Hardware (10): Monitors, Audio, Network, Bluetooth, Power, Battery, Idle, Night Light
    if any(
        tok in key
        for tok in ("monitor", "display", "audio", "volume", "sound", "network", "wifi", "bluetooth", "bt", "power", "battery", "idle", "night_light", "nightlight", "brightness", "lumen")
    ) or ".lumen." in sid:
        return "10-system"

    # Applications & Productivity (13): Launcher, Clipboard, Capture, Calendar, Notes, Timers, Media, Plugins, AI, Games
    if (
        any(x in sid for x in (".moji.", ".lens.", ".clock_app.", ".shot_state."))
        or any(
            tok in key
            for tok in ("launcher", "clipboard", "capture", "screenshot", "recorder", "snip", "calendar", "agenda", "alarm", "timer", "pomodoro", "note", "todo", "media", "plugin", "agent", "ai", "game", "kde")
        )
    ):
        return "13-productivity"

    # Profiles & Presets (14)
    if any(tok in key for tok in ("profile", "preset", "backup")):
        return "14-profiles"

    return "15-advanced"


def _ch(*items: tuple[str, str]) -> list[dict[str, str]]:
    return [{"key": k, "label": lbl} for k, lbl in items]


def _s(
    scy_id: str,
    section: str,
    label: str,
    help_text: str,
    concrete_type: str,
    default: Any,
    ui_widget: str,
    *,
    min_val: float | int | None = None,
    max_val: float | int | None = None,
    step: float | int | None = None,
    unit: str = "",
    choices: list[dict[str, str]] | None = None,
    live_preview: str = "scy_tokens",
) -> dict[str, Any]:
    orig = scy_id.removeprefix("scy.")
    return {
        "scy_id": scy_id,
        "original_key": orig,
        "source_project": "scy",
        "source_file": "config.toml",
        "storage": "scy_native",
        "category": section,
        "studio_section": section,
        "type": concrete_type,
        "concrete_type": concrete_type,
        "ui_widget": ui_widget,
        "default": str(default),
        "default_value": default,
        "label": label,
        "help": help_text,
        "min": min_val,
        "max": max_val,
        "step": step,
        "unit": unit,
        "choices": choices or [],
        "live_preview": live_preview,
    }


SCY_NATIVE_SETTINGS: tuple[dict[str, Any], ...] = (
    # --- 01: PERSONALIZATION & DESIGN TOKENS ---
    _s("scy.design.display_font", "01-personalization", "Display Heading Font", "Primary expressive heading typeface across Studio, Lock Screen, and Cards.", "string", "Google Sans", "text"),
    _s("scy.design.ui_font", "01-personalization", "Interface UI Font", "Primary UI body typeface across bars, menus, notifications, and controls.", "string", "Google Sans", "text"),
    _s("scy.design.mono_font", "01-personalization", "Monospace Telemetry Font", "Monospace font for system metrics, clocks, keycaps, and code.", "string", "JetBrains Mono", "text"),
    _s("scy.design.heading_weight", "01-personalization", "Heading Font Weight", "Typography weight for display titles and section headers.", "int", 700, "slider", min_val=400, max_val=900, step=100),
    _s("scy.design.tracking_scale", "01-personalization", "Letter-Spacing Scale", "Fine typographic tracking multiplier across Scy-Shell surfaces.", "float", 1.0, "slider", min_val=0.85, max_val=1.20, step=0.01),
    _s("scy.design.icon_theme", "01-personalization", "Icon Theme", "System & dock icon pack name.", "string", "Papirus-Dark", "text"),
    _s("scy.design.cursor_theme", "01-personalization", "Cursor Theme", "Wayland/Hyprcursor pointer theme.", "string", "Bibata-Modern-Ice", "text"),
    _s("scy.design.cursor_size", "01-personalization", "Cursor Size", "Pointer cursor size in logical pixels.", "int", 24, "slider", min_val=16, max_val=64, step=2, unit="px"),
    _s("scy.design.wallpaper_extract", "01-personalization", "Wallpaper Dynamic Color", "Automatically extract OKLCH + Material 3 Expressive accents when wallpaper changes.", "bool", True, "switch", live_preview="theme_accent"),
    _s("scy.design.palette_harmony", "01-personalization", "Palette Harmony Algorithm", "Color harmony curve for generated desktop tokens.", "enum", "expressive", "segmented", choices=_ch(("expressive", "Expressive"), ("tonal-spot", "Tonal Spot"), ("vibrant", "Vibrant"), ("neutral", "Neutral"), ("monochrome", "Monochrome")), live_preview="theme_accent"),
    _s("scy.design.accent_intensity", "01-personalization", "Global Accent Chroma Intensity", "Scales OKLCH chroma saturation of primary and tertiary accents.", "float", 1.0, "slider", min_val=0.40, max_val=1.60, step=0.05, live_preview="theme_accent"),
    _s("scy.design.bar_accent", "01-personalization", "Top Bar Custom Accent", "Optional hex override (#RRGGBB) or #00000000 to inherit global accent.", "color", "#7aa2f7", "color", live_preview="scy_tokens"),
    _s("scy.design.bar_use_custom_accent", "01-personalization", "Use Custom Bar Accent", "Override the global accent color specifically on the top bar.", "bool", False, "switch"),
    _s("scy.design.dock_accent", "01-personalization", "Dock Custom Accent", "Custom accent color for dock indicators, glow, and active pills.", "color", "#7aa2f7", "color"),
    _s("scy.design.dock_use_custom_accent", "01-personalization", "Use Custom Dock Accent", "Override the global accent color specifically on the dock.", "bool", False, "switch"),
    _s("scy.design.cc_accent", "01-personalization", "Control Center Custom Accent", "Custom accent color for Control Center quick tiles and sliders.", "color", "#7aa2f7", "color"),
    _s("scy.design.cc_use_custom_accent", "01-personalization", "Use Custom Control Center Accent", "Override the global accent color inside Control Center.", "bool", False, "switch"),

    # --- 02: DESKTOP EXPERIENCE & DYNAMIC ISLAND ---
    _s("scy.island.enabled", "02-desktop", "Scy Dynamic Island", "Enable unified central interactive capsule for media, timers, workspaces, and live alerts.", "bool", True, "switch"),
    _s("scy.island.mode", "02-desktop", "Dynamic Island Presentation", "Visual style of the central Scy Dynamic Island.", "enum", "adaptive-pill", "segmented", choices=_ch(("adaptive-pill", "Adaptive Pill"), ("notch-carved", "Carved Notch"), ("compact-capsule", "Compact"))),
    _s("scy.island.width", "02-desktop", "Dynamic Island Resting Width", "Resting width of the Dynamic Island capsule.", "int", 220, "slider", min_val=120, max_val=520, step=10, unit="px"),
    _s("scy.island.height", "02-desktop", "Dynamic Island Height", "Resting height of the Dynamic Island capsule.", "int", 34, "slider", min_val=24, max_val=56, step=2, unit="px"),
    _s("scy.island.expand_on_media", "02-desktop", "Expand Island on Media Playback", "Morph Dynamic Island with cover art and waveform during MPRIS playback.", "bool", True, "switch"),
    _s("scy.island.show_timer", "02-desktop", "Show Active Focus Timer in Island", "Display live countdown inside Dynamic Island when a timer is running.", "bool", True, "switch"),
    _s("scy.island.show_notifications", "02-desktop", "Morph Urgent Notifications in Island", "Briefly expand Dynamic Island for incoming high-priority alerts.", "bool", True, "switch"),
    _s("scy.desktop.floating_elements", "02-desktop", "Allow Floating Desktop Overlays", "Enable floating utility pills and quick-pin cards over the desktop canvas.", "bool", True, "switch"),
    _s("scy.desktop.edit_grid_px", "02-desktop", "Desktop Edit Snap Grid", "Snap interval in pixels when dragging desktop widgets and panels.", "int", 8, "slider", min_val=1, max_val=32, step=1, unit="px"),
    _s("scy.desktop.workspace_style", "02-desktop", "Workspace Indicator Style", "Visual presentation of workspace indicators across panels.", "enum", "morphing-pills", "dropdown", choices=_ch(("morphing-pills", "Morphing Pills"), ("numbered-chips", "Numbered Chips"), ("app-icons", "Active App Icons"), ("dots", "Minimal Dots"), ("roman", "Roman Numerals"), ("kanji", "Kanji"))),

    # --- 03: DOCK STUDIO (PRIMARY LUCID-INSPIRED SCY-SHELL DOCK) ---
    _s("scy.dock.mode", "03-dock-studio", "Dock Architecture & Mode", "Single authoritative dock owner: Island, Carved Notch, Split Islands, Minimal Rail, or Disabled.", "enum", "island", "segmented", choices=_ch(("island", "Scy Island"), ("notch", "Carved Notch"), ("split", "Split Islands"), ("rail", "Compact Rail"), ("disabled", "Off")), live_preview="dock_sync"),
    _s("scy.dock.placement", "03-dock-studio", "Screen Edge / Floating Placement", "Place dock on Bottom, Left, Right edge, or detached Floating coordinates.", "enum", "bottom", "segmented", choices=_ch(("bottom", "Bottom"), ("left", "Left"), ("right", "Right"), ("floating", "Floating")), live_preview="dock_sync"),
    _s("scy.dock.float_offset_x", "03-dock-studio", "Floating Horizontal Offset", "Horizontal offset from screen center when placement is Floating.", "int", 0, "slider", min_val=-600, max_val=600, step=4, unit="px", live_preview="dock_sync"),
    _s("scy.dock.float_offset_y", "03-dock-studio", "Floating Vertical Margin", "Distance from bottom screen edge in Floating or Island mode.", "int", 14, "slider", min_val=0, max_val=160, step=2, unit="px", live_preview="dock_sync"),
    _s("scy.dock.min_width", "03-dock-studio", "Minimum Dock Width", "Minimum dock container width (0 = wrap icons tightly).", "int", 0, "slider", min_val=0, max_val=1200, step=20, unit="px", live_preview="dock_sync"),
    _s("scy.dock.max_width", "03-dock-studio", "Maximum Dock Width", "Maximum dock container width before scrolling/compacting.", "int", 1600, "slider", min_val=320, max_val=3840, step=40, unit="px", live_preview="dock_sync"),
    _s("scy.dock.height_override", "03-dock-studio", "Custom Dock Thickness", "Explicit dock thickness override (0 = automatic from icon size + padding).", "int", 0, "slider", min_val=0, max_val=128, step=2, unit="px", live_preview="dock_sync"),
    _s("scy.dock.icon_size", "03-dock-studio", "Application Icon Size", "Base application icon dimension inside the dock.", "int", 42, "slider", min_val=24, max_val=84, step=1, unit="px", live_preview="dock_sync"),
    _s("scy.dock.icon_spacing", "03-dock-studio", "Icon Spacing", "Spacing between adjacent dock icons.", "int", 12, "slider", min_val=2, max_val=32, step=1, unit="px", live_preview="dock_sync"),
    _s("scy.dock.padding_inner", "03-dock-studio", "Dock Inner Padding", "Internal padding between dock glass border and icons.", "int", 10, "slider", min_val=2, max_val=28, step=1, unit="px", live_preview="dock_sync"),
    _s("scy.dock.magnify_enabled", "03-dock-studio", "Cursor Magnification Wave", "Smooth Gaussian icon magnification wave when hovering across the dock.", "bool", True, "switch", live_preview="dock_sync"),
    _s("scy.dock.magnify_scale", "03-dock-studio", "Magnification Peak Scale", "Peak scale multiplier of the hovered dock icon.", "float", 1.35, "slider", min_val=1.0, max_val=2.0, step=0.05, live_preview="dock_sync"),
    _s("scy.dock.active_indicator", "03-dock-studio", "Focused App Indicator Style", "Indicator drawn beneath the currently focused window's dock icon.", "enum", "pill-wide", "segmented", choices=_ch(("pill-wide", "Wide Pill"), ("dot", "Glow Dot"), ("bar-line", "Edge Line"), ("tint-tile", "Tinted Tile")), live_preview="dock_sync"),
    _s("scy.dock.running_indicator", "03-dock-studio", "Running Windows Count Indicator", "How multiple open windows of an application are indicated.", "enum", "multi-dots", "segmented", choices=_ch(("multi-dots", "Window Dots"), ("single-pill", "Single Pill"), ("count-badge", "Count Badge"), ("none", "Hidden")), live_preview="dock_sync"),
    _s("scy.dock.workspace_aware", "03-dock-studio", "Workspace-Aware Running Filter", "Highlight or filter running applications belonging to the active workspace.", "bool", False, "switch", live_preview="dock_sync"),
    _s("scy.dock.notification_badges", "03-dock-studio", "Unread Notification Badges", "Display unread notification dot/count badges on matching dock icons.", "bool", True, "switch", live_preview="dock_sync"),
    _s("scy.dock.show_recent_apps", "03-dock-studio", "Show Recently Used Section", "Append recently closed applications after a separator on the dock.", "bool", True, "switch", live_preview="dock_sync"),
    _s("scy.dock.recent_limit", "03-dock-studio", "Recent Applications Limit", "Maximum number of recently used unpinned apps shown.", "int", 3, "slider", min_val=0, max_val=8, step=1, live_preview="dock_sync"),
    _s("scy.dock.show_frequent_apps", "03-dock-studio", "Suggest Frequent Applications", "Include top frequently launched apps when recent slots are free.", "bool", False, "switch", live_preview="dock_sync"),
    _s("scy.dock.app_groups_enabled", "03-dock-studio", "Enable Application Groups", "Group related pinned apps into expandable dock folders.", "bool", True, "switch", live_preview="dock_sync"),
    _s("scy.dock.show_separators", "03-dock-studio", "Show Section Separators", "Draw subtle glass dividers between launcher, pinned, grouped, and running sections.", "bool", True, "switch", live_preview="dock_sync"),
    _s("scy.dock.material", "03-dock-studio", "Dock Surface Material", "Material treatment of the dock container.", "enum", "scy-frosted", "dropdown", choices=_ch(("scy-frosted", "Scy Frosted Glass"), ("liquid-crystal", "Liquid Crystal"), ("obsidian-matte", "Obsidian Matte"), ("tinted-acrylic", "Tinted Acrylic"), ("minimal-clear", "Minimal Clear")), live_preview="dock_sync"),
    _s("scy.dock.opacity", "03-dock-studio", "Dock Background Opacity", "Background fill opacity of the dock surface.", "float", 0.84, "slider", min_val=0.10, max_val=1.0, step=0.02, live_preview="dock_sync"),
    _s("scy.dock.blur_enabled", "03-dock-studio", "Dock Background Blur", "Apply compositor dual-kawase blur behind the dock.", "bool", True, "switch", live_preview="dock_sync"),
    _s("scy.dock.border_width", "03-dock-studio", "Dock Border Thickness", "Specular glass rim thickness around the dock.", "int", 1, "slider", min_val=0, max_val=4, step=1, unit="px", live_preview="dock_sync"),
    _s("scy.dock.shadow_strength", "03-dock-studio", "Dock Elevation Shadow", "Ambient drop-shadow intensity beneath floating dock.", "float", 0.45, "slider", min_val=0.0, max_val=1.0, step=0.05, live_preview="dock_sync"),
    _s("scy.dock.glow_strength", "03-dock-studio", "Dock Accent Underglow", "Subtle accent-colored underglow intensity on active dock.", "float", 0.18, "slider", min_val=0.0, max_val=1.0, step=0.05, live_preview="dock_sync"),
    _s("scy.dock.auto_hide_mode", "03-dock-studio", "Intelligent Auto-Hide Policy", "When the dock hides to maximize screen space.", "enum", "dodge-windows", "dropdown", choices=_ch(("never", "Always Visible"), ("dodge-windows", "Dodge Overlapping Windows"), ("dodge-maximized", "Dodge Maximized / Fullscreen"), ("always-hide", "Always Auto-Hide")), live_preview="dock_sync"),
    _s("scy.dock.reveal_delay_ms", "03-dock-studio", "Edge Hover Reveal Delay", "Pointer dwell time at screen edge before hidden dock rises.", "int", 120, "slider", min_val=0, max_val=600, step=20, unit="ms", live_preview="dock_sync"),
    _s("scy.dock.monitor_policy", "03-dock-studio", "Multi-Monitor Dock Policy", "Which displays show the Scy-Shell dock.", "enum", "primary", "segmented", choices=_ch(("primary", "Primary Display"), ("focused", "Focused Display"), ("all", "All Displays")), live_preview="dock_sync"),
    _s("scy.dock.locked", "03-dock-studio", "Lock Dock Layout", "Prevent accidental drag-and-drop unpinning or reordering on the dock.", "bool", False, "switch", live_preview="dock_sync"),
    _s("scy.dock.preset", "03-dock-studio", "Dock Preset", "Quick architectural dock preset.", "enum", "lucid-signature", "dropdown", choices=_ch(("lucid-signature", "Lucid Signature Island"), ("carved-notch", "Carved Bottom Notch"), ("trinity-split", "Trinity Split Islands"), ("left-studio-rail", "Left Studio Rail"), ("minimal-float", "Minimal Micro-Float")), live_preview="dock_sync"),

    # --- 04: VISUAL EFFECTS & MOTION ---
    _s("scy.effects.material_preset", "04-visual-effects", "Global Surface Material Preset", "Master material preset governing glass, grain, rim specular, and elevation.", "enum", "scy-frosted", "dropdown", choices=_ch(("scy-frosted", "Scy Frosted Glass"), ("liquid-crystal", "Liquid Crystal"), ("obsidian-matte", "Obsidian Matte"), ("tinted-acrylic", "Tinted Acrylic"), ("minimal-flat", "Crisp Flat"))),
    _s("scy.effects.bg_opacity", "04-visual-effects", "Panel Background Opacity", "Global background opacity across panels, drawers, and popovers.", "float", 0.86, "slider", min_val=0.20, max_val=1.0, step=0.02),
    _s("scy.effects.surface_opacity", "04-visual-effects", "Card Surface Opacity", "Elevated card and tile opacity inside panels and widgets.", "float", 0.92, "slider", min_val=0.30, max_val=1.0, step=0.02),
    _s("scy.effects.blur_strength", "04-visual-effects", "Compositor Blur Passes", "Dual-Kawase blur pass depth on glass shell layers.", "int", 3, "slider", min_val=0, max_val=6, step=1),
    _s("scy.effects.blur_radius", "04-visual-effects", "Compositor Blur Radius", "Blur kernel size in pixels for frosted shell surfaces.", "int", 8, "slider", min_val=0, max_val=24, step=1, unit="px"),
    _s("scy.effects.saturation", "04-visual-effects", "Glass Backdrop Saturation", "Vibrancy saturation boost behind blurred glass panels.", "float", 1.12, "slider", min_val=0.50, max_val=1.80, step=0.02),
    _s("scy.effects.contrast", "04-visual-effects", "Glass Backdrop Contrast", "Contrast shaping behind translucent surfaces.", "float", 1.04, "slider", min_val=0.70, max_val=1.50, step=0.02),
    _s("scy.effects.brightness", "04-visual-effects", "Glass Backdrop Brightness", "Brightness multiplier behind translucent surfaces.", "float", 1.0, "slider", min_val=0.60, max_val=1.40, step=0.02),
    _s("scy.effects.gradient_angle", "04-visual-effects", "Surface Gradient Direction", "Directional lighting gradient angle across glass borders and cards.", "int", 135, "slider", min_val=0, max_val=360, step=15, unit="deg"),
    _s("scy.effects.gradient_intensity", "04-visual-effects", "Surface Gradient Intensity", "Subtle tonal gradient strength on elevated cards.", "float", 0.22, "slider", min_val=0.0, max_val=1.0, step=0.02),
    _s("scy.effects.border_thickness", "04-visual-effects", "Global Rim Border Thickness", "Crisp hairline border width on shell panels and popups.", "int", 1, "slider", min_val=0, max_val=4, step=1, unit="px"),
    _s("scy.effects.border_opacity", "04-visual-effects", "Rim Border Opacity", "Specular border highlight opacity.", "float", 0.28, "slider", min_val=0.0, max_val=1.0, step=0.02),
    _s("scy.effects.shadow_softness", "04-visual-effects", "Elevation Shadow Softness", "Blur spread of panel and popup shadows.", "int", 28, "slider", min_val=0, max_val=72, step=2, unit="px"),
    _s("scy.effects.shadow_distance", "04-visual-effects", "Elevation Shadow Distance", "Vertical shadow offset for floating shell surfaces.", "int", 10, "slider", min_val=0, max_val=32, step=1, unit="px"),
    _s("scy.effects.glow_intensity", "04-visual-effects", "Interactive Accent Glow", "Soft accent halo around focused controls and active capsules.", "float", 0.20, "slider", min_val=0.0, max_val=1.0, step=0.05),
    _s("scy.effects.glass_reflection", "04-visual-effects", "Top-Edge Glass Specular", "Top-edge inner specular highlight simulating real beveled glass.", "float", 0.30, "slider", min_val=0.0, max_val=1.0, step=0.05),
    _s("scy.effects.shader_preset", "04-visual-effects", "Compositor Surface Shader", "Supported Wayland/Hyprland visual post-processing shader.", "enum", "none", "dropdown", choices=_ch(("none", "None (Native Color)"), ("subtle-grain", "Subtle Film Grain"), ("warm-cinema", "Warm Cinema"), ("high-contrast", "Crisp High Contrast"))),
    _s("scy.effects.motion_preset", "04-visual-effects", "Animation Physics Preset", "Master animation curve and spring personality.", "enum", "expressive-spring", "segmented", choices=_ch(("expressive-spring", "Expressive"), ("fluid-silk", "Fluid Silk"), ("crisp-snappy", "Snappy"), ("minimal", "Minimal"), ("instant", "Instant"))),
    _s("scy.effects.duration_scale", "04-visual-effects", "Animation Duration Multiplier", "Scales transition durations globally (0 = instant, 1.0 = standard).", "float", 1.0, "slider", min_val=0.0, max_val=2.0, step=0.05),
    _s("scy.effects.delay_ms", "04-visual-effects", "Cascade Stagger Delay", "Stagger delay between sequential list/card animations.", "int", 18, "slider", min_val=0, max_val=80, step=2, unit="ms"),
    _s("scy.effects.spring_stiffness", "04-visual-effects", "Spring Stiffness", "Hooke stiffness constant for morphing panels, Dynamic Island, and dock.", "int", 380, "slider", min_val=120, max_val=800, step=10),
    _s("scy.effects.spring_damping", "04-visual-effects", "Spring Damping Ratio", "Spring damping ratio (lower = bouncier, 1.0 = critically damped).", "float", 0.78, "slider", min_val=0.45, max_val=1.0, step=0.01),
    _s("scy.effects.entry_animation", "04-visual-effects", "Panel Entry Transition", "Entry animation style when opening launcher, Control Center, and popovers.", "enum", "morph-scale", "dropdown", choices=_ch(("morph-scale", "Morph & Scale"), ("slide-edge", "Slide from Edge"), ("fade-lift", "Fade & Lift"), ("none", "Instant"))),
    _s("scy.effects.exit_animation", "04-visual-effects", "Panel Exit Transition", "Exit animation style when dismissing overlays.", "enum", "sink-fade", "dropdown", choices=_ch(("sink-fade", "Sink & Fade"), ("slide-edge", "Slide to Edge"), ("fade", "Quick Fade"), ("none", "Instant"))),
    _s("scy.effects.workspace_animation", "04-visual-effects", "Workspace Switch Transition", "Hyprland workspace transition style.", "enum", "slide", "segmented", choices=_ch(("slide", "Horizontal Slide"), ("slidevert", "Vertical Slide"), ("fade", "Cross-Fade"), (" slidefade", "Slide + Fade"))),

    # --- 05: LAYOUT & COMPOSITION ---
    _s("scy.layout.active_preset", "05-layout", "Active Desktop Layout Preset", "Complete panel/dock/widget spatial composition.", "enum", "scy-signature", "dropdown", choices=_ch(("scy-signature", "Scy Signature (Top Island + Bottom Dock)"), ("unity-left", "Studio Left Rail + Top Bar"), ("minimal-top", "Minimal Single Top Bar"), ("bottom-deck", "Unified Bottom Deck"), ("dual-stage", "Creator Dual-Edge Stage"))),
    _s("scy.layout.global_scale", "05-layout", "Shell UI Density & Scale", "Global layout scaling across all Scy-Shell panels and Studio.", "float", 1.0, "slider", min_val=0.80, max_val=1.50, step=0.05),
    _s("scy.layout.corner_radius_scale", "05-layout", "Global Corner Radius Scale", "Multiplier applied to panel, card, button, and popup corner radii.", "float", 1.0, "slider", min_val=0.0, max_val=1.60, step=0.05),
    _s("scy.layout.spacing_scale", "05-layout", "Internal Spacing Scale", "Multiplier for internal container padding and module gaps.", "float", 1.0, "slider", min_val=0.70, max_val=1.50, step=0.05),
    _s("scy.layout.outer_margin", "05-layout", "Screen-Edge Floating Margin", "Outer breathing space around floating bars and side drawers.", "int", 8, "slider", min_val=0, max_val=32, step=1, unit="px"),
    _s("scy.layout.bar_layer", "05-layout", "Top Bar Wayland Layer Priority", "Wayland wlr-layer-shell Z-order for the primary bar.", "enum", "top", "segmented", choices=_ch(("bottom", "Bottom"), ("top", "Top"), ("overlay", "Overlay"))),
    _s("scy.layout.multi_monitor_mode", "05-layout", "Multi-Monitor Bar Distribution", "How panels deploy across connected displays.", "enum", "all-displays", "segmented", choices=_ch(("all-displays", "All Displays"), ("primary-only", "Primary Only"), ("focused-follow", "Follow Focus"))),
    _s("scy.layout.compact_breakpoint", "05-layout", "Responsive Compact Width", "Display logical width below which bars and Studio switch to compact density.", "int", 1366, "slider", min_val=960, max_val=1920, step=20, unit="px"),

    # --- 06: WIDGETS & COMPONENTS ---
    _s("scy.widgets.board_preset", "06-widgets", "Desktop Widget Board Preset", "Curated desktop widget layout.", "enum", "balanced-glance", "dropdown", choices=_ch(("balanced-glance", "Balanced Glance (Clock + Weather + Media)"), ("minimal-zen", "Minimal Zen Clock"), ("telemetry-pro", "System Telemetry Pro"), ("productivity-hub", "Agenda + Notes + Pomodoro"), ("clean-slate", "Clean Desktop (No Widgets)"))),
    _s("scy.widgets.live_preview", "06-widgets", "Live Desktop Component Preview", "Apply Component Laboratory adjustments to the live desktop in real time.", "bool", True, "switch"),
    _s("scy.widgets.sync_glass", "06-widgets", "Synchronize Widget Glass with Shell", "Keep all desktop widgets harmonized with Global Surface Material tokens.", "bool", True, "switch"),

    # --- 07: WINDOW MANAGEMENT (HYPRLAND 0.57+) ---
    _s("scy.windows.layout_engine", "07-windows", "Hyprland Tiling Layout Engine", "Primary window tiling algorithm in Hyprland 0.57+.", "enum", "dwindle", "segmented", choices=_ch(("dwindle", "Dwindle Spiral"), ("master", "Master + Stack")), live_preview="hypr_trial"),
    _s("scy.windows.smart_gaps", "07-windows", "Smart Single-Window Gaps", "Reduce outer gaps automatically when only one tiled window is on a workspace.", "bool", False, "switch", live_preview="hypr_trial"),
    _s("scy.windows.dim_inactive", "07-windows", "Dim Unfocused Windows", "Subtly dim background windows to highlight active focus.", "bool", False, "switch", live_preview="hypr_trial"),
    _s("scy.windows.dim_strength", "07-windows", "Unfocused Window Dimming", "Dimming factor applied to inactive windows.", "float", 0.12, "slider", min_val=0.0, max_val=0.50, step=0.02, live_preview="hypr_trial"),
    _s("scy.windows.center_floating", "07-windows", "Auto-Center New Floating Dialogs", "Automatically center newly spawned floating utility windows.", "bool", True, "switch"),

    # --- 08: INTERACTIONS ---
    _s("scy.interactions.profile", "08-interactions", "Interaction Profile", "Curated input, gesture, and shortcut preset.", "enum", "default", "segmented", choices=_ch(("default", "Balanced"), ("laptop-touch", "Trackpad First"), ("vim-keyboard", "Keyboard Driven"), ("creator-mouse", "Mouse Precision"))),
    _s("scy.interactions.corner_top_left", "08-interactions", "Top-Left Hot Corner", "Action triggered when dwelling pointer in top-left screen corner.", "enum", "overview", "dropdown", choices=_ch(("none", "Disabled"), ("overview", "Workspace Overview"), ("launcher", "App Launcher"), ("control-center", "Control Center"), ("lock", "Lock Screen"))),
    _s("scy.interactions.corner_top_right", "08-interactions", "Top-Right Hot Corner", "Action triggered in top-right screen corner.", "enum", "control-center", "dropdown", choices=_ch(("none", "Disabled"), ("overview", "Workspace Overview"), ("launcher", "App Launcher"), ("control-center", "Control Center"), ("notifications", "Notification Drawer"))),
    _s("scy.interactions.corner_bottom_left", "08-interactions", "Bottom-Left Hot Corner", "Action triggered in bottom-left screen corner.", "enum", "none", "dropdown", choices=_ch(("none", "Disabled"), ("launcher", "App Launcher"), ("overview", "Workspace Overview"), ("dock-reveal", "Reveal Dock"))),
    _s("scy.interactions.corner_bottom_right", "08-interactions", "Bottom-Right Hot Corner", "Action triggered in bottom-right screen corner.", "enum", "none", "dropdown", choices=_ch(("none", "Disabled"), ("desktop-peek", "Peek Desktop"), ("notes", "Quick Notes"), ("control-center", "Control Center"))),
    _s("scy.interactions.bar_scroll_workspaces", "08-interactions", "Scroll on Top Bar Switches Workspaces", "Allow mouse-wheel/two-finger scrolling on the bar to step workspaces.", "bool", True, "switch"),

    # --- 09: NOTIFICATIONS & CONTROL CENTER ---
    _s("scy.control_center.columns", "09-notifications", "Control Center Quick-Tile Columns", "Number of columns in the Control Center quick-toggle grid.", "int", 2, "segmented", choices=_ch(("2", "2 Columns"), ("3", "3 Columns"), ("4", "4 Compact"))),
    _s("scy.control_center.show_wifi", "09-notifications", "Show Wi-Fi Quick Toggle", "Display live NetworkManager Wi-Fi tile in Control Center.", "bool", True, "switch"),
    _s("scy.control_center.show_bluetooth", "09-notifications", "Show Bluetooth Quick Toggle", "Display BlueZ Bluetooth tile in Control Center.", "bool", True, "switch"),
    _s("scy.control_center.show_power_profiles", "09-notifications", "Show Power Profile Selector", "Display power-profiles-daemon / TLP mode switcher in Control Center.", "bool", True, "switch"),
    _s("scy.control_center.show_night_light", "09-notifications", "Show Night Light Quick Tile", "Display warm color-temperature eye-comfort toggle.", "bool", True, "switch"),
    _s("scy.control_center.show_caffeine", "09-notifications", "Show Caffeine Idle-Inhibitor Tile", "Allow preventing screen sleep with one click from Control Center.", "bool", True, "switch"),
    _s("scy.control_center.show_media_player", "09-notifications", "Embed MPRIS Media Card", "Show active media artwork and transport controls inside Control Center.", "bool", True, "switch"),
    _s("scy.control_center.history_limit", "09-notifications", "Notification History Retention", "Maximum notifications retained in scrollable Notification Center history.", "int", 50, "slider", min_val=10, max_val=200, step=10),

    # --- 10: SYSTEM, HARDWARE & INTELLIGENT PERFORMANCE ---
    _s("scy.performance.tier", "10-system", "Intelligent Performance Profile", "Hardware-aware visual & power profile with explicit effect explanations.", "enum", "balanced", "segmented", choices=_ch(("max-quality", "Max Visuals"), ("balanced", "Balanced"), ("performance", "Performance"), ("battery", "Battery Saver")), live_preview="perf_tier"),
    _s("scy.performance.keep_blur_on_battery", "10-system", "Keep Glass Blur in Battery Saver", "Explicit override: retain frosted blur even when Battery Saver tier is selected.", "bool", False, "switch"),
    _s("scy.performance.keep_animations_on_perf", "10-system", "Keep Smooth Animations in Performance Mode", "Explicit override: retain spring transitions in Performance mode.", "bool", True, "switch"),
    _s("scy.performance.lazy_studio_tabs", "10-system", "On-Demand Lazy Studio Page Loading", "Unload inactive Studio pages when closed to minimize idle RAM footprint.", "bool", True, "switch"),
    _s("scy.performance.vrr_policy", "10-system", "Variable Refresh Rate (VRR / Adaptive Sync)", "Hyprland VRR policy for supported high-refresh displays.", "enum", "fullscreen-only", "segmented", choices=_ch(("off", "Off"), ("on", "Always On"), ("fullscreen-only", "Fullscreen / Games"))),

    # --- 11: LOCK SCREEN STUDIO (INDEPENDENT OF LOGIN!) ---
    _s("scy.lock.clock_style", "11-lock-screen", "Lock Screen Clock Layout", "Typography and spatial layout of the session lock clock.", "enum", "stacked-expressive", "dropdown", choices=_ch(("stacked-expressive", "Stacked Expressive"), ("inline-bold", "Inline Bold"), ("editorial-serif", "Editorial"), ("minimal-pill", "Minimal Pill"), ("orbit-analog", "Orbit Analog")), live_preview="lock_preview"),
    _s("scy.lock.date_format", "11-lock-screen", "Lock Screen Date Format", "Qt/strftime date format string displayed beneath the lock clock.", "string", "dddd, d MMMM", "text", live_preview="lock_preview"),
    _s("scy.lock.show_weather", "11-lock-screen", "Show Live Weather on Lock Screen", "Display current temperature and condition badge on the lock screen.", "bool", True, "switch", live_preview="lock_preview"),
    _s("scy.lock.show_media", "11-lock-screen", "Show MPRIS Media Controls when Locked", "Allow pausing/skipping current audio track from the lock screen.", "bool", True, "switch", live_preview="lock_preview"),
    _s("scy.lock.notification_privacy", "11-lock-screen", "Locked Notification Privacy", "How incoming notifications appear while the session is locked.", "enum", "summary-only", "segmented", choices=_ch(("full", "Full Content"), ("summary-only", "App Name Only"), ("count-only", "Count Pill"), ("hidden", "Hidden")), live_preview="lock_preview"),
    _s("scy.lock.wallpaper_override", "11-lock-screen", "Dedicated Lock Screen Wallpaper", "Optional image path specifically for Lock Screen (empty = use desktop wallpaper).", "string", "", "text", live_preview="lock_preview"),
    _s("scy.lock.glass_preset", "11-lock-screen", "Lock Prompt Glass Material", "Material treatment of the password card and lock widgets.", "enum", "scy-frosted", "segmented", choices=_ch(("scy-frosted", "Frosted"), ("liquid-crystal", "Crystal"), ("obsidian-matte", "Obsidian")), live_preview="lock_preview"),
    _s("scy.lock.show_avatar", "11-lock-screen", "Show User Avatar on Lock Screen", "Display circular user profile portrait above the unlock prompt.", "bool", True, "switch", live_preview="lock_preview"),
    _s("scy.lock.auth_feedback", "11-lock-screen", "Authentication Feedback Animation", "Visual response on password verification and failed attempts.", "enum", "spring-shake", "segmented", choices=_ch(("spring-shake", "Spring Shake + Halo"), ("pulse-ring", "Pulse Ring"), ("subtle", "Subtle Color")), live_preview="lock_preview"),
    _s("scy.lock.show_system_info", "11-lock-screen", "Show Battery & Keyboard Layout Pill", "Display battery percentage, caps-lock warning, and XKB layout on lock screen.", "bool", True, "switch", live_preview="lock_preview"),

    # --- 12: LOGIN EXPERIENCE STUDIO (INDEPENDENT OF LOCK SCREEN!) ---
    _s("scy.login.greeter_target", "12-login", "Active System Login Greeter", "System display manager theme managed by Scy-Shell (stages safely without clobbering).", "enum", "preserve", "segmented", choices=_ch(("preserve", "Preserve System DM"), ("scy-sddm", "Scy-Shell SDDM Theme"), ("scy-greetd", "Scy-Shell Greetd")), live_preview="preauth_stage"),
    _s("scy.login.mirror_lock_layout", "12-login", "Mirror Lock Screen Clock into Login", "Explicit opt-in: off by default so Lock Screen and Login configurations stay independent.", "bool", False, "switch", live_preview="preauth_stage"),
    _s("scy.login.user_list_style", "12-login", "Login User Selector Layout", "Presentation of system accounts on the login screen.", "enum", "avatar-cards", "segmented", choices=_ch(("avatar-cards", "Avatar Cards"), ("carousel", "Centered Carousel"), ("compact-dropdown", "Compact Selector")), live_preview="preauth_stage"),
    _s("scy.login.avatar_ring", "12-login", "Login Avatar Accent Ring", "Draw Scy-Shell OKLCH accent ring around selected user avatar.", "bool", True, "switch", live_preview="preauth_stage"),
    _s("scy.login.password_style", "12-login", "Login Password Field Style", "Visual style of the pre-login authentication input.", "enum", "glass-pill", "segmented", choices=_ch(("glass-pill", "Frosted Pill"), ("outlined-card", "Outlined Card"), ("minimal-line", "Minimal Line")), live_preview="preauth_stage"),
    _s("scy.login.show_session_picker", "12-login", "Show Wayland Session Selector", "Allow choosing Hyprland (Scy-Shell) or other installed sessions at login.", "bool", True, "switch", live_preview="preauth_stage"),
    _s("scy.login.show_power_actions", "12-login", "Show Power / Reboot / Suspend Controls", "Display system power buttons on the login greeter.", "bool", True, "switch", live_preview="preauth_stage"),
    _s("scy.login.background_path", "12-login", "Independent Login Background", "Dedicated wallpaper path for the login screen (never overwritten by Lock Screen).", "string", "", "text", live_preview="preauth_stage"),
    _s("scy.login.background_blur", "12-login", "Login Background Blur Radius", "Backdrop blur applied behind the login card.", "int", 36, "slider", min_val=0, max_val=80, step=2, unit="px", live_preview="preauth_stage"),
    _s("scy.login.clock_24h", "12-login", "Login 24-Hour Clock", "Use 24-hour time formatting on the login screen.", "bool", True, "switch", live_preview="preauth_stage"),
    _s("scy.login.login_animation", "12-login", "Login Entry & Handoff Animation", "Transition animation when greeting and handing off into Hyprland.", "enum", "smooth-rise", "segmented", choices=_ch(("smooth-rise", "Smooth Rise"), ("zoom-dissolve", "Zoom Dissolve"), ("minimal", "Minimal")), live_preview="preauth_stage"),
    _s("scy.login.high_contrast", "12-login", "Login High-Contrast Accessibility", "Boost border and text contrast on the login screen for readability.", "bool", False, "switch", live_preview="preauth_stage"),
    _s("scy.login.ui_scale", "12-login", "Login Greeter HiDPI Scale", "Independent UI scaling factor for the pre-login greeter.", "float", 1.0, "slider", min_val=0.75, max_val=2.0, step=0.05, live_preview="preauth_stage"),

    # --- 13: APPLICATIONS & PRODUCTIVITY ---
    _s("scy.productivity.calc_converter", "13-productivity", "Launcher Math & Unit Converter", "Evaluate math expressions and unit conversions directly inside the launcher.", "bool", True, "switch"),
    _s("scy.productivity.web_search_provider", "13-productivity", "Launcher `?` Web Search Engine", "Search engine opened when typing `? <query>` in the launcher.", "enum", "duckduckgo", "dropdown", choices=_ch(("duckduckgo", "DuckDuckGo"), ("brave", "Brave Search"), ("google", "Google"), ("kagi", "Kagi"), ("searxng", "Local SearXNG"))),
    _s("scy.productivity.clipboard_history_max", "13-productivity", "Clipboard History Entries", "Maximum entries retained in searchable clipboard history.", "int", 100, "slider", min_val=10, max_val=500, step=10),
    _s("scy.productivity.quick_notes_enabled", "13-productivity", "Quick Notes Scratchpad", "Enable persistent Markdown quick-notes accessible from launcher and widgets.", "bool", True, "switch"),
    _s("scy.productivity.focus_minutes", "13-productivity", "Default Focus / Pomodoro Duration", "Default work session duration for Scy Focus Timer.", "int", 25, "slider", min_val=5, max_val=120, step=5, unit="min"),
    _s("scy.productivity.screenshot_ocr", "13-productivity", "Enable OCR Text Extraction in Capture", "Offer one-click Tesseract OCR text copy when capturing a screen region.", "bool", True, "switch"),
    _s("scy.productivity.recorder_fps", "13-productivity", "Screen Recorder Frame Rate", "Target frame rate when recording via wf-recorder.", "int", 60, "segmented", choices=_ch(("30", "30 FPS"), ("60", "60 FPS"), ("120", "120 FPS"))),

    # --- 14: PROFILES & PRESETS ---
    _s("scy.profiles.active", "14-profiles", "Active Desktop Profile", "Complete Scy-Shell desktop configuration profile.", "enum", "balanced", "dropdown", choices=_ch(("balanced", "Balanced (Scy Default)"), ("minimal", "Minimal Zen"), ("productivity", "Productivity Focus"), ("immersive", "Immersive Glass"), ("gaming", "Gaming Low-Latency"), ("creative", "Creative Studio"), ("cinema", "Cinema OLED"), ("custom", "Custom User Profile")), live_preview="profile_apply"),
    _s("scy.profiles.auto_backup_on_switch", "14-profiles", "Snapshot Before Profile Switch", "Automatically create a recoverable backup snapshot before applying a desktop profile.", "bool", True, "switch"),
)
