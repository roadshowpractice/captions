#!/usr/bin/env python
"""Download a tar archive and extract a sorted file list using a config file."""
import json
import os
import sys
import subprocess
import tempfile
import logging

import requests

# Add lib directory to Python path for shared utilities
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
lib_path = os.path.join(root_dir, "lib")
sys.path.append(lib_path)

from teton_utils import initialize_logging


def download_file(url: str, dest: str) -> str:
    """Download file from URL to destination path."""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return dest


def run_untar_and_list(tar_path: str, output_dir: str) -> str:
    """Run the provided untar_and_list script and return the JSON file path."""
    script = os.path.join(os.path.dirname(__file__), "untar_and_list.py")
    result = subprocess.run(
        [sys.executable, script, tar_path, output_dir],
        capture_output=True,
        text=True,
        check=True,
    )
    json_path = result.stdout.strip().splitlines()[-1]
    return json_path


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python call_untar_and_sort.py <config_json>")
        sys.exit(1)

    config_path = sys.argv[1]
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    url = data.get("url")
    download_path = data.get("download_path", "downloads")
    os.makedirs(download_path, exist_ok=True)

    logger = initialize_logging("call_untar_and_sort.log")
    logger.info("Starting tar download and extraction")

    tmp_fd, tmp_tar = tempfile.mkstemp(suffix=".tar")
    os.close(tmp_fd)
    logger.info(f"Downloading tar from {url}")
    download_file(url, tmp_tar)

    output_dir = os.path.join(download_path, "untarred")
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Extracting tar to {output_dir}")

    json_list = run_untar_and_list(tmp_tar, output_dir)
    logger.info(f"File list generated at {json_list}")
    print(json_list)


if __name__ == "__main__":
    main()
