# Stage 0 Deliverable 6 — Visual Implementation Inventory & Provider/Presentation Separability Matrix

Per Sections 5 & 6, **Scy-Shell** adopts **Lucid 2's Material 3 Expressive** language as its primary cohesive visual identity while preserving every visual presentation, Look, shader, shape, spring, and preset from both Lucid 2 and Mandara.

---

## 1. Visual Primitives & Rendering Stack Comparison

| Visual Domain | Lucid 2 (`v1.21.1` — Quickshell / Qt6 RHI) | Mandara (`v0.38.2` — Forked GPUI / wgpu + `shm_canvas`) | Scy-Shell Unification Strategy |
|---|---|---|---|
| **Color Science** | **Matugen HCT** (Hue-Chroma-Tone Material 3 dynamic tonal palettes: 50+ semantic tokens in `Theme.qml`, light & dark) | **OKLCH perceptual palette** (`palette.rs`) + **15 curated TOML themes** + Matugen import | **Unified Palette Engine:** One wallpaper/seed change computes BOTH full M3 HCT tokens AND OKLCH tokens simultaneously, updating both QML and GPUI surfaces in <30ms with zero visual drift! |
| **Typography** | **Google Sans** (variable UI) + **JetBrains Mono** + **Material Symbols Rounded** (variable optical size/fill/weight/grade) | **Space Grotesk**, **Inter**, **Noto Sans Arabic**, **Cairo**, **JetBrains Mono** + **Phosphor Icons** | Default UI font across BOTH engines set to **Google Sans** (with Noto Sans Arabic/CJK fallback & RTL shaping preserved); all Mandara Look font pairings remain selectable! |
| **Organic & Architectural Shapes** | **`MaterialShape.qml` & `Shapes.js`:** Morphing M3 Expressive polygons (`cookie-4`, `cookie-6`, `cookie-7`, `cookie-9`, `cookie-12`, `clover`, `arch`, `pill`, `scallop`, `slanted-pill`, `burst`, `gem`, `shield`, `heart`) | **Architectural Look Silhouettes:** `Sharp` (0px), `Rounded`, `Squircle`, `Pill`, `Scalloped`, `TornPaper` (`library-desk`), `WashiTape`, `BrushBorder` (`ink-rush`), `CRT Bezel` (`phosphor`) | Lucid keeps native QML `MaterialShape`; Scy-Shell adds SVG/path M3 Expressive polygon primitives into Mandara's new default `scy-m3-expressive` Look while retaining all 19 architectural Looks! |
| **Spring & Motion Physics** | **`Jelly.qml`:** Velocity-coupled directional **2D squash-and-stretch** (`scaleX`/`scaleY` deformation) + expressive overshoot curves | **`mandara-motion` (`SpringValue`):** Analytical 2nd-order harmonic oscillator + **11 presets** (`Snappy`, `Fluid`, `Bouncy`, `Gentle`, `Crisp`, `Weighted`, `Playful`, `Editorial`, `Minimal`, `Instant`, `Custom`) + **5 surface entrances** | Both engines share a master `Motion Scale` / `Reduced Motion` accessibility bus while keeping `Jelly.qml` 2D deformation parameters AND Mandara's 11 analytical spring presets independently tunable! |
| **Glass, Blur & Texture** | **`Glass.qml`:** Wayland `ext-background-effect-v1` compositor blur region + multi-stop specular highlight rim + M3 surface tint (`blur.json`) | **`ChromaticGlass` + `SurfaceGrain`:** GPU refractive edge dispersion, frosted backdrop, procedural film/paper noise (`grain.rs`), plus zero-GPU **`shm_canvas`** mode | Both preserved! On Hyprland, Scy-Shell's `layers.lua` applies matching `blur` & `ignore_alpha` rules to BOTH `lucid-*` and `mandara-*` layer namespaces! |

---

## 2. Complete Inventory of Selectable Visual Styles & Presets

1. **Status Bar Presentations (14 Total):**
   - **Lucid Bar Modes (5):** Floating Islands, Pill Bar, Full-Width Flush, Edge-Hugger, Vertical Left/Right Rail (+ 22 toggleable M3 modules).
   - **Mandara `BarStyle`s (9):** `Islands`, `FullBar`, `FloatingPill`, `Segmented`, `FramedBezel`, `MinimalLine`, `VerticalRail`, `RetroBlock`, `DockHybrid` (+ 19 slot presets + CPU `shm_canvas` mode).
2. **Architectural Shell `Looks` (20 Total in Scy-Shell):**
   - **Primary Default (`1`):** `scy-m3-expressive` (Lucid 2 Material 3 Expressive token/font/shape/motion harmonization across QML + GPUI).
   - **Mandara Original `Looks` (`19`):** `corniche-dusk`, `pharos-ink`, `montaza-crimson`, `qaitbay-forest`, `anfushi-wave`, `night-frame`, `redmond`, `cupertino`, `corniche-frame`, `raml-line`, `lighthouse-rail`, `phosphor`, `pharos-lantern`, `stanley-arches`, `souk-tiles`, `sea-glass`, `library-desk`, `ink-rush`, `zen`.
3. **Session Lock & Pre-Auth Login Designs (12 Total):**
   - **Lucid Lock & SDDM Presets (`6`):** `centre`, `split`, `panel` (left/right sheet), `minimal`, `bento` (card grid), `deck` (hero media) — with 10 modular slot widgets.
   - **Mandara Lock & `greetd` `AuthDesign`s (`6`):** `Mandara`, `MidnightCard`, `MaterialYou`, `Ghostline`, `ChromeHalo`, `Meridian` — with freeform canvas element placement.
4. **Desktop Widget Collections (`113+` Total):**
   - **Lucid M3 Expressive Widgets:** **25 categories / 88 style-and-size variants** + 6 curated desktop presets.
   - **Mandara Built-in & WASM Widgets:** **88 built-in plugins** + unlimited sandboxed `wasm32-wasip2` widgets.
5. **Wallpaper & Generative Visuals:**
   - **Lucid:** `awww` (10 transitions: `wipe`, `wave`, `grow`, `outer`, `any`, `fade`, `left`, `right`, `top`, `bottom`) + `LiveShell.qml` MP4/WebM video & interactive GLSL shaders.
   - **Mandara:** **13 `Wallgen` procedural styles** (`Aurora`, `Topographic`, `Bauhaus`, `Voronoi`, `FlowField`, `IsoCubes`, `Halftone`, `Waves`, `MeshGradient`, `BrutalistGrid`, `Starfield`, `Chladni`, `Ripples`) + Ken Burns / Orbs.
6. **Compositor Window Motion Styles (`8` Mandara + Lucid M3 Bezier Trees):**
   - Lucid M3 Expressive window/layer curves + Mandara's 8 `WindowStyle` presets (`Classic`, `Slide`, `Pop`, `Zoom`, `Glide`, `Snap`, `Minimal`, `Zero`).

---

## 3. Functional Provider vs. Visual Presentation Separability Matrix (Section 6)

Per Section 6, Scy-Shell separates **Functional Provider** (data/daemon logic) from **Presentation / Renderer** wherever Wayland & D-Bus protocols cleanly allow event/data decoupling, and documents bundled pairs transparently where rendering is tightly coupled to widget trees:

| Subsystem | Functional Provider Options | Presentation / Renderer Options | Separation Level & Technical Mechanism |
|---|---|---|---|
| **Notifications & Toasts** | `Lucid Notifs` (Default) / `Mandara Notifications` | `Lucid M3 Toasts` (Default) / `Mandara GPUI Toasts` | **FULLY SEPARABLE!** `scy-daemon` Notification Broker forwards normalized `ToastEvent` + action callbacks over IPC, so Mandara's rule/grouping backend can render through Lucid's M3 Jelly Toasts (and vice versa). |
| **OSD (Audio / Brightness / Keys)** | `Scy-Shell Hardware/PipeWire State` | `Lucid M3 Jelly OSD` (Default) / `Mandara GPUI OSD` | **FULLY SEPARABLE!** Hardware volume/backlight changes emit normalized `OsdEvent { kind, value, muted }` on `scy-shell.sock`; either OSD renderer can display it. |
| **Wallpaper & `Wallgen`** | `Lucid Gallery` / `Mandara Wallgen (13 Styles)` / `Scheduled Rotator` | `Lucid awww + LiveShell` (Default) / `Mandara wgpu` / `Mandara CPU shm_canvas` | **FULLY SEPARABLE!** `Wallgen` outputs standard PNG/JPEG/MP4 files + palette seeds that `Lucid awww`/`LiveShell` renders natively! |
| **Launcher & AI / Plugins** | `Lucid App/File/Clip Providers` + `Mandara Local AI & 88 Plugins` | `Lucid M3 Morphing Launcher` (Default) / `Mandara GPUI Launcher` | **FEDERATED SEPARATION!** Lucid's M3 Launcher queries `mandara-agent` (`!ai`) and `mandara-plugin-host` (`@`) over local Unix socket JSON-RPC while rendering results in pure M3 Expressive QML! |
| **Calendar & Cloud Sync** | `Lucid Local Reminders` + `Mandara CalDAV/Google/Outlook Sync` | `Lucid Calendar & Lock Agenda` (Default) / `Mandara Calendar` | **FULLY SEPARABLE DATA!** Mandara's background `calendar_sync` exports normalized iCal/JSON agenda items consumed directly by Lucid's `lucidcalendar` and `LockAgenda.qml`. |
| **Desktop Widgets** | `Lucid Widgets` / `Mandara Plugins & WASM` / **`Hybrid Both`** | `Lucid M3 QML` / `Mandara GPUI` / **`Coexisting Non-Overlapping`** | **COEXISTING HYBRID!** Wayland `wl_surface.set_input_region` allows both widget canvases to render side-by-side on `LAYER_BOTTOM` without blocking clicks! |
| **Status Bar** | `Lucid Bar` (Default) / `Mandara Bar` / `Per-Monitor Mix` | Lucid 5 Layouts / Mandara 9 `BarStyle`s (incl. `scy-m3-expressive` Look) | **BUNDLED PER-SURFACE + PLUGIN BRIDGE:** QML bar modules and GPUI bar widgets run in their own GPU scene graphs, so each monitor picks Lucid Bar or Mandara Bar — PLUS Lucid Bar gains a native `ScyPluginPill.qml` button opening Mandara's 88/WASM plugin popovers! |
| **Session Lock (`ext-session-lock-v1`)** | `Lucid Lock` (Default) / `Mandara Lock` | Lucid 6 Slot Presets / Mandara 6 `AuthDesign`s | **BUNDLED BY SECURITY DESIGN:** Wayland `ext-session-lock-v1` requires PAM + surface creation in the single locking client process to avoid spoofing/IPC lockouts. Studio clearly badges the 6 Lucid presets and 6 Mandara designs with their provider. |
