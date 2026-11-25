# Settings Architecture & 2,026-Parameter Reference

## 1. Unified Catalogue Breakdown (`schema/settings_catalogue.json`)

Scy-Shell `v2.0.0` (`schema_version = 2`) unifies **2,026 typed, range-validated settings** with zero generic `config_field` placeholders:

- **Scy-Shell Native Settings (`scy.*`)**: `151` settings (Design Tokens, Dynamic Island, Dock Studio extensions, Layout Composer, Component Lab, Performance Tiers, Isolated Lock & Login, Productivity, Profiles).
- **Lucid QML Runtime Settings (`scy.providers.lucid.*`)**: `643` settings (`prefs`, `hypr`, `glass`, `widget_opts`, `lock_widgets`, `sddm`, `moji`, `lumen`, `lens`, `clock_app`, `shot_state`, `keys`).
- **Mandara GPUI/WASM Runtime Settings (`scy.providers.mandara.*`)**: `1,232` settings (`config.toml`, `wallgen.toml`, `staged-greeter.toml`).

### Distribution Across the 15 Studio Sections

| Section | Count |
|---|---:|
| `01-personalization` | 209 |
| `02-desktop` | 211 |
| `03-dock` | 120 |
| `04-visual-effects` | 120 |
| `05-layout` | 20 |
| `06-widgets` | 64 |
| `07-windows` | 137 |
| `08-interactions` | 38 |
| `09-notifications` | 118 |
| `10-system-hardware` | 138 |
| `11-lock-screen` | 81 |
| `12-login` | 156 |
| `13-productivity` | 389 |
| `14-profiles` | 4 |
| `15-advanced` | 221 |
| **Total** | **2,026** |

---

## 2. Persistence & Login-Safety Architecture

1. **Canonical Store**: `~/.config/scy-shell/config.toml` (with automatic shadow copy `~/.config/scy-shell/config.toml.last-good`).
2. **Design Token Broadcast**: `~/.config/scy-shell/design-tokens.json` + `~/.local/state/scy-shell/live_values.json` + `~/.local/state/scy-shell/state.json` watched live via `Quickshell.Io.FileView`.
3. **SHA-256 Persistence Ledger (`~/.local/state/scy-shell/persistence-ledger.json`)**:
   - Tracks cryptographic hashes and per-key snapshots of native runtime files (`prefs.json`, `blur.json`, `mandara/config.toml`, `wallgen.toml`).
   - On login/daemon startup, `reconcile_live_engine_stores()` detects any changes written directly by QML or Rust during the previous session and merges them into `config.toml` *before* `flush_all()` runs — permanently preventing login overwrites.
4. **Special Sentinel Preservation**:
   - `scy.providers.lucid.prefs.surfaceDarkness` (`-1` = Auto, `0.0 .. 1.0` manual) and `scy.providers.lucid.prefs.surfaceTint` (`-1` = Auto, `0.0 .. 1.0` manual) preserve `-1` across Python validation, TOML/JSON serialization, and Studio UI controls.

---

## 3. Querying & Modifying Settings from Zsh / CLI

```zsh
# Search across all 2,026 settings (optionally filtered to one Studio section)
scy-shell config search blur --section 04-visual-effects

# Read a setting
scy-shell config get scy.dock.mode

# Write a validated setting (immediately synced & persisted)
scy-shell config set scy.dock.icon_size 44
scy-shell config set scy.effects.material_preset liquid-crystal

# Reset a single setting or an entire Studio section
scy-shell config reset scy.dock.icon_size
scy-shell config reset-section 04-visual-effects
```
