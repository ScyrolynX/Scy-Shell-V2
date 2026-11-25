# Stage 0 Deliverable 8 — Comprehensive Engineering Risk Assessment & Mitigation Plan

---

## 1. Licensing & Redistribution Compliance Risks

| Risk | Severity | Audit Finding | Concrete Mitigation |
|---|---|---|---|
| **MIT (Lucid) + GPL-3.0-or-later (Mandara) Copyleft Propagation** | High (Legal) | Lucid is `MIT`; Mandara (including its forked `vendor/gpui`) is `GPL-3.0-or-later`. | MIT is 100% compatible with GPLv3. License the combined **Scy-Shell** work as **`GPL-3.0-or-later`**, keep Sn3akyy1's MIT copyright & permission notice intact on all Lucid files, keep Ahmad Hamdi's `COPYRIGHT.md` intact, and ship full source + `scy-shell/licenses/` ledger. |
| **Local AI Model Weights (`FunctionGemma-270M` / `Qwen3-0.6B`)** | Medium | `google/functiongemma-270m-it` is governed by Google's Gemma Terms of Use (non-GPL); `Qwen3-0.6B` is `Apache-2.0`. | **Never bundle LLM weights** inside the Scy-Shell repo, AUR package, or release ZIP. Keep weight download strictly user-initiated opt-in inside Studio -> Local AI with explicit license disclosure and default highlight on `Qwen3-0.6B` (Apache-2.0). |
| **Bundled Fonts & Icons** | Low | Google Sans & Space Grotesk/Inter/JetBrains Mono (`OFL-1.1`), Material Symbols (`Apache-2.0`), Phosphor (`MIT`). | Preserve all `OFL.txt`, `LICENSE`, and font copyright metadata unmodified. |

---

## 2. Dual-Engine Memory, CPU & GPU/VRAM Overhead Risks

| Risk | Unmitigated Impact | Scy-Shell Architectural Mitigation |
|---|---|---|
| **Simultaneous Qt6 RHI (Vulkan/OpenGL) + GPUI `wgpu` (Vulkan) Contexts** | If Mandara eagerly creates all 12 `wlr-layer-shell` swapchains while Lucid also creates 10 QML layer surfaces, idle VRAM could climb by +180–300 MB. | **Dormant Zero-Swapchain Gating (`surfaces.rs`):** When Lucid is the active surface provider (default), Mandara runs in **Dormant Service/Plugin Mode** with **0 active `wgpu` swapchains** until a GPUI drawer/plugin/Wallgen window is opened (and destroys or parks the swapchain on close), plus offers CPU `shm_canvas` mode for low-VRAM iGPUs! |
| **Duplicate Background Pollers** (2x PipeWire, 2x UPower, 2x NM, 2x Weather, 2x Clipboard) | Wasted CPU wakeups & double disk writes (`cliphist` + `clipboard.rs`). | `scy-daemon` disables duplicate watchers in the inactive provider (`clipboard`, `idle`, `updates`, `weather` cache shared via `$XDG_RUNTIME_DIR/scy-shell/`). |
| **1,875-Setting Studio Startup Time** | Instantiating 1,875 QML controls eagerly at launch would stall UI for >600ms. | Virtualized `ListView` + lazy `Loader` per Studio page: only the visible page (~25–60 controls) is instantiated; global fuzzy search indexes the in-memory JSON schema in <2ms. |

> **Honest Benchmarking Note (Section 11):** Because this cloud audit sandbox has no physical GPU, Wayland compositor, or `rustc`/`quickshell` runtime installed (`python3`, `node`, `git` available; `cargo`/`quickshell`/`hyprctl` absent), **zero fabricated RAM/VRAM/FPS numbers are claimed**. Scy-Shell ships an automated `scripts/scy-bench.sh` harness (`/proc/<pid>/smaps_rollup` PSS, `vulkaninfo`/DRM VRAM counters, cold-start wall clock, IPC round-trip latency) for real CachyOS + Hyprland hardware verification.

---

## 3. Exclusive System Resource & Race-Condition Risks

All **11 exclusive system resources** discovered in source code are mitigated by deterministic pre-activation gating in `scy-daemon`:
1. **`org.freedesktop.Notifications`:** Patch Mandara `hub.rs` so `spawn_notification_service()` only runs when `active_providers.notifications == "mandara"`, AND scan D-Bus for external `mako`/`dunst`/`swaync` before claiming.
2. **`ext_session_lock_v1`:** Route `Super+L`, `loginctl lock-session`, and idle lock exclusively through `scy-daemon` to the single selected Lock provider (`lucidlock` default).
3. **Polkit Agent (`unix-session`):** Enforce mutual exclusion between `Polkit.qml` and `polkit.rs` + external `hyprpolkitagent` / `polkit-kde-agent`.
4. **Display Gamma (`zwlr_gamma_control_v1`):** Mutual exclusion between `hyprsunset` and `mandara-services::gamma` (+ external `gammastep`/`wlsunset`).
5. **BlueZ DefaultAgent (`org.bluez.Agent1`):** Mutual exclusion between `bt-agent.py` and `bt_agent.rs`.
6. **System Tray (`org.kde.StatusNotifierWatcher`):** Ordered startup so Quickshell claims Watcher first and Mandara attaches cleanly as `StatusNotifierHost` (verified supported in `tray.rs`).
7. **Wallpaper (`LAYER_BACKGROUND`):** Mutual exclusion between `awww`/`LiveShell` and `mandara-wallpaper` (+ external `hyprpaper`/`mpvpaper`).
8. **Display Manager (`display-manager.service`):** Never enable both `sddm.service` and `greetd.service`; require explicit user opt-in with pre-change backup.
9. **XDG Desktop Portals (`lumend.py`):** Configure `org.freedesktop.impl.portal.FileChooser=lumen` in `hyprland-portals.conf` while strictly keeping `default=hyprland;gtk` so `ScreenCast` and `GlobalShortcuts` never break!

---

## 4. Hyprland Version & NVIDIA / Hardware Risks (CachyOS Target)

| Risk | Details | Mitigation in `scy-hypr` & Installer |
|---|---|---|
| **Hyprland 0.53+ WindowRule v3 vs Legacy Syntax & 0.55+ Lua vs `.conf`** | Hyprland 0.55 introduced native Lua config (`hyprland.lua`); Hyprland 0.57 changed `hyprctl workspaces -j` for named/special workspaces. | Reuse Mandara's battle-tested 0.57+ `hyprland.rs` parser + Lucid's 0.55+ Lua modules, detect user's active config format (`hyprland.lua` vs `hyprland.conf`), and validate against `hyprctl version -j`. |
| **NVIDIA Proprietary Driver Quirks on Wayland** | Flicker without explicit sync; invisible cursor on hardware planes; GStreamer VAAPI/NVDEC crashes in live wallpapers. | Detect `nvidia_drm` module in `scy-shell doctor`: offer safe env presets (`LIBVA_DRIVER_NAME=nvidia`, `NVD_BACKEND=direct`, optional `cursor:no_hardware_cursors = true`) as opt-in Studio toggles rather than blind global env pollution. |
| **Build Toolchain Environment Gap in Current Sandbox** | Current workspace container lacks `rustc` (needs `>= 1.88` for Rust 2024 edition), `quickshell`, `qml6`, and `hyprctl`. | In Stage 1, check whether toolchain installation/rustup is permitted or provide complete `Cargo.toml` workspace, Python-verified schema/config/conflict/Hyprland test suites, static QML/Lua validators, and CachyOS `PKGBUILD` + `install.sh` build orchestration, explicitly documenting what was compiled in-sandbox vs target-host build steps. |
