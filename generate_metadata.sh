#!/bin/bash

SRC_DIR="tests/stamped3"
OUT_FILE="metadata.json"

echo "[" > "$OUT_FILE"

first=1

for file in "$SRC_DIR"/*.png; do
    # Extract full filename
    base=$(basename "$file")

    # Extract timestamp (first part of filename) and UUID part
    timestamp="${base%%_*}"
    uuid_name="${base#*_}"

    # Convert UNIX timestamp to ISO 8601 (UTC)
    iso_time=$(date -u -r "$timestamp" +"%Y-%m-%dT%H:%M:%SZ")

    # Comma between JSON objects, except before the first
    if [ $first -eq 0 ]; then
        echo "," >> "$OUT_FILE"
    fi
    first=0

    # Write JSON object
    cat <<EOF >> "$OUT_FILE"
  {
    "timestamp": $timestamp,
    "datetime": "$iso_time",
    "filename": "$uuid_name",
    "filepath": "$SRC_DIR/$base"
  }
EOF

done

echo "]" >> "$OUT_FILE"

echo "✅ JSON written to $OUT_FILE"


