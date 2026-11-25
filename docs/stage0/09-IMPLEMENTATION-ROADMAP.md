# Stage 0 Deliverable 9 — 12-Phase Implementation Roadmap (Stage 1 Execution Plan)

> **GATE STATUS:** Execution of Phases 1–12 below is **HELD** pending user review and approval of Stage 0.

---

## Phase-by-Phase Engineering Plan

### Phase 1 — Upstream Verification & Working-Branch Baseline (COMPLETE IN STAGE 0)
- **Deliverables:** Untouched `sources/lucid-upstream` (`v1.21.1`) & `sources/mandara-upstream` (`v0.38.2`/`8a50e16a`), SHA-256 manifests, source snapshots, clean `scy-working` branches in `sources/lucid-working` & `sources/mandara-working`.
- **Verification Gate:** `git status --porcelain` empty on all 4 clones; SHA-256 manifests verified.

### Phase 2 — Scy-Shell Core Schema, Config Engine & IPC Bus (`scy-schema`, `scy-ipc`, `scy-daemon`)
- **Deliverables:**
  - Unified `~/.config/scy-shell/config.toml` parser/serializer supporting `[identity]`, `[active_providers]`, `[presentations]`, `[providers.lucid]` (all 643 keys), and `[providers.mandara]` (all 1,232 keys).
  - Bidirectional lossless sync adapters (`prefs.json` <-> `scy-daemon` <-> `mandara/config.toml`) with atomic temp-file-and-rename writes and timestamped backups.
  - Unix domain socket JSON-RPC server (`$XDG_RUNTIME_DIR/scy-shell.sock`) + `scy-shell` CLI (`ipc`, `get`, `set`, `provider`, `status`).
- **Automated Tests:** Round-trip serialization test asserting **all 1,875 catalogued settings** survive provider switches (`lucid -> mandara -> lucid`) with 0 dropped keys.

### Phase 3 — Pre-Activation Conflict Detector & Exclusive Resource Arbitrator (`scy-conflicts`)
- **Deliverables:**
  - Scanner for all 11 exclusive D-Bus, Wayland protocol, `/proc`, systemd DM, and keybind domains (detecting external `mako`, `dunst`, `swaync`, `waybar`, `ags`, `swww`, `hyprpaper`, `hypridle`, `swayidle`, `hyprpolkitagent` + internal Lucid/Mandara ownership).
  - Non-destructive Lucid (`ScyBridge.qml` + `Loader` gates in `lucid-working`) and Mandara (`hub.rs` & `surfaces.rs` gates in `mandara-working`) patches so inactive providers release exclusive claims cleanly.
- **Automated Tests:** Simulated D-Bus/process table conflict matrix tests verifying pre-flight block, auto-handoff, and clean rollback on failure.

### Phase 4 — Visual Identity Unification (Material 3 Expressive Primary Language + 19 Looks)
- **Deliverables:**
  - `scy-theme`: Unified Matugen HCT + Mandara OKLCH palette pipeline + 28-app SHA-256 tamper-safe external app-theming ledger (combining Lucid's templates and Mandara's 24-app ledger).
  - `scy-m3-expressive` Look in `mandara-working/crates/mandara-ui/src/looks/`: Google Sans typography, HCT dynamic tokens, M3 Expressive pill/cookie shapes, and spring curves harmonized with `Jelly.qml`.
  - Preservation of all 19 original Mandara `Looks` as selectable presentation modes.
- **Automated Tests:** Token parity tests verifying HCT <-> OKLCH contrast ratios (WCAG AA) and SHA-256 tamper-protection tests ensuring user-modified GTK/Kitty/Ghostty files are never overwritten without consent.

### Phase 5 — Core Shell Surfaces, Provider Switching & Cross-Engine Federation
- **Deliverables:**
  - Live provider switching for Bar (including Per-Monitor Hybrid + `ScyPluginPill.qml` inside Lucid Bar), Dock (shared `pinned-apps.json`), Quick Settings, Notifications & Toasts (separable broker + renderer!), OSD, and Wallpaper (`awww`/`LiveShell` + `Wallgen` 13-style integration + `shm_canvas`).
  - Launcher Query Federation: `!ai` (`mandara-agent`) and `@` (88 built-in + WASM plugins) inside Lucid's M3 Expressive Launcher.
- **Automated Tests:** IPC federation contract tests, toast routing tests, and pinned-apps bidirectional sync tests.

### Phase 6 — Desktop Canvas, Widgets (`Hybrid` Mode), Standalone Apps & Portals
- **Deliverables:**
  - Coexistence of Lucid `DesktopIcons.qml` (`~/Desktop`), Lucid's 25 M3 widgets (88 variants), and Mandara's GPUI/WASM desktop widgets via Wayland input-region bounding-box coordination.
  - Full integration of Lucid `Lumen` (+ safe `hyprland-portals.conf` `FileChooser` configuration), `Lens` (wired to `scy-shell ipc wallpaper set`), `Clock`, `LucidShot`, `LucidMoji`, `LucidKeys`, Mandara `Game Shelf`, `CalDAV/Mail` bridge to `lucidcalendar`/`LockAgenda`, and `Screen Time`.
- **Automated Tests:** Bounding-box collision resolver tests and portal configuration syntax tests.

### Phase 7 — Security Surfaces: Session Lock, Polkit, Keyring & Display Managers (SDDM / `greetd`)
- **Deliverables:**
  - Exclusive `ext-session-lock-v1` routing (`lucidlock` 6 presets vs `mandara-lock` 6 `AuthDesign`s), Polkit agent gate, and Display Manager manager supporting `Lucid SDDM` (`sync-sddm.sh`), `Mandara greetd` (`/etc/mandara/greeter.toml`), or `Preserve Existing`.
- **Automated Tests:** Single-lock-client invariant tests and SDDM/`greeter.toml` config generation tests.

### Phase 8 — Comprehensive Hyprland Coordinator (`scy-hypr`) & Multi-Compositor Preservation
- **Deliverables:**
  - `scy-hypr` modular config emitter supporting both Hyprland 0.55+ Lua (`~/.config/hypr/scy-shell/*.lua`) and `.conf`, Hyprland 0.57+ workspace compatibility, `lucid.solo` / `cursor_tilt` / `find_pointer`, lossless `keybinds.rs` span editing, pre-apply backup, directive validation, and 15-second auto-revert safety timer.
  - Unified Keybinding Engine implementing the Stage 0 Deliverable 5 table (61 Lucid binds + conflict-free Mandara chords + chord collision detector).
  - Preservation of Mandara's 10 non-Hyprland compositor backends.
- **Automated Tests:** Parser/emitter golden tests for Lua & `.conf`, keybind collision detection tests, and backup/rollback integrity tests.

### Phase 9 — Central Scy-Shell Studio (Material 3 Expressive Unified Settings GUI)
- **Deliverables:**
  - Complete QML Material 3 Expressive **Scy-Shell Studio** (`scy-shell/studio/`) organized into the 7 cohesive groups / 26 pages, rendering **100% of all 1,875 settings** from `04-settings-catalogue.json` + custom visual designers (Bar Module/Slot Builder, Lock/Greeter Preset Picker, Wallgen Previewer, Hyprland Monitor/Rule/Keybind Visual Editor, Conflict Inspector, Backup Time-Machine, and Config Doctor).
- **Automated Tests:** Schema coverage test verifying every single `scy_id` in `04-settings-catalogue.json` (`1,875 / 1,875`) is bound to a navigable, searchable Studio control!

### Phase 10 — Performance Optimization, Diagnostics & `scy-shell doctor`
- **Deliverables:**
  - Dormant-engine memory trimming, QML `Loader` lazy instantiation audit, `scy-shell doctor` health & dependency verifier, and `scripts/scy-bench.sh` reproducible benchmark suite.
- **Automated Tests:** Doctor diagnostic unit tests across mocked healthy/broken environments.

### Phase 11 — CachyOS / Arch Installer, PKGBUILD & Safe Session Setup
- **Deliverables:**
  - Interactive & non-interactive `install.sh` (`--dry-run`, `--profile`, `--uninstall`, `--restore-backup`), CachyOS/Arch `PKGBUILD`, `scy-shell.desktop` Wayland session entry, systemd user units (`scy-daemon.service`, `scy-lucid.service`, `scy-mandara.service`), and automatic migration from standalone Lucid or Mandara configs.
- **Automated Tests:** Dry-run & temporary-root (`DESTDIR` / fake `$HOME`) installer & uninstaller idempotency tests.

### Phase 12 — Full Verification Matrix, Documentation Suite & Release Packaging
- **Deliverables:**
  - Complete documentation (`README.md`, `INSTALL.md`, `ARCHITECTURE.md`, `FEATURE-MATRIX.md`, `SETTINGS-REFERENCE.md`, `HYPRLAND-GUIDE.md`, `TROUBLESHOOTING.md`, `CHANGELOG.md`, `LICENSES.md`).
  - Final Feature-Preservation & 1,875-Setting Verification Report + Release Archive (`scy-shell-v1.0.0.zip`) in workspace.
