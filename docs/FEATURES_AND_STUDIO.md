# Features & Unified 15-Section Studio Guide

## 1. Unified 15-Section Scy-Shell Studio

Open Scy-Shell Studio anytime via the top bar, dock, `Super+Escape` / `Super+I`, or CLI (`scy-shell studio`). Studio organizes all **2,026** parameters into **15 user-intent sections** — never splitting the experience into competing Lucid vs Mandara settings apps:

| # | Section ID | Intent & Key Controls |
|---|---|---|
| **01** | `01-personalization` | **Personalization**: Dynamic Design Engine (OKLCH + Material 3 Expressive wallpaper extraction), 20 architectural Looks, Procedural Wallgen (13 styles), fonts, icons, cursors |
| **02** | `02-desktop` | **Desktop Experience**: Status bar silhouette & edge, **Scy Dynamic Island**, workspace indicators, app launcher behavior, desktop icons |
| **03** | `03-dock` | **Dock Studio**: Single-owner dock style (`Island`, `Notch`, `Split`, `Rail`, `Disabled`), placement, icon geometry, parabolic magnification, auto-hide/window-dodge, app groups, separators, recents/frequents, notification badges, multi-monitor policy |
| **04** | `04-visual-effects` | **Visual Effects**: Material presets (`Scy Frosted`, `Liquid Crystal`, `Obsidian Matte`, `Tinted Acrylic`, `Crisp Flat`), Dual-Kawase blur passes & radius, opacity, tint, specular rim borders, shadows, shaders, spring motion physics |
| **05** | `05-layout` | **Layout & Composition**: **Scy Layout Composer** (`Scy Signature`, `Unity Left`, `Minimal Top`, `Bottom Deck`, `Dual Stage`), global UI scale, corner-radius scale, outer margins, multi-monitor policy |
| **06** | `06-widgets` | **Widgets & Components**: Ambient desktop widget board, **Scy Component Laboratory** per-surface material overrides (`dock`, `bar`, `island`, `cards`, `lock`, `cc`), 89 built-in & sandboxed `wasm32-wasip2` extensions |
| **07** | `07-windows` | **Window Management**: Hyprland `0.57+` tiling (`dwindle`/`master`), inner/outer gaps, rounding, active/inactive borders, inactive window dimming, **Scy Workspace Experience** overview, scratchpads |
| **08** | `08-interactions` | **Interactions**: 67 collision-checked compositor shortcuts, trackpad workspace gestures, pointer acceleration, 4-corner hot actions |
| **09** | `09-notifications` | **Notifications & Control Center**: **Scy Control Center** quick-toggle grid, Wi-Fi/Bluetooth/PipeWire/Brightness/Night Light/Power sliders, Do Not Disturb, quiet hours, toast cards, OSD |
| **10** | `10-system-hardware` | **System & Hardware**: **Scy Intelligent Performance** hardware advisor & 4 tiers (`Max Quality`, `Balanced`, `Performance`, `Battery`), monitor refresh/VRR/HDR, PipeWire audio, NetworkManager, BlueZ, power/idle, storage |
| **11** | `11-lock-screen` | **Lock Screen**: Strictly isolated in-session Wayland lock screen (`lockLoginSync = false`), expressive clock layouts, dedicated lock wallpaper/blur, MPRIS media, notification privacy, PAM unlock feedback |
| **12** | `12-login` | **Login Experience**: Strictly isolated pre-session login greeter (`Preserve System DM`, `Scy-Shell SDDM`, `Scy-Shell Greetd`), user avatar cards, session picker, independent background & HiDPI scale |
| **13** | `13-productivity` | **Applications & Productivity**: **Scy Productivity Layer** (`=` AST calculator, unit converter, `?` web search, Quick Notes, Focus/Pomodoro timer), clipboard history, LucidShot region capture + Tesseract OCR, `wf-recorder`, offline AI & 3D Game Shelf |
| **14** | `14-profiles` | **Profiles & Presets**: **Scy Profile System** (`Balanced`, `Minimal`, `Productivity`, `Immersive`, `Gaming`, `Creative`, `Cinema` + custom user profiles with JSON export/import) |
| **15** | `15-advanced` | **Advanced Configuration**: Snapshot Time-Machine backups, Persistence Ledger inspector, System Doctor, D-Bus/Wayland conflict scanner, Hyprland `0.57+` 15s trial emitter, and the **2,026-Setting Parameter Vault** |

---

## 2. Transactional Live Preview & Scoped Resets

Every unified Studio section inherits `ScyStudioSectionBase`:
- **Live Preview Bar**: Stage changes, inspect real-time desktop updates, and click **Commit** or **Revert** (`scy-shell preview stage | diff | commit | revert`).
- **Scoped Resets**:
  - Reset a single control to its schema default (`scy-shell config reset <scy_id>`).
  - Reset an entire Studio section (`01`..`15`) without disturbing other sections (`scy-shell config reset-section <section-id>`).
  - Re-apply a clean profile baseline (`scy-shell profile apply balanced`).
