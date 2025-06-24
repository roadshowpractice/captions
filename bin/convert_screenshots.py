#!/usr/bin/env python
"""Convert screenshot timestamps from MST to UTC and create a timeline."""
import sys
import os

# Ensure library path is available
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
lib_path = os.path.join(root_dir, "lib")
sys.path.append(lib_path)

from python_utils import screenshot_utils as su


def main(mst_json: str, output_dir: str = "metadata") -> None:
    screens = su.load_screenshots(mst_json)
    screens = su.convert_screenshots_to_utc(screens)
    utc_path = os.path.join(output_dir, "screenshot_times_utc.json")
    su.save_screenshots(screens, utc_path)

    timeline = su.build_timeline(screens)
    timeline_path = os.path.join(output_dir, "screenshot_timeline.json")
    with open(timeline_path, "w", encoding="utf-8") as f:
        import json
        json.dump(timeline, f, indent=2)

    print(utc_path)
    print(timeline_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: convert_screenshots.py <mst_json> [output_dir]")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "metadata")
