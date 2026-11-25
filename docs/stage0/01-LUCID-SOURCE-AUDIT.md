# Stage 0 Deliverable 1 — Lucid 2 (`v1.21.1`) Complete Source Audit

- **Upstream Repository:** `https://github.com/Sn3akyy1/lucid`
- **Pinned Commit:** `15f13429bc59b4a97223bcfe5592735cb1eb92be` (`tag: v1.21.1`)
- **Primary Stack:** Quickshell (`0.2+` / Qt 6.8+ QML), Hyprland (`0.55+` native Lua runtime), Matugen (Material You HCT palette engine), `awww` + GStreamer/ShaderEffect live wallpapers, Python 3 (`dbus-next` / `pydbus` / `gi`) & POSIX/Bash helpers.
- **Design Identity:** **Material 3 Expressive** — dynamic HCT tonal palettes (`Theme.qml`), damped analytical squash-and-stretch spring physics (`Jelly.qml`), expressive organic/cookie/clover/scallop shapes (`MaterialShape.qml`), real compositor `ext-background-effect-v1` frosted glass (`Glass.qml`), Google Sans + Material Symbols Rounded variable fonts.

---

## 1. Complete Directory & Module Inventory

### 1.1 Root Entrypoint & Core Singletons (`upstream/lucid/`)
| File | Type | Responsibility & Architectural Details |
|---|---|---|
| `shell.qml` | Root `ShellRoot` | Instantiates all surfaces, registers **26 `Quickshell.Io.IpcHandler` targets**, binds hot-reload watchers, manages multi-monitor `Variants`, coordinates startup splash (`StartupSplash.qml`), idle, lock, OSD, toasts, bars, docks, desktop widgets, and overlays. |
| `Prefs.qml` | Singleton (`JsonAdapter`) | Central reactive settings store backed by `~/.config/quickshell/lucidprefs/prefs.json` (**382 persisted properties**), schema migration logic, profile export/import, and live Matugen/Hyprland sync triggers. |
| `HyprConfig.qml` | Singleton | Live bidirectional bridge to Hyprland: reads **66 native Hyprland options** via `hyprctl getoption -j`, merges **6 `lucid.*` synthetic extensions** (`border`, `inactive_border`, `solo`, `cursor_tilt`, `cursor_tilt_apps`, `find_pointer`), writes `~/.config/hypr/lucid-settings.lua`, and hot-applies via `hyprctl keyword` / `hyprctl eval`. |
| `Theme.qml` | Singleton | Material 3 Expressive token engine: watches Matugen-generated JSON (`colors.json`), exposes 50+ semantic tokens (`bg`, `surface0..3`, `accent`, `accentContainer`, `outline`, `scrim`, semantic status colors), glass tinting, and `blur.json` integration. |
| `Jelly.qml` | Singleton / Component | Expressive spring motion engine: analytical critically/under-damped spring physics (`damping`, `response`, `motionScale`), directional squash-and-stretch (`scaleX`/`scaleY` deformation on velocity), shared across popups, pills, switches, bar islands, and launcher morphs. |
| `Glass.qml` | Component | Wayland `ext-background-effect-v1` frosted glass region binder + multi-stop specular highlight rim, inner shadow, surface tint, and automatic opaque fallback when blur is off or unsupported. |
| `MaterialShape.qml` & `Shapes.js` | Component / JS | M3 Expressive geometric morphing polygons (cookie-4/6/7/9/12, clover, arch, pill, flower, scalloped badge, slanted pill, burst, gem, shield, heart) rendered via QML `ShapePath` / `Canvas`. |
| `Widgets.qml` | Singleton | Desktop widget registry & layout engine (`~/.config/quickshell/widgets.json`): **25 widget types**, **88 size/style variants**, **6 curated layout presets**, snap grid, edit-mode drag/resize handles, and per-instance option schema. |
| `Notifs.qml` | Singleton | `Quickshell.Services.Notifications.NotificationServer` claiming `org.freedesktop.Notifications`; persistent history (`~/.local/state/lucid/notifs.json`), app grouping, inline actions, DND, scheduled Quiet Hours, privacy masking on lock, urgency routing, and sound triggers. |
| `Audio.qml` | Singleton | `Quickshell.Services.Pipewire` graph integration: default sink/source volume & mute, per-app `PwNode` stream routing, mic privacy detection, Sound Weaver ambient mixer hooks, and EasyEffects preset switching. |
| `Network.qml` | Singleton | `nmcli` / NetworkManager D-Bus state machine: Wi-Fi scan/connect/saved networks, WPA password prompts, Ethernet, Hotspot toggle, VPN profiles (WireGuard/NM), Airplane mode, and live rx/tx throughput. |
| `Bluetooth.qml` | Singleton | BlueZ state + `support/bt-agent.py` (`org.bluez.Agent1` PIN/passkey pairing) + `support/bt-receive.py` (`org.bluez.obex.Agent1` OBEX file transfer inbox). |
| `Battery.qml` | Singleton | UPower battery metrics, time-to-empty/full, charge health, `power-profiles-daemon` (`power-saver`, `balanced`, `performance`), low-battery warnings, and critical hibernate/suspend triggers. |
| `Mpris.qml` | Singleton | `Quickshell.Services.Mpris` multi-player controller, active player pinning, cover-art color extraction, Cava spectrum integration, and lyric lookup (`support/lyrics.py`). |
| `Weather.qml` & `Location.qml` | Singletons | Open-Meteo weather forecast (hourly, 7-day, UV, wind, humidity, WMO glyphs) + automatic IP/GPS geolocation (`gpsMode`, manual lat/lon override). |
| `Wallpapers.qml` & `LiveShell.qml` | Singleton / Surface | Static wallpaper orchestration via `awww` (10 transition types, custom bezier/angle/fps/duration, scheduled rotation, per-monitor assignment) + **Live Wallpapers**: MP4/WebM video playback (hardware-decoded loop, pause-on-fullscreen/battery) and interactive GLSL/QML procedural shaders + parallax depth. |
| `SystemStats.qml` & `Storage.qml` | Singletons | CPU load/temp/governor, GPU load/VRAM/temp (AMD/NVIDIA/Intel), RAM/Swap, disk mounts & free-space alerts, top processes. |
| `Privacy.qml` | Singleton | Real-time PipeWire + `/proc` / `fuser` camera, microphone, and screencast (`xdg-desktop-portal`) active-use indicator pills in the bar. |
| `KdeConnect.qml` | Singleton | Bridges `org.kde.kdeconnect` via `support/kdeconnect-bridge.py`: phone battery, ring device, clipboard push, file share, SMS/notification sync. |
| `Polkit.qml` | Singleton / Overlay | `Quickshell.Services.Polkit` authentication agent (`unix-session`) rendering a Material 3 Expressive modal card with Jelly shake on failure. |
| `Idle.qml` | Singleton | Coordinates `hypridle` / Wayland idle timers: dim screen → lock session → DPMS off → suspend, with media/fullscreen inhibitors and Caffeine toggle. |
| `Updates.qml` | Singleton | Arch/CachyOS (`checkupdates` + `paru`/`yay` AUR + `flatpak`) background update checker with one-click terminal upgrade launch. |
| `Timers.qml` | Singleton | Pomodoro focus timer (work/short-break/long-break cycles, sound alerts), multi-timer countdowns, alarms, and scheduled desktop reminders. |
| `Gamemode.qml` | Singleton | Detects Feral `gamemoded` or manual Game Mode; optionally disables Hyprland animations/blur/gaps/shadows, pauses live wallpaper, and suppresses non-critical toasts. |
| `I18n.qml` | Singleton | Localization catalogue loader (`support/i18n/*.json`) with RTL layout mirroring support and `support/i18n-check.py` static verifier. |
| `Sounds.qml` | Singleton | Low-latency UI feedback & event sound player (`pw-play` / Qt Multimedia): volume tick, notification chime, screenshot shutter, plug/unplug, lock/unlock, timer alarm. |

### 1.2 All 21 Subdirectories & Standalone Applications
1. **`lucidbar/`** — Adaptive M3 Expressive status bar:
   - **Positions:** Top, Bottom, Left (vertical), Right (vertical).
   - **Styles/Layouts:** Floating islands, Pill bar, Full-width flush, Edge-hugger, Auto-hide / dodge windows.
   - **Modules (22+):** Start/Launcher glyph, Active Window title/app icon, Workspaces (pills, dots, numbers, Japanese kanji, Roman numerals, app icons inside workspaces, special workspace chip), Media mini-player + Cava bars, Clock/Date/Pomodoro chip, Weather chip, Privacy dot (cam/mic/cast), Tray (`StatusNotifierWatcher`), Clipboard, Updates badge, GameMode badge, Idle/Caffeine, Night Light, Quick System cluster (Wi-Fi, BT, Volume, Battery), Notification bell, Power pill.
2. **`luciddock/`** — Expressive application dock (`~/.config/quickshell/pinned.json`):
   - Pinned + running tasks, multi-window preview hover cards, workspace indicators, trash module, separator, launcher button, intelligent auto-hide (dodge active, dodge any, always visible), Jelly magnification/bounce.
3. **`lucidlaunch/`** — Unified Launcher & Command Palette:
   - Modes: Apps (fuzzy desktop entry search, frequency ranking, pin to dock, GPU/discrete launch), Calculator (`qalc`/JS math + unit/currency conversion), Clipboard (`cliphist` text & image previews, pin/clear), Emoji/Kaomoji/Glyphs, Wallpaper switcher, Windows switcher, Shell commands (`>`), Web search (`?`), System actions (`!`), File search (`fd`/`plocate`).
4. **`lucidquick/`** — Control Centre & Notification Centre:
   - Expandable M3 Expressive tiles (Wi-Fi sub-sheet, Bluetooth sub-sheet, Audio sink/source/per-app mixer sub-sheet, Night Light warmth/schedule, Power profile, Caffeine, Game Mode, DND, Airplane Mode, Screen Record, Screenshot, Color Picker), Brightness + Volume thick M3 sliders, Media transport card, and grouped Notification list.
5. **`lucidcalendar/`** — Calendar, Weather, Timers & World Clock Popover:
   - Month grid with local reminders/agenda, 7-day + hourly Open-Meteo weather card, Pomodoro focus ring, countdown timers, stopwatch, and multi-timezone clocks.
6. **`lucidwidgets/`** — Desktop Widget Canvas (`LAYER_BOTTOM`):
   - **25 widget types across 88 variants:** Digital/Analog/Morphing M3 Clocks, Weather (compact/card/forecast), Media Deck/Vinyl/Cover, Calendar, Quotes, Notes/Sticky, Todo list, Habits tracker, Countdown, World Clock, System Gauges (CPU/RAM/GPU/Disk/Network rings & sparklines), Battery/Devices, Cava Audio Visualizer, Photo Frame (expressive M3 cookie/clover frames!), GitHub contribution graph, Quick Launch grid, Pomodoro, Now Playing Lyrics, Uptime/OS Fetch card, Sound Weaver ambient mixer.
7. **`lucidlock/`** — Wayland Session Lock (`WlSessionLock` / `ext-session-lock-v1`):
   - **6 Layout Presets** (`Catalog.js`): `centre`, `split`, `panel` (left/right sheet), `minimal`, `bento` (card grid), `deck` (hero media).
   - **10 Lock Widgets**: `clock` (stacked/inline/dial/M3-shapes), `date`, `greeting`, `weather`, `status` (chips/icons), `power`, `message` (owner contact), `media` (card/compact/cover/deck), `notifications` (list/icons/count + privacy redact), `agenda`.
   - Includes `OnScreenKeys.qml` virtual keyboard, PAM + fprintd fingerprint auth, multi-monitor secondary clock/blank mode, and live/blurred wallpaper backdrop.
8. **`support/sddm/lucid/`** — Matching Pre-Auth SDDM Display Manager Theme:
   - Shares `Catalog.js` layout presets with `lucidlock` via `support/sync-sddm.sh` so each user's login screen matches their personal lock-screen preset, palette, and wallpaper!
9. **`lucidosd/`** — Expressive On-Screen Displays:
   - Volume, Microphone mute, Brightness, Keyboard backlight, Caps Lock / Num Lock / Layout switch, Workspace OSD, Media track toast.
10. **`lucidtoast/`** — Floating Notification Toasts:
    - Corner placement (TL/TC/TR/BR/BC/BL), urgency styling, action buttons, hover-to-pause timeout, swipe-to-dismiss, compact mode.
11. **`lucidshot/`** — Screenshot, Annotation, OCR & Screen Recording Suite:
    - Region/Window/Monitor capture (`grim` + Hyprland client geometry), interactive crop & annotation canvas (arrows, rectangles, blur/pixelate redact, text, step numbers, highlighter), Tesseract OCR (`tesseract`), QR code decode (`zbarimg`), color loupe (`hyprpicker`), and `gpu-screen-recorder` / `wf-recorder` MP4/GIF recording with mic/system audio toggles.
12. **`lucidoverview/` & `lucidexpose/`** — Workspace Overview, Exposé & Alt-Tab Switcher:
    - Live `ScreencopyView` window thumbnails across workspaces, drag-and-drop window between workspaces, search-to-focus filter, and keyboard Alt-Tab ring.
13. **`lucidpower/`** — Fullscreen / Card Session Power Menu:
    - Lock, Log out, Suspend, Hibernate, Reboot, Reboot to UEFI (`systemctl reboot --firmware-setup`), Shut down — with active inhibitor/unsaved-work warnings and configurable countdown.
14. **`lucidmoji/`** — Standalone Floating Emoji, Kaomoji, Nerd Font & Symbol Picker (`wtype` / `wl-copy` paste).
15. **`lucidkeys/`** — On-Screen Virtual Keyboard (`wtype` / virtual-keyboard input, layout-aware) + **Keybind Cheat Sheet** (`KeySheet.qml` reading `keybinds.json` + user binds).
16. **`lucidwall/`** — Dedicated Visual Wallpaper Browser, Tag Filter, Matugen Preview & Live Wallpaper Picker.
17. **`lucidlumen/` (`Lumen`)** — Full Material 3 Expressive File Manager AND `org.freedesktop.impl.portal.FileChooser` backend (`support/lumend.py`!):
    - Dual-pane tabs, Miller columns / Grid / List views, Archive mount/extract, Trash management, Bulk rename, Git status badges, Image/PDF/Text preview pane, Bookmark sidebar, and native XDG FileChooser portal dialog replacement!
18. **`lucidlens/` (`Lens`)** — Standalone M3 Expressive Image Viewer & Quick Editor (zoom/pan, EXIF inspector, crop/rotate/flip, slideshow, set-as-wallpaper).
19. **`lucidclock/` (`Clock`)** — Standalone M3 Expressive Clock App (Alarms, World Clocks, Timer presets, Lap Stopwatch, Bedtime/Focus).
20. **`lucid desktop` (`Desktop.qml` + `DesktopIcons.qml`)** — Full Desktop Icons Canvas (`~/Desktop`):
    - Grid snap, rubber-band multi-select, drag-and-drop file move/copy, inline F2 rename, thumbnails, Trash/Home special icons, context menus, and 17 keyboard shortcuts (`support/desktop-icons.py`).
21. **`lucidprefs/`** — **28 Settings Pages (`516` UI controls)** organized into a cohesive M3 Expressive settings studio:
    - `AppearancePage`, `ThemePage`, `BarPage`, `BarModulesPage`, `DockPage`, `LauncherPage`, `WidgetsPage`, `DesktopPage`, `WallpapersPage`, `LockPage`, `NotifsPage`, `OsdPage`, `SoundPage`, `NetworkPage`, `BluetoothPage`, `DisplaysPage`, `HyprWindowsPage`, `HyprMotionPage`, `HyprInputPage`, `HyprRulesPage`, `KeybindsPage`, `TimePage`, `PrivacyPage`, `PowerPage`, `StoragePage`, `UpdatesPage`, `SystemPage`, `AboutPage`.

---

## 2. Hyprland 0.55+ Lua Integration (`support/hypr/`)
Lucid pioneered native **Hyprland 0.55+ Lua configuration** (`~/.config/hypr/hyprland.lua`), structured into **18 modular Lua files**:
1. `init.lua` — Bootstrap loader & safe `pcall` wrapper
2. `env.lua` — Toolkit/Wayland/NVIDIA/cursor env vars
3. `monitors.lua` — Per-display mode, scale, VRR, HDR/bitdepth, transform, mirror (`monitors.json`)
4. `general.lua` — Gaps, border sizes, `lucid.border` dynamic M3 accent gradients, layout (`dwindle`/`master`/`scrolling`)
5. `decoration.lua` — Rounding, `rounding_power` (squircle), blur passes/size/vibrancy, shadow
6. `animations.lua` — M3 Expressive bezier curves & layer/window animation trees
7. `input.lua` — XKB layouts/variants/options, touchpad gestures, sensitivity, repeat rate, **cursor tilt (`cursor:warp` / dynamic tilt plugin hook)**
8. `binds.lua` — Loads `keybinds.json` (**61 bind definitions**) via `qs ipc call ...`
9. `rules.lua` — Window rules (floating modals, PiP, Steam/Lutris, Picture-in-Picture pin, Lucid app sizing, opacity overrides)
10. `layers.lua` — Layer rules (`blur on`, `ignore_alpha`, `xray` on `lucid-*` namespaces)
11. `autostart.lua` — Starts `qs`, `awww-daemon`, `wl-paste --watch cliphist`, `lumend.py`, `bt-agent.py`, `bt-receive.py`, `kdeconnect-bridge.py`
12. `colors.lua` — Matugen-generated Lua color table
13. `solo.lua` — `lucid.solo` smart single-window no-gaps/no-border mode
14. `pointer.lua` — Shake-to-find-cursor (`lucid.find_pointer`) & cursor theme sync
15. `gestures.lua` — 3/4-finger workspace & overview swipe gestures
16. `plugins.lua` — Optional `hyprexpo` / `hyprscrolling` / `hyprtrails` integration
17. `lucid-settings.lua` — Auto-generated overrides from `HyprConfig.qml`
18. `hypr-user.lua` — **Loaded LAST** so user custom Lua overrides always win.

---

## 3. All 26 `Quickshell.Io.IpcHandler` Targets (`shell.qml`)
`launcher`, `quick` (control centre), `calendar`, `overview`, `expose`, `lock`, `power`, `shot`, `record`, `wall`, `prefs`, `moji`, `keys`, `keysheet`, `clipboard`, `audio`, `brightness`, `nightlight`, `dnd`, `gamemode`, `caffeine`, `bar`, `dock`, `widgets`, `theme`, `reload`.

---

## 4. Matugen App-Theming Templates (`support/matugen/`)
Renders live Material You palettes (`support/render-templates.sh`) for:
- GTK 3 & GTK 4 / `libadwaita` (`~/.config/gtk-3.0`, `~/.config/gtk-4.0`)
- Qt5ct & Qt6ct / KColorScheme
- Kitty, Foot, Ghostty, Alacritty
- Fuzzel / Rofi, Cava, Btop, Yazi, Neovim, VS Code / VSCodium, Vesktop/Discord, Zen/Firefox userChrome, Hyprland Lua colors, SDDM theme.

---

## 5. Identified Strengths, Dependencies & Standalone Limitations
- **Strengths:** Unmatched **Material 3 Expressive** visual craft (`Jelly.qml` squash-and-stretch springs, `MaterialShape.qml` organic shapes, `Glass.qml`), complete desktop application suite (`Lumen` + XDG FileChooser portal, `Lens`, `Clock`, `LucidShot` annotation/OCR), rich desktop icons (`DesktopIcons.qml`), shared Lock + SDDM preset engine, and first-class Hyprland 0.55+ Lua modularity.
- **Hard Dependencies:** `quickshell-git` (0.2+), `hyprland` (0.55+ for Lua config), `matugen`, `awww`, `grim`, `slurp`, `wl-clipboard`, `cliphist`, `pipewire`, `networkmanager`, `bluez`, `upower`, `polkit`, `python3` (`dbus-next`, `pygobject`).
- **Limitations (Solved by Mandara in Scy-Shell):**
  1. **Hyprland-only:** Hardcoded to Hyprland IPC/Lua (no Niri, Sway, MangoWC, Scroll, River, Cosmic, Labwc, Miracle, or KDE support).
  2. **No compiled plugin sandbox:** Widgets are QML-only; no WASM (`wasm32-wasip2`) plugin ecosystem or community store.
  3. **No local AI / natural-language shell agent:** No local LLM function-calling agent (`FunctionGemma`/`Qwen3`) or voice STT (`Whisper`).
  4. **No procedural GPU wallpaper generator (`Wallgen`)** or 3D Lutris/Steam game shelf or Screen-Time analytics daemon or CalDAV/OAuth2 cloud sync or `Config doctor` diagnostic suite.
