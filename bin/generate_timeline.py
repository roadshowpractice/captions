#!/usr/bin/env python3
"""Generate a timeline JSON from screenshot metadata."""
import json
import os
import sys
from typing import Dict

current_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.join(current_dir, "..", "lib", "python_utils")
sys.path.append(lib_dir)

from screenshot_utils import build_timeline


def generate_timeline(metadata_path: str, output_path: str) -> Dict:
    with open(metadata_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for entry in data:
        if "timestamp_utc" not in entry:
            entry["timestamp_utc"] = entry.get("datetime")

    timeline = build_timeline(data)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2)

    return timeline


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate timeline JSON")
    parser.add_argument("metadata", help="Expanded metadata JSON")
    parser.add_argument("output", help="Output timeline JSON")
    args = parser.parse_args()

    generate_timeline(args.metadata, args.output)
    print(args.output)


if __name__ == "__main__":
    main()
