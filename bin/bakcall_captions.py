import os
import sys
import json
import traceback
import logging

def initialize_logging(config):
    log_dir = config.get("log_dir", "./logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "call_captions.log")
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(asctime)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    logger.info("Logging initialized.")
    return logger

def load_source_text(source_path):
    """Load source text for captions from the provided file."""
    try:
        with open(source_path, 'r') as file:
            return file.read().strip()
    except Exception as e:
        logger.error(f"Error loading source text from {source_path}: {e}")
        sys.exit(1)
        
def load_app_config():
    """Load configuration from app_config.json."""
    try:
        config_path = "./conf/app_config.json"
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found at {config_path}")
        with open(config_path, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        app_config = load_app_config()
        captions_config = app_config.get("captions", {})
        logger = initialize_logging(app_config)
        # Extract clips from the configuration
        clips = app_config.get("captions", {}).get("clips", [])
        if not clips:
            logger.warning("No clips found in the configuration.")
        else:
            logger.info(f"Clips extracted from configuration: {clips}")

        if len(sys.argv) < 2:
            logger.error("Usage: python caller_script.py <video_file_path>")
            sys.exit(1)

        input_video_path = sys.argv[1]
        captions_config["input_video_path"] = input_video_path
        captions_config["download_path"] = os.path.dirname(input_video_path)
              
        # Add the `lib/python_utils` directory to sys.path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        lib_path = os.path.join(current_dir, "../lib/python_utils")
        sys.path.append(lib_path)
        logger.debug(f"Current sys.path: {sys.path}")

        # Load source text from file for captions
        source_path = captions_config.get("source_path")
        if source_path:
            captions_config["paragraph"] = load_source_text(source_path)
        else:
            logger.error("No source_path found in captions configuration.")
            sys.exit(1)

        from basic_captions3 import add_captions
        result = add_captions(captions_config)

        if result:
            logger.info(f"Captioning completed successfully. Output video: {result['to_process']}")
        else:
            logger.error("Captioning failed.")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

