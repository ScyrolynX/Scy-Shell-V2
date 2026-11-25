#!/usr/bin/env bash
# Scy-Shell v2.0.0 — Safe Uninstaller & Backup Recovery Wrapper
# Preserves all user backups under ~/.local/share/scy-shell/backups/
set -euo pipefail
SCY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCY_ROOT/install.sh" --uninstall "$@"
