# Stage 0 Deliverable 3 — Complete Feature-by-Feature Comparison & Classification Matrix

Every feature in **Lucid 2 (`v1.21.1`)** and **Mandara (`v0.38.2`)** has been audited in source code and classified into one of the six mandatory Scy-Shell architectural classes (**Classes A–F**). Machine-readable full metadata (all 15 fields per feature) is saved alongside this document in [`03-feature-inventory.json`](./03-feature-inventory.json).

## 1. Classification Summary

| Class | Definition | Subsystems | Scy-Shell Policy |
|---|---|---:|---|
| **Class A** | Present only in **Lucid 2** | 9 | Preserved 100% intact; integrated with Scy-Shell bus & primary M3 identity. |
| **Class B** | Present only in **Mandara** | 11 (incl. 88 plugins, AI, Wallgen, 19 Looks, 11 compositors) | Preserved 100% intact; bridged to Lucid surfaces & styled with M3 Expressive default Look. |
| **Class C** | Equivalent functionality in both | 2 (OSD, Clipboard watcher) | **Lucid default**; Mandara selectable; single active daemon enforced. |
| **Class D** | Materially different implementations in both | 9 (Bar, Dock, Launcher, Quick Settings, Notifs/Toasts, Desktop Widgets, Wallpaper, Lock, Capture, Overview) | **Dual Provider + Presentation** preserved; Lucid default; Mandara selectable globally/per-surface; hybrid modes where Wayland-safe. |
| **Class E** | Present in **neither** (Integration layer) | 3 (`scy-daemon`, Unified M3 Studio, Conflict Detector) | Built natively in **Scy-Shell** (`scy-shell/`). |
| **Class F** | Exclusive system / D-Bus / Wayland / Config resources | 6 (+ D-05/D-07/D-08) | Strict single-owner arbitration + atomic handoff via `scy-daemon`. |

---

## 2. Complete Feature Matrix (All 15 Audited Dimensions)

### `A-01` — Lumen File Manager & XDG FileChooser Portal
- **Classification:** **Class A (Lucid-only)**
- **Category:** Standalone Desktop Apps & Portals | **Source Project:** Lucid
- **Source Files:** `lucidlumen/Lumen.qml`, `support/lumend.py`
- **User-Facing Behavior:** Full M3 Expressive dual-pane/tabbed file manager (grid/list/column views, preview pane, archive extraction, trash, bulk rename, git badges) AND native org.freedesktop.impl.portal.FileChooser open/save file dialog replacement.
- **Settings Keys:** `scy.providers.lucid.lumen.* (17 keys)`
- **Keybindings:** Super+E (open Lumen)
- **IPC / D-Bus / Sockets:** `qs ipc call lumen ...`, `org.freedesktop.impl.portal.FileChooser (lumend.py)`
- **Wayland / Hyprland Hooks:** `windowrule float/size for portal dialogs`
- **Visual Presentation:** Material 3 Expressive window + Glass sidebar + Jelly transitions
- **Dependencies:** quickshell, python3-dbus-next, xdg-desktop-portal
- **Conflicts & Risks:** Must declare portal priority cleanly in ~/.config/xdg-desktop-portal/hyprland-portals.conf without breaking ScreenCast/Screenshot portals.
- **Scy-Shell Target Design:** Preserve 100% intact as Scy-Shell's default File Manager & optional XDG FileChooser portal toggle in Scy-Shell Studio.

### `A-02` — Lens Image Viewer & Quick Editor
- **Classification:** **Class A (Lucid-only)**
- **Category:** Standalone Desktop Apps | **Source Project:** Lucid
- **Source Files:** `lucidlens/Lens.qml`
- **User-Facing Behavior:** Standalone M3 Expressive image viewer with smooth zoom/pan, EXIF metadata inspector, filmstrip, slideshow, crop/rotate/flip, and one-click Set as Wallpaper.
- **Settings Keys:** `scy.providers.lucid.lens.* (22 keys)`
- **Keybindings:** Launched via MIME association / Lumen
- **IPC / D-Bus / Sockets:** `qs -p lucidlens/Lens.qml`
- **Wayland / Hyprland Hooks:** `Standard Wayland toplevel + wallpaper IPC trigger`
- **Visual Presentation:** Material 3 Expressive chromeless glass viewer
- **Dependencies:** quickshell, qt6-imageformats
- **Conflicts & Risks:** None (standalone app).
- **Scy-Shell Target Design:** Preserve 100% intact and connect 'Set as Wallpaper' to Scy-Shell's unified Wallpaper Coordinator.

### `A-03` — Lucid Standalone Clock App
- **Classification:** **Class A (Lucid-only)**
- **Category:** Standalone Desktop Apps | **Source Project:** Lucid
- **Source Files:** `lucidclock/ClockApp.qml`, `Timers.qml`
- **User-Facing Behavior:** Dedicated M3 Expressive desktop application for Alarms, World Clocks, Multi-Timers, Lap Stopwatch, and Pomodoro focus sessions.
- **Settings Keys:** `scy.providers.lucid.clock_app.* (5 keys)`, `Prefs.pomodoro*`, `Prefs.timer*`
- **Keybindings:** Launched from Launcher or Calendar popover
- **IPC / D-Bus / Sockets:** `Shares Timers.qml state with Lucid bar/calendar`
- **Wayland / Hyprland Hooks:** `Standard Wayland toplevel`
- **Visual Presentation:** Material 3 Expressive morphing shapes & expressive numerals
- **Dependencies:** quickshell
- **Conflicts & Risks:** Timer state sync when Mandara Pomodoro plugin is used.
- **Scy-Shell Target Design:** Preserve 100% intact and bridge timer/pomodoro state over Scy-Shell Event Bus.

### `A-04` — Desktop File & Folder Icons Canvas (~/Desktop)
- **Classification:** **Class A (Lucid-only)**
- **Category:** Desktop Surface | **Source Project:** Lucid
- **Source Files:** `Desktop.qml`, `DesktopIcons.qml`, `support/desktop-icons.py`
- **User-Facing Behavior:** Full interactive desktop icon grid for ~/Desktop (files, folders, .desktop launchers, Trash, Home) with rubber-band selection, drag-and-drop move/copy, inline F2 rename, thumbnails, context menus, and 17 keyboard shortcuts.
- **Settings Keys:** `Prefs.desktopIcons*`, `DesktopIcons 17 shortcut actions`
- **Keybindings:** F2, Del, Shift+Del, Ctrl+C/X/V/A/Z, Enter, Space, Menu (when desktop focused)
- **IPC / D-Bus / Sockets:** `support/desktop-icons.py JSON helper`
- **Wayland / Hyprland Hooks:** `wlr-layer-shell LAYER_BOTTOM`
- **Visual Presentation:** M3 Expressive icon tiles, rubber-band pill marquee, Glass context menu
- **Dependencies:** quickshell, python3
- **Conflicts & Risks:** Layer Z-order & pointer hit-testing with desktop widgets.
- **Scy-Shell Target Design:** Preserve 100% intact; compose cleanly with widget input regions via Scy-Shell Layer Coordinator.

### `A-05` — Jelly Squash-and-Stretch Physics & MaterialShape Organic Polygons
- **Classification:** **Class A (Lucid-only — promoted to Scy-Shell Primary Identity)**
- **Category:** Visual Identity & Motion | **Source Project:** Lucid
- **Source Files:** `Jelly.qml`, `MaterialShape.qml`, `Shapes.js`
- **User-Facing Behavior:** Signature M3 Expressive directional velocity-driven squash-and-stretch deformation (Jelly) and morphing geometric cookies/clovers/scallops/arches across UI controls, avatars, clocks, and photo frames.
- **Settings Keys:** `Prefs.jelly`, `Prefs.jellyAmount`, `Prefs.motionScale`, `Prefs.cornerScale`
- **Keybindings:** None / GUI-triggered
- **IPC / D-Bus / Sockets:** ``
- **Wayland / Hyprland Hooks:** ``
- **Visual Presentation:** Defining visual signature of Lucid 2 / Material 3 Expressive
- **Dependencies:** quickshell
- **Conflicts & Risks:** Mandara GPUI surfaces lack M3 Expressive cookie shapes & Jelly deformation natively.
- **Scy-Shell Target Design:** Retain natively in all Lucid surfaces AND port M3 Expressive SVG/path cookie shapes, HCT tokens, Google Sans, and spring parameters into Scy-Shell's default M3-Expressive Look for Mandara GPUI surfaces.

### `A-06` — On-Screen Virtual Keyboard (lucidkeys)
- **Classification:** **Class A (Lucid-only)**
- **Category:** Input & Accessibility | **Source Project:** Lucid
- **Source Files:** `lucidkeys/Keyboard.qml`, `lucidlock/parts/OnScreenKeys.qml`
- **User-Facing Behavior:** Floating/docked Wayland touch & mouse virtual keyboard supporting XKB layouts, modifiers, emoji switch, and lock-screen password entry.
- **Settings Keys:** `scy.providers.lucid.keys.* (4 keys)`, `Prefs.lockOsk*`
- **Keybindings:** Super+K / IPC toggle `keys`
- **IPC / D-Bus / Sockets:** `qs ipc call keys toggle`
- **Wayland / Hyprland Hooks:** `wlr-layer-shell LAYER_OVERLAY (no focus steal), wtype`
- **Visual Presentation:** M3 Expressive keycaps with Jelly press feedback
- **Dependencies:** quickshell, wtype
- **Conflicts & Risks:** None.
- **Scy-Shell Target Design:** Preserve 100% intact across both session and lock screen.

### `A-07` — SDDM Theme Synced with Per-User Lock Layout
- **Classification:** **Class A (Lucid-only — paired with B-09 greetd)**
- **Category:** Display Manager / Pre-Auth | **Source Project:** Lucid
- **Source Files:** `support/sddm/lucid/`, `support/sync-sddm.sh`, `lucidlock/parts/Catalog.js`
- **User-Facing Behavior:** Qt6 SDDM theme sharing the exact 6 presets and slot widgets of lucidlock, synced per-user via sync-sddm.sh.
- **Settings Keys:** `scy.providers.lucid.sddm.* (25 keys)`, `Prefs.lockPreset`, `Prefs.lockSlots`
- **Keybindings:** None / GUI-triggered
- **IPC / D-Bus / Sockets:** `sddm-helper`
- **Wayland / Hyprland Hooks:** `SDDM greeter session`
- **Visual Presentation:** Material 3 Expressive SDDM login screen
- **Dependencies:** sddm, qt6-declarative
- **Conflicts & Risks:** System-level mutual exclusion with greetd.service (Mandara Greeter).
- **Scy-Shell Target Design:** Preserve 100% intact; installer & Scy-Shell Studio allow explicit choice between Lucid SDDM, Mandara greetd, or keeping existing DM untouched.

### `A-08` — Hyprland Solo Mode, Cursor Tilt & Shake-to-Find Pointer
- **Classification:** **Class A (Lucid-only)**
- **Category:** Compositor Extensions | **Source Project:** Lucid
- **Source Files:** `support/hypr/modules/solo.lua`, `support/hypr/modules/pointer.lua`, `HyprConfig.qml`
- **User-Facing Behavior:** Smart single-window borderless/gapless mode (`lucid.solo`), velocity-based cursor tilt, and shake-mouse-to-enlarge/highlight cursor (`lucid.find_pointer`).
- **Settings Keys:** `lucid.solo`, `lucid.cursor_tilt`, `lucid.cursor_tilt_apps`, `lucid.find_pointer`
- **Keybindings:** None / GUI-triggered
- **IPC / D-Bus / Sockets:** `Hyprland Lua event listeners`
- **Wayland / Hyprland Hooks:** `Hyprland 0.55+ Lua runtime hooks`
- **Visual Presentation:** Overlay locator ring + seamless window framing
- **Dependencies:** hyprland >= 0.55
- **Conflicts & Risks:** Must live inside Scy-Shell's modular Lua generator so Mandara compositor edits never clobber it.
- **Scy-Shell Target Design:** Preserve 100% intact in Scy-Shell Hyprland Lua module set and expose toggles in Scy-Shell Studio -> Hyprland.

### `A-09` — Bluetooth OBEX File Receiver Daemon & Toast Inbox
- **Classification:** **Class A (Lucid-only)**
- **Category:** Connectivity | **Source Project:** Lucid
- **Source Files:** `support/bt-receive.py`, `Bluetooth.qml`
- **User-Facing Behavior:** Receives incoming Bluetooth files via org.bluez.obex.Agent1 with interactive Accept/Decline toast and automatic Downloads placement.
- **Settings Keys:** `Prefs.btReceive`, `Prefs.btAutoAcceptTrusted`
- **Keybindings:** None / GUI-triggered
- **IPC / D-Bus / Sockets:** `org.bluez.obex.Agent1`
- **Wayland / Hyprland Hooks:** ``
- **Visual Presentation:** Interactive transfer progress toast
- **Dependencies:** bluez-obex, python3-dbus-next
- **Conflicts & Risks:** None.
- **Scy-Shell Target Design:** Preserve 100% intact and route transfer prompts to whichever Toast provider is active.

### `B-01` — Sandboxed WASM Plugin Host (wasm32-wasip2) & 88 Built-in Plugins
- **Classification:** **Class B (Mandara-only)**
- **Category:** Plugin Ecosystem | **Source Project:** Mandara
- **Source Files:** `crates/mandara-plugin-api/`, `crates/mandara-plugin-host/`, `crates/mandara-ui/src/plugins/`, `assets/catalog.json`
- **User-Facing Behavior:** 88 built-in bar/panel/desktop/launcher plugins (Docker, Systemd, Tailscale, WireGuard, SSH, Git watcher, Port killer, Stocks/Crypto, RSS, Prayer Times, 3D Game Shelf, Kanban, etc.) PLUS capability-sandboxed third-party WebAssembly plugins via Wasmtime.
- **Settings Keys:** `/plugins/enabled`, `/plugins/disabled`, `/plugins/approved_capabilities/*`, `/plugins/settings/*`
- **Keybindings:** Super+Shift+P (Plugin Drawer) + per-plugin chords
- **IPC / D-Bus / Sockets:** `mandara plugin install/list/enable/disable`
- **Wayland / Hyprland Hooks:** `Rendered in Mandara GPUI surfaces or bridged to Lucid bar via Scy-Shell Plugin Pill`
- **Visual Presentation:** GPUI native cards styled with Scy-Shell M3 Expressive Look tokens by default, or any of 19 Mandara Looks
- **Dependencies:** wasmtime (compiled in mandara binary)
- **Conflicts & Risks:** Plugin capability prompts must surface cleanly in Scy-Shell Studio.
- **Scy-Shell Target Design:** Preserve all 88 built-in plugins + WASM host! Expose a 'Scy-Shell Plugin Drawer' triggerable directly from Lucid's Bar even when Lucid Bar is active!

### `B-02` — Local AI Command Agent (FunctionGemma-270M / Qwen3-0.6B) & Whisper Voice Input
- **Classification:** **Class B (Mandara-only)**
- **Category:** AI & Natural Language | **Source Project:** Mandara
- **Source Files:** `crates/mandara-agent/`
- **User-Facing Behavior:** 100% offline on-device LLM agent (`candle`) that translates natural-language text or spoken voice commands into validated shell & compositor tool calls.
- **Settings Keys:** `/integrations/agent/*`
- **Keybindings:** Super+Shift+A
- **IPC / D-Bus / Sockets:** `scy-shell ipc agent ...`
- **Wayland / Hyprland Hooks:** `Dispatches actions through Scy-Shell Core to active providers & Hyprland`
- **Visual Presentation:** Floating M3-styled command pill / Launcher `!ai` mode
- **Dependencies:** Opt-in user model download (never bundled)
- **Conflicts & Risks:** Model weights licensing (Gemma Terms) -> strictly opt-in user download with consent modal.
- **Scy-Shell Target Design:** Preserve 100% intact and extend tool-call router to control BOTH Lucid and Mandara active providers!

### `B-03` — Wallgen Procedural GPU/CPU Wallpaper & Video Generator (13 Styles)
- **Classification:** **Class B (Mandara-only)**
- **Category:** Wallpaper & Generative Art | **Source Project:** Mandara
- **Source Files:** `crates/mandara-wallgen/`, `crates/mandara-config/src/wallgen.rs`
- **User-Facing Behavior:** Generates 4K/8K procedural still wallpapers and seamless loop MP4/WebM videos in 13 algorithmic styles seeded from the active palette, with scheduled regeneration.
- **Settings Keys:** `scy.providers.mandara.wallgen.* (21 keys)`
- **Keybindings:** Super+Shift+W
- **IPC / D-Bus / Sockets:** `scy-shell ipc wallgen ...`
- **Wayland / Hyprland Hooks:** `Outputs PNG/JPEG/MP4 directly consumable by BOTH Lucid (`awww`/`LiveShell`) and Mandara (`mandara-wallpaper`)!`
- **Visual Presentation:** Interactive Wallgen Studio previewer
- **Dependencies:** mandara-wallgen
- **Conflicts & Risks:** None when routed through Scy-Shell Wallpaper Coordinator.
- **Scy-Shell Target Design:** Preserve 100% intact and wire generated wallpapers/videos into Scy-Shell's active wallpaper renderer + Matugen palette regeneration!

### `B-04` — 19 Complete Architectural Looks & Surface Grain / Chromatic Glass
- **Classification:** **Class B (Mandara-only)**
- **Category:** Visual Identity & Presets | **Source Project:** Mandara
- **Source Files:** `crates/mandara-ui/src/looks/`, `crates/mandara-config/src/grain.rs`
- **User-Facing Behavior:** 19 holistic aesthetic transformations (`corniche-dusk`, `pharos-ink`, `phosphor`, `cupertino`, `redmond`, `library-desk`, `ink-rush`, `sea-glass`, etc.) plus procedural film/paper `SurfaceGrain` and refractive `ChromaticGlass`.
- **Settings Keys:** `/appearance/look`, `/grain/*`, `/style/*`
- **Keybindings:** Super+Alt+T (Look/Theme quick switcher)
- **IPC / D-Bus / Sockets:** `scy-shell ipc look set <id>`
- **Wayland / Hyprland Hooks:** `Syncs border/rounding/shadow hints`
- **Visual Presentation:** 19 distinct visual languages on Mandara GPUI surfaces
- **Dependencies:** mandara-ui
- **Conflicts & Risks:** Must default to Scy-Shell's primary Material 3 Expressive look while keeping all 19 Mandara Looks selectable.
- **Scy-Shell Target Design:** Add 20th Look (`scy-m3-expressive`, default) to Mandara so GPUI surfaces match Lucid 2 out of the box, while preserving all 19 original Looks in Studio!

### `B-05` — Multi-Compositor Backend Abstraction (11 Wayland Compositors)
- **Classification:** **Class B (Mandara-only)**
- **Category:** Compositor Support | **Source Project:** Mandara
- **Source Files:** `crates/mandara-compositor/src/`
- **User-Facing Behavior:** Native workspace, window, monitor, and config adapters for Hyprland, Niri, Sway, Scroll, MangoWC, Miracle WM, River, Labwc, COSMIC, KDE KWin, and generic wlr-foreign-toplevel.
- **Settings Keys:** `/compositor/*`
- **Keybindings:** Auto-translated per compositor syntax
- **IPC / D-Bus / Sockets:** `Per-compositor IPC sockets`
- **Wayland / Hyprland Hooks:** `wlr-foreign-toplevel-management, ext-workspace`
- **Visual Presentation:** Transparent backend service
- **Dependencies:** mandara-compositor
- **Conflicts & Risks:** Lucid's HyprConfig.qml assumes Hyprland; Scy-Shell Core exposes normalized workspace/window state on non-Hyprland compositors too.
- **Scy-Shell Target Design:** Hyprland is primary target; all other 10 compositor backends remain preserved in Scy-Shell Core!

### `B-06` — Screen Time & Per-App Focus Analytics
- **Classification:** **Class B (Mandara-only)**
- **Category:** Productivity & Analytics | **Source Project:** Mandara
- **Source Files:** `crates/mandara-services/src/screen_time.rs`
- **User-Facing Behavior:** Tracks active window focus duration per app/category locally, with daily/weekly charts, app usage limits, and break nudges.
- **Settings Keys:** `/screen_time/*`
- **Keybindings:** None / GUI-triggered
- **IPC / D-Bus / Sockets:** `mandara-services background tracker`
- **Wayland / Hyprland Hooks:** `Active window event stream`
- **Visual Presentation:** Studio Screen Time charts + Desktop/Sidebar widget
- **Dependencies:** mandara-services
- **Conflicts & Risks:** Zero exclusive conflict (read-only focus listener).
- **Scy-Shell Target Design:** Enable cleanly in Scy-Shell background services (opt-out toggle preserved) and surface analytics in Scy-Shell Studio.

### `B-07` — CalDAV / Google / Microsoft OAuth2 Cloud Calendar & Mail Sync
- **Classification:** **Class B (Mandara-only)**
- **Category:** Cloud & Productivity | **Source Project:** Mandara
- **Source Files:** `crates/mandara-services/src/calendar_sync.rs`, `crates/mandara-services/src/mail.rs`
- **User-Facing Behavior:** Cloud sync with CalDAV, Google Calendar, Outlook, and IMAP/OAuth unread mail badges stored in SecretService keyring.
- **Settings Keys:** `/calendar/*`, `/integrations/mail/*`
- **Keybindings:** None / GUI-triggered
- **IPC / D-Bus / Sockets:** `org.freedesktop.secrets`
- **Wayland / Hyprland Hooks:** ``
- **Visual Presentation:** Calendar events feed into BOTH Mandara Calendar and Lucid Calendar/Lock Agenda via Scy-Shell Event Bus!
- **Dependencies:** gnome-keyring or kwallet
- **Conflicts & Risks:** None.
- **Scy-Shell Target Design:** Preserve 100% intact and bridge synced events into Lucid's `lucidcalendar` & `LockAgenda.qml`!

### `B-08` — 3D Steam / Lutris / Heroic Game Shelf
- **Classification:** **Class B (Mandara-only)**
- **Category:** Gaming | **Source Project:** Mandara
- **Source Files:** `crates/mandara-ui/src/plugins/games/`
- **User-Facing Behavior:** Scans local Steam VDF, Lutris SQLite, and Heroic libraries to render an interactive cover-art game launcher shelf with playtime badges and GameMode auto-engage.
- **Settings Keys:** `/plugins/settings/games/*`
- **Keybindings:** Super+Shift+G
- **IPC / D-Bus / Sockets:** `scy-shell ipc plugin toggle games`
- **Wayland / Hyprland Hooks:** `Triggers Gamemode optimizations on launch`
- **Visual Presentation:** GPUI hardware-accelerated cover shelf
- **Dependencies:** mandara-ui
- **Conflicts & Risks:** None.
- **Scy-Shell Target Design:** Preserve 100% intact and link launch events to Lucid/Scy-Shell GameMode state.

### `B-09` — greetd Native Wayland Login Greeter (`mandara-greeter`)
- **Classification:** **Class B (Mandara-only — paired with A-07 SDDM)**
- **Category:** Display Manager / Pre-Auth | **Source Project:** Mandara
- **Source Files:** `crates/mandara-greeter/`
- **User-Facing Behavior:** Standalone Wayland login greeter for greetd supporting all 6 AuthDesigns, video/shader/orb backgrounds, spring physics, and accessibility options.
- **Settings Keys:** `scy.providers.mandara.greeter.* (115 keys in /etc/mandara/greeter.toml)`
- **Keybindings:** None / GUI-triggered
- **IPC / D-Bus / Sockets:** `GREETD_SOCK`
- **Wayland / Hyprland Hooks:** `Runs inside compositor session launched by greetd`
- **Visual Presentation:** 6 AuthDesigns (including MaterialYou)
- **Dependencies:** greetd
- **Conflicts & Risks:** Systemd display-manager.service mutual exclusion with SDDM (A-07).
- **Scy-Shell Target Design:** Preserve 100% intact alongside Lucid SDDM; user chooses SDDM, greetd, or Neither in installer & Studio.

### `B-10` — Edge Drawers, Side Bars, Hot Corners & Screen Bezel Corners
- **Classification:** **Class B (Mandara-only)**
- **Category:** Shell Surfaces | **Source Project:** Mandara
- **Source Files:** `crates/mandara-ui/src/sidebar/`, `crates/mandara-config/src/edges.rs`, `crates/mandara-ui/src/corners.rs`
- **User-Facing Behavior:** Slide-out screen-edge drawers, persistent secondary sidebars, 4 configurable hot-corner dwell/click triggers, and rounded outer screen bezel masks.
- **Settings Keys:** `/sidebar/*`, `/side_bars/*`, `/edges/*`, `/hot_corners/*`, `/screen_corners/*`
- **Keybindings:** Edge hover / configurable chord
- **IPC / D-Bus / Sockets:** `scy-shell ipc sidebar toggle`
- **Wayland / Hyprland Hooks:** `wlr-layer-shell exclusive/overlay edges`
- **Visual Presentation:** M3 Expressive or selected Look edge sheets
- **Dependencies:** mandara-ui
- **Conflicts & Risks:** Edge hit-boxes must avoid active Bar/Dock edge.
- **Scy-Shell Target Design:** Preserve 100% intact; Scy-Shell Layer Coordinator auto-suppresses edge triggers along edges occupied by an active Bar or Dock.

### `B-11` — 24-App Tamper-Safe Theme Ledger & `Config doctor`
- **Classification:** **Class B/F (Unified into Scy-Shell Theme Coordinator)**
- **Category:** Theming & Diagnostics | **Source Project:** Mandara
- **Source Files:** `crates/mandara-config/src/templates/`, `crates/mandara-config/src/doctor.rs`
- **User-Facing Behavior:** Generates theme configs for 24 external apps with SHA-256 ledger tracking so user edits are NEVER overwritten without consent, plus `doctor` health checks.
- **Settings Keys:** `/apps/*`
- **Keybindings:** None / GUI-triggered
- **IPC / D-Bus / Sockets:** `scy-shell doctor`
- **Wayland / Hyprland Hooks:** ``
- **Visual Presentation:** Studio App-Theming matrix & Doctor report
- **Dependencies:** mandara-config
- **Conflicts & Risks:** Overlaps on 11 target files with Lucid's `render-templates.sh`.
- **Scy-Shell Target Design:** Merge Lucid's Matugen templates + Mandara's 24-app SHA-256 ledger into ONE Scy-Shell App-Theme Coordinator (28 total app targets with SHA-256 tamper protection).

### `D-01` — Top / Side / Bottom Status Bar
- **Classification:** **Class D (Both — Selectable Provider & Presentation)**
- **Category:** Core Shell Surfaces | **Source Project:** Both (Materially Different)
- **Source Files:** `Lucid: lucidbar/*.qml`, `Mandara: crates/mandara-ui/src/bar/, bar_styles.rs`
- **User-Facing Behavior:** Lucid offers M3 Expressive islands/pills/vertical bars with Jelly physics & 22 modules; Mandara offers 9 architectural BarStyles, 19 slot presets, CPU low-VRAM `shm_canvas` mode, and 88 bar plugins.
- **Settings Keys:** `Lucid: Prefs.bar* + show* (58 keys)`, `Mandara: /bar/* (74 keys)`
- **Keybindings:** Super+Shift+B (toggle bar visibility)
- **IPC / D-Bus / Sockets:** `scy-shell ipc bar toggle`
- **Wayland / Hyprland Hooks:** `wlr-layer-shell LAYER_TOP + exclusive zone`
- **Visual Presentation:** Selectable: Lucid M3 Expressive Bar (Default) OR Mandara Bar (with M3-Expressive Look or any of 9 BarStyles/19 Looks) OR Hybrid Per-Monitor!
- **Dependencies:** quickshell / mandara-ui
- **Conflicts & Risks:** Double exclusive-zone reservation if both run on same monitor edge.
- **Scy-Shell Target Design:** Default Provider: Lucid Bar. User can switch globally or per-monitor to Mandara Bar, OR embed a 'Mandara Plugins Pill' inside Lucid Bar!

### `D-02` — Application Dock
- **Classification:** **Class D (Both — Selectable Provider, Shared Pinned Apps)**
- **Category:** Core Shell Surfaces | **Source Project:** Both (Materially Different)
- **Source Files:** `Lucid: luciddock/*.qml`, `Mandara: crates/mandara-ui/src/dock/`
- **User-Facing Behavior:** Pinned & running apps dock with auto-hide/dodge, live window hover previews (Lucid ScreencopyView), Trash, and bounce/Jelly magnification.
- **Settings Keys:** `Lucid: Prefs.dock* (21 keys)`, `Mandara: /dock/* (24 keys)`
- **Keybindings:** IPC dock toggle
- **IPC / D-Bus / Sockets:** `Shared pinned-apps adapter (`~/.config/scy-shell/pinned-apps.json`)`
- **Wayland / Hyprland Hooks:** `wlr-layer-shell LAYER_TOP/OVERLAY`
- **Visual Presentation:** Lucid M3 Expressive Glass Dock (Default) or Mandara GPUI Dock
- **Dependencies:** quickshell / mandara-ui
- **Conflicts & Risks:** Simultaneous bottom-edge collision.
- **Scy-Shell Target Design:** Default Provider: Lucid Dock. Pinned apps list is two-way synced.

### `D-03` — Application Launcher & Command Palette
- **Classification:** **Class D (Both — Selectable Provider + Query Federation Bridge)**
- **Category:** Core Shell Surfaces | **Source Project:** Both (Materially Different)
- **Source Files:** `Lucid: lucidlaunch/*.qml`, `Mandara: crates/mandara-ui/src/launcher/`
- **User-Facing Behavior:** Lucid provides M3 Expressive morphing launcher (apps, calc, cliphist, emoji, wallpapers, windows, files, shell); Mandara adds WASM plugin providers, SSH/Docker/Dev-ports, and Local AI agent.
- **Settings Keys:** `Lucid: Prefs.launcher* (19 keys)`, `Mandara: /launcher/* (38 keys)`
- **Keybindings:** Super+Space
- **IPC / D-Bus / Sockets:** `scy-shell ipc launcher toggle [mode]`
- **Wayland / Hyprland Hooks:** `wlr-layer-shell LAYER_OVERLAY keyboard-interactive`
- **Visual Presentation:** Lucid M3 Expressive Launcher (Default) + Query Federation to Mandara AI & 88 Plugins, OR full Mandara GPUI Launcher
- **Dependencies:** quickshell / mandara-ui
- **Conflicts & Risks:** Exclusive keyboard grab if both open simultaneously.
- **Scy-Shell Target Design:** Default Provider: Lucid Launcher with live JSON-RPC query federation to `mandara-agent` and `mandara-plugin-host`; full Mandara Launcher also selectable.

### `D-04` — Quick Settings / Control Centre
- **Classification:** **Class D (Both — Selectable Provider, Shared State Bus)**
- **Category:** Core Shell Surfaces | **Source Project:** Both (Materially Different)
- **Source Files:** `Lucid: lucidquick/*.qml`, `Mandara: crates/mandara-ui/src/control_center/`
- **User-Facing Behavior:** Expandable Wi-Fi, BT, Audio per-app mixer, Night Light, Power profile, Caffeine, GameMode, VPN/Tailscale/Docker tiles, and media card.
- **Settings Keys:** `Lucid: Prefs.system* (16 keys)`, `Mandara: /panels/* (29 keys)`
- **Keybindings:** Super+S / Bar click
- **IPC / D-Bus / Sockets:** `scy-shell ipc quick toggle`
- **Wayland / Hyprland Hooks:** `wlr-layer-shell LAYER_OVERLAY`
- **Visual Presentation:** Lucid M3 Expressive Control Sheet (Default) or Mandara Control Center
- **Dependencies:** PipeWire, NetworkManager, BlueZ, UPower
- **Conflicts & Risks:** State divergence if DND / Night Light / Caffeine not synced.
- **Scy-Shell Target Design:** Default Provider: Lucid Control Centre; DND, Night Light, Caffeine, and GameMode states synchronized over Scy-Shell Core.

### `D-05` — Notifications Daemon, Toasts & Notification Centre
- **Classification:** **Class D + Class F (Exclusive D-Bus Resource + Separable Toast Renderer)**
- **Category:** Notifications & Exclusive D-Bus | **Source Project:** Both (Exclusive D-Bus Bus Name)
- **Source Files:** `Lucid: Notifs.qml, lucidtoast/*.qml`, `Mandara: crates/mandara-services/src/notifications.rs, crates/mandara-ui/src/toast/`
- **User-Facing Behavior:** Desktop notification server (`org.freedesktop.Notifications`) with grouping, inline actions, urgency rules, DND/Quiet Hours, persistent history, and floating toasts.
- **Settings Keys:** `Lucid: Prefs.notif* + toast* + dnd* (26 keys)`, `Mandara: /notifications/* (34 keys)`
- **Keybindings:** Super+N (history), Super+Shift+N (DND)
- **IPC / D-Bus / Sockets:** `org.freedesktop.Notifications (EXCLUSIVE!)`
- **Wayland / Hyprland Hooks:** `wlr-layer-shell LAYER_OVERLAY`
- **Visual Presentation:** Separable Functional Provider & Toast Presentation Renderer!
- **Dependencies:** D-Bus session bus
- **Conflicts & Risks:** CRITICAL: Mandara's `hub.rs` claims `org.freedesktop.Notifications` unconditionally at boot. Must gate in `mandara-working`.
- **Scy-Shell Target Design:** Default Provider & Renderer: Lucid (`Notifs.qml` + `lucidtoast`). Gate `spawn_notification_service()` in `mandara-working`; allow cross-routing Toast rendering over Scy-Shell Event Bus.

### `C-01` — On-Screen Display (OSD: Volume, Brightness, Mic, Caps/Layout)
- **Classification:** **Class C (Equivalent -> Lucid Default, Mandara Selectable)**
- **Category:** Shell Feedback | **Source Project:** Both (Equivalent Role)
- **Source Files:** `Lucid: lucidosd/*.qml`, `Mandara: crates/mandara-ui/src/osd/`
- **User-Facing Behavior:** Transient pill HUD for audio volume/mute, backlight brightness, keyboard backlight, mic mute, and Caps/Num lock.
- **Settings Keys:** `Lucid: Prefs.osd* (9 keys)`, `Mandara: /osd/* (16 keys)`
- **Keybindings:** XF86Audio*, XF86MonBrightness*, Caps_Lock
- **IPC / D-Bus / Sockets:** `scy-shell ipc osd ...`
- **Wayland / Hyprland Hooks:** `wlr-layer-shell LAYER_OVERLAY (click-through)`
- **Visual Presentation:** Lucid M3 Expressive Jelly OSD (Default) or Mandara OSD
- **Dependencies:** PipeWire, brightnessctl / sysfs
- **Conflicts & Risks:** Double OSD popups on XF86 keys if both listen un-gated.
- **Scy-Shell Target Design:** Single active OSD renderer gated by `scy.active_providers.osd` (default: `lucid`).

### `D-06` — Desktop Widgets Canvas
- **Classification:** **Class D (Both — Selectable OR Hybrid Coexistence!)**
- **Category:** Desktop Surface | **Source Project:** Both (Materially Different)
- **Source Files:** `Lucid: Widgets.qml, lucidwidgets/*.qml`, `Mandara: crates/mandara-ui/src/desktop/, widget_kinds.rs`
- **User-Facing Behavior:** Lucid offers 25 M3 Expressive widgets (88 variants: cookie photo frames, morphing clocks, Sound Weaver, habits, lyrics); Mandara offers GPUI + WASM widgets.
- **Settings Keys:** `Lucid: ~/.config/quickshell/widgets.json + 58 opts`, `Mandara: /desktop/* + widget instances`
- **Keybindings:** Edit-mode toggle
- **IPC / D-Bus / Sockets:** `scy-shell ipc widgets edit`
- **Wayland / Hyprland Hooks:** `wlr-layer-shell LAYER_BOTTOM`
- **Visual Presentation:** Lucid M3 Widgets (Default), Mandara Widgets, OR Coexisting Non-Overlapping Hybrid Mode!
- **Dependencies:** quickshell / mandara-ui
- **Conflicts & Risks:** Input region masking on `LAYER_BOTTOM`.
- **Scy-Shell Target Design:** Support `lucid` (default), `mandara`, AND `hybrid` mode using Wayland `wl_surface.set_input_region` bounding-box masks!

### `D-07` — Wallpaper Engine (Static, Transitions, Video, Shaders & Wallgen)
- **Classification:** **Class D + Class F (Exclusive Layer Surface + Shared Wallgen & Matugen Pipeline)**
- **Category:** Desktop Surface | **Source Project:** Both (Materially Different)
- **Source Files:** `Lucid: Wallpapers.qml, LiveShell.qml, lucidwall/`, `Mandara: crates/mandara-ui/src/wallpaper/, mandara-wallgen/`
- **User-Facing Behavior:** Lucid uses `awww` (10 transitions) + `LiveShell.qml` (MP4/WebM video & GLSL shaders); Mandara offers CPU-efficient `shm_canvas` / wgpu renderer + 13-style procedural `Wallgen`.
- **Settings Keys:** `Lucid: Prefs.wallpaper* + wallTrans* + live* (28 keys)`, `Mandara: /wallpaper/* + wallgen.* (49 keys)`
- **Keybindings:** Super+W (Picker), Super+Shift+W (Wallgen)
- **IPC / D-Bus / Sockets:** `scy-shell ipc wallpaper set <path>`
- **Wayland / Hyprland Hooks:** `wlr-layer-shell LAYER_BACKGROUND (EXCLUSIVE per output)`
- **Visual Presentation:** Lucid `awww`+`LiveShell` (Default) or Mandara `mandara-wallpaper`; `Wallgen` feeds BOTH!
- **Dependencies:** awww, gst-libav / mandara-wallgen
- **Conflicts & Risks:** Two `LAYER_BACKGROUND` surfaces waste ~40–120 MB VRAM/RAM.
- **Scy-Shell Target Design:** Only ONE `LAYER_BACKGROUND` renderer runs (`lucid` default, `mandara` selectable). Setting or generating a wallpaper triggers Scy-Shell's single Matugen/OKLCH palette pipeline for BOTH engines.

### `D-08` — Wayland Session Lock (`ext-session-lock-v1`)
- **Classification:** **Class D + Class F (Exclusive Security Surface)**
- **Category:** Security & Auth | **Source Project:** Both (Exclusive Wayland Protocol)
- **Source Files:** `Lucid: lucidlock/*.qml`, `Mandara: crates/mandara-services/src/session_lock.rs, crates/mandara-ui/src/lock/`
- **User-Facing Behavior:** Lucid offers 6 slot-customizable presets + 10 widgets + OSK; Mandara offers 6 `AuthDesign`s + freeform canvas placement.
- **Settings Keys:** `Lucid: Prefs.lock* + Catalog.js (63 keys)`, `Mandara: /lock/* (44 keys)`
- **Keybindings:** Super+L
- **IPC / D-Bus / Sockets:** `scy-shell ipc lock`
- **Wayland / Hyprland Hooks:** `ext_session_lock_manager_v1 (STRICTLY ONE CLIENT)`
- **Visual Presentation:** All 6 Lucid Lock Presets (Default) + All 6 Mandara AuthDesigns selectable in Studio!
- **Dependencies:** PAM, fprintd (optional)
- **Conflicts & Risks:** CRITICAL: Wayland `ext-session-lock-v1` rejects a second lock client with protocol error.
- **Scy-Shell Target Design:** Default Provider: Lucid Lock (`lucidlock`). User can switch to Mandara Lock (`mandara-lock`) in Studio; inactive lock engine has its lock handler strictly disabled.

### `D-09` — Screenshot, OCR, Annotation & Screen Recording
- **Classification:** **Class D (Lucid Default — Richer Annotation & Recording Suite)**
- **Category:** Capture | **Source Project:** Both (Materially Different)
- **Source Files:** `Lucid: lucidshot/*.qml`, `Mandara: crates/mandara-ui/src/capture/, vendor/uni-ocr-0.2.0`
- **User-Facing Behavior:** Lucid has interactive crop, vector annotations, Tesseract OCR, QR decode, color picker, and MP4/GIF screen recorder; Mandara has GPUI region capture + `uni-ocr`.
- **Settings Keys:** `Lucid: Prefs.shot* + record* + ShotOverlay (27 keys)`, `Mandara: capture keys`
- **Keybindings:** Print, Super+Shift+S, Super+Shift+R
- **IPC / D-Bus / Sockets:** `scy-shell ipc shot [region|window|screen|ocr]`
- **Wayland / Hyprland Hooks:** `wlr-screencopy / grim / gpu-screen-recorder`
- **Visual Presentation:** Lucid `LucidShot` Annotation Studio (Default) or Mandara Capture
- **Dependencies:** grim, tesseract, zbar, gpu-screen-recorder / wf-recorder
- **Conflicts & Risks:** Chord collision on `Print` and `Super+Shift+S`.
- **Scy-Shell Target Design:** Default Provider: `LucidShot`, with Mandara Capture selectable.

### `D-10` — Workspace Overview, Exposé & Window Switcher (Alt-Tab)
- **Classification:** **Class D (Both — Selectable per surface)**
- **Category:** Window Management UI | **Source Project:** Both (Materially Different)
- **Source Files:** `Lucid: lucidoverview/*.qml, lucidexpose/*.qml`, `Mandara: crates/mandara-ui/src/switcher/`
- **User-Facing Behavior:** Lucid provides live `ScreencopyView` workspace grid drag-and-drop + live Exposé; Mandara provides fast cross-compositor keyboard switcher.
- **Settings Keys:** `Lucid: Prefs.overview*`, `Mandara: /switcher/* (18 keys)`
- **Keybindings:** Super+Tab (Overview), Alt+Tab (Switcher)
- **IPC / D-Bus / Sockets:** `scy-shell ipc overview / switcher`
- **Wayland / Hyprland Hooks:** `Hyprland IPC / wlr-foreign-toplevel / Screencopy`
- **Visual Presentation:** Lucid Live Thumbnail Overview/Exposé (Default on Hyprland) + Mandara Switcher (Selectable)
- **Dependencies:** quickshell / mandara-ui
- **Conflicts & Risks:** Alt+Tab / Super+Tab bind ownership.
- **Scy-Shell Target Design:** Default on Hyprland: Lucid Overview & Expose; user can independently pick Lucid or Mandara for `Alt+Tab`.

### `C-02` — Clipboard History Manager
- **Classification:** **Class C + Class F (Single Active Watcher Daemon)**
- **Category:** Utilities & Exclusive Wayland Data-Control | **Source Project:** Both
- **Source Files:** `Lucid: lucidlaunch/Clipboard, wl-paste --watch cliphist`, `Mandara: crates/mandara-services/src/clipboard.rs`
- **User-Facing Behavior:** Persistent text & image clipboard history, pin favorites, wipe, and sensitive password-manager exclusion.
- **Settings Keys:** `Lucid: Prefs.clipboard*`, `Mandara: /clipboard/* (15 keys)`
- **Keybindings:** Super+V
- **IPC / D-Bus / Sockets:** `cliphist DB vs Mandara clipboard store`
- **Wayland / Hyprland Hooks:** `ext-data-control-v1 / zwlr_data_control_manager_v1`
- **Visual Presentation:** Lucid Launcher Clipboard mode (Default) or Mandara Clipboard popup
- **Dependencies:** wl-clipboard, cliphist
- **Conflicts & Risks:** Running BOTH watchers duplicates image storage in RAM/disk.
- **Scy-Shell Target Design:** Only ONE clipboard watcher runs (`cliphist` when Lucid clipboard is active; `mandara-services::clipboard` when Mandara is active).

### `F-01` — Polkit Authentication Agent (`unix-session`)
- **Classification:** **Class F (Exclusive Session Resource)**
- **Category:** Exclusive Security Infrastructure | **Source Project:** Both
- **Source Files:** `Lucid: Polkit.qml`, `Mandara: crates/mandara-services/src/polkit.rs`
- **User-Facing Behavior:** Graphical privilege escalation modal for `pkexec` / systemd / package operations.
- **Settings Keys:** `Mandara: /general/polkit_agent`, `Scy-Shell: scy.active_providers.polkit`
- **Keybindings:** None / GUI-triggered
- **IPC / D-Bus / Sockets:** `org.freedesktop.PolicyKit1.Authority::RegisterAuthenticationAgent (EXCLUSIVE)`
- **Wayland / Hyprland Hooks:** `LAYER_OVERLAY modal`
- **Visual Presentation:** Lucid M3 Polkit Modal (Default) or Mandara Polkit Modal
- **Dependencies:** polkit
- **Conflicts & Risks:** CRITICAL: `polkitd` rejects the second agent registration.
- **Scy-Shell Target Design:** Default: Lucid `Polkit.qml`; Scy-Shell sets Mandara `/general/polkit_agent = false` automatically unless user selects Mandara Polkit.

### `F-02` — Night Light / Display Gamma Control (`zwlr_gamma_control_v1`)
- **Classification:** **Class F (Exclusive Wayland Output Resource)**
- **Category:** Exclusive Display Protocol | **Source Project:** Both
- **Source Files:** `Lucid: NightLight (`hyprsunset`)`, `Mandara: crates/mandara-services/src/gamma.rs`
- **User-Facing Behavior:** Color temperature warmth (K) + sunrise/sunset schedule.
- **Settings Keys:** `Lucid: Prefs.nightLight* (6 keys)`, `Mandara: /night_light/* (11 keys)`
- **Keybindings:** IPC toggle nightlight
- **IPC / D-Bus / Sockets:** `scy-shell ipc nightlight ...`
- **Wayland / Hyprland Hooks:** `zwlr_gamma_control_manager_v1 (EXCLUSIVE PER wl_output)`
- **Visual Presentation:** Controlled from either Quick Settings / Studio
- **Dependencies:** hyprsunset OR Mandara native `gamma.rs`
- **Conflicts & Risks:** CRITICAL: `zwlr_gamma_control_v1` rejects a second gamma client on the same monitor.
- **Scy-Shell Target Design:** Single active gamma backend (`hyprsunset` default on Hyprland with automatic fallback to `mandara-gamma` if `hyprsunset` absent).

### `F-03` — System Tray (`org.kde.StatusNotifierWatcher` & `Host`)
- **Classification:** **Class F (Shared Bus — Verified Peaceful Coexistence)**
- **Category:** Shared D-Bus Infrastructure | **Source Project:** Both
- **Source Files:** `Lucid: Quickshell.Services.SystemTray`, `Mandara: crates/mandara-services/src/tray.rs`
- **User-Facing Behavior:** SNI tray icons + DBusMenu context menus.
- **Settings Keys:** `Lucid: Prefs.tray*`, `Mandara: /bar/tray*`
- **Keybindings:** None / GUI-triggered
- **IPC / D-Bus / Sockets:** `org.kde.StatusNotifierWatcher + org.kde.StatusNotifierHost-*`
- **Wayland / Hyprland Hooks:** ``
- **Visual Presentation:** Rendered in active Bar
- **Dependencies:** D-Bus
- **Conflicts & Risks:** Verified in source: Mandara `tray.rs` gracefully falls back to `StatusNotifierHost` when `StatusNotifierWatcher` is already owned by Quickshell!
- **Scy-Shell Target Design:** Start Lucid/Quickshell Watcher first; both engines can display tray items cleanly.

### `F-04` — Bluetooth Pairing Agent (`org.bluez.Agent1`)
- **Classification:** **Class F (Exclusive BlueZ DefaultAgent)**
- **Category:** Exclusive Connectivity Agent | **Source Project:** Both
- **Source Files:** `Lucid: support/bt-agent.py`, `Mandara: crates/mandara-services/src/bt_agent.rs`
- **User-Facing Behavior:** Handles Bluetooth PIN, Passkey confirmation, and authorization prompts.
- **Settings Keys:** `Mandara: /bluetooth/pairing_agent`, `Scy-Shell: scy.active_providers.bt_agent`
- **Keybindings:** None / GUI-triggered
- **IPC / D-Bus / Sockets:** `org.bluez.AgentManager1::RegisterAgent (DefaultAgent)`
- **Wayland / Hyprland Hooks:** ``
- **Visual Presentation:** Pairing prompt modal/toast
- **Dependencies:** bluez
- **Conflicts & Risks:** Only one DefaultAgent receives BlueZ pairing requests.
- **Scy-Shell Target Design:** Gate `bt-agent.py` vs `bt_agent.rs` via `scy.active_providers.bt_agent` (default: `lucid`).

### `F-05` — Idle Management & DPMS (`ext-idle-notify-v1` / `hypridle`)
- **Classification:** **Class F (Exclusive Timer Orchestrator)**
- **Category:** Power & Session Lifecycle | **Source Project:** Both
- **Source Files:** `Lucid: Idle.qml + hypridle`, `Mandara: crates/mandara-services/src/idle.rs`
- **User-Facing Behavior:** Screen dim, automatic session lock, DPMS monitor power-off, and suspend timeouts + Caffeine inhibitor.
- **Settings Keys:** `Lucid: Prefs.idle* (9 keys)`, `Mandara: /idle/* (12 keys)`
- **Keybindings:** IPC caffeine toggle
- **IPC / D-Bus / Sockets:** `org.freedesktop.ScreenSaver / systemd-inhibit`
- **Wayland / Hyprland Hooks:** `ext_idle_notifier_v1, zwlr_output_power_management_v1`
- **Visual Presentation:** Bar Caffeine pill
- **Dependencies:** Wayland compositor
- **Conflicts & Risks:** Dual idle daemons firing competing lock/DPMS timers.
- **Scy-Shell Target Design:** Single active Idle Coordinator invoking the active Lock provider.

### `F-06` — Hyprland Configuration, Rules, Monitors & Keybind Generation
- **Classification:** **Class F + Class E (Unified Scy-Shell Hyprland Coordinator)**
- **Category:** Compositor Configuration | **Source Project:** Both
- **Source Files:** `Lucid: HyprConfig.qml + support/hypr/modules/*.lua`, `Mandara: crates/mandara-compositor/src/hyprland.rs, keybinds.rs`
- **User-Facing Behavior:** Live GUI editing of gaps, borders, blur, animations, input, monitors, window rules, layer rules, and keybindings.
- **Settings Keys:** `Lucid: 72 HyprConfig keys + 61 keybinds`, `Mandara: /compositor/* + /displays/*`
- **Keybindings:** All shell & WM keybinds
- **IPC / D-Bus / Sockets:** `Hyprland .socket.sock & .socket2.sock`
- **Wayland / Hyprland Hooks:** `~/.config/hypr/scy-shell/ modular includes`
- **Visual Presentation:** Unified Scy-Shell Studio -> Hyprland & Displays & Keybinds
- **Dependencies:** hyprland (0.55+ Lua or .conf fallback)
- **Conflicts & Risks:** CRITICAL: Direct dual writes would clobber each other.
- **Scy-Shell Target Design:** ONE authoritative Scy-Shell Hyprland Coordinator (`scy-hypr`) with timestamped backups, version-validated directives, and instant rollback.

### `E-01` — Scy-Shell Unified Core Daemon, State Bus & Provider Arbitrator (`scy-daemon`)
- **Classification:** **Class E (Scy-Shell Native Required)**
- **Category:** Scy-Shell Native Core | **Source Project:** Neither (Scy-Shell Native)
- **Source Files:** `scy-shell/crates/scy-daemon/, scy-ipc/, scy-schema/`
- **User-Facing Behavior:** Single source of truth for active providers, active presentations, pre-activation conflict detection, cross-engine event synchronization, lazy/dormant process lifecycle, and atomic config transactions.
- **Settings Keys:** `scy.active_providers.*, scy.presentations.*, scy.profiles.*`
- **Keybindings:** None / GUI-triggered
- **IPC / D-Bus / Sockets:** `$XDG_RUNTIME_DIR/scy-shell.sock + org.scyshell.Daemon`
- **Wayland / Hyprland Hooks:** ``
- **Visual Presentation:** Headless high-efficiency Rust coordinator (<8 MB RSS target)
- **Dependencies:** Rust std + Unix domain sockets
- **Conflicts & Risks:** Eliminates all 11 exclusive-resource conflicts by design.
- **Scy-Shell Target Design:** Built in Rust inside `scy-shell/crates/scy-daemon`, bridged to Lucid via `ScyBridge.qml` and to Mandara via `scy_adapter.rs`.

### `E-02` — Unified Scy-Shell Studio (Material 3 Expressive Central Settings & Conflict UI)
- **Classification:** **Class E (Scy-Shell Native Required)**
- **Category:** Scy-Shell Native Studio | **Source Project:** Neither (Scy-Shell Native)
- **Source Files:** `scy-shell/studio/`
- **User-Facing Behavior:** One cohesive Material 3 Expressive Settings & Customization Studio exposing ALL 643 Lucid settings + ALL 1,232 Mandara settings (1,875 total), per-feature Provider & Presentation pickers, Inactive-Provider drawers, Live Conflict Inspector, Resource Monitor, and Comprehensive Hyprland Configurator.
- **Settings Keys:** `All 1,875 union settings`
- **Keybindings:** Super+Comma (`Super+,`) / Super+I
- **IPC / D-Bus / Sockets:** `scy-shell studio`
- **Wayland / Hyprland Hooks:** `Standard Wayland window`
- **Visual Presentation:** Material 3 Expressive (Google Sans, HCT dynamic palette, Jelly springs, expressive shapes)
- **Dependencies:** quickshell + scy-daemon
- **Conflicts & Risks:** Lazy-render sections so 1,875 settings open in <120ms.
- **Scy-Shell Target Design:** Built natively in QML on Lucid's M3 Expressive component kit with schema-driven rendering for all `04-settings-catalogue.json` entries.

### `E-03` — Pre-Activation External & Internal Conflict Detector (`scy-shell conflicts`)
- **Classification:** **Class E (Scy-Shell Native Required)**
- **Category:** Scy-Shell Native Safety | **Source Project:** Neither (Scy-Shell Native)
- **Source Files:** `scy-shell/crates/scy-conflicts/`
- **User-Facing Behavior:** Detects running external daemons (`mako`, `dunst`, `swaync`, `waybar`, `ags`, `hyprpaper`, `swww`, `lxqt-policykit`, `hypridle`, `swayidle`, duplicate `wl-paste`) AND internal Lucid/Mandara collisions BEFORE enabling a feature.
- **Settings Keys:** `scy.safety.conflict_policy`
- **Keybindings:** None / GUI-triggered
- **IPC / D-Bus / Sockets:** `D-Bus ListNames/GetNameOwner + /proc + Hyprland layers`
- **Wayland / Hyprland Hooks:** `hyprctl layers -j`
- **Visual Presentation:** Interactive Conflict Resolution Banner & Modal in Scy-Shell Studio
- **Dependencies:** scy-daemon
- **Conflicts & Risks:** Prevents silent D-Bus/Wayland crashes.
- **Scy-Shell Target Design:** Mandatory pre-flight check before every provider switch or session startup.
