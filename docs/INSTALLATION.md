# Scy-Shell v2.0.0 — Installation Guide

Scy-Shell targets **CachyOS Linux** (and Arch Linux derivatives) running **Hyprland `0.57+`**, **Quickshell**, and **Zsh** (or POSIX `bash`/`sh` — `fish` is never required).

---

## 1. Preflight Check & Dry Run

Before modifying anything on your system, verify your environment and inspect every planned step:

```zsh
./install.sh --check-env
./install.sh --dry-run --profile balanced --with-hypr
```

`--dry-run` is guaranteed to leave `$HOME` untouched.

---

## 2. Standard CachyOS Installation

```zsh
./install.sh --install-packages --profile balanced --with-hypr --enable-services
```

### What `install.sh` Does Safely
1. **Creates a Recoverable Pre-Install Backup**: Snapshots any existing `~/.config/scy-shell`, `~/.config/lucid`, `~/.config/mandara`, `~/.config/quickshell/lucid`, and `~/.config/hypr` into `~/.local/share/scy-shell/backups/install-<YYYYMMDD-HHMMSS>/` with a `manifest.json`.
2. **Installs Runtime & Single-Instance Launchers**: Copies `src/`, `schema/`, `studio/`, and `bin/` into `~/.local/share/scy-shell/runtime/` and symlinks `scy-shell`, `scy-daemon`, `scy-launch-engine`, and `scy-shell-ipc` into `~/.local/bin/`.
3. **Installs Zsh Completion**: Installs `_scy-shell` into `~/.local/share/zsh/site-functions/_scy-shell`. Ensure `~/.local/bin` is on `$PATH` and `~/.local/share/zsh/site-functions` is on `$fpath` in `~/.zshrc`:
   ```zsh
   export PATH="$HOME/.local/bin:$PATH"
   fpath=("$HOME/.local/share/zsh/site-functions" $fpath)
   autoload -Uz compinit && compinit
   ```
4. **Installs Unified Studio & QML Shell Tree**: Installs the patched Quickshell tree + 15 unified Studio sections into `~/.config/quickshell/lucid/`.
5. **Reconciles & Migrates Existing Settings**: Imports any pre-existing standalone Lucid or Mandara user preferences without overwriting them with defaults, stages isolated Lock/Login configs, and generates `~/.config/scy-shell/design-tokens.json`.
6. **Attaches Modular Hyprland `0.57+` Hook (`--with-hypr`)**: Emits `~/.config/hypr/scy-shell/scy-shell.conf` (and `init.lua` if `hyprland.lua` is used) using modern Hyprland `0.57+` `match:namespace` syntax, and appends a single clean `source = ~/.config/hypr/scy-shell/scy-shell.conf` line to your backed-up `hyprland.conf`.
7. **Enables Single-Instance `systemd --user` Units (`--enable-services`)**: Enables `scy-daemon.service`, `scy-lucid.service`, and `scy-mandara.service` ordered after `scy-daemon.service` via `scy-launch-engine` (`flock` single-instance guard).

---

## 3. Choosing an Initial Profile

Pass `--profile <name>` during installation (or switch live anytime via Studio Section `14` or `scy-shell profile apply <name>`):

| Profile | Focus |
|---|---|
| `balanced` *(default)* | Signature Scy-Shell frosted glass, floating Island dock, adaptive Dynamic Island, balanced GPU cost |
| `minimal` | Ultra-clean top bar, auto-hidden dock, crisp radii, reduced visual noise |
| `productivity` | Tiling-focused density, workspace telemetry, clipboard/notes/calculator ready, snappy motion |
| `immersive` | Edge-to-edge canvas, dodge-windows dock & bar, rich atmospheric blur |
| `gaming` | Low-latency instant transitions, zero blur overhead during fullscreen VRR games |
| `creative` | Neutral color harmony, floating dock, quick color picker & OCR screenshot workflow |
| `cinema` | Deep darkened surfaces, warm cinema tone, Do Not Disturb & idle inhibit friendly |

---

## 4. Arch / CachyOS `makepkg` Package Build (Optional)

A clean `PKGBUILD` is provided at `packaging/arch/PKGBUILD`:

```zsh
cd packaging/arch
makepkg -si
```
