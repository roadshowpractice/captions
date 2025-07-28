#!/usr/bin/env python3
"""Expand screenshot metadata with identity labels."""
import json
import os
from typing import List, Dict


def expand_metadata(metadata_path: str, identity_map_path: str, output_path: str) -> List[Dict]:
    """Load metadata JSON, attach identity info, and save to output."""
    with open(metadata_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # identity map may map by filename or filepath
    if os.path.exists(identity_map_path):
        with open(identity_map_path, "r", encoding="utf-8") as f:
            id_map = json.load(f)
    else:
        id_map = {}

    for entry in data:
        fname = entry.get("filename")
        fpath = entry.get("filepath")
        identity = id_map.get(fname) or id_map.get(fpath) or "unknown"
        entry["identity"] = identity

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return data


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Expand screenshot metadata")
    parser.add_argument("metadata", help="Input metadata JSON")
    parser.add_argument("identity_map", help="Mapping file with identity info")
    parser.add_argument("output", help="Output expanded metadata JSON")
    args = parser.parse_args()

    expand_metadata(args.metadata, args.identity_map, args.output)
    print(args.output)


if __name__ == "__main__":
    main()
