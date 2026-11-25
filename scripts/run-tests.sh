#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${ROOT_DIR}/src"

echo "========================================================================"
echo "  Scy-Shell v1.0.0 — Tier 1: Portable Automated Test Suite"
echo "  Root: ${ROOT_DIR}"
echo "  Requires: Python 3.11+ & POSIX userland only (zero host/GUI deps)"
echo "========================================================================"
python3 -m unittest discover -s "${ROOT_DIR}/tests" -p "test_phase*.py" -v

echo ""
echo "========================================================================"
echo "  Scy-Shell v1.0.0 — Tier 2: Host Toolchain & Compositor Suite"
echo "  Requires: cargo/rustc, quickshell/qmllint, Wayland + Hyprland (CachyOS)"
echo "  (Cleanly skips unavailable host capabilities outside CachyOS Wayland)"
echo "========================================================================"
python3 -m unittest discover -s "${ROOT_DIR}/tests/hardware" -p "test_*.py" -v
