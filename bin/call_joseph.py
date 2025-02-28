import sys
import os
import json
import logging
import traceback
import platform
from datetime import datetime
import requests
from bs4 import BeautifulSoup

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

def download_josephus(download_path, logger):
    """Download the correct UTF-8 version of Josephus' works from Project Gutenberg."""
    josephus_url = "https://www.gutenberg.org/ebooks/2850"  # The main book page
    response = requests.get(josephus_url)

    if response.status_code != 200:
        logger.error("Failed to retrieve Josephus' book page.")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Look for the correct UTF-8 text file link
    text_link = soup.select_one("a[href*='txt.utf-8']")  # Most reliable selector

    if not text_link:
        logger.error("No UTF-8 text file found on the book page.")
        return
    
    text_url = "https://www.gutenberg.org" + text_link["href"]
    text_response = requests.get(text_url)

    if text_response.status_code == 200:
        filename = os.path.join(download_path, "Wars.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text_response.text)
        logger.info(f"Downloaded: {filename}")
    else:
        logger.error(f"Failed to download text file from {text_url}")

def main():
    try:
        # Load configurations
        platform_config = load_config()
        logger = init_logging(platform_config["logging"])

        # Set up paths
        target_usb = platform_config["target_usb"]
        download_date = datetime.now().strftime("%Y-%m-%d")
        download_path = os.path.join(target_usb, download_date)

        # Ensure USB is mounted and writable
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

        # Download Josephus' works
        download_josephus(download_path, logger)

    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
