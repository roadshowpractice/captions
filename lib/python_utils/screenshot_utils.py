import json
from datetime import datetime, timedelta, timezone
from typing import List, Dict

MST_OFFSET_HOURS = -7  # Idaho Mountain Standard Time offset from UTC

def load_screenshots(path: str) -> List[Dict]:
    """Load screenshot metadata from JSON."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def mst_to_utc(timestamp: str) -> str:
    """Convert 'YYYY-MM-DD HH:MM:SS' MST time to UTC ISO 8601."""
    local = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    local = local.replace(tzinfo=timezone(timedelta(hours=MST_OFFSET_HOURS)))
    return local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def convert_screenshots_to_utc(screens: List[Dict]) -> List[Dict]:
    """Return screenshots with added 'timestamp_utc' entries."""
    for entry in screens:
        ts = entry.get("timestamp")
        if ts:
            entry["timestamp_utc"] = mst_to_utc(ts)
    return screens


def save_screenshots(data: List[Dict], path: str) -> None:
    """Save screenshot metadata to JSON."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def build_timeline(screens: List[Dict], width: int = 1200, height: int = 800) -> Dict:
    """Create a timeline JSON compatible with ``timeline_compositor``.

    Each screenshot becomes a bar in a single track called ``screenshots``. The
    ``x`` positions are pre-calculated using the timestamps so that the timeline
    box spans from the first to the last screenshot.
    """

    if not screens:
        return {"canvas": {"width": width, "height": height}, "timeline_box": {"event_tracks": []}}

    # Parse timestamps in UTC and determine overall range
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    ordered = sorted(screens, key=lambda s: s.get("timestamp_utc", s.get("timestamp")))
    start_dt = datetime.strptime(ordered[0]["timestamp_utc"], fmt)
    end_dt = datetime.strptime(ordered[-1]["timestamp_utc"], fmt)
    total_seconds = max((end_dt - start_dt).total_seconds(), 1)

    box = {"x": 100, "y": 400, "width": width - 200, "height": 200, "color": "whitesmoke"}
    px_per_second = box["width"] / total_seconds

    bars = []
    for entry in ordered:
        dt = datetime.strptime(entry["timestamp_utc"], fmt)
        delta = (dt - start_dt).total_seconds()
        bars.append({
            "label": entry.get("filename"),
            "start": entry["timestamp_utc"],
            "end": entry["timestamp_utc"],
            "x": box["x"] + delta * px_per_second,
            "width": 2,
            "color": "#888888",
        })

    track = {
        "track": "screenshots",
        "label": "Screenshots",
        "y_axis": 0.5,
        "bar_height": 20,
        "bars": bars,
    }

    box["event_tracks"] = [track]
    canvas = {"width": width, "height": height, "timeline_box": box}
    return {"canvas": canvas}

