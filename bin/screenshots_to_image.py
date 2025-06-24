#!/usr/bin/env python
"""Create a timeline image from screenshot metadata."""
import sys
import os
import json

# Ensure library path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
lib_path = os.path.join(root_dir, "lib")
sys.path.append(lib_path)

from python_utils import screenshot_utils as su
from python_utils.timeline_compositor import compose_timeline_with_images


def main(mst_json: str, image_dir: str, output_dir: str = "metadata") -> None:
    screens = su.load_screenshots(mst_json)
    screens = su.convert_screenshots_to_utc(screens)
    os.makedirs(output_dir, exist_ok=True)

    utc_path = os.path.join(output_dir, "screenshot_times_utc.json")
    su.save_screenshots(screens, utc_path)

    timeline = su.build_timeline(screens)
    timeline_path = os.path.join(output_dir, "screenshot_timeline.json")
    with open(timeline_path, "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2)

    mapping = {s["filename"]: os.path.join(image_dir, s["filename"]) for s in screens}
    image_path = os.path.join(output_dir, "screenshot_timeline.png")
    compose_timeline_with_images(timeline_path, mapping, image_path)

    print(utc_path)
    print(timeline_path)
    print(image_path)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: screenshots_to_image.py <mst_json> <image_dir> [output_dir]")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "metadata")

