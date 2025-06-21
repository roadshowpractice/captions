# ==================================================
# teton_utils.py - Utility functions for video processing
# ==================================================

# --------------------------------------------------
# INSTRUCTIONS FOR ADDING A NEW FUNCTION:
# --------------------------------------------------
# 1. To add a new function, place it alphabetically in the list.
# 2. Be sure to write a brief description of the function's purpose in the comment.
# 3. The function's name should be clear and follow a consistent naming convention.
# 4. Do NOT number the function list manually; it should remain unnumbered and sorted alphabetically.
# 5. Always include the return type in the format "-> [return_type]" and specify what it returns.
#    Example: `def example_function() -> None:` or `def another_function() -> str:`.
# 6. After adding the function to the list, write the function definition below.
#    The function should have a detailed docstring explaining:
#    - What the function does.
#    - The parameters it accepts (with types).
#    - The return type.
#
# Function List:
#
# - create_original_filename(params: dict) -> dict
#    Generates an original filename for the video based on parameters and ensures a fallback name if uploader is missing.
#
# - create_output_directory(base_dir: str = "clips") -> str
#    Creates a timestamped output directory based on the video name.
#
# - create_subdir(base_dir: str = "clips", subdir_name: str = "orange") -> str
#    Creates a subdirectory with a custom name inside a timestamped folder based on the input video name.
#
# - download_video(params: dict) -> dict
#    Downloads a video from a given URL using yt-dlp.
#
# - extract_metadata(params: dict) -> dict
#    Extracts all available metadata from a YouTube video without downloading it and saves it to a file.
#
# - generate_minute_clips_to_yaml(json_metadata_path: str, output_yaml_path: str = None, interval_seconds: int = 60) -> str
#    Generate 1-minute interval clips based on metadata duration and save to a YAML file.
#
# - initialize_logging() -> logging.Logger
#    Initializes logging for the script.
#
# - load_app_config() -> dict
#    Load the application configuration from a JSON file.
#
# - load_config() -> dict
#    Load configuration based on the operating system.
#
# - mask_metadata(params: dict) -> dict
#    Masks certain metadata for privacy and returns the masked data.
#
# - store_params_as_json(params: dict) -> dict
#    Stores the params dictionary as a JSON file in the output directory. The filename should match the video file, but with a .json extension.
#
# - unique_output_path(path: str, filename: str) -> str
#    Generates a unique output file path by appending a counter to the filename if it already exists.
#


import os
import time
import logging
import json
import yt_dlp
from datetime import datetime
import sys
import platform

logger = logging.getLogger(__name__)


def create_original_filename(params: dict) -> dict:
    """
    Generates an original filename for the video based on parameters and ensures a fallback name if uploader is missing.

    Args:
        params (dict): The input dictionary containing relevant fields.

    Returns:
        dict: A dictionary containing the original filename.
    """
    # Extract the required fields from params
    download_path = params.get("download_path", "/Volumes/BallardTim/")
    video_uploader = params.get(
        "uploader", ""
    ).strip()  # Ensure it's a string and strip whitespace
    video_date = params.get("video_date", "").strip()

    # Ensure valid defaults if uploader or date is missing
    if not video_uploader:
        logger.warning("Uploader missing from metadata, using 'unknown_uploader'.")
        video_uploader = "unknown_uploader"

    if not video_date:
        logger.warning("Video date missing from metadata, using 'unknown_date'.")
        video_date = "unknown_date"

    # Format the uploader name to be filename-safe
    video_uploader_filename = video_uploader.replace(" ", "_").replace("/", "_")
    ext = params.get("ext", "mp4")  # Default to mp4 if not specified

    # Construct the output filename
    output_filename = f"{video_uploader_filename}_{video_date}.{ext}"

    # Generate a unique filename to avoid overwrites
    unique_filename = unique_output_path(download_path, output_filename)

    # Update params with the generated filename
    params["original_filename"] = unique_filename

    logger.info(f"Generated original filename: {unique_filename}")
    return {"original_filename": unique_filename}


def create_output_directory(base_dir="clips") -> str:
    """
    Creates a timestamped output directory based on the video name.

    Args:
        base_dir (str): Base directory to create the output directory in.

    Returns:
        str: Path to the created output directory.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_video_name = os.path.splitext(os.path.basename(sys.argv[1]))[0]
    output_dir = os.path.join(base_dir, f"{input_video_name}_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def create_subdir(base_dir="clips", subdir_name="orange") -> str:
    """
    Creates a subdirectory with a custom name inside a timestamped folder based on the input video name.

    Args:
        base_dir (str): Base directory to create the subdirectory in.
        subdir_name (str): Name of the subdirectory to create.

    Returns:
        str: Path to the created subdirectory.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_video_name = os.path.splitext(os.path.basename(sys.argv[1]))[0]
    root_output = os.path.join(base_dir, f"{input_video_name}_{timestamp}")

    subdir_timestamp = datetime.now().strftime("%H%M%S")
    full_subdir_name = f"{subdir_name}_{subdir_timestamp}"
    subdir_path = os.path.join(root_output, full_subdir_name)
    os.makedirs(subdir_path, exist_ok=True)
    return subdir_path

def download_video(params: dict) -> dict:
    """
    Downloads a video from a given URL using yt-dlp.

    Args:
        params (dict): Parameters for the download including:
            - url (str): Video URL.
            - video_download (dict): Video download configuration.

    Returns:
        dict: Path to the downloaded video, or None if download fails.
    """
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

        cookie_path = video_download_config.get("cookie_path")
        ydl_opts = {
            "outtmpl": params["original_filename"],
            "format": video_download_config.get("format", "bestvideo+bestaudio/best"),
            "noplaylist": video_download_config.get("noplaylist", True),
            "verbose": True,
        }

        # Only include the cookie file if it exists and is non-empty
        if cookie_path and os.path.isfile(cookie_path) and os.path.getsize(cookie_path) > 0:
            ydl_opts["cookiefile"] = cookie_path
            logger.info(f"✅ Using cookie file: {cookie_path}")
        else:
            logger.info("⚠️ No valid cookie file used.")

        logger.debug(f"yt-dlp options: {ydl_opts}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info("About to download video.")
            ydl.download([url])
            logger.info("Video download completed.")

        end_time = time.time()
        logger.info(f"Download completed in {end_time - start_time:.2f} seconds")

        return {"to_process": params["original_filename"]}

    except Exception as e:
        logger.error(f"❌ Error during download: {e}")
        traceback.print_exc()
        return None





def extract_metadata(params: dict) -> dict:
    """
    Extracts all available metadata from a video URL without downloading it and saves it to a file.

    Args:
        params (dict): Parameters for extracting metadata, including:
            - url (str): Video URL.
            - metadata_path (str): Path to save the metadata JSON file.
            - video_download (dict): Optional configuration including cookie_path.

    Returns:
        dict: A dictionary containing all available metadata about the video.
    """
    logger.info("Received parameters for metadata extraction:")
    for key, value in params.items():
        logger.info(f"{key}: {value}")

    url = params.get("url")
    metadata_path = params.get("metadata_path")
    video_download_config = params.get("video_download", {})

    try:
        ydl_opts = {
            "noplaylist": True,
            "skip_download": True,
        }

        cookie_path = video_download_config.get("cookie_path")
        if cookie_path and os.path.isfile(cookie_path) and os.path.getsize(cookie_path) > 0:
            ydl_opts["cookiefile"] = cookie_path
            logger.info(f"✅ Using cookie file: {cookie_path}")
        else:
            logger.info("⚠️ No valid cookie file used for metadata extraction.")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)

            if metadata_path:
                with open(metadata_path, "w", encoding="utf-8") as f:
                    json.dump(info_dict, f, indent=4, ensure_ascii=False)
                logger.info(f"Metadata saved to {metadata_path}")

            return info_dict
    except Exception as e:
        logger.error(f"Failed to extract metadata: {e}")
        return {}



def initialize_logging():
    log_dir = "./logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "tja.log")

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("%(asctime)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    logger.info("Logging initialized.")
    return logger



def load_app_config():
    """Load the application configuration from a JSON file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(current_dir, "../")

    if not os.path.exists(base_dir):
        raise FileNotFoundError(f"Base directory not found at {base_dir}")

    config_path = os.path.join(base_dir, "conf/app_config.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at {config_path}")

    try:
        with open(config_path, "r") as file:
            app_config = json.load(file)
        return app_config
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON configuration at {config_path}: {e}")




# Load Platform-Specific Configuration
def load_config():
    """Load configuration based on the operating system."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "../conf/config.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at {config_path}")

    with open(config_path, "r") as file:
        config = json.load(file)

    os_name = platform.system()
    if os_name not in config:
        raise ValueError(f"Unsupported platform: {os_name}")

    return config[os_name]


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

    # Extract metadata
    metadata = extract_metadata(params)  # ✅ Indented properly
    if metadata:
        normalized_metadata = {}

        key_mapping = {
            "video_title": ["title"],
            "video_date": ["upload_date"],
            "uploader": ["uploader", "uploader_id"],
            "file_path": ["file_path"],
            "duration": ["duration"],
            "width": ["width"],
            "height": ["height"],
            "ext": ["ext"],
            "resolution": ["resolution"],
            "fps": ["fps"],
            "channels": ["channels"],
            "filesize": ["filesize"],
            "tbr": ["tbr"],
            "protocol": ["protocol"],
            "vcodec": ["vcodec"],
            "vbr": ["vbr"],
            "acodec": ["acodec"],
            "abr": ["abr"],
            "asr": ["asr"],
        }

        # Normalize metadata values
        for standard_key, possible_keys in key_mapping.items():
            for key in possible_keys:
                if key in metadata:
                    normalized_metadata[standard_key] = metadata[key]
                    break  # Stop at the first found key

        # Process video title separately (replace spaces)
        if "video_title" in normalized_metadata:
            normalized_metadata["video_title"] = normalized_metadata[
                "video_title"
            ].replace(" ", "_")

        logger.info("Extracted and normalized metadata:")
        for key, value in normalized_metadata.items():
            logger.info(f"{key}: {value}")

        return normalized_metadata  # ✅ Now properly inside the function




# Function to store params as a JSON file in the output directory
def store_params_as_json(params):
    """
    Stores the params dictionary as a JSON file in the output directory.
    The filename should match the video file, but with a .json extension.

    Args:
        params (dict): The parameters dictionary to store.

    Returns:
        dict: A dictionary with key 'config_json' and value as the path of the JSON file.
    """
    try:
        original_filename = params.get("original_filename")
        if original_filename:
            json_filename = os.path.splitext(original_filename)[0] + ".json"
            with open(json_filename, "w") as json_file:
                json.dump(params, json_file, indent=4)
            logger.info(f"Params saved to JSON file: {json_filename}")
            return {"config_json": json_filename}
        else:
            logger.warning("No original filename found in params to create JSON file.")
            return {"config_json": None}
    except Exception as e:
        logger.error(f"Failed to save params to JSON: {e}")
        logger.debug(traceback.format_exc())
        return {"config_json": None}


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
