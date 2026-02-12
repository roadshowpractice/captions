#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FONT_DIR="${ROOT_DIR}/fonts"
FONT_NAME="Inter-Bold.ttf"
FONT_PATH="${FONT_DIR}/${FONT_NAME}"
RELEASE_API_URL="https://api.github.com/repos/rsms/inter/releases/latest"
TMP_DIR="$(mktemp -d)"
TMP_ZIP="${TMP_DIR}/inter_latest.zip"

cleanup() {
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

mkdir -p "${FONT_DIR}"

echo "Installing Inter Bold font..."
echo "Resolving latest Inter release archive..."

ZIP_URL="$(python3 - <<'PY'
import json
import re
import sys
import urllib.request

url = "https://api.github.com/repos/rsms/inter/releases/latest"
req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})

try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.load(resp)
except Exception:
    print("", end="")
    sys.exit(0)

for asset in data.get("assets", []):
    name = asset.get("name", "")
    download_url = asset.get("browser_download_url", "")
    if re.fullmatch(r"Inter-[0-9]+\.[0-9]+(\.[0-9]+)?\.zip", name):
        print(download_url)
        sys.exit(0)

print("", end="")
PY
)"

if [[ -z "${ZIP_URL}" ]]; then
  echo "ERROR: Could not find an Inter-<version>.zip asset in latest release metadata (${RELEASE_API_URL})." >&2
  exit 1
fi

echo "Downloading: ${ZIP_URL}"
curl --retry 3 --retry-delay 2 -fSL -o "${TMP_ZIP}" "${ZIP_URL}"

echo "Extracting ${FONT_NAME}..."
unzip -jo "${TMP_ZIP}" "Inter-*/ttf/${FONT_NAME}" -d "${FONT_DIR}" >/dev/null

if [[ -f "${FONT_PATH}" ]]; then
  echo "Installed: ${FONT_PATH}"
else
  echo "ERROR: ${FONT_PATH} not found after extraction" >&2
  exit 1
fi
