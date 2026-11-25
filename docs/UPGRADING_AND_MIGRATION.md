# Upgrading & Migration Guide (`v1.0.0` -> `v2.0.0`)

Scy-Shell `v2.0.0` includes automatic, backup-protected migration from both **Scy-Shell `v1.0.0`** (`schema_version = 1`) and standalone **Lucid 2** / **Mandara** configurations.

---

## 1. Upgrading from Scy-Shell `v1.0.0`

Simply run the `v2.0.0` installer over your existing setup:

```zsh
./install.sh --with-hypr --enable-services
```

### Automatic `v1 -> v2` Migration Steps
1. **Pre-Upgrade Backup**: `install.sh` creates `~/.local/share/scy-shell/backups/install-<timestamp>/` and `ScyConfigStore` creates `migrate-v1-to-v2` before modifying `config.toml`.
2. **Live Session Edit Absorption (`persistence-ledger.json`)**: Any tweaks you made directly in `~/.config/quickshell/lucidprefs/prefs.json`, `blur.json`, `widgets.json`, or `~/.config/mandara/config.toml` are absorbed into `config.toml` rather than overwritten.
3. **Single-Owner Dock Synchronization**: Your `v1` `active_providers.dock` and `dockStyle` (`island`, `notch`, `split`, `mandara`, `none`) are mapped losslessly to `scy.dock.mode` and `[scy_gates]`.
4. **Lock vs Login Decoupling**: `lockLoginSync` is migrated safely to `false` unless you explicitly enable `scy.login.mirror_lock_layout` in Studio Section `12`.
5. **Hyprland `0.57+` Rule Upgrade**: Re-emitting Hyprland configs (`--with-hypr` or `scy-shell hypr emit`) replaces legacy `<0.53` layerrule lines with Hyprland `0.57+` v2 `layerrule = blur on, match:namespace ...` syntax and comments out duplicate `exec-once` shell spawns after backing up `hyprland.conf`.

---

## 2. Migrating from Standalone Dotfiles (Lucid / Mandara / ML4W / end-4)

- Existing `~/.config/lucid/settings.json`, `~/.config/quickshell/lucidprefs/prefs.json`, and `~/.config/mandara/config.toml` keys are imported automatically on first install (`ScyConfigMigrator`).
- User-owned Hyprland files (`monitors.conf`, custom keybinds, environment rules) are **never deleted**; Scy-Shell attaches via a single modular `source = ~/.config/hypr/scy-shell/scy-shell.conf` line.
- If your `hyprland.conf` currently launches `waybar`, `nwg-dock-hyprland`, or standalone `quickshell`, `scy-shell hypr dedup-autostart` (or commenting out the old `exec-once` line) ensures external bars/docks do not run alongside Scy-Shell.
