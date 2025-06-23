#!/usr/bin/env python
"""Download a tar archive and extract a sorted file list using a config file."""
import json
import os
import sys
import subprocess
import tempfile

import requests


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

    tmp_fd, tmp_tar = tempfile.mkstemp(suffix=".tar")
    os.close(tmp_fd)
    download_file(url, tmp_tar)

    output_dir = os.path.join(download_path, "untarred")
    os.makedirs(output_dir, exist_ok=True)

    json_list = run_untar_and_list(tmp_tar, output_dir)
    print(json_list)


if __name__ == "__main__":
    main()
