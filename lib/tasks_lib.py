import os
import json
import logging


def find_url_json(url, metadata_dir="./metadata"):
    """Search metadata directory for a JSON file whose 'url' field matches."""
    if not os.path.isdir(metadata_dir):
        return None, None

    for name in os.listdir(metadata_dir):
        if not name.endswith(".json"):
            continue
        path = os.path.join(metadata_dir, name)
        try:
            with open(path, "r") as fh:
                data = json.load(fh)
            if data.get("url") == url:
                return path, data
        except Exception as e:
            logging.warning(f"Failed to parse {path}: {e}")
    return None, None
