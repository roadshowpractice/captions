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
    """Create a simple timeline JSON structure from ordered screenshots."""
    events = [
        {"label": s.get("filename"), "timestamp": s.get("timestamp_utc", s.get("timestamp"))}
        for s in screens
    ]
    return {"canvas": {"width": width, "height": height}, "events": events}
