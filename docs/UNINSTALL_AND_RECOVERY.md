# Uninstall & Backup Recovery Guide

Scy-Shell is designed so every installation, migration, profile switch, and Hyprland config emission is **100% reversible**.

---

## 1. Clean Uninstall

To remove Scy-Shell binaries, runtime files, `systemd --user` service units, Zsh completion, and the modular Hyprland `source` line while **preserving all user backups**:

```zsh
./uninstall.sh
# Equivalent to:
./install.sh --uninstall
```

### What Uninstall Removes
- `~/.local/bin/{scy-shell,scy-daemon,scy-launch-engine,scy-shell-ipc}`
- `~/.local/share/scy-shell/runtime/`
- `~/.config/systemd/user/{scy-daemon,scy-lucid,scy-mandara}.service` (disabled & stopped cleanly)
- `~/.local/share/zsh/site-functions/_scy-shell`
- `~/.config/hypr/scy-shell/` and the single Scy-Shell hook line in `~/.config/hypr/hyprland.conf` / `hyprland.lua`

### What Uninstall Preserves
- `~/.local/share/scy-shell/backups/` (all pre-install and manual snapshots)
- Your personal wallpapers, screenshots, notes, and user desktop configs

---

## 2. Listing & Restoring Backups

### List Snapshots via CLI
```zsh
scy-shell backup list
```

### Restore a Snapshot via `scy-shell`
```zsh
scy-shell backup restore <snapshot-name-or-path>
```
`scy-shell backup restore` validates every destination path against symlink/traversal attacks and rolls back atomically if an I/O failure occurs mid-restore.

### Restore a Pre-Install Snapshot via `install.sh` (Even After Uninstall)
```zsh
ls -la ~/.local/share/scy-shell/backups/
./install.sh --restore-backup ~/.local/share/scy-shell/backups/install-<YYYYMMDD-HHMMSS>
```
