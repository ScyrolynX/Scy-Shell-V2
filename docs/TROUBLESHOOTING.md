# Troubleshooting Guide

## 1. Run `scy-shell doctor` First

```zsh
scy-shell doctor
scy-shell conflicts --json
```
`scy-shell doctor` inspects binaries, Wayland/Hyprland environment variables, single-owner surface gates, persistence logs, and resource discipline.

---

## 2. Common Questions & Fixes

### Q: I previously saw two docks on screen in `v1.0.0` or after importing old dotfiles.
1. Check active dock owner:
   ```zsh
   scy-shell dock status
   ```
2. Resynchronize single-owner gates and deduplicate legacy Hyprland `exec-once` lines (automatically backs up `hyprland.conf` first):
   ```zsh
   scy-shell conflicts --resync
   scy-shell hypr dedup-autostart
   ```
3. Verify no third-party dock (`waybar`, `nwg-dock-hyprland`, `plank`) is launched in `~/.config/hypr/hyprland.conf`.

### Q: How do I check if a config write or corrupted file recovery occurred?
Inspect the persistence log and change journal:
```zsh
cat ~/.local/state/scy-shell/persistence-errors.log
tail -n 30 ~/.local/state/scy-shell/changes.jsonl
```
If `config.toml` was ever truncated by a hard power-off, Scy-Shell automatically quarantines the broken file under `~/.local/share/scy-shell/backups/corrupted-*` and restores `~/.config/scy-shell/config.toml.last-good`.

### Q: Why didn't changing my Lock Screen wallpaper change my SDDM / Greetd Login screen?
By design in `v2.0.0`, **Section `11` (Lock Screen)** and **Section `12` (Login Experience)** are strictly separated so lock-screen tweaks never clobber your system login greeter.
- To customize the login greeter, open **Studio -> `12 Login Experience`**.
- To perform a one-time visual token copy from Lock Screen to Login without permanent coupling:
  ```zsh
  scy-shell preauth copy-lock-to-login-once
  ```

### Q: Hyprland `0.57+` reported a config warning from old dotfiles.
Re-emit Scy-Shell's `0.57+` v2 drop-in:
```zsh
scy-shell hypr emit
```
Scy-Shell `v2.0.0` exclusively emits Hyprland `0.57+` `layerrule = blur on, match:namespace ...` and `hl.layer_rule(...)` syntax (never deprecated `<0.53` positional `layerrule = blur, name` or `ignorezero` rules).

### Q: How do I roll back everything to before a profile switch or install?
```zsh
scy-shell backup list
scy-shell backup restore <backup-name>
```
