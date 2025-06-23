#!/usr/bin/env python
import sys
import os
import json
import logging

current_dir = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.join(current_dir, "../lib/python_utils")
sys.path.append(lib_path)

from timeline_compositor import compose_timeline_with_images


def main():
    if len(sys.argv) < 4:
        print(
            "Usage: python composite_timeline.py <timeline_json> <mapping_json> <output_image>"
        )
        sys.exit(1)

    timeline_json = sys.argv[1]
    mapping_json = sys.argv[2]
    output_image = sys.argv[3]

    logging.basicConfig(level=logging.INFO)
    with open(mapping_json, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    compose_timeline_with_images(timeline_json, mapping, output_image)
    print(output_image)


if __name__ == "__main__":
    main()
