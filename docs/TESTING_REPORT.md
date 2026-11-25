# Testing & Verification Report (`v2.0.0`)

In strict accordance with Scy-Shell engineering standards, this report distinguishes **executed automated tests**, **static compiler/linter checks**, and **skipped host-hardware tests** (never claiming unexecuted GUI/compositor tests ran inside a headless build container).

---

## 1. Summary Matrix

| Category | Tool / Suite | Result | Details |
|---|---|---|---|
| **Qt6 QML Static Analysis** | `scripts/lint-qml.sh` (`qmllint 6.8.2 --bare -W 0`) | **PASS (`28/28` files, `0` warnings, `0` errors)** | Verified `ScyDesignTokens.qml`, `ScyBridge.qml`, `ScyDynamicIsland.qml`, `ScyPluginPill.qml`, `ScyStudioSectionBase.qml`, all 15 `ScySec01..ScySec15.qml` pages, `ScyVaultPage.qml`, and all sub-workbenches |
| **C11 IPC Client Build** | `gcc -O3 -Wall -Wextra -Werror -std=c11` | **PASS (`0` warnings)** | Compiled `csrc/scy_ipc_client.c` -> `bin/scy-shell-ipc` and verified live Unix-socket roundtrip |
| **Python Bytecode & Syntax** | `python3 -m compileall` + `py_compile` | **PASS (`100%`)** | Verified all `src/scy_core/*.py` modules and `bin/{scy-shell,scy-daemon,scy-launch-engine}` |
| **Shell Script Syntax** | `bash -n` | **PASS (`100%`)** | Verified `install.sh`, `uninstall.sh`, and `scripts/lint-qml.sh` |
| **Upstream & Reversible Patch Provenance** | `scy-shell provenance` (`SHA-256` + `patch -p1 -R`) | **PASS (`ok: true`, `3,708` manifest files, `0` mismatches)** | Verified exact reverse-patching of all 6 modified Lucid files and all 6 modified Mandara Rust files back to upstream SHA-256 digests |
| **Automated Python Integration & Regression Suite** | `python3 -m unittest discover -s tests -v` | **PASS (`50` passed, `0` failed, `0` errors, `4` skipped)** | Executed across 12 test suites (`test_phase1` .. `test_phase14_v2_evolution_and_regressions`) |

---

## 2. Mandatory Bug-Fix Regressions Verified (`tests/test_phase14_v2_evolution_and_regressions.py`)

1. **Bug #1 — Dock Switching**: Automated test verified single-action switching (`lucid` <-> `mandara` <-> `split` <-> `disabled`), live `[scy_gates]` + `Prefs.dockEnabled` synchronization, QML `Dock.qml` `ScyBridge.owns("dock")` binding, Rust `plugins/dock/mod.rs` `cfg.scy_gates.dock_enabled()` gate, and survival across restart. **PASSED.**
2. **Bug #2 — Duplicate Docks & Competing Startups**: Automated test spawned a live background process holding kernel `flock` on `engine-lucid.lock`, launched a concurrent `scy-launch-engine lucid`, verified clean `exit 0` single-instance rejection without `killall`/`pkill`, and verified non-destructive `hyprland.conf` `exec-once` deduplication with backup. **PASSED.**
3. **Bug #3 — Settings Disappearing After Re-Login & Corruption**:
   - Full `2,026`-setting roundtrip test (`test_phase2`) verified persistence across `config.toml` and all 14 native runtime stores across provider switches. **PASSED.**
   - Simulated live in-session QML edits to `prefs.json` (`themeColour`, `dockBottomMargin`) followed by next-login startup -> verified `persistence-ledger.json` absorbed user edits instead of overwriting them. **PASSED.**
   - Simulated power-loss corruption (`<<<CORRUPTED TOML`) -> verified automatic recovery from `config.toml.last-good` and logging to `persistence-errors.log`. **PASSED.**
4. **Bug #4 — Divided Studio**: Verified `Settings.qml` opens on `"01-personalization"`, `Prefs.qml` exposes all 15 unified Studio sections (`53` total addressable routes mapped 1-to-1 to existing QML files), lazy `paneLoader.active`, transactional Live Preview (`stage` -> `diff` -> `revert` / `commit`), and setting/section resets. **PASSED.**
5. **Bug #5 — Lock Screen (`11`) vs Login (`12`) Separation**: Verified `lockLoginSync == False` default, `launch-shell.sh` opt-in guard, bi-directional non-interference between Section `11` (`scy.lock.*`, `lockBlur`) and Section `12` (`scy.login.*`), and rejection of password fields (`assert_no_credentials`). **PASSED.**

---

## 3. Skipped Host-Hardware / Live-Compositor Tests (`tests/hardware/test_cachyos_host_integration.py`)

The following **4** tests were intentionally **skipped** inside the headless build sandbox (`1.94 GiB` RAM, no GPU/Wayland display, no local `rustc` binary) and are ready to run directly on a target CachyOS + Hyprland `0.57+` machine:

1. `test_host_01_native_rust_837_unit_tests_config_theme_i18n_version` — Requires host `cargo` + `rustc`.
2. `test_host_02_native_rust_release_fat_lto_binary_mandara_delta` — Requires host `cargo` + `rustc`.
3. `test_host_04_mandara_app_full_release_binary` — Requires `>= 4.0 GiB` RAM + `cargo` to link `gpui` + `wasmtime` + `tract-core`.
4. `test_host_05_live_layer_surfaces_ipc_arbitration_and_provider_switching` — Requires active `WAYLAND_DISPLAY` + `HYPRLAND_INSTANCE_SIGNATURE` + running `quickshell` session.

To execute the full suite including host hardware tests on CachyOS:
```zsh
PYTHONPATH=src python3 -m unittest discover -s tests -v
```
