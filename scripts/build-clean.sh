#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${ROOT_DIR}/src"
MANDARA_DIR="${SCY_MANDARA_DIR:-${ROOT_DIR}/engines/mandara}"
LUCID_DIR="${SCY_LUCID_DIR:-${ROOT_DIR}/engines/lucid}"

echo "[1/5] Verifying Phase 1 upstream SHA-256 baseline & reversible adapter patches..."
python3 "${ROOT_DIR}/bin/scy-shell" provenance >/dev/null
echo "      OK — Upstream SHA-256 manifests and reverse-patch check passed."

echo "[2/5] Compiling native C11 hotkey IPC client (bin/scy-shell-ipc)..."
cc -std=c11 -O2 -Wall -Wextra -Werror -s \
  "-ffile-prefix-map=${ROOT_DIR}=." \
  "-ffile-prefix-map=${HOME}=." \
  "${ROOT_DIR}/csrc/scy_ipc_client.c" -o "${ROOT_DIR}/bin/scy-shell-ipc"
echo "      OK — Built ${ROOT_DIR}/bin/scy-shell-ipc"

echo "[3/5] Running FATAL Qt6 QML lint (-W 0, zero warnings tolerated)..."
SCY_LUCID_DIR="${LUCID_DIR}" "${ROOT_DIR}/scripts/lint-qml.sh"

echo "[4/5] Building native Rust Mandara GPUI engine (-p mandara-app)..."
if command -v cargo >/dev/null 2>&1 && command -v rustc >/dev/null 2>&1; then
  TARGET_OUT="${CARGO_TARGET_DIR:-${MANDARA_DIR}/target}"
  MEM_KB="$(awk '/^MemTotal:/ {print $2}' /proc/meminfo 2>/dev/null || echo 8000000)"
  EXTRA_CARGO_ARGS=()
  if [[ "$MEM_KB" -lt 4000000 ]]; then
    export CARGO_BUILD_JOBS="${CARGO_BUILD_JOBS:-1}"
    EXTRA_CARGO_ARGS+=(
      --config 'profile.release.lto="off"'
      --config 'profile.release.opt-level=1'
      --config 'profile.release.codegen-units=16'
      --config 'profile.release.package."*".opt-level=1'
      --config 'profile.release.package."*".codegen-units=16'
    )
  fi
  GIT_CEILING_DIRECTORIES="$(dirname "${MANDARA_DIR}")" \
  CARGO_TARGET_DIR="${TARGET_OUT}" \
    cargo build --release --locked -p mandara-app "${EXTRA_CARGO_ARGS[@]}" --manifest-path "${MANDARA_DIR}/Cargo.toml"
  "${TARGET_OUT}/release/mandara" --version
  echo "      OK — Built native Rust binary ${TARGET_OUT}/release/mandara"
else
  echo "FATAL: cargo/rustc not installed on this machine." >&2
  exit 2
fi

echo "[5/5] Running Tier 1 portable automated test suite..."
SCY_LUCID_DIR="${LUCID_DIR}" SCY_MANDARA_DIR="${MANDARA_DIR}" \
  python3 -m unittest discover -s "${ROOT_DIR}/tests" -p "test_phase*.py"

echo "Clean build & verification complete."
