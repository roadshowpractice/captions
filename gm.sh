#!/bin/bash

SRC_DIR="tests/stamped3"
OUT_FILE="$SRC_DIR/metadata.json"

echo "[" > "$OUT_FILE"
first=1

for file in "$SRC_DIR"/*.{png,jpg,jpeg,JPG,PNG}; do
    [ -e "$file" ] || continue  # Skip if no matching file

    filename=$(basename "$file")
    extension="${filename##*.}"

    # Try to extract timestamp from filename
    if [[ "$filename" =~ ^([0-9]{10})_ ]]; then
        timestamp="${BASH_REMATCH[1]}"
    else
        # Use modification time if no timestamp prefix
        timestamp=$(stat -f "%m" "$file")
    fi

    # Convert to ISO 8601 format
    iso_time=$(date -u -r "$timestamp" +"%Y-%m-%dT%H:%M:%SZ")

    # Add comma between entries
    if [ $first -eq 0 ]; then
        echo "," >> "$OUT_FILE"
    fi
    first=0

    # Write JSON object
    cat <<EOF >> "$OUT_FILE"
  {
    "timestamp": $timestamp,
    "datetime": "$iso_time",
    "filename": "$filename",
    "filepath": "$file"
  }
EOF

done

echo "]" >> "$OUT_FILE"

echo "✅ metadata.json written to $OUT_FILE"

