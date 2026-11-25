# Stage 0 Deliverable 7 — Scy-Shell Architecture & Dual-Engine Integration Blueprint

## 1. Architectural Philosophy: Why Dual-Engine Supervision Beats a Rewrite

1. **Zero Feature Regression:** Rewriting `531,775` lines of Rust (`mandara-services`, `mandara-compositor`, `mandara-wallgen`, `mandara-plugin-host`, `mandara-agent`, 88 plugins) into QML — or rewriting Lucid's fluid `Jelly.qml` physics, `MaterialShape.qml` organic polygons, `Lumen` FileChooser portal, `Lens`, and `LucidShot` into GPUI — would destroy stability, introduce hundreds of regressions, and violate Section 4.
2. **True Native Strengths:** Quickshell/Qt6 excels at declarative **Material 3 Expressive** vector morphing, shader effects, and desktop apps; Rust/GPUI excels at zero-cost background services, 11-compositor socket abstractions, sandboxed Wasmtime execution, procedural `Wallgen`, CPU `shm_canvas`, and local `candle` LLM inference.
3. **Dormant-Zero-Surface Overhead:** When Mandara is running in **Headless/Dormant Adapter Mode** (providing AI, `Wallgen`, Cloud Calendar sync, Screen-Time, and on-demand Plugin drawers while Lucid renders Bar/Dock/Toast/Wallpaper), Mandara spawns **zero persistent `wgpu` swapchains** until a GPUI surface is actually toggled open!

---

## 2. High-Level System Topology

```text
+-----------------------------------------------------------------------------------+
|                        CENTRAL SCY-SHELL STUDIO (QML M3 Expressive)               |
|  - Exposes all 1,875 settings (643 Lucid + 1,232 Mandara) via Schema Registry     |
|  - Provider & Presentation Matrix + Inactive-Provider Drawer (0 settings lost)    |
|  - Pre-Flight Conflict Inspector + Live Resource Monitor + Hyprland Studio        |
+-----------------------------------------+-----------------------------------------+
                                          | JSON-RPC 2.0 / Event Stream
                                          v ($XDG_RUNTIME_DIR/scy-shell.sock)
+-----------------------------------------------------------------------------------+
|                         SCY-SHELL UNIFIED CORE (`scy-daemon`)                     |
|  +-------------------+ +--------------------+ +----------------+ +--------------+ |
|  | `scy-config`      | | `scy-arbitrator`   | | `scy-theme`    | | `scy-hypr`   | |
|  | ~/.config/        | | Exclusive D-Bus &  | | Unified HCT +  | | Safe Modular | |
|  | scy-shell/        | | Wayland Layer Gate | | OKLCH + 28-App | | Lua/.conf +  | |
|  | config.toml       | | + Ext. Conflict    | | SHA-256 Ledger | | Backup/Undo  | |
|  +-------------------+ +--------------------+ +----------------+ +--------------+ |
+--------------------+-----------------------------------------+--------------------+
                     |                                         |
     Adapter Bridge  | (`ScyBridge.qml`)                       | (`scy_adapter.rs`)
                     v                                         v
+----------------------------------------+ +----------------------------------------+
|   LUCID 2 ENGINE (`lucid-working`)     | |  MANDARA ENGINE (`mandara-working`)    |
|   Quickshell / Qt6 / M3 Expressive     | |  Rust / Forked GPUI / Wasmtime / AI    |
|                                        | |                                        |
| - Default: Bar, Dock, Launcher, Quick, | | - Active Always: 88 Plugins + WASM,    |
|   Notifs/Toasts, OSD, Lock, LucidShot, | |   Wallgen (13 styles), Local AI Agent, |
|   Overview, Wallpaper (awww/LiveShell),| |   CalDAV/Mail Sync, Screen Time,       |
|   Desktop Icons, 25 M3 Widgets         | |   11-Compositor Backend, Config Doctor |
| - Apps: Lumen (+FileChooser), Lens,    | | - Selectable Surfaces: 9 BarStyles,    |
|   Clock, LucidMoji, LucidKeys, SDDM    | |   19 Looks, Dock, Launcher, Sidebar,   |
|                                        | |   Edge Drawers, 6 Lock Designs, greetd |
+----------------------------------------+ +----------------------------------------+
```

---

## 3. Repository & Directory Structure (`scy-shell/`)

```text
scy-shell/
├── Cargo.toml                     # Workspace for Scy-Shell Rust core & CLI
├── crates/
│   ├── scy-schema/                # Typed schema for all 1,875 settings, providers & migrations
│   ├── scy-ipc/                   # Unix socket JSON-RPC protocol & CLI client (`scy-shell ipc ...`)
│   ├── scy-conflicts/             # Pre-activation D-Bus, /proc, Wayland layer & keybind scanner
│   ├── scy-hypr/                  # Version-aware Hyprland 0.55+/0.57+ Lua/.conf generator + backup/revert
│   ├── scy-theme/                 # Unified Matugen HCT + Mandara OKLCH + 28-app SHA-256 ledger coordinator
│   ├── scy-daemon/                # Central supervisor, state bus, notification/OSD/federation broker
│   └── scy-cli/                   # `scy-shell` unified binary (`start`, `studio`, `ipc`, `doctor`, `conflicts`, `backup`)
├── studio/                        # Unified Scy-Shell Studio (Material 3 Expressive QML application)
├── adapters/
│   ├── lucid/                     # `ScyBridge.qml` & minimal non-destructive hooks applied in `sources/lucid-working/`
│   └── mandara/                   # `scy_adapter.rs` & `scy-m3-expressive` Look applied in `sources/mandara-working/`
├── configs/                       # Default `config.toml`, keybind profiles, portal configs, systemd user units
├── installer/                     # Safe CachyOS/Arch installer (`install.sh`), PKGBUILD, dry-run & rollback scripts
├── tests/                         # Unit, schema-completeness (1,875-key assertion), conflict, Hyprland & headless integration tests
├── provenance/                    # Stage 0 cryptographic SHA-256 manifests & upstream provenance records
└── docs/                          # Stage 0 audit suite + Stage 1 user/architecture/troubleshooting docs
```

---

## 4. Minimal Adapter Patches in Working Trees (Zero Destructive Rewrites)

### 4.1 `sources/lucid-working/` (`scy-working` branch)
1. **`ScyBridge.qml` singleton:** Connects to `$XDG_RUNTIME_DIR/scy-shell.sock`, syncs `Prefs.qml` <-> `scy-daemon`, and exposes `Scy.providerActive(surface)` booleans.
2. **Surface & Exclusive-Resource Gates (`shell.qml`, `Notifs.qml`, `Polkit.qml`, `Idle.qml`):**
   - Wrap Bar, Dock, Launcher, Quick, Toast, OSD, Lock, Polkit, Wallpaper, and Widgets `Loader`s with `active: ScyBridge.isLucidActive("<surface>")` so switching any surface to Mandara cleanly unloads the QML surface and releases its D-Bus/Wayland claim!
3. **Federation Hooks:**
   - `lucidlaunch/`: Add `!ai` (queries `mandara-agent`) and `@` (queries Mandara's 88/WASM plugins) result sections.
   - `lucidbar/`: Add optional `ScyPluginPill.qml` chip to summon Mandara Plugin Drawers & Sidebars directly from Lucid's M3 Bar.
   - `lucidcalendar/` & `LockAgenda.qml`: Merge synced CalDAV/Google/Outlook events from `scy-daemon`.
4. **Hyprland Write Delegation (`HyprConfig.qml`):** Route writes through `scy-hypr` instead of overwriting `~/.config/hypr/lucid-settings.lua` unilaterally.

### 4.2 `sources/mandara-working/` (`scy-working` branch)
1. **Fix Unconditional Exclusive Claims (`crates/mandara-app/src/hub.rs`):**
   - Gate `spawn_notification_service()`, `polkit::spawn()`, `bt_agent::spawn()`, `gamma::spawn()`, `session_lock::spawn()`, `idle::spawn()`, and `clipboard::spawn()` behind `scy_adapter::owns_resource(...)` with dynamic runtime acquire/release!
2. **Surface Gating & Dormant Zero-Swapchain Mode (`crates/mandara-app/src/surfaces.rs`):**
   - Only materialize GPUI layer surfaces (`mandara-bar`, `mandara-dock`, `mandara-wallpaper`, etc.) whose provider is set to `"mandara"` (or `"hybrid"` for desktop widgets / per-monitor bars).
3. **20th Look — `scy-m3-expressive` (`crates/mandara-ui/src/looks/m3_expressive.rs`):**
   - Consumes exact HCT tokens from `scy-theme`, uses Google Sans + Material Symbols / Phosphor harmony, M3 Expressive pill/cookie radii, and spring curves matching `Jelly.qml` so any active Mandara surface looks 100% native alongside Lucid 2!
4. **Hyprland & App-Theme Delegation:** Route compositor and app-theme writes through `scy-hypr` and `scy-theme` SHA-256 ledger.

---

## 5. Unified Configuration Layout & Two-Way Lossless Sync

```toml
# ~/.config/scy-shell/config.toml
schema_version = 1

[identity]
primary_style = "m3-expressive"     # Or any of the 19 Mandara Looks
wallpaper = "/path/to/wall.png"
matugen_scheme = "scheme-tonal-spot"
dark_mode = true

[active_providers]
bar = "lucid"                       # "lucid" | "mandara" | { DP-1 = "lucid", HDMI-A-1 = "mandara" }
dock = "lucid"                      # "lucid" | "mandara" | "none"
launcher = "lucid"                  # "lucid" (with AI/Plugin federation) | "mandara"
quick_settings = "lucid"            # "lucid" | "mandara"
notifications = "lucid"             # "lucid" | "mandara" (EXCLUSIVE D-Bus owner)
osd = "lucid"                       # "lucid" | "mandara"
wallpaper = "lucid"                 # "lucid" (awww+LiveShell) | "mandara" (wgpu/shm_canvas)
desktop_widgets = "lucid"           # "lucid" | "mandara" | "hybrid"
desktop_icons = "lucid"             # "lucid" | "none"
lock_screen = "lucid"               # "lucid" | "mandara" (EXCLUSIVE ext-session-lock-v1)
polkit = "lucid"                    # "lucid" | "mandara" (EXCLUSIVE unix-session agent)
night_light = "lucid"               # "lucid" (hyprsunset) | "mandara" (zwlr-gamma-v1)
bt_agent = "lucid"                  # "lucid" | "mandara"
idle = "lucid"                      # "lucid" | "mandara"
clipboard = "lucid"                 # "lucid" (cliphist) | "mandara"
capture = "lucid"                   # "lucid" (LucidShot) | "mandara"
overview = "lucid"                  # "lucid" | "mandara"
switcher = "lucid"                  # "lucid" | "mandara"
display_manager = "preserve"        # "lucid-sddm" | "mandara-greetd" | "preserve"

[presentations]
toasts = "lucid"                    # Separable from notifications provider!
osd_style = "lucid-jelly"           # Separable from hardware listener!
mandara_surface_look = "scy-m3-expressive"

[providers.lucid]
# Lossless mirror of all 643 Lucid settings (never erased when inactive)

[providers.mandara]
# Lossless mirror of all 1,232 Mandara settings (never erased when inactive)
```

---

## 6. Safe, Non-Destructive Hyprland Coordinator (`scy-hypr`)

1. **Never Overwrites User Config:** Before touching `~/.config/hypr/`, `scy-hypr` creates a timestamped snapshot in `~/.local/share/scy-shell/backups/hypr-YYYYMMDD-HHMMSS/` with a SHA-256 manifest and one-command restore (`scy-shell backup restore <id>`).
2. **Modular Include Architecture:**
   - Supports **both** Hyprland `0.55+` Lua (`hyprland.lua` -> `require("scy-shell.init")` BEFORE `hypr-user.lua`) AND classic `hyprland.conf` (`source = ~/.config/hypr/scy-shell/scy-shell.conf`), auto-detected from the user's active Hyprland entrypoint!
   - Generated files live strictly inside `~/.config/hypr/scy-shell/` (`monitors`, `general`, `decoration`, `animations`, `input`, `binds`, `windowrules`, `layerrules`, `colors`, `solo`, `pointer`, `env`).
3. **Live Directive Validation & Transactional Apply:**
   - Queries `hyprctl version -j` and `hyprctl descriptions -j` (when running under Hyprland) so **zero deprecated or invented directives** are ever emitted (handling Hyprland 0.53+ `windowrule` v2/v3 syntax and 0.57+ named workspace IDs).
   - Every Display/Monitor or Hyprland change applies with a **15-second confirmation timer** in Scy-Shell Studio; if the display goes black or Hyprland reports config errors (`hyprctl configerrors`), `scy-hypr` automatically reverts to the last known-good snapshot!
