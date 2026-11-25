#!/usr/bin/env bash
# Scy-Shell v2.0.0 ("Ultimate Unified Desktop Evolution")
# Safe, Idempotent Installer & Recovery Tool for CachyOS Linux + Hyprland 0.57+ + Quickshell + Zsh
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail

SCY_VERSION="2.0.0"
SCY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -d "$SCY_ROOT/engines/lucid" ]]; then
  DEFAULT_LUCID_SRC="$SCY_ROOT/engines/lucid"
else
  DEFAULT_LUCID_SRC="$SCY_ROOT/../sources/lucid-working"
fi
if [[ -d "$SCY_ROOT/engines/mandara" ]]; then
  DEFAULT_MANDARA_SRC="$SCY_ROOT/engines/mandara"
else
  DEFAULT_MANDARA_SRC="$SCY_ROOT/../sources/mandara-working"
fi
LUCID_SRC="${LUCID_WORKING_DIR:-$DEFAULT_LUCID_SRC}"
MANDARA_SRC="${MANDARA_WORKING_DIR:-$DEFAULT_MANDARA_SRC}"

DRY_RUN=0
SKIP_ENGINE_BUILD="${SCY_SKIP_ENGINE_BUILD:-0}"
PROFILE="balanced"
WITH_HYPR=0
ENABLE_SERVICES=0
ACTION="install"
RESTORE_DIR=""
TARGET_HOME="${HOME}"
INSTALL_PKGS=0

usage() {
  cat <<USAGE
Scy-Shell v${SCY_VERSION} Installer (CachyOS + Hyprland 0.57+ + Quickshell + Zsh)

Usage: ./install.sh [options]

Options:
  --dry-run                 Show every planned action without modifying any files
  --check-env               Inspect OS, Hyprland, Quickshell, GPU, and Zsh compatibility only
  --profile <p>             Profile: balanced | minimal | productivity | immersive | gaming | creative | cinema | full
  --with-hypr               Safely attach Hyprland 0.57+ modular drop-in to ~/.config/hypr (backs up first)
  --enable-services         Enable systemd --user units (scy-daemon, scy-lucid, scy-mandara)
  --skip-engine-build       Skip local Rust/Cargo Mandara build step
  --install-packages        Install CachyOS / Arch packages via pacman (requires sudo)
  --home <dir>              Override target HOME directory (default: \$HOME)
  --restore-backup <dir>    Restore configuration snapshot created by Scy-Shell
  --uninstall               Cleanly remove Scy-Shell hooks, binaries & user units (preserves backups)
  -h, --help                Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --check-env) ACTION="check-env"; shift ;;
    --skip-engine-build) SKIP_ENGINE_BUILD=1; shift ;;
    --profile) PROFILE="$2"; shift 2 ;;
    --with-hypr) WITH_HYPR=1; shift ;;
    --enable-services) ENABLE_SERVICES=1; shift ;;
    --install-packages) INSTALL_PKGS=1; shift ;;
    --home) TARGET_HOME="$2"; shift 2 ;;
    --restore-backup) ACTION="restore"; RESTORE_DIR="$2"; shift 2 ;;
    --uninstall) ACTION="uninstall"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 2 ;;
  esac
done

run_cmd() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[DRY-RUN] $*"
  else
    "$@"
  fi
}

detect_environment() {
  local os_id="unknown" os_pretty="Linux" hypr_ver="not-found" qs_ver="not-found" user_shell="unknown"
  if [[ -r /etc/os-release ]]; then
    # shellcheck disable=SC1091
    source /etc/os-release
    os_id="${ID:-unknown}"
    os_pretty="${PRETTY_NAME:-Linux}"
  fi
  if command -v hyprctl >/dev/null 2>&1; then
    hypr_ver="$(hyprctl version 2>/dev/null | head -n1 | tr -s ' ' || echo 'installed')"
  elif command -v Hyprland >/dev/null 2>&1; then
    hypr_ver="$(Hyprland --version 2>/dev/null | head -n1 | tr -s ' ' || echo 'installed')"
  fi
  if command -v quickshell >/dev/null 2>&1; then
    qs_ver="$(quickshell --version 2>/dev/null | head -n1 || echo 'installed')"
  fi
  user_shell="$(basename "${SHELL:-/bin/sh}")"

  echo "[Scy-Shell v${SCY_VERSION}] Environment Preflight:"
  echo "  • Distro       : ${os_pretty} (id=${os_id})"
  echo "  • Compositor   : ${hypr_ver} (targets Hyprland 0.57+ v2 layerrule/windowrule syntax)"
  echo "  • Quickshell   : ${qs_ver}"
  echo "  • User Shell   : ${user_shell} (POSIX/Zsh native — zero Fish requirement)"
}

create_preinstall_backup() {
  local ts bkp_root copied=0
  ts="$(date +%Y%m%d-%H%M%S)"
  bkp_root="$TARGET_HOME/.local/share/scy-shell/backups/install-${ts}"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[DRY-RUN] Create recoverable pre-install backup snapshot at $bkp_root"
    return 0
  fi
  mkdir -p "$bkp_root"
  for cfg_sub in scy-shell lucid mandara hypr; do
    if [[ -d "$TARGET_HOME/.config/$cfg_sub" ]]; then
      cp -a "$TARGET_HOME/.config/$cfg_sub" "$bkp_root/$cfg_sub"
      copied=$((copied + 1))
    fi
  done
  if [[ -d "$TARGET_HOME/.config/quickshell/lucid" ]]; then
    mkdir -p "$bkp_root/quickshell"
    cp -a "$TARGET_HOME/.config/quickshell/lucid" "$bkp_root/quickshell/lucid"
    copied=$((copied + 1))
  fi
  cat > "$bkp_root/manifest.json" <<JSON
{
  "version": "${SCY_VERSION}",
  "created_at": "${ts}",
  "target_home": "${TARGET_HOME}",
  "backed_up_entries": ${copied}
}
JSON
  echo "[Scy-Shell] Saved recoverable pre-install backup (${copied} config trees) -> $bkp_root"
}

if [[ "$ACTION" == "check-env" ]]; then
  detect_environment
  exit 0
fi

if [[ "$ACTION" == "restore" ]]; then
  [[ -d "$RESTORE_DIR" ]] || { echo "Backup directory not found: $RESTORE_DIR" >&2; exit 1; }
  echo "[Scy-Shell] Restoring snapshot from $RESTORE_DIR -> $TARGET_HOME/.config ..."
  for sub in hypr scy-shell lucid mandara; do
    if [[ -d "$RESTORE_DIR/$sub" ]]; then
      run_cmd rm -rf "$TARGET_HOME/.config/$sub"
      run_cmd mkdir -p "$TARGET_HOME/.config"
      run_cmd cp -a "$RESTORE_DIR/$sub" "$TARGET_HOME/.config/$sub"
    fi
  done
  if [[ -d "$RESTORE_DIR/quickshell/lucid" ]]; then
    run_cmd rm -rf "$TARGET_HOME/.config/quickshell/lucid"
    run_cmd mkdir -p "$TARGET_HOME/.config/quickshell"
    run_cmd cp -a "$RESTORE_DIR/quickshell/lucid" "$TARGET_HOME/.config/quickshell/lucid"
  fi
  echo "[Scy-Shell] Restore complete."
  exit 0
fi

if [[ "$ACTION" == "uninstall" ]]; then
  echo "[Scy-Shell] Uninstalling Scy-Shell v${SCY_VERSION} user binaries, systemd units, and Hyprland hook (preserving backups & user data)..."
  if command -v systemctl >/dev/null 2>&1 && [[ "$DRY_RUN" -eq 0 ]]; then
    systemctl --user disable --now scy-mandara.service scy-lucid.service scy-daemon.service >/dev/null 2>&1 || true
  fi
  run_cmd rm -f \
    "$TARGET_HOME/.local/bin/scy-shell" \
    "$TARGET_HOME/.local/bin/scy-daemon" \
    "$TARGET_HOME/.local/bin/scy-launch-engine" \
    "$TARGET_HOME/.local/bin/scy-shell-ipc"
  run_cmd rm -rf "$TARGET_HOME/.local/share/scy-shell/runtime"
  run_cmd rm -f \
    "$TARGET_HOME/.config/systemd/user/scy-daemon.service" \
    "$TARGET_HOME/.config/systemd/user/scy-lucid.service" \
    "$TARGET_HOME/.config/systemd/user/scy-mandara.service" \
    "$TARGET_HOME/.local/share/zsh/site-functions/_scy-shell"
  if [[ -f "$TARGET_HOME/.config/hypr/hyprland.lua" && "$DRY_RUN" -eq 0 ]]; then
    sed -i '/-- Scy-Shell modular hook/d; /pcall(require, "scy-shell.init")/d' "$TARGET_HOME/.config/hypr/hyprland.lua"
  fi
  if [[ -f "$TARGET_HOME/.config/hypr/hyprland.conf" && "$DRY_RUN" -eq 0 ]]; then
    sed -i '/# Scy-Shell modular drop-in/d; /scy-shell\/scy-shell\.conf/d' "$TARGET_HOME/.config/hypr/hyprland.conf"
  fi
  run_cmd rm -rf "$TARGET_HOME/.config/hypr/scy-shell"
  echo "[Scy-Shell] Uninstall complete. Recoverable backups remain in $TARGET_HOME/.local/share/scy-shell/backups/"
  exit 0
fi

detect_environment
echo "[Scy-Shell v${SCY_VERSION}] Installing profile='$PROFILE' into HOME='$TARGET_HOME' (dry_run=$DRY_RUN)..."

# Always snapshot existing desktop configs before touching anything
create_preinstall_backup

# Optional CachyOS / Arch package installation
if [[ "$INSTALL_PKGS" -eq 1 ]]; then
  PKGS=(hyprland quickshell zsh gcc make rust cargo pkgconf wayland-protocols clang qt6-declarative qt6-svg qt6-multimedia python awww matugen cliphist wl-clipboard xdg-desktop-portal-hyprland xdg-desktop-portal-gtk)
  if [[ "$PROFILE" == "full" || "$PROFILE" == "creative" || "$PROFILE" == "productivity" ]]; then
    PKGS+=(tesseract wf-recorder ddcutil kdeconnect)
  fi
  run_cmd sudo pacman -S --needed "${PKGS[@]}"
fi

# 1. Build C11 IPC binary (gcc) & Mandara Rust GPUI engine (cargo) when available
if command -v gcc >/dev/null 2>&1; then
  run_cmd gcc -O3 -Wall -Wextra -Werror -std=c11 "$SCY_ROOT/csrc/scy_ipc_client.c" -o "$SCY_ROOT/bin/scy-shell-ipc"
fi
if [[ "$SKIP_ENGINE_BUILD" -eq 0 && -d "$MANDARA_SRC" ]] && command -v cargo >/dev/null 2>&1 && ! command -v mandara >/dev/null 2>&1; then
  echo "[Scy-Shell] Building Mandara Rust GPUI & WASM engine from bundled source ($MANDARA_SRC)..."
  if [[ "$DRY_RUN" -eq 0 ]]; then
    (cd "$MANDARA_SRC" && cargo build --release --locked)
    mkdir -p "$TARGET_HOME/.local/bin"
    for bin_name in mandara mandara-greeter wallgen; do
      if [[ -x "$MANDARA_SRC/target/release/$bin_name" ]]; then
        cp -f "$MANDARA_SRC/target/release/$bin_name" "$TARGET_HOME/.local/bin/$bin_name"
      fi
    done
  else
    echo "[DRY-RUN] (cd $MANDARA_SRC && cargo build --release) -> $TARGET_HOME/.local/bin/mandara"
  fi
fi

# 2. Install runtime tree, single-instance launchers, systemd user services & Zsh completion
RUNTIME_DEST="$TARGET_HOME/.local/share/scy-shell/runtime"
ZSH_COMP_DIR="$TARGET_HOME/.local/share/zsh/site-functions"
run_cmd mkdir -p "$TARGET_HOME/.local/bin" "$RUNTIME_DEST" "$TARGET_HOME/.config/systemd/user" "$ZSH_COMP_DIR"
if [[ "$DRY_RUN" -eq 0 ]]; then
  cp -a "$SCY_ROOT/src" "$SCY_ROOT/schema" "$SCY_ROOT/studio" "$SCY_ROOT/bin" "$RUNTIME_DEST/"
  chmod +x "$RUNTIME_DEST/bin/scy-shell" "$RUNTIME_DEST/bin/scy-daemon" "$RUNTIME_DEST/bin/scy-launch-engine"
  ln -sf "$RUNTIME_DEST/bin/scy-shell" "$TARGET_HOME/.local/bin/scy-shell"
  ln -sf "$RUNTIME_DEST/bin/scy-daemon" "$TARGET_HOME/.local/bin/scy-daemon"
  ln -sf "$RUNTIME_DEST/bin/scy-launch-engine" "$TARGET_HOME/.local/bin/scy-launch-engine"
  ln -sf "$RUNTIME_DEST/bin/scy-shell-ipc" "$TARGET_HOME/.local/bin/scy-shell-ipc"
  cp -a "$SCY_ROOT/packaging/systemd/"*.service "$TARGET_HOME/.config/systemd/user/"
  if [[ -f "$SCY_ROOT/packaging/zsh/_scy-shell" ]]; then
    cp -f "$SCY_ROOT/packaging/zsh/_scy-shell" "$ZSH_COMP_DIR/_scy-shell"
  fi
else
  echo "[DRY-RUN] Copy runtime -> $RUNTIME_DEST, symlink binaries -> $TARGET_HOME/.local/bin/, install Zsh completion -> $ZSH_COMP_DIR/_scy-shell"
fi

# 3. Install Unified Scy-Shell + Lucid QML tree into ~/.config/quickshell/lucid
if [[ -d "$LUCID_SRC" ]]; then
  QS_LUCID="$TARGET_HOME/.config/quickshell/lucid"
  run_cmd mkdir -p "$TARGET_HOME/.config/quickshell"
  if [[ "$DRY_RUN" -eq 0 ]]; then
    rm -rf "$QS_LUCID"
    mkdir -p "$QS_LUCID"
    for item in "$LUCID_SRC"/*; do
      base="$(basename "$item")"
      if [[ "$base" == "wallpapers" ]]; then
        ln -snf "$item" "$QS_LUCID/wallpapers"
      else
        cp -a "$item" "$QS_LUCID/"
      fi
    done
    # Ensure studio/ & scy-schema/ in runtime match installed QML tree
    cp -f "$SCY_ROOT/studio/Scy"*.qml "$QS_LUCID/lucidprefs/"
    mkdir -p "$QS_LUCID/scy-schema"
    cp -f "$SCY_ROOT/schema/settings_catalogue.json" "$QS_LUCID/scy-schema/settings_catalogue.json"
  else
    echo "[DRY-RUN] Install Unified Scy-Shell Studio + QML runtime -> $QS_LUCID"
  fi
fi

# 4. Run lossless startup state reconciliation, migration, profile setup & isolated Lock/Login staging
if [[ "$DRY_RUN" -eq 0 ]]; then
  PYTHONPATH="$SCY_ROOT/src" python3 - "$TARGET_HOME" "$PROFILE" <<'PY'
import sys
from pathlib import Path
from scy_core.config_store import ScyConfigStore
from scy_core.migrator import ScyConfigMigrator
from scy_core.profiles import ScyProfileManager, BUILTIN_PROFILES
from scy_core.theme_engine import ScyThemeCoordinator
from scy_core.desktop_canvas import ScyDesktopCoordinator
from scy_core.security_preauth import ScyPreAuthCoordinator

home = Path(sys.argv[1])
req_profile = sys.argv[2].strip().lower()
eff_profile = "balanced" if req_profile == "full" else req_profile

had_scy_cfg = (home / ".config" / "scy-shell" / "config.toml").exists()
pre_mandara = home / ".config" / "mandara" / "config.toml"
pre_mandara_bytes = pre_mandara.read_bytes() if (not had_scy_cfg and pre_mandara.exists()) else None

store = ScyConfigStore(home_dir=home)
if pre_mandara_bytes is not None:
    pre_mandara.write_bytes(pre_mandara_bytes)
mig = ScyConfigMigrator(store).migrate_existing_configs()
rec = store.reconcile_startup_state()

# Only apply initial profile defaults on fresh installs so existing user tweaks are never clobbered
if mig["imported_lucid_keys"] == 0 and mig["imported_mandara_keys"] == 0 and eff_profile in BUILTIN_PROFILES:
    ScyProfileManager(store).apply_profile(eff_profile)

thm = ScyThemeCoordinator(store)
thm.write_mandara_portable_m3_look()
thm.apply_palette(seed_hex=str(store.doc["providers"]["lucid"]["prefs"].get("themeColour", "#7AA2F7")))
ScyDesktopCoordinator(store).write_portal_config()
ScyPreAuthCoordinator(store).stage_display_manager_configs()
print(f"[Scy-Shell] Migrated standalone keys: Lucid={mig['imported_lucid_keys']}, Mandara={mig['imported_mandara_keys']} (profile={store.get_setting('scy.profiles.active')})")
PY
else
  echo "[DRY-RUN] Reconcile & migrate ~/.config/{lucid,mandara} -> ~/.config/scy-shell/config.toml (ledger-protected)"
fi

# 5. Optional safe Hyprland 0.57+ modular hook + competing autostart audit
if [[ "$WITH_HYPR" -eq 1 ]]; then
  if [[ "$DRY_RUN" -eq 0 ]]; then
    if [[ -f "$TARGET_HOME/.config/hypr/hyprland.conf" ]]; then
      if grep -Eq '^[[:space:]]*exec-once[[:space:]]*=.*(waybar|nwg-dock|sfwbar|plank|cairo-dock)' "$TARGET_HOME/.config/hypr/hyprland.conf"; then
        echo "[Scy-Shell] WARNING: Detected competing dock/bar exec-once entries in ~/.config/hypr/hyprland.conf."
        echo "            Comment them out to prevent external duplicate bars/docks (backup preserved)."
      fi
    fi
    "$SCY_ROOT/bin/scy-shell" --home "$TARGET_HOME" hypr emit >/dev/null
    echo "[Scy-Shell] Emitted validated Hyprland 0.57+ modular config + keybinds (backup saved)."
  else
    echo "[DRY-RUN] Emit modular Hyprland 0.57+ config under $TARGET_HOME/.config/hypr/scy-shell/"
  fi
fi

# 6. Optional systemd --user unit activation
if [[ "$ENABLE_SERVICES" -eq 1 ]]; then
  if command -v systemctl >/dev/null 2>&1; then
    run_cmd systemctl --user daemon-reload
    run_cmd systemctl --user enable --now scy-daemon.service scy-lucid.service scy-mandara.service
  else
    echo "[Scy-Shell] systemctl not available in current container/chroot; skipping --enable-services."
  fi
fi

echo "[Scy-Shell v${SCY_VERSION}] Installation finished cleanly."
