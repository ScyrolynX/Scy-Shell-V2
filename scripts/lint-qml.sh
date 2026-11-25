#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LUCID_DIR="${SCY_LUCID_DIR:-${ROOT_DIR}/engines/lucid}"

QMLLINT_BIN=""
for candidate in qmllint /usr/lib/qt6/bin/qmllint /usr/lib64/qt6/bin/qmllint; do
  if command -v "$candidate" >/dev/null 2>&1; then
    QMLLINT_BIN="$(command -v "$candidate")"
    break
  elif [[ -x "$candidate" ]]; then
    QMLLINT_BIN="$candidate"
    break
  fi
done

if [[ -z "$QMLLINT_BIN" ]]; then
  echo "FATAL: Qt6 qmllint binary not found (install qt6-declarative / qt6-declarative-dev-tools)." >&2
  exit 127
fi

IMPORT_ARGS=(-I "${ROOT_DIR}/scripts/qml-stubs" -I "${ROOT_DIR}/studio")
for sys_qml in /usr/lib/qt6/qml /usr/lib/*-linux-gnu/qt6/qml /usr/lib64/qt6/qml; do
  [[ -d "$sys_qml" ]] && IMPORT_ARGS+=(-I "$sys_qml")
done

if [[ "$#" -gt 0 ]]; then
  TARGETS=("$@")
else
  if [[ ! -d "$LUCID_DIR" ]]; then
    echo "FATAL: Lucid QML directory not found at ${LUCID_DIR}" >&2
    exit 1
  fi
  IMPORT_ARGS+=(-I "${LUCID_DIR}/lucidprefs")
  TARGETS=(
    "${LUCID_DIR}/ScyBridge.qml"
    "${LUCID_DIR}/ScyDesignTokens.qml"
    "${LUCID_DIR}/lucidbar/ScyPluginPill.qml"
    "${LUCID_DIR}/lucidbar/ScyDynamicIsland.qml"
    "${LUCID_DIR}/lucidprefs/ScyStudioSectionBase.qml"
    "${LUCID_DIR}/lucidprefs/ScySec01Personalization.qml"
    "${LUCID_DIR}/lucidprefs/ScySec02Desktop.qml"
    "${LUCID_DIR}/lucidprefs/ScySec03Dock.qml"
    "${LUCID_DIR}/lucidprefs/ScySec04Effects.qml"
    "${LUCID_DIR}/lucidprefs/ScySec05Layout.qml"
    "${LUCID_DIR}/lucidprefs/ScySec06Widgets.qml"
    "${LUCID_DIR}/lucidprefs/ScySec07Windows.qml"
    "${LUCID_DIR}/lucidprefs/ScySec08Interactions.qml"
    "${LUCID_DIR}/lucidprefs/ScySec09Notifications.qml"
    "${LUCID_DIR}/lucidprefs/ScySec10System.qml"
    "${LUCID_DIR}/lucidprefs/ScySec11LockScreen.qml"
    "${LUCID_DIR}/lucidprefs/ScySec12Login.qml"
    "${LUCID_DIR}/lucidprefs/ScySec13Productivity.qml"
    "${LUCID_DIR}/lucidprefs/ScySec14Profiles.qml"
    "${LUCID_DIR}/lucidprefs/ScySec15Advanced.qml"
    "${LUCID_DIR}/lucidprefs/ScyAiPage.qml"
    "${LUCID_DIR}/lucidprefs/ScyConflictsPage.qml"
    "${LUCID_DIR}/lucidprefs/ScyLooksPage.qml"
    "${LUCID_DIR}/lucidprefs/ScyPluginsPage.qml"
    "${LUCID_DIR}/lucidprefs/ScyPreAuthPage.qml"
    "${LUCID_DIR}/lucidprefs/ScyProvidersPage.qml"
    "${LUCID_DIR}/lucidprefs/ScyVaultPage.qml"
    "${LUCID_DIR}/lucidprefs/ScyWallgenPage.qml"
  )
fi

export LC_ALL=C.UTF-8
# STRICT FATAL EXECUTION: ZERO `|| true` — ANY syntax, import, unresolved-type, missing-property, or duplicate-binding error exits non-zero!
"$QMLLINT_BIN" \
  --bare -W 0 \
  "${IMPORT_ARGS[@]}" \
  "${TARGETS[@]}"

echo "qmllint PASS: ${#TARGETS[@]} QML files verified with 0 errors (fatal mode)."
