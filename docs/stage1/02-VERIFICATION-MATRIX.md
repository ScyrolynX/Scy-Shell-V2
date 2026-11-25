# Scy-Shell v1.0.0 — Verification Matrix (Tier 1 Portable vs. Tier 2 Host/Compositor)

## Tier 1 — Portable Automated Test Suite (`make test-portable`)

Executed from any clean extracted release directory via:
```bash
./scripts/run-tests.sh
```
or:
```bash
PYTHONPATH=./src python3 -m unittest discover -s ./tests -p "test_phase*.py" -v
```

| Test Module | Phase(s) Covered | What Is Verified |
|---|---|---|
| `test_phase1_provenance_and_baseline.py` | **Phase 1** | `PROVENANCE.json` commit SHAs & `GPL-3.0-or-later`, `3,708` SHA-256 baseline entries (`920` Lucid + `2,788` Mandara), `patch -p1 -R` byte-for-byte upstream SHA-256 restoration on modified Lucid & Mandara files, and `scy-shell provenance` CLI |
| `test_phase2_schema_config_ipc.py` | **Phase 2** | `1,875` settings (`643` + `1,232`) search & lossless round-trip across full provider switching, pinned-app sync, backup/restore, and live Unix-socket IPC with native `bin/scy-shell-ipc` |
| `test_phase3_conflicts_and_gates.py` | **Phase 3 & 5** | External daemon clash detection (`mako`, `waybar`, `hyprpolkitagent`, `sddm`/`greetd`), gate drift repair, `ScyBridge.qml`, `ScyPluginPill.qml` bar mount, `Dock.qml` `!ai`/`@<plugin>` hooks, and Mandara `scy_gates.rs` |
| `test_phase4_visual_identity_and_themes.py` | **Phase 4** | WCAG AA contrast (`>= 7.0:1` text, `>= 4.5:1` accents) dark & light, SHA-256 user-edit protection across all `28` app targets, and `20` Mandara Looks (`LOOKS: [LookDef; 20]`) |
| `test_phases5_6_7_federation_desktop_security.py` | **Phases 5–7** | `89` plugin `@` search & persistence, `!ai` command execution, `13` Wallgen procedural SVG generators, hybrid desktop AABB widget resolver, XDG portals, ICS/GCal agenda bridge, `6+6` lock designs, and SDDM/Greetd staging |
| `test_phase8_hyprland_and_keybinds.py` | **Phase 8** | Hyprland directive allowlist, `67` unified compositor binds (`0` collisions), all `17` Stage 0 grouped & `22` QML `DesktopIcons.keyActions` slots (`19` bound + `3` user-bindable via `Prefs.desktopKeys`), `0` cross-scope overlaps, all `25` Mandara `default_keybinds()`, and `15s` auto-revert trial |
| `test_phase9_studio_1875_coverage.py` | **Phase 9** | Balanced QML delimiters across all `14` new/modified QML files, `38/38` `Settings.qml` page routes, and `engines/lucid/scy-schema/{settings,plugins,keybindings}_catalogue.json` |
| `test_phase10_cli_doctor_and_bench.py` | **Phase 10** | `scy-shell` CLI (`status`, `doctor --json`, `provider`, `config`, `wallgen`, `plugins`, `hypr keybinds --full`) and measured RSS/IPC benchmark checks |
| `test_phase11_installer_migration_and_packaging.py` | **Phase 11** | `install.sh --dry-run`, full isolated `--home` installation + standalone Lucid/Mandara migration, clean `--uninstall`, `PKGBUILD`, and systemd user units |
| `test_phase12_upstream_integrity_and_full_matrix.py` | **Phase 12** | Zero hard-coded workspace paths across code/scripts/tests/docs, `340/340` Rust `include_bytes!`/`include_str!` assets present, exhaustive `ShellConfig` literal check, `41` subsystems, and license notices |

---

## Tier 2 — Host Toolchain & Live CachyOS Wayland Suite (`make test-hardware`)

Executed via:
```bash
PYTHONPATH=./src python3 -m unittest discover -s ./tests/hardware -p "test_*.py" -v
./scripts/build-clean.sh
./scripts/verify-cachyos-live.sh
```

| Test / Script | Host Requirement | Behavior Outside CachyOS Wayland Host |
|---|---|---|
| `test_host_01_mandara_cargo_test_config_crate` | `cargo` + `rustc` | Explicitly reports `SKIPPED` when Rust toolchain is not installed |
| `test_host_02_mandara_workspace_release_check` | `cargo` + `rustc` + system Wayland/PipeWire/PAM libs | Explicitly reports `SKIPPED` when Rust toolchain is not installed |
| `test_host_03_lucid_qml_adapter_lint` | Qt6 `qmllint` | Explicitly reports `SKIPPED` when `qmllint` is not installed |
| `test_host_04_live_hyprland_layer_surfaces_and_quickshell_ipc` | Active `WAYLAND_DISPLAY` + `HYPRLAND_INSTANCE_SIGNATURE` + `quickshell` | Explicitly reports `SKIPPED` outside a live Wayland/Hyprland session |
