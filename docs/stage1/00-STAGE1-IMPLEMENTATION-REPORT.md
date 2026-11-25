# Scy-Shell v1.0.0 — Stage 1 Complete Implementation Report (Phases 1–12)

## 1. Executive Summary

**Scy-Shell (`v1.0.0`)** unifies **Lucid** (Quickshell QML Wayland Shell, upstream commit `15f13429bc59b4a97223bcfe5592735cb1eb92be`) and **Mandara** (Rust GPUI Desktop Shell, upstream commit `8a50e16af3a59cd8745df36e5656d825e5284641`) into a cohesive **Material 3 Expressive** desktop shell for **Hyprland (`0.55+` Lua & `.conf`)** on **CachyOS / Arch Linux**.

Every requirement from Stage 0 (`docs/stage0/00`–`09`) is implemented across **all 12 phases (Phases 1–12)** with zero dropped features, zero hard-coded build-host paths, reversible upstream patches, and strict separation between portable automated verification and host-hardware/compositor verification.

---

## 2. Phase-by-Phase Implementation Matrix (Phases 1–12)

| Phase | Scope | Primary Artifacts | Verification |
|---|---|---|---|
| **Phase 1** | **Cryptographic Provenance, SHA-256 Baseline & Reversible Working-Tree Adapters** | `provenance/PROVENANCE.json`, `provenance/lucid-v1.21.1-sha256sums.txt` (`920` files), `provenance/mandara-v0.38.2-sha256sums.txt` (`2,788` files), `adapters/{lucid,mandara}/*-scy-adapter.patch`, `src/scy_core/provenance.py`, `scy-shell provenance` | `tests/test_phase1_provenance_and_baseline.py` verifies `3,708` SHA-256 digests and runs live `patch -p1 -R` reconstruction in a temporary directory |
| **Phase 2** | **Unified 1,875-Setting Schema, Two-Way Sync Store & Sub-ms C11 IPC Bus** | `schema/settings_catalogue.json` (`643` Lucid + `1,232` Mandara = `1,875`), `src/scy_core/{paths,schema,config_store,ipc_bus}.py`, `src/c/scy_shell_ipc.c` (`bin/scy-shell-ipc`) | `tests/test_phase2_schema_config_ipc.py` tests round-trip persistence of all `1,875` settings across full provider switching + live Unix socket IPC |
| **Phase 3** | **11-Resource Conflict Prevention & Zero-Swapchain Engine Gating** | `src/scy_core/conflicts.py`, `engines/lucid/ScyBridge.qml`, `engines/lucid/shell.qml`, `engines/mandara/crates/mandara-config/src/scy_gates.rs`, `hub.rs`, `surfaces.rs` | `tests/test_phase3_conflicts_and_gates.py` tests external daemon detection (`mako`, `waybar`, `sddm`/`greetd`), gate drift repair, and dormant swapchain suppression |
| **Phase 4** | **Material 3 Expressive Identity, 20 Looks & Tamper-Safe 28-App Theming** | `src/scy_core/theme_engine.py`, `engines/mandara/crates/mandara-config/src/looks.rs` (`LOOKS: [LookDef; 20]` adding `scy-m3-expressive`) | `tests/test_phase4_visual_identity_and_themes.py` verifies WCAG AA contrast (`>= 4.5:1` / `>= 7.0:1`) and SHA-256 user-edit protection across all `28` app targets |
| **Phase 5** | **89-Plugin Federation, Bar Pill Mount, `!ai` & `@<plugin>` Launcher & 13-Style Wallgen** | `src/scy_core/federation.py`, `schema/plugins_catalogue.json` (`89` plugins), `engines/lucid/lucidbar/ScyPluginPill.qml` (mounted in `shell.qml`), `engines/lucid/luciddocks/Dock.qml` (`!ai` & `@<plugin>` live rows) | `tests/test_phases5_6_7_federation_desktop_security.py` & `tests/test_phase3_conflicts_and_gates.py` |
| **Phase 6** | **Hybrid Desktop Canvas AABB Resolver, XDG Portal Routing & Agenda Bridge** | `src/scy_core/desktop_canvas.py` | `tests/test_phases5_6_7_federation_desktop_security.py` verifies non-overlapping widget placement, `xdg-desktop-portal` routing, and shared ICS/Google Calendar JSON bridge |
| **Phase 7** | **Single-Owner PAM Session Lock (`6+6` Designs) & SDDM / Greetd Pre-Auth Staging** | `src/scy_core/security_preauth.py` | `tests/test_phases5_6_7_federation_desktop_security.py` verifies all `6` Lucid presets, `6` Mandara auth designs, and non-destructive SDDM/Greetd staging |
| **Phase 8** | **Hyprland `0.55+` Lua / `.conf` Coordinator, 15s Safe Trial & Complete Shortcut Ledger** | `src/scy_core/hypr_coordinator.py`, `schema/lucid_keybinds_default.json`, `schema/keybindings_catalogue.json` | `tests/test_phase8_hyprland_and_keybinds.py` verifies directive allowlist, `15s` auto-revert trial, `67` compositor binds, `17`/`22` `DesktopIcons.qml` shortcuts, and `25` Mandara binds |
| **Phase 9** | **Unified 38-Page Studio (`30` Lucid + `8` Scy-Shell Pages) Exposing All 1,875 Settings** | `engines/lucid/Prefs.qml`, `engines/lucid/lucidprefs/{Settings,Scy*Page}.qml`, `engines/lucid/scy-schema/*.json` | `tests/test_phase9_studio_1875_coverage.py` verifies QML delimiter balance, `38/38` page routing, and live `1,875`-setting Vault binding |
| **Phase 10** | **`scy-shell` CLI, Health Doctor & Measured Runtime Metrics** | `bin/scy-shell`, `src/scy_core/doctor.py`, `docs/stage1/benchmark-results.json` | `tests/test_phase10_cli_doctor_and_bench.py` verifies CLI subcommands, dormant-GPU reporting, and measured daemon RSS / C11 IPC latency |
| **Phase 11** | **Non-Destructive Installer, Standalone Config Migrator, Systemd Units & Arch `PKGBUILD`** | `install.sh`, `src/scy_core/migrator.py`, `packaging/arch/PKGBUILD`, `packaging/systemd/scy-*.service` | `tests/test_phase11_installer_migration_and_packaging.py` tests `--dry-run`, full isolated `$HOME` install + migration, and clean `--uninstall` |
| **Phase 12** | **Clean-Extract Portability, 340-Asset Rust Audit & Tier 1 / Tier 2 Verification Harness** | `Makefile`, `scripts/{run-tests,build-clean,verify-cachyos-live}.sh`, `tests/hardware/test_cachyos_host_integration.py` | `tests/test_phase12_upstream_integrity_and_full_matrix.py` enforces zero hard-coded host paths and `340/340` Rust `include_bytes!`/`include_str!` integrity |

---

## 3. Complete Shortcut & Keybinding Accounting (`103` Original Upstream Shortcuts -> `0` Collisions)

Stage 0 Deliverable 5 (`docs/stage0/05-KEYBINDING-INVENTORY.md`) inventoried **103** original shortcuts across both upstream projects: **61** Lucid Hyprland compositor binds + **17** grouped Lucid `DesktopIcons.qml` shortcuts + **25** Mandara `compositor.rs::default_keybinds()`. Scy-Shell accounts for **100%** of them across their exact execution scopes (`scy-shell hypr keybinds --full`):

### 3.1 Global Hyprland Compositor Scope (`67` Unified Active Chords, `0` Collisions)
- **61 Original Lucid Binds Preserved (`engines/lucid/support/hypr/keybinds.json`):** Every workspace, window management, scratchpad (`SUPER + SHIFT + S`), OCR (`SUPER + SHIFT + T`), Region Snap (`Print` / `SUPER + D`), Fullscreen Shot (`SUPER + Print`), Overview (`SUPER + Tab`), Wallpaper (`SUPER + B`), Session (`SUPER + Escape`), Lock (`SUPER + L`), Studio (`SUPER + I`), and hardware `XF86*` bind is preserved intact. Shared actions route dynamically through `scy-shell-ipc` (`SHARED_CMD_REWRITES`) so switching active providers in Studio works without editing Hyprland configs.
- **6 Conflict-Free Mandara Superpower Chords Added:**
  1. `SUPER + SHIFT + A` -> `scy-shell-ipc agent toggle` (Local AI Command Agent)
  2. `SUPER + SHIFT + B` -> `scy-shell-ipc sidebar toggle` (Mandara Edge Sidebar; preserves `SUPER + B` Wallpaper)
  3. `SUPER + ALT + T` -> `scy-shell-ipc look picker` (20-Look Switcher; resolves upstream `SUPER + SHIFT + T` collision with Lucid OCR)
  4. `SUPER + SHIFT + P` -> `scy-shell-ipc plugins` (89 Built-in & WASM Plugins Drawer)
  5. `SUPER + SHIFT + G` -> `scy-shell-ipc games` (3D Game Shelf)
  6. `SUPER + SHIFT + W` -> `scy-shell-ipc wallgen` (13-Style Procedural Wallgen)
- **All 25 Mandara `compositor.rs::default_keybinds()` Accounted For:** `6` exposed on the conflict-free chords above + `19` mapped losslessly onto equivalent unified `scy-shell-ipc` & single-owner `XF86*` hardware chords (`schema/keybindings_catalogue.json` -> `mandara_25_default_keybinds_accounting`).

### 3.2 Desktop Canvas Focus Scope (`DesktopIcons.qml` + `luciddesktop/IconBoard.qml`)
Desktop icon shortcuts only fire when the desktop icon canvas holds keyboard focus, so they never intercept global `SUPER` compositor chords (`cross_scope_compositor_overlaps == []`):
- **All 17 Stage 0 Grouped Shortcuts Preserved (`stage0_17_desktop_icons_shortcuts`):** `Return` (Open), `space` (Quick Look), `F2` (Rename), `Delete` (Trash), `SHIFT + Delete` (Delete Permanently), `CTRL + C` (Copy), `CTRL + X` (Cut), `CTRL + V` (Paste), `CTRL + D` (Duplicate), `CTRL + A` (Select All), `CTRL + SHIFT + N` (New Folder), `CTRL + Z` (Undo), `Menu / SHIFT + F10` (Context Menu), `Arrow Keys` (Grid/Quick-Look step), `SHIFT + Arrows` (Range select), `Home / End` (First/Last icon), and `Escape` (Exit Edit / Close Info & Quick Look / Deselect).
- **Full 22 Remappable QML `DesktopIcons.keyActions` Slots (`desktop_icons_qml_key_actions`):** Includes all **19** default-bound actions (explicitly tracking `ALT + Return` Get Info, `CTRL + SHIFT + C` Copy Path, `CTRL + I` Invert Selection, `CTRL + ALT + N` New Text File, `CTRL + ALT + T` Open in Terminal, `CTRL + H` Show Hidden Files, and `F5` Refresh in addition to the 12 core file chords above) plus **3** user-bindable slots (`compress`, `arrange`, `hideIcons`) customizable via `Prefs.desktopKeys` (`scy.providers.lucid.prefs.desktopKeys`), with live intra-scope clash and cross-scope compositor collision checks in `ScyHyprCoordinator.build_complete_shortcut_ledger()`.

---

## 4. Verification Architecture: Tier 1 (Portable) vs. Tier 2 (Host / Compositor)

Scy-Shell strictly separates portable automated verification from host-toolchain and live Wayland/Hyprland verification:

1. **Tier 1 — Portable Automated Test Suite (`make test-portable` / `tests/test_phase*.py`):**
   - Runs from **any clean extracted release directory** using only Python 3.11+ and POSIX tools (`patch`, `sh`), with isolated temporary `$HOME` directories and zero hard-coded build-host path dependencies.
   - Covers Phases 1–12: SHA-256 upstream provenance + `patch -p1 -R` reversibility, `1,875` settings round-trip, C11 Unix-socket IPC, 11-domain conflict resolution, WCAG AA M3 token math + 28-app SHA-256 tamper protection, 89-plugin & `!ai` federation, 13-style Wallgen SVG generation, hybrid widget AABB layout, `67 + 17/22 + 25` shortcut accounting, 38-page QML Studio structural/routing checks, `340/340` Rust compile-time asset verification, and full `--home` isolated install/migrate/uninstall.
2. **Tier 2 — Host Toolchain & Live CachyOS Wayland Suite (`make test-hardware`, `scripts/build-clean.sh`, `scripts/verify-cachyos-live.sh`):**
   - Executes native Rust compilation (`cargo test --locked -p mandara-config`, `cargo build --release --locked`), Qt6 `qmllint` checks, and live Hyprland (`hyprctl layers`, `qs ipc show`) checks when run on a CachyOS / Arch Linux Wayland host.
   - Explicitly reports **`SKIPPED`** (never counted as fake passes) when `cargo`/`rustc`, `qmllint`/`quickshell`, or `WAYLAND_DISPLAY` / `HYPRLAND_INSTANCE_SIGNATURE` are absent in a headless build container.
