# Scy-Shell v2.0.0 — Ultimate Unified Desktop Evolution

**Scy-Shell `v2.0.0`** is a unified, modern Wayland desktop environment engineered specifically for **CachyOS Linux**, **Hyprland `0.57+`**, **Quickshell (Qt6 QML)**, and **Zsh**.

Rather than exposing separate shells or competing configuration apps, Scy-Shell fuses its expressive frosted-glass QML shell surfaces, hardware-accelerated Rust GPUI companion capabilities, 89 built-in/WASM extensions, and centralized OKLCH + Material 3 Expressive design system (`ScyDesignTokens`) into **one cohesive Scy-Shell desktop product** governed by a single **15-Section Studio** and **2,026-setting lossless persistence engine**.

---

## Highlights of v2.0.0

1. **Unified 15-Section Scy-Shell Studio (`01 Personalization` .. `15 Advanced Configuration`)**
   - Replaces the divided `v1.0.0` provider-centric settings tabs with **15 user-intent Studio sections**.
   - Every section includes real-time updates, **Transactional Live Preview (`Apply` / `Revert`)**, per-setting reset, per-section reset, and deep-linked access to specialized visual workbenches and the **2,026-setting Advanced Parameter Vault** (`151` Scy-Shell native + `643` Lucid + `1,232` Mandara settings — zero silent feature loss).
   - Lazy `Loader` tab activation keeps Studio memory and resize latency low even on high-refresh displays.

2. **Single-Owner Dock Architecture & Dock Studio (`03 Dock Studio`)**
   - Preserves Scy-Shell's signature floating glass dock (`Island`, `Carved Notch`, `Trinity Split`) as the primary dock while allowing instant, single-click switching to `Compact Rail` or `Disabled`.
   - Eliminates duplicate docks at **both** the process level (`scy-launch-engine` kernel `flock` single-instance lock + Hyprland `exec-once` deduplication, without `killall`/`pkill`) and the Wayland surface ownership level (`ScyBridge.owns("dock")` in `Dock.qml` + `ScyGates::dock_enabled()` in `plugins/dock/mod.rs`).

3. **Login-Safe Persistence Engine & Corruption Recovery**
   - Atomic temp-file + `fsync` + `os.replace` writes across `~/.config/scy-shell/config.toml` and all 14 native runtime stores.
   - **SHA-256 Persistence Ledger (`persistence-ledger.json`)** reconciles live in-session QML/Rust changes (`prefs.json`, `blur.json`, `widgets.json`, `mandara/config.toml`) on startup *before* flushing, ensuring settings never disappear or revert after re-login.
   - Automatic `.last-good` shadow recovery and `persistence-errors.log` diagnostics if power loss corrupts `config.toml`.

4. **Strictly Separated Lock Screen (`11`) & Login Experience (`12`)**
   - In-session Wayland Lock Screen (`Section 11`) and pre-session SDDM / `greetd` Login Greeter (`Section 12`) are independently configured (`lockLoginSync = false` by default; automatic login-painting disabled unless explicitly opted in).
   - Passwords and secrets are never stored in shell configuration (`PAM` handles all authentication).

5. **Signature Scy-Shell v2.0 Capabilities**
   - **Scy Dynamic Design Engine (`ScyDesignTokens`)**: Unified OKLCH + Material 3 Expressive tokens, glass blur/refraction/tint (`-1` Auto sentinel preserved), corner-radius scale, typography, and spring physics shared across every bar, dock, widget, notification, lock screen, and Studio card.
   - **Scy Dynamic Island**: Adaptive central bar capsule morphing smoothly between workspace telemetry, active MPRIS media, Focus/Pomodoro countdowns, and live alerts.
   - **Scy Layout Composer & Component Laboratory**: One-click spatial desktop topologies (`Scy Signature`, `Unity Left`, `Minimal Top`, `Bottom Deck`, `Dual Stage`) and per-surface material overrides.
   - **Scy Profile System**: 7 built-in complete desktop profiles (`Balanced`, `Minimal`, `Productivity`, `Immersive`, `Gaming`, `Creative`, `Cinema`) plus custom user profiles with JSON export/import.
   - **Scy Productivity Layer & Intelligent Performance**: Safe AST calculator (`= (12 * 8) + 4`), unit converter (`100 km to mi`), `?` web search, Markdown Quick Notes, Focus Timer, and hardware-aware performance tiers (`Maximum Visual Quality`, `Balanced`, `Performance`, `Battery Efficiency`).
   - **Hyprland `0.57+` & First-Class Zsh Support**: Emits modern Hyprland `0.57+` v2 `layerrule = blur on, match:namespace ...` and Lua `hl.layer_rule(...)` drop-ins with 15-second auto-revert safety trials, plus native `_scy-shell` Zsh completions (zero `fish` requirement).

---

## Quick Start (CachyOS / Arch Linux)

```zsh
# 1. Inspect detected distro, Hyprland 0.57+, Quickshell, and Zsh environment
./install.sh --check-env

# 2. Preview all planned actions without modifying any files
./install.sh --dry-run --profile balanced --with-hypr

# 3. Install Scy-Shell (automatically creates a recoverable backup first)
./install.sh --install-packages --profile balanced --with-hypr --enable-services
```

---

## Essential CLI Commands (`scy-shell`)

```zsh
scy-shell status                        # Inspect active profile, dock owner, and 15 Studio sections
scy-shell studio 01-personalization     # Open Unified Scy-Shell Studio at any section (01..15)
scy-shell dock status                   # Inspect single-owner dock state
scy-shell dock lucid                    # Switch to primary Scy-Shell Glass Dock (or: mandara | none)
scy-shell profile apply productivity    # Apply any built-in or custom desktop profile
scy-shell layout apply unity-left       # Apply a Scy Layout Composer spatial preset
scy-shell performance apply max-quality # Switch Scy Intelligent Performance tier
scy-shell hypr emit                     # Emit validated Hyprland 0.57+ modular drop-in
scy-shell doctor                        # Run full CachyOS / Hyprland / Quickshell / persistence check
scy-shell backup create my-snapshot     # Create timestamped configuration backup
```

---

## Documentation Index

- [Installation Guide](docs/INSTALLATION.md)
- [Upgrading & Migration Guide](docs/UPGRADING_AND_MIGRATION.md)
- [Uninstall & Backup Recovery](docs/UNINSTALL_AND_RECOVERY.md)
- [Features & Unified 15-Section Studio Guide](docs/FEATURES_AND_STUDIO.md)
- [Settings Architecture & 2,026-Parameter Reference](docs/SETTINGS_REFERENCE.md)
- [Dependencies (Required vs Optional)](docs/DEPENDENCIES.md)
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- [Changelog (`v2.0.0`)](docs/CHANGELOG.md)
- [Known Limitations](docs/KNOWN_LIMITATIONS.md)
- [Testing & Verification Report](docs/TESTING_REPORT.md)

---

## License & Attribution

Scy-Shell is distributed under **GPL-3.0-or-later**, preserving upstream MIT copyright notices for Lucid 2 (`Copyright (c) 2026 Sn3akyy1`), GPL-3.0-or-later notices for Mandara (`Copyright (C) 2026 Ahmad Hamdi and contributors`), and third-party asset licenses documented in `LICENSE` and `THIRD_PARTY_NOTICES.md`. Architectural design inspiration from `Serpantinum`, `end-4 / illogical-impulse`, `end4-pC`, `NAnDoroid`, `Caelestia`, and `ML4W` is implemented natively in Scy-Shell code with full license respect.
