#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FONT_DIR="${ROOT_DIR}/fonts"
FONT_NAME="Inter-Bold.ttf"
FONT_PATH="${FONT_DIR}/${FONT_NAME}"
TMP_DIR="$(mktemp -d)"
TMP_ZIP="${TMP_DIR}/Inter.zip"

cleanup() {
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

mkdir -p "${FONT_DIR}"

echo "Installing Inter Bold font..."
echo "Downloading official Inter release archive..."
curl --retry 3 --retry-delay 2 -fSL \
  -o "${TMP_ZIP}" \
  "https://github.com/rsms/inter/releases/latest/download/Inter.zip"

echo "Extracting ${FONT_NAME}..."
unzip -jo "${TMP_ZIP}" "Inter-*/ttf/${FONT_NAME}" -d "${FONT_DIR}"

if [[ -f "${FONT_PATH}" ]]; then
  echo "Installed: ${FONT_PATH}"
else
  echo "ERROR: ${FONT_PATH} not found after install" >&2
  exit 1
fi
