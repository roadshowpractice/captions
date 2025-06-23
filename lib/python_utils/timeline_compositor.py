import os
import json
import logging
from typing import Dict, Optional
from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)


def _load_json(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Timeline JSON not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _create_canvas(canvas_data: dict) -> Image.Image:
    width = canvas_data.get("width", 800)
    height = canvas_data.get("height", 600)
    bg_color = canvas_data.get("outer_background", {}).get("color", "white")
    logger.debug(f"Creating canvas {width}x{height} with color {bg_color}")
    return Image.new("RGB", (width, height), bg_color)


def _draw_timeline_box(img: Image.Image, box: dict) -> ImageDraw.ImageDraw:
    draw = ImageDraw.Draw(img)
    x = box.get("x", 0)
    y = box.get("y", 0)
    width = box.get("width", img.width)
    height = box.get("height", 100)
    color = box.get("color", "white")
    draw.rectangle([x, y, x + width, y + height], fill=color)
    return draw


def compose_timeline_with_images(
    timeline_json: str,
    image_map: Optional[Dict[str, str]] = None,
    output_path: str = "timeline_output.png",
) -> str:
    """Create a composite timeline image using the provided JSON and images.

    Args:
        timeline_json: Path to the timeline JSON definition.
        image_map: Optional mapping of event labels to image file paths.
        output_path: Where to save the final image.
    Returns:
        Path to the saved image.
    """
    data = _load_json(timeline_json)
    canvas_data = data.get("canvas", {})
    timeline_box = canvas_data.get("timeline_box", {})
    img = _create_canvas(canvas_data)
    draw = _draw_timeline_box(img, timeline_box)

    event_tracks = timeline_box.get("event_tracks", [])
    for track in event_tracks:
        y_axis = int(timeline_box.get("y", 0) + track.get("y_axis", 0) * timeline_box.get("height", 0))
        bar_height = track.get("bar_height", 20)
        for bar in track.get("bars", []):
            x_pos = int(timeline_box.get("x", 0) + bar.get("x", 0))
            width = int(bar.get("width", 0))
            color = bar.get("color", "#000000")
            draw.rectangle([x_pos, y_axis, x_pos + width, y_axis + bar_height], fill=color)
            label = bar.get("label")
            if image_map and label in image_map:
                path = image_map[label]
                try:
                    event_img = Image.open(path).convert("RGBA")
                    event_img.thumbnail((bar_height * 3, bar_height * 3))
                    img.paste(event_img, (x_pos, y_axis - event_img.height - 4), event_img)
                except Exception as exc:
                    logger.warning(f"Failed to load image '{path}': {exc}")

    img.save(output_path)
    logger.info(f"Timeline composite saved to {output_path}")
    return output_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create a composite timeline image")
    parser.add_argument("timeline_json", help="Path to timeline JSON file")
    parser.add_argument("mapping_json", help="JSON file mapping event labels to images")
    parser.add_argument("output_image", help="Output image file")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    mapping = _load_json(args.mapping_json)
    compose_timeline_with_images(args.timeline_json, mapping, args.output_image)
    print(args.output_image)
