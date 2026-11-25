# Changelog

## v2.0.0 — "Ultimate Unified Desktop Evolution" (2026-11-24)

### Architectural Unification & Studio Overhaul
- **Unified 15-Section Scy-Shell Studio**: Replaced `v1.0.0`'s divided provider-centric settings tabs (`ScyProvidersPage` default landing) with 15 intent-driven sections (`01 Personalization` through `15 Advanced Configuration`) built on `ScyStudioSectionBase.qml`.
- **Expanded 2,026-Setting Schema (`schema_version = 2`)**: Preserved all `1,875` baseline engine settings (`643` Lucid + `1,232` Mandara) with zero feature loss and added `151` first-class `scy.*` settings wired to live runtime behavior.
- **Centralized `ScyDesignTokens` Singleton**: Added `ScyDesignTokens.qml` + `~/.config/scy-shell/design-tokens.json` broadcasting unified OKLCH/M3 palettes, glass blur/refraction/tint, corner-radius scale, typography, and spring physics across all surfaces.
- **Transactional Live Preview & Scoped Resets**: Added `stage_preview`, `preview_diff`, `commit_preview`, `revert_preview`, per-setting reset, per-section reset (`01`..`15`), and profile reset.
- **Lazy Studio Tab Loading**: Updated `Settings.qml` `paneLoader.active` to load tabs lazily (`ScyBridge.lazyStudioTabs`), eliminating offscreen tab layout stalls during window resize.

### Mandatory Bug Fixes (`v1.0.0` -> `v2.0.0`)
1. **Dock Switching Fixed**: Wired `scy-shell dock <lucid|mandara|island|notch|split|rail|disabled>`, `ScyBridge.owns("dock")` in `Prefs.qml` & `Dock.qml`, `IpcHandler { target: "dock" }`, and `ScyGates::dock_enabled()` in Mandara `crates/mandara-ui/src/plugins/dock/mod.rs` so dock switching takes effect in a single click and persists across restarts.
2. **Duplicate Docks Eliminated**: Enforced single-owner surface gating in both QML and Rust, added `bin/scy-launch-engine` kernel `flock` single-instance engine guard in `systemd --user` services, and added non-destructive Hyprland `exec-once` autostart deduplication (`ProcessSupervisor.deduplicate_hyprland_autostart`) without broad `killall`/`pkill`.
3. **Settings Disappearing After Re-Login Fixed**: Implemented `persistence-ledger.json` SHA-256 reconciliation (`reconcile_live_engine_stores()`) before daemon/session flush so live QML/Rust edits are absorbed on login rather than overwritten by stale `config.toml`; added `.last-good` shadow recovery, `v1 -> v2` backup-protected migration, and `persistence-errors.log`. Fixed `staged-sddm-theme.conf` flush overwriting explicit `sddm.*` keys and `set_provider("dock")` overwriting dock tuning keys.
4. **Divided Studio Unified**: Consolidated all navigation into the 15 unified Studio sections while keeping specialized interactive sub-workbenches deep-linkable (`"hidden": true`).
5. **Lock Screen (`11`) & Login (`12`) Separated**: Changed `lockLoginSync` default to `false`, gated `launch-shell.sh`'s `sync-sddm.sh` behind explicit opt-in, separated Section `11` (`scy.lock.*`) and Section `12` (`scy.login.*` / `login-greeter.json`), and enforced `assert_no_credentials` so passwords are never stored in shell configs.

### New Scy-Shell Native Subsystems
- **Scy Dynamic Island (`lucidbar/ScyDynamicIsland.qml`)**: Adaptive central bar capsule for workspace state, MPRIS media, Focus/Pomodoro countdowns, and alerts.
- **Scy Layout Composer & Component Laboratory (`layout_and_lab.py`)**: 5 spatial desktop presets and per-component material overrides.
- **Scy Profile System (`profiles.py`)**: 7 built-in complete desktop profiles (`Balanced`, `Minimal`, `Productivity`, `Immersive`, `Gaming`, `Creative`, `Cinema`) + custom profile creation, duplication, JSON export, and import.
- **Scy Productivity Engine & Intelligent Performance (`native_services.py`)**: Safe AST calculator, unit converter, `?` web search, Quick Notes, Focus Timer, Control Center backend, and 4 hardware-aware performance tiers.
- **Hyprland `0.57+` & Zsh Integration**: Updated `hypr_coordinator.py` to emit Hyprland `0.57+` v2 `layerrule = blur on, match:namespace ...` syntax; added `packaging/zsh/_scy-shell`, `uninstall.sh`, and upgraded `install.sh` (`--check-env`, automatic pre-install backup manifest).

---

## v1.0.0 — Baseline Release
- Initial baseline packaging of Lucid 2 (`v1.21.1`) + Mandara (`v0.38.2`) with `1,875`-setting catalogue and Unix-socket C11 IPC client.
