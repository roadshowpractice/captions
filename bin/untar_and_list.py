#!/usr/bin/env python
"""Extract a tar archive and output a JSON list of sorted files."""
import json
import os
import sys
import tarfile


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: python untar_and_list.py <tar_path> [output_dir] [json_output]"
        )
        sys.exit(1)

    tar_path = sys.argv[1]
    output_dir = (
        sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(tar_path)[0]
    )
    json_output = (
        sys.argv[3]
        if len(sys.argv) > 3
        else os.path.join(output_dir, "file_list.json")
    )

    os.makedirs(output_dir, exist_ok=True)

    with tarfile.open(tar_path, "r:*") as tar:
        tar.extractall(output_dir)

    collected = []
    for root, _, files in os.walk(output_dir):
        for name in files:
            rel = os.path.relpath(os.path.join(root, name), output_dir)
            collected.append(rel)

    collected.sort()

    with open(json_output, "w", encoding="utf-8") as f:
        json.dump(collected, f, indent=2)

    print(json_output)


if __name__ == "__main__":
    main()
