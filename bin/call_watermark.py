import os
import sys
import json
import logging
import traceback
import platform
from datetime import datetime


## this routine needs to be locked in
# Load Application Configuration
def load_app_config():
    """Load the application configuration from a JSON file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(current_dir, "../")
    
    if not os.path.exists(base_dir):
        # Squeaky error message if the base directory doesn't exist
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

# Initialize Logging
def init_logging(logging_config):
    """Set up logging based on the configuration."""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if logging_config.get("log_to_file"):
        log_file = os.path.expanduser(logging_config["log_filename"])
        log_dir = os.path.dirname(log_file)

        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging_config.get("level", "DEBUG"))
        file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    if logging_config.get("log_to_console"):
        console_handler = logging.StreamHandler(stream=sys.stderr)
        console_handler.setLevel(logging_config.get("console_level", "INFO"))
        console_formatter = logging.Formatter("%(asctime)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    logger.info("Logging initialized.")
    return logger


def looks_like_filename(value):
    if not value:
        return False
    text = str(value)
    return (
        "/" in text
        or "\\" in text
        or text.lower().endswith((".mp4", ".mov", ".mkv", ".webm", ".avi"))
    )

if __name__ == "__main__":
    try:
        # Load app configuration
        app_config = load_app_config()
        watermark_config = app_config.get("watermark_config", {})
        logger = init_logging(app_config.get("logging", {}))

        # Add the `lib/python_utils` directory to sys.path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        lib_path = os.path.join(current_dir, "../lib/python_utils")
        sys.path.append(lib_path)
        logger.debug(f"Current sys.path: {sys.path}")

        # Attempt to import the watermarking function
        try:
            from watermarker2 import add_watermark
        except ImportError as e:
            logger.error(f"Failed to import add_watermark: {e}")
            sys.exit(1)

        # Validate input arguments
        if len(sys.argv) < 2:
            logger.error("Usage: python call_watermark.py <video_file_path>")
            sys.exit(1)

        input_video_path = sys.argv[1]
        if not os.path.isfile(input_video_path):
            logger.error(f"Input video file does not exist: {input_video_path}")
            sys.exit(1)

        logger.info(f"Processing video file: {input_video_path}")

        # Locate and read metadata JSON
        base_name = os.path.splitext(input_video_path)[0]
        json_path = f"{base_name}.json"
        logger.info(f"Looking for metadata file: {json_path}")

        if not os.path.isfile(json_path):
            logger.error(f"Metadata file not found: {json_path}")
            sys.exit(1)

        try:
            with open(json_path, "r") as file:
                data = json.load(file)
            logger.info(f"Loaded metadata from: {json_path}")
            username = data.get("uploader", "")
            if looks_like_filename(username):
                logger.warning("Metadata uploader looks like a filename; skipping username watermark.")
                username = ""
            # this field changes insta uses upload_date ; yt uses upload_date
            video_date = data.get("video_date", datetime.now().strftime("%Y-%m-%d"))
            #video_date = data.get("upload_date", datetime.now().strftime("%Y-%m-%d"))
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON metadata from {json_path}: {e}")
            sys.exit(1)

        # Prepare parameters for watermarking.
        # Use a copied config and apply explicit overrides once to avoid duplicate keys.
        merged_watermark_config = dict(watermark_config)
        params = {
            **merged_watermark_config,
            "input_video_path": input_video_path,
            "download_path": os.path.dirname(input_video_path),
            "username": username,
            "video_date": video_date,
        }

        # Debugging appconfig
        logger.debug(f"Watermark configuration: {watermark_config}")

        # Start watermarking
        logger.info("Starting watermarking process...")
        result = add_watermark(params)

        if result and "to_process" in result:
            logger.info(f"Watermarked video created successfully: {result['to_process']}")
            print(result["to_process"])
        else:
            logger.error("Watermarking process failed or did not return valid output.")
            sys.exit(1)

    except Exception as e:
        # Fallback to `print` if `logger` is not defined
        if 'logger' in globals():
            logger.error(f"An unexpected error occurred: {e}")
            logger.debug(traceback.format_exc())
        else:
            print(f"Unexpected error: {e}")
            print(traceback.format_exc())
        sys.exit(1)
