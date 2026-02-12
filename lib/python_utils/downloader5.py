# downloader5.py
# mask_metadata calls extract_metadata
# works with 10.caller.py
# adding logging

import yt_dlp
import requests
import os
import json
import traceback
import time
import logging
import gzip

####################
# Logger setup
# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
###########################








def unique_output_path(path, filename):
    """
    Generates a unique output file path by appending a counter to the filename if it already exists.

    Args:
        path (str): Directory path.
        filename (str): Original filename.

    Returns:
        str: A unique file path.
    """
    base, ext = os.path.splitext(filename)
    counter = 1
    unique_filename = filename
    while os.path.exists(os.path.join(path, unique_filename)):
        unique_filename = f"{base}_{counter}{ext}"
        counter += 1
    return os.path.join(path, unique_filename)


def extract_metadata(params):
    """
    Extracts all available metadata from a YouTube video without downloading it and saves it to a file.

    Args:
        params (dict): Parameters for extracting metadata, including:
            - url (str): Video URL.
            - metadata_path (str): Path to save the metadata JSON file.
            - cookie_path (str): Path to the cookie file (optional).

    Returns:
        dict: A dictionary containing all available metadata about the video.
    """
    logger.info("Received parameters for metadata extraction:")
    for key, value in params.items():
        logger.info(f"{key}: {value}")

    url = params.get("url")
    cookie_path = params.get("cookie_path")
    metadata_path = params.get("metadata_path")

    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.join(current_dir, "../../")
        config_path = os.path.join(base_dir, "conf/app_config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            app_config = json.load(f)
    except Exception as e:
        logger.warning(f"Could not read app_config.json: {e}")
        app_config = {}

    metadata_dir = app_config.get("metadata_dir", "./metadata")
    os.makedirs(metadata_dir, exist_ok=True)

    try:
        # Set up yt-dlp options for extracting metadata
        ydl_opts = {
            "cookiefile": (
                cookie_path if cookie_path and os.path.exists(cookie_path) else None
            ),
            "noplaylist": True,  # Ensure only the single video is processed if the URL is a playlist
            "skip_download": True,  # Skip actual video download
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(
                url, download=False
            )  # Extract metadata without downloading

            video_identifier = (
                info_dict.get("id")
                or info_dict.get("display_id")
                or info_dict.get("webpage_url_basename")
                or str(int(time.time()))
            )

            if not metadata_path:
                # Use video ID/shortcode naming instead of timestamp-based filenames.
                filename = f"{video_identifier}.json"
                metadata_path = unique_output_path(metadata_dir, filename)
                params["metadata_path"] = metadata_path

            index_record = {
                "url": url,
                "metadata_file": os.path.basename(metadata_path),
                "id": info_dict.get("id"),
                "shortcode": info_dict.get("display_id") or info_dict.get("webpage_url_basename"),
            }

            index_path = os.path.join(metadata_dir, "index.jsonl")
            with open(index_path, "a", encoding="utf-8") as index_file:
                index_file.write(json.dumps(index_record, ensure_ascii=False) + "\n")

            raw_mode = app_config.get("raw_metadata_mode", "gzip")
            if raw_mode in {"gzip", "json"}:
                raw_dir = os.path.join(metadata_dir, "raw")
                os.makedirs(raw_dir, exist_ok=True)
                if raw_mode == "gzip":
                    raw_path = os.path.join(raw_dir, f"{video_identifier}.json.gz")
                    with gzip.open(raw_path, "wt", encoding="utf-8") as raw_file:
                        json.dump(info_dict, raw_file, indent=2, ensure_ascii=False)
                else:
                    raw_path = os.path.join(raw_dir, f"{video_identifier}.json")
                    with open(raw_path, "w", encoding="utf-8") as raw_file:
                        json.dump(info_dict, raw_file, indent=2, ensure_ascii=False)
                params["raw_metadata_path"] = raw_path

            # Save metadata to file
            if metadata_path:
                with open(metadata_path, "w", encoding="utf-8") as f:
                    json.dump(info_dict, f, indent=4, ensure_ascii=False)
                logger.info(f"Metadata saved to {metadata_path}")

            return info_dict
    except Exception as e:
        logger.error(f"Failed to extract metadata: {e}")
        logger.debug(traceback.format_exc())
        return {}


# New function to mask metadata
def mask_metadata(params):
    """
    Masks certain metadata for privacy and returns the masked data.

    Args:
        params (dict): The input dictionary containing metadata.

    Returns:
        dict: A dictionary containing masked metadata fields.
    """
    logger.info("Masking metadata")
    masked_metadata = {}

    # Call the extract_metadata function to get video information
    metadata = extract_metadata(params)
    if metadata:
        # Original fields to be filtered
        filtered_metadata_keys = [
            "title",
            "upload_date",
            "uploader",
            "file_path",
            "duration",
            "width",
            "height",
        ]

        # Adding new fields based on your request
        new_metadata_keys = [
            "id",
            "ext",
            "resolution",
            "fps",
            "channels",
            "filesize",
            "tbr",
            "protocol",
            "vcodec",
            "vbr",
            "acodec",
            "abr",
            "asr",
        ]

        # Combine original fields with new fields
        filtered_metadata_keys.extend(new_metadata_keys)

        # Filter metadata to only include the specified keys
        filtered_metadata = {
            key: metadata.get(key) for key in filtered_metadata_keys if key in metadata
        }

        logger.info("Extracted metadata:")
        for key, value in filtered_metadata.items():
            logger.info(f"{key}: {value}")

        # Masking filtered metadata fields and replacing spaces with underscores
        if "title" in filtered_metadata:
            masked_metadata["video_title"] = filtered_metadata["title"].replace(
                " ", "_"
            )
        if "upload_date" in filtered_metadata:
            masked_metadata["video_date"] = filtered_metadata["upload_date"]
        if "uploader" in filtered_metadata:
            masked_metadata["uploader"] = filtered_metadata["uploader"]
        if "file_path" in filtered_metadata:
            masked_metadata["file_path"] = filtered_metadata["file_path"]
        if "duration" in filtered_metadata:
            masked_metadata["duration"] = filtered_metadata["duration"]
        if "width" in filtered_metadata:
            masked_metadata["width"] = filtered_metadata["width"]
        if "height" in filtered_metadata:
            masked_metadata["height"] = filtered_metadata["height"]

        # Adding the new fields to the masked metadata
        for key in new_metadata_keys:
            if key in filtered_metadata:
                masked_metadata[key] = filtered_metadata[key]

    logger.info("Metadata masking complete")
    return masked_metadata


def get_codecs_by_extension(extension):
    # Determine codecs based on file extension
    codecs = {
        ".webm": {"video_codec": "libvpx", "audio_codec": "libvorbis"},
        ".mp4": {"video_codec": "libx264", "audio_codec": "aac"},
        ".ogv": {"video_codec": "libtheora", "audio_codec": "libvorbis"},
        ".mkv": {"video_codec": "libx264", "audio_codec": "aac"},
    }
    return codecs.get(extension, {"video_codec": "libx264", "audio_codec": "aac"})


def create_original_filename(params):
    """
    Generates an original filename for the video based on parameters and returns it as a dictionary.

    Args:
        params (dict): The input dictionary containing relevant fields.

    Returns:
        dict: A dictionary containing the original filename.
    """
    # Extract the required fields from params
    download_path = params.get("download_path", "/Volumes/BallardTim/")
    video_uploader = params.get("uploader", "unknown_uploader")
    video_date = params.get("video_date", "unknown_date")

    # Generate the filename using the uploader, date, and extension
    # Replace spaces and slashes when constructing the filename
    video_uploader_filename = video_uploader.replace(" ", "_").replace("/", "_")
    ext = params.get("ext", "mp4")  # Default to mp4 if not specified
    output_filename = f"{video_uploader_filename}_{video_date}.{ext}"
    
    # Generate a unique filename to avoid overwrites
    unique_filename = unique_output_path(download_path, output_filename)

    # Update params with the generated filename
    params["original_filename"] = unique_filename

    logger.info(f"Generated original filename: {unique_filename}")
    return {"original_filename": unique_filename}



def download_video(params):
    """
    Downloads a video from a given URL using yt-dlp.

    Args:
        params (dict): Parameters for the download including:
            - url (str): Video URL.
            - video_download (dict): Video download configuration.

    Returns:
        str: The path to the downloaded video, or None if download fails.
    """
    # Log incoming parameters for diagnostics
    logger.info("Received parameters: download_video:")
    for key, value in params.items():
        logger.info(f"{key}: {value}")

    url = params.get("url")
    video_download_config = params.get("video_download", {})

    if not url:
        logger.error("No URL provided for download.")
        return None

    try:
        start_time = time.time()
        logger.info(f"Starting download for URL: {url}")

        # Set up yt-dlp options for actual download based on video_download_config
        ydl_opts = {
            "outtmpl": params["original_filename"],
            "cookiefile": video_download_config.get("cookie_path"),
            "format": video_download_config.get("format", "bestvideo+bestaudio/best"),
            "noplaylist": video_download_config.get("noplaylist", True),
            "verbose": True,
        }

        logger.debug(f"yt-dlp options: {ydl_opts}")

        # Perform the video download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info("About to download video.")
            ydl.download([url])
            logger.info("Video download completed.")

        end_time = time.time()
        logger.info(f"Download completed in {end_time - start_time:.2f} seconds")
        #save params
        #save_params_to_json(params)
        return {"to_process": params["original_filename"]}
    except Exception as e:
        logger.error(f"Failed to download video: {e}")
        logger.debug(traceback.format_exc())
        return None
        

def save_params_to_json(params):
    """
    Saves the parameters as a .json file in the same output directory.

    Args:
        params (dict): Dictionary containing all parameters.
    """
    try:
        # Get the output filename and create the JSON filename by changing the extension to .json
        original_filename = params.get("original_filename")
        if not original_filename:
            logger.error("No original filename found in parameters. Unable to save JSON.")
            return

        # Replace the extension with .json
        json_filename = os.path.splitext(original_filename)[0] + ".json"

        # Save the parameters to a JSON file
        with open(json_filename, "w", encoding="utf-8") as json_file:
            json.dump(params, json_file, indent=4, ensure_ascii=False)

        logger.info(f"Parameters saved to JSON file: {json_filename}")
    except Exception as e:
        logger.error(f"Failed to save parameters to JSON: {e}")
        logger.debug(traceback.format_exc())


