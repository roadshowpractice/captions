#!/usr/bin/env python
"""Download images listed in a JSON file from Google Drive."""
import json
import os
import sys
from typing import List

import requests

GOOGLE_DRIVE_DOWNLOAD_URL = "https://drive.google.com/uc?export=download"


def extract_drive_id(url: str) -> str:
    """Extract the file ID from a Google Drive share link."""
    if "/d/" in url:
        return url.split("/d/")[1].split("/")[0]
    raise ValueError(f"Cannot extract file id from URL: {url}")


def get_confirm_token(response: requests.Response) -> str:
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value
    return ""


def save_response_content(response: requests.Response, destination: str) -> None:
    chunk_size = 32768
    with open(destination, "wb") as f:
        for chunk in response.iter_content(chunk_size):
            if chunk:
                f.write(chunk)


def download_file(file_id: str, dest_path: str) -> None:
    session = requests.Session()
    response = session.get(
        GOOGLE_DRIVE_DOWNLOAD_URL, params={"id": file_id}, stream=True
    )
    token = get_confirm_token(response)
    if token:
        params = {"id": file_id, "confirm": token}
        response = session.get(GOOGLE_DRIVE_DOWNLOAD_URL, params=params, stream=True)
    save_response_content(response, dest_path)


def download_from_json(json_path: str, output_dir: str) -> List[str]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    urls = data.get("gdrive_urls", [])
    if not urls:
        raise ValueError("No 'gdrive_urls' found in JSON file")

    os.makedirs(output_dir, exist_ok=True)
    downloaded = []

    for url in urls:
        file_id = extract_drive_id(url)
        dest_file = os.path.join(output_dir, file_id)
        download_file(file_id, dest_file)
        downloaded.append(dest_file)
        print(f"Downloaded {dest_file}")

    return downloaded


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python download_images.py <link_json> [output_dir]")
        sys.exit(1)

    link_json = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "downloaded_images"
    download_from_json(link_json, output_dir)


if __name__ == "__main__":
    main()
