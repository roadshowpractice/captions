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
        
# Load Application Configuration
def load_app_config():
    """Load the application configuration from a JSON file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(current_dir, "../")
    
    if not os.path.exists(base_dir):
        # Squeaky error message if the base directory doesn't exist
        raise FileNotFoundError(f"Base directory not found at {base_dir}. Please ensure the directory structure is correct.")
    
    config_path = os.path.join(base_dir, "conf/app_config.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    
    try:
        with open(config_path, "r") as file:
            app_config = json.load(file)
        return app_config
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON configuration at {config_path}: {e}")

if __name__ == "__main__":
    try:
        app_config = load_app_config()
        captions_config = app_config.get("captions", {})
        logger = initialize_logging(app_config)

        if len(sys.argv) < 2:
            logger.error("Usage: python caller_script.py <video_file_path> [<source_text_file_path>]")
            sys.exit(1)

        input_video_path = sys.argv[1]
        captions_config["input_video_path"] = input_video_path
        captions_config["download_path"] = os.path.dirname(input_video_path)
              
        # Add the `lib/python_utils` directory to sys.path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        lib_path = os.path.join(current_dir, "../lib/python_utils")
        sys.path.append(lib_path)
        logger.debug(f"Current sys.path: {sys.path}")

        # Use ARGV2 as source_path if provided, otherwise fallback to config
        if len(sys.argv) > 2:
            source_path = sys.argv[2]
            logger.info(f"Using source text from command line argument: {source_path}")
        else:
            source_path = captions_config.get("source_path")
            if source_path:
                logger.info(f"Using source text from config: {source_path}")
            else:
                logger.error("No source_path provided in arguments or configuration.")
                sys.exit(1)

        captions_config["paragraph"] = load_source_text(source_path)

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

