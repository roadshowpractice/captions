#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FONT_DIR="${ROOT_DIR}/fonts"
FONT_PATH="${FONT_DIR}/Inter-Bold.ttf"
FONT_URL="https://cdn.jsdelivr.net/gh/rsms/inter@master/docs/font-files/Inter-Bold.ttf"
EXPECTED_SHA256="5c1247acef7f2b8522a31742c76d6adcb5569bacc0be7ceaa4dc39dd252ce895"

mkdir -p "${FONT_DIR}"

echo "Downloading Inter-Bold.ttf ..."
curl -fsSL "${FONT_URL}" -o "${FONT_PATH}"

echo "Verifying checksum ..."
ACTUAL_SHA256="$(sha256sum "${FONT_PATH}" | awk '{print $1}')"
if [[ "${ACTUAL_SHA256}" != "${EXPECTED_SHA256}" ]]; then
  echo "Checksum mismatch for ${FONT_PATH}" >&2
  echo "Expected: ${EXPECTED_SHA256}" >&2
  echo "Actual:   ${ACTUAL_SHA256}" >&2
  exit 1
fi

echo "Installed ${FONT_PATH}"
