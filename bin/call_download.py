import sys
import os
import json
import logging
import traceback
import platform
from datetime import datetime

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

# Main Function
def main():
    try:
        # Load configurations
        platform_config = load_config()
        logger = init_logging(platform_config["logging"])

        # Add the `lib/python_utils` directory to sys.path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        lib_path = os.path.join(current_dir, "../lib/python_utils")
        sys.path.append(lib_path)
        logger.debug(f"Current sys.path: {sys.path}")

        # Attempt to import downloader5 and utilities1
        try:
            import downloader5
            import utilities1
        except ImportError as e:
            logger.error(f"Failed to import modules: {e}")
            sys.exit(1)

        # Set up paths
        target_usb = platform_config["target_usb"]
        download_date = datetime.now().strftime("%Y-%m-%d")
        download_path = os.path.join(target_usb, download_date)

        # Check if the USB is mounted and writable
        if not os.path.exists(target_usb):
            logger.error(f"Error: USB drive {target_usb} is not mounted.")
            sys.exit(1)
        
        if not os.path.exists(download_path):
            logger.warning(f"Download path {download_path} does not exist. Creating it now.")
            try:
                os.makedirs(download_path, exist_ok=True)
            except PermissionError:
                logger.error(f"Permission denied: Unable to create {download_path}")
                sys.exit(1)

        elif not os.access(download_path, os.W_OK):
            logger.error(f"Error: No write permission to {download_path}.")
            sys.exit(1)

        logger.info(f"Download directory confirmed: {download_path}")

        # Prepare parameters for function calls
        params = {
            "download_path": download_path,
            "cookie_path": platform_config.get("cookie_path"),
            "url": None,
            **platform_config.get("watermark_config", {}),
        }

        # Validate URL input
        if len(sys.argv) < 2:
            logger.error("The URL is missing. Please provide a valid URL as a command-line argument.")
            sys.exit(1)

        params["url"] = sys.argv[1].strip()

        # Execute function calls in sequence
        function_calls = [
            downloader5.mask_metadata,
            downloader5.create_original_filename,
            downloader5.download_video,
            utilities1.store_params_as_json,
        ]

        for func in function_calls:
            logger.info(f"Entering function: {func.__name__}")
            try:
                result = func(params)
                if result:
                    params.update(result)
            except Exception as e:
                logger.error(f"Error executing {func.__name__}: {e}")
                logger.debug(traceback.format_exc())

        # Output the original filename
        original_filename = params.get("original_filename", "")
        if original_filename:
            logger.info(f"Returning original filename: {original_filename}")
            print(original_filename)  # Print filename to stdout
            return original_filename
        else:
            logger.warning("No original filename to return.")
            return None

    except Exception as e:
        print(f"Unexpected error: {e}")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
