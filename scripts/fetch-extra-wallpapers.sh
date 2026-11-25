#!/usr/bin/env bash
# Optional helper to fetch the full 1.2 GB 4K animated MP4 wallpaper pack from Sn3akyy1/lucid v1.21.1
set -euo pipefail
DEST="${1:-$HOME/.config/quickshell/lucid/wallpapers}"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

echo "[Scy-Shell] Fetching full Lucid v1.21.1 4K animated & static wallpaper pack into $DEST ..."
git clone --depth 1 --branch v1.21.1 https://github.com/Sn3akyy1/lucid.git "$TMP_DIR/lucid"
mkdir -p "$DEST"
cp -rn "$TMP_DIR/lucid/wallpapers/"* "$DEST/"
echo "[Scy-Shell] Done! Wallpapers installed in $DEST"
