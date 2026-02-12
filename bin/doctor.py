#!/usr/bin/env python
import importlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def load_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f), None
    except Exception as exc:
        return None, str(exc)


def check_imports():
    packages = [
        ("numpy", "numpy"),
        ("moviepy", "moviepy"),
        ("cv2", "opencv-python"),
        ("yt_dlp", "yt-dlp"),
        ("requests", "requests"),
    ]
    ok = True
    for module_name, package_name in packages:
        try:
            importlib.import_module(module_name)
            print(f"[OK] import {module_name}")
        except Exception as exc:
            ok = False
            print(f"[ERR] import {module_name} failed ({package_name}): {exc}")
    return ok


def check_dir(label: str, path_value: str):
    try:
        os.makedirs(path_value, exist_ok=True)
        writable = os.access(path_value, os.W_OK)
        if writable:
            print(f"[OK] {label}: {path_value} exists and is writable")
            return True
        print(f"[ERR] {label}: {path_value} exists but is not writable")
        return False
    except Exception as exc:
        print(f"[ERR] {label}: failed to create/check {path_value}: {exc}")
        return False


def check_ffmpeg():
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        print("[ERR] ffmpeg not found on PATH")
        return False

    try:
        result = subprocess.run([ffmpeg_bin, "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] ffmpeg available: {ffmpeg_bin}")
            return True
        print(f"[ERR] ffmpeg returned non-zero exit code: {result.returncode}")
        return False
    except Exception as exc:
        print(f"[ERR] unable to execute ffmpeg: {exc}")
        return False


def resolve_output_dir(config):
    return config.get("output_dir") or config.get("target_usb")


def main():
    repo_root = Path(__file__).resolve().parent.parent
    app_config_path = repo_root / "conf" / "app_config.json"
    config_path = repo_root / "conf" / "config.json"

    app_config, app_error = load_json(app_config_path)
    platform_config_map, platform_error = load_json(config_path)

    status = True

    if app_error:
        print(f"[ERR] malformed app config {app_config_path}: {app_error}")
        return 1
    print(f"[OK] loaded app config: {app_config_path}")

    if platform_error:
        print(f"[ERR] malformed platform config {config_path}: {platform_error}")
        return 1
    print(f"[OK] loaded platform config: {config_path}")

    platform_name = "Darwin" if sys.platform == "darwin" else "Linux"
    platform_config = platform_config_map.get(platform_name)
    if not platform_config:
        print(f"[ERR] missing platform section '{platform_name}' in {config_path}")
        return 1

    output_dir = resolve_output_dir(platform_config)
    metadata_dir = app_config.get("metadata_dir")

    if not output_dir:
        print("[ERR] output_dir missing in conf/config.json (target_usb fallback also empty)")
        status = False
    else:
        status = check_dir("output_dir", output_dir) and status

    if not metadata_dir:
        print("[ERR] metadata_dir missing in conf/app_config.json")
        status = False
    else:
        status = check_dir("metadata_dir", metadata_dir) and status

    status = check_imports() and status
    status = check_ffmpeg() and status

    print("[OK] doctor completed" if status else "[ERR] doctor found issues")
    return 0 if status else 2


if __name__ == "__main__":
    raise SystemExit(main())
