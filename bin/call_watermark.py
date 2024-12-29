import os
import sys
import json
import logging
import traceback
from datetime import datetime  # Corrected import

#########
# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Define log directory and ensure it exists
current_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(current_dir, "../log")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Log file path
log_file = os.path.join(log_dir, "call_watermark.log")

# File handler for persistent logs
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Console handler for immediate feedback
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(asctime)s - %(message)s")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)
########

lib_path = os.path.abspath(os.path.join(current_dir, "../lib/python_utils"))
if lib_path not in sys.path:
    sys.path.append(lib_path)
    logger.info(f"Added library path: {lib_path}")

try:
    # Import the watermarking function
    from watermarker2 import add_watermark
except ImportError as e:
    logger.error(f"Failed to import add_watermark: {e}")
    sys.exit(1)

logger.info("Watermarking script started.")

if __name__ == "__main__":
    try:
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
            username = data.get("uploader", "UnknownUploader")
            video_date = data.get("upload_date", datetime.now().strftime("%Y-%m-%d"))
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON metadata from {json_path}: {e}")
            sys.exit(1)

        # Prepare parameters for watermarking
        download_path = os.path.dirname(input_video_path)
        params = {
            "input_video_path": input_video_path,
            "download_path": download_path,
            "username": username,
            "video_date": video_date,
            "font": "Arial-Bold",
            "font_size": 48,
            "username_color": "yellow",
            "date_color": "cyan",
            "timestamp_color": "red",
            "username_position": ("left", "top"),
            "date_position": ("left", "bottom"),
            "timestamp_position": ("right", "bottom"),
        }

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
        logger.error(f"An unexpected error occurred: {e}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

