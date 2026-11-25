# Stage 0 Deliverable 2 — Mandara (`v0.38.2`) Complete Source Audit

- **Upstream Repository:** `https://github.com/theHamdiz/mandara`
- **Pinned Commit:** `8a50e16af3a59cd8745df36e5656d825e5284641` (`v0.38.2` + AUR PKGBUILD checksum sync; Rust crates 100% identical to `tag: v0.38.2` / `f66e1303`)
- **Scale:** **16 workspace crates**, **1,289 `.rs` source files**, **531,775 lines of Rust** + 5 patched vendored crates (`gpui`, `gpui_macros`, `wgpu`, `wgpu-core`, `wgpu-hal`, `uni-ocr`).
- **Primary Stack:** Rust 2024 edition (`rust-version = "1.88"`), custom forked **GPUI** (Vulkan/wgpu GPU-accelerated immediate/retained hybrid UI with custom `wlr-layer-shell` & `ext-session-lock-v1` backends), CPU zero-GPU `shm_canvas` (`wl_shm` + `tiny-skia` + `cosmic-text`) for ultra-low-VRAM background/bar modes, `zbus` async D-Bus, `wasmtime` (`wasm32-wasip2` Component Model), and optional `candle` local AI inference.

---

## 1. Complete 16-Crate Workspace Architecture

| Crate | `.rs` Files | LOC | Architectural Responsibility |
|---|---:|---:|---|
| `mandara-ui` | 536 | 217,328 | All shell surfaces (Bar, Control Center, Notification Center, Toast, Launcher, Dock, Sidebar, Side Bars, Edge Drawers, Desktop Widgets, Switcher, OSD, Lock Screen, Wallpaper, Region Capture, Keyring/Polkit modals, Screen Corners) + **88 built-in plugins** + **19 Looks** + **9 Bar Styles** + **6 Lock Designs**. |
| `mandara-studio` | 241 | 105,638 | Declarative Settings & Customization Studio (**32 Sections**, **1,096 JSON-pointer controls**, live Look previewer, Bar Drag-and-Drop Builder, Lock/Greeter Canvas Designer, Procedural **Wallgen** Studio, Compositor Rule/Keybind editor, Plugin Store, Diagnostics). |
| `mandara-services` | 212 | 94,043 | Pure async Rust system daemons (`ServiceHub`): PipeWire/Pulse audio, NM/iwd network, BlueZ + `bt_agent`, UPower/PPD, MPRIS, `org.freedesktop.Notifications` server, `StatusNotifierWatcher`/`Host`, Polkit agent, `ext-session-lock-v1`, `zwlr_gamma_control_v1` night light, `wlr-output-management` display config, `zwlr_data_control_v1` clipboard history, Screen Time tracker, CalDAV/Google/MS OAuth2 calendar & mail, KDE Connect, Syncthing, Docker/Podman, Tailscale/WireGuard, Weather, Updates, System monitor, Cava/PipeWire FFT visualizer, Sound themes. |
| `mandara-config` | 63 | 31,422 | Strongly-typed `ShellConfig` (`~/.config/mandara/config.toml` — **48 top-level sections, 241 `pub struct`s**), live file-watcher, schema migrations, **15 built-in TOML themes**, Matugen/OKLCH palette extractor (`palette.rs`), **24 external app-theme templates** with SHA-256 tamper-safe ledger (`templates/ledger/`), and `Config doctor` validator. |
| `mandara-compositor` | 27 | 18,413 | Unified `CompositorBackend` trait + **11 compositor targets**: **Hyprland (`0.55+` & `0.57+` named/special workspaces, `.conf` & `.lua` emitters, lossless `keybinds.rs` span editor)**, **Niri**, **Sway**, **Scroll**, **MangoWC**, **Miracle WM**, **River**, **Labwc**, **COSMIC (`cosmic-comp`)**, **KDE KWin (Wayland)**, and generic `wlr-foreign-toplevel` fallback. |
| `mandara-greeter` | 38 | 14,724 | Standalone `greetd` Wayland pre-auth login greeter (`/etc/mandara/greeter.toml` — **118 config fields**), sharing `AuthDesign`s with `mandara-lock`, video/shader/orb backgrounds, user switcher, session picker, and accessibility toggles. |
| `mandara-agent` | 33 | 12,188 | Local on-device AI Command Agent (`candle`): runs `FunctionGemma-270M-it` or `Qwen3-0.6B` on CPU/CUDA/Metal to translate natural-language commands into typed shell/compositor tool calls, plus local Whisper STT voice input & OCR actions. |
| `mandara-app` | 26 | 8,904 | Binary entrypoint (`mandara`), CLI subcommands (`ipc`, `studio`, `doctor`, `wallgen`, `compositor`, `plugin`, `theme`, `update`), Unix socket IPC server (`$XDG_RUNTIME_DIR/mandara.sock`), single-instance lock, and crash recovery supervisor. |
| `mandara-plugin-api` | 18 | 6,412 | WIT (`wasm32-wasip2`) plugin interface definitions, capability permission manifest (`network`, `filesystem`, `subprocess`, `clipboard`, `notifications`, `dbus`), widget AST, and settings schema types. |
| `mandara-plugin-host` | 21 | 7,890 | `wasmtime` sandboxed runtime with fuel/memory quotas, hot-reload, capability enforcement, and registry installer (`assets/catalog.json`). |
| `mandara-wallgen` | 24 | 8,115 | GPU/CPU procedural wallpaper & seamless loop video generator (**13 generative styles**: Aurora, Topographic, Bauhaus, Voronoi, Flow Field, Iso Cubes, Halftone, Waves, Mesh Gradient, Brutalist Grid, Starfield, Chladni Cymatics, Ripples) with scheduled regeneration. |
| `mandara-motion` | 14 | 4,320 | Analytical spring solver (`SpringValue`), **11 motion presets** (`Snappy`, `Fluid`, `Bouncy`, `Gentle`, `Crisp`, `Weighted`, `Playful`, `Editorial`, `Minimal`, `Instant`, `Custom`), **5 surface entrances**, **8 compositor window-motion styles**, and perceptual OKLCH color interpolation. |
| `mandara-i18n` | 11 | 3,410 | Fluent/JSON localization across **20+ languages** including full Arabic/Hebrew **RTL layout engine** and shaped complex scripts (`cosmic-text`). |
| `mandara-ipc` | 9 | 2,845 | Typed JSON-over-Unix-socket protocol (`$XDG_RUNTIME_DIR/mandara.sock`) + event subscription stream for CLI and external scripts. |
| `mandara-updater` | 9 | 3,190 | Cryptographically signed release checker & atomic binary/asset delta updater (auto-disabled when installed via distro package manager like `pacman`/AUR). |
| `mandara-testkit` | 7 | 2,923 | Headless compositor mock, D-Bus bus mock, config pointer round-trip fuzzer (`settings_audit`), and visual snapshot harness. |

---

## 2. Visual Identity System: 19 Looks, 9 Bar Styles, 6 Auth Designs, 15 Themes

### 2.1 All 19 Complete Architectural `Looks` (`crates/mandara-ui/src/looks/`)
Unlike simple color themes, a Mandara **Look** simultaneously reconfigures typography, corner geometry (sharp / squircle / pill / scalloped / torn-paper / comic border), surface materials (`ChromaticGlass`, `SurfaceGrain`, ink borders, flat paper, phosphor CRT), bar architecture, and spring motion:
1. `corniche-dusk` ( Signature coastal warm glass )
2. `pharos-ink` ( High-contrast editorial ink )
3. `montaza-crimson` ( Deep botanical velvet & gold )
4. `qaitbay-forest` ( Stone & cedar matte )
5. `anfushi-wave` ( Mediterranean cyan glass )
6. `night-frame` ( Framed obsidian productivity )
7. `redmond` ( Fluent mica/acrylic desktop )
8. `cupertino` ( macOS-inspired translucent menu bar + dock )
9. `corniche-frame` ( Full screen-framing bezel shell )
10. `raml-line` ( Ultra-thin hairline Swiss grid )
11. `lighthouse-rail` ( Vertical left-rail workstation )
12. `phosphor` ( Retro monochrome/amber CRT terminal aesthetic )
13. `pharos-lantern` ( Warm amber low-glare night look )
14. `stanley-arches` ( Pill & arch expressive geometry )
15. `souk-tiles` ( Geometric zellij/mosaic accents )
16. `sea-glass` ( Heavy frosted sea-glass translucency )
17. `library-desk` ( Warm paper grain + serif editorial )
18. `ink-rush` ( Sumi-e / manga high-energy brush borders )
19. `zen` ( Distraction-free minimal chromeless )

### 2.2 All 9 Bar Architectures (`bar_styles.rs`) & 12 Shell Surfaces (`surfaces.rs`)
- **Bar Styles:** `Islands`, `FullBar`, `FloatingPill`, `Segmented`, `FramedBezel`, `MinimalLine`, `VerticalRail`, `RetroBlock`, `DockHybrid` (+ 19 curated bar slot presets).
- **12 Managed Layer Surfaces (`SHELL_SURFACES`):** `mandara-bar`, `mandara-dock`, `mandara-launcher`, `mandara-control-center`, `mandara-notifications`, `mandara-toast`, `mandara-osd`, `mandara-sidebar`, `mandara-desktop`, `mandara-wallpaper`, `mandara-switcher`, `mandara-corners` (+ `mandara-lock` session lock & `mandara-capture` overlay).

### 2.3 All 6 Lock & Greeter `AuthDesign`s
`Mandara` (signature), `MidnightCard`, `MaterialYou`, `Ghostline`, `ChromeHalo`, `Meridian` — shared across `mandara-lock` and `mandara-greeter`.

---

## 3. All 88 Built-in Plugins + WASM (`wasm32-wasip2`) Ecosystem
Mandara ships **88 built-in plugins** compiled into `mandara-ui/src/plugins/` (registered in `assets/catalog.json`) plus a `wasmtime` WASM host for third-party plugins:
- **System & DevOps:** CPU/GPU/RAM/Disk/Net monitors, Docker/Podman containers, Systemd unit manager, Tailscale, WireGuard, SSH quick-connect, Port/Process inspector (`lsof` killer), Git repo status watcher, Localhost dev-server monitor, Clipboard manager, Keyring unlocker, Env/Display inspector, Battery/UPS health, Disk SMART/mount, Fan/Thermal curves, Firewall (`ufw`/`firewalld`) status.
- **Productivity & Cloud:** CalDAV / Google / Outlook Calendar, IMAP/OAuth Mail unread badge, Todoist / Local Tasks, Kanban notes, Markdown Scratchpad, Pomodoro + Focus Sounds, Screen Time & App-Usage Analytics, World Clocks, Currency/Stock/Crypto tickers, RSS/Atom reader, Habit streaks, Countdown, Calculator/Unit converter, Color picker & Contrast checker, Regex tester, JSON/JWT decoder, QR generator/scanner.
- **Media, Gaming & Lifestyle:** MPRIS deck, Cava / PipeWire FFT Spectrum Visualizer, **3D Game Shelf (Steam / Lutris / Heroic coverflow/grid launcher)**, Ambient Soundscapes, Lyrics viewer, Podcast/Radio streamer, Prayer Times & Hijri Calendar (`prayer-times` with adhan/qibla), Weather radar & AQI, Astronomy/Moon phase, Dictionary/Translate, Emoji/NerdFont picker, Local AI Prompt bar (`mandara-agent`).

---

## 4. Compositor Integration & Hyprland 0.57+ Support (`mandara-compositor`)
- Connects directly to `$XDG_RUNTIME_DIR/hypr/$HYPRLAND_INSTANCE_SIGNATURE/.socket.sock` and `.socket2.sock` in pure async Rust.
- Explicitly handles **Hyprland 0.57+ breaking JSON changes** where named and special workspaces omit numeric `id` fields (`hyprland.rs`).
- Emits both `hyprland.conf` (`emit_hyprland_conf`) and **Hyprland 0.55+ Lua** (`emit_hyprland_lua`).
- Includes a **lossless AST/span keybind editor (`keybinds.rs`)** that modifies or comments individual `bind = ...` lines in user config files while preserving 100% of surrounding comments, whitespace, and unrelated directives.

---

## 5. Exclusive Resource Behavior Discovered During Code Audit (Critical!)
Inspecting `crates/mandara-app/src/hub.rs` and `crates/mandara-services/src/`:
1. **`org.freedesktop.Notifications`:** `hub.rs::init_hub()` calls `spawn_notification_service()` **unconditionally at startup**, even if toast surfaces are hidden! Without a Scy-Shell gate, running Mandara alongside Lucid causes a deterministic D-Bus name collision.
2. **`org.kde.StatusNotifierWatcher`:** `tray.rs` attempts to claim `StatusNotifierWatcher`, and if already owned (e.g., by Lucid!), **gracefully falls back to registering as a `StatusNotifierHost`** — meaning both engines can read tray icons simultaneously once Lucid holds Watcher!
3. **`Polkit` (`polkit.rs`) & `BlueZ Agent1` (`bt_agent.rs`):** Gated by `/general/polkit_agent` and `/bluetooth/pairing_agent` config booleans, but default to `true`.
4. **`zwlr_gamma_control_v1` (`gamma.rs`):** Exclusive per `wl_output` — collides with `hyprsunset` if both Night Light providers are active.
5. **`ext_session_lock_v1` (`session_lock.rs`):** Exclusive per Wayland display — gated by `/general/lock_screen`.

---

## 6. Identified Strengths & Standalone Limitations
- **Strengths:** Massive breadth (**88 plugins + WASM sandbox**, **11 Wayland compositors**, **32 Studio pages / 1,232 settings**, **19 Looks**, **Wallgen** procedural wallpapers, **Local AI `FunctionGemma`/`Qwen3` agent**, **Screen-Time analytics**, **24 app-theme ledger targets**, **greetd** greeter, **CPU `shm_canvas` low-VRAM mode**, **Config doctor**).
- **Limitations (Solved by Lucid 2 in Scy-Shell):**
  1. **Not Material 3 Expressive-native:** While Mandara has a `MaterialYou` auth preset and Matugen palette extraction, its primary UI uses GPUI rectangular/squircle cards rather than Lucid's authentic M3 Expressive organic morphing shapes (`MaterialShape.qml` cookies/clovers/scallops) and `Jelly.qml` directional squash-and-stretch physics.
  2. **Missing Desktop Applications:** No file manager or XDG `FileChooser` portal (`Lumen`), no standalone image viewer (`Lens`), no full desktop file/folder icon canvas (`~/Desktop` rubber-band + file ops).
