import sys
import logging
import os
import tempfile
import time
import cv2
import numpy as np
import json


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


# ==================================================
# LOGGING INITIALIZATION
# ==================================================
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



# ==================================================
# SCREENSHOT CONFIGURATION
# ==================================================
config = {
    "screenshots_dir": "screenshots",  # Directory to save screenshots
    "screenshot_times": [1, 5, 10, 30],  # Times (in seconds) to capture screenshots from the video
    "screen_quality": [100],  # Highest quality for screenshots (0-100)
    "bilateral_filter_d": 9,  # Diameter for bilateral filter
    "bilateral_filter_sigma_color": 400,  # Increased sigma for stronger color filtering
    "bilateral_filter_sigma_space": 400,  # Increased sigma for stronger space filtering
    "median_blur_ksize": 5,  # Kernel size for median blur
    "adaptive_thresh_block_size": 9,  # Block size for adaptive thresholding
    "adaptive_thresh_C": 9,  # Constant C for adaptive thresholding
}

# ==================================================
# SCREENSHOT CAPTURE AND CARTOONIZING
# ==================================================
def capture_screenshots(video_path, config):
    """Capture screenshots at specified times."""
    video = cv2.VideoCapture(video_path)
    os.makedirs(config["screenshots_dir"], exist_ok=True)
    
    for time_sec in config["screenshot_times"]:
        video.set(cv2.CAP_PROP_POS_MSEC, time_sec * 1000)
        ret, frame = video.read()
        if ret:
            screenshot_path = os.path.join(config["screenshots_dir"], f"screenshot_{time_sec}.jpg")
            # Save the screenshot in BGR format (no conversion to RGB here)
            cv2.imwrite(screenshot_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), config["screen_quality"][0]])
            print(f"Saved screenshot: {screenshot_path}")
    video.release()

def cartoonize_image(image_path, config):
    """Apply exaggerated cartoon effect to an image."""
    img = cv2.imread(image_path)
    
    # Apply bilateral filter to reduce noise while keeping edges sharp (more exaggerated)
    img_filtered = cv2.bilateralFilter(img, config["bilateral_filter_d"], config["bilateral_filter_sigma_color"], config["bilateral_filter_sigma_space"])
    
    # Convert image to grayscale
    gray = cv2.cvtColor(img_filtered, cv2.COLOR_BGR2GRAY)
    
    # Apply median blur
    gray_blurred = cv2.medianBlur(gray, config["median_blur_ksize"])
    
    # Apply adaptive thresholding
    edges = cv2.adaptiveThreshold(gray_blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, config["adaptive_thresh_block_size"], config["adaptive_thresh_C"])
    
    # Combine edges with the filtered image
    cartoon = cv2.bitwise_and(img_filtered, img_filtered, mask=edges)
    
    # Exaggerate the cartoon effect by boosting color and contrast
    cartoon = cv2.convertScaleAbs(cartoon, alpha=1.5, beta=50)  # Increase contrast and brightness

    # Save the cartoonized image in BGR format (no conversion to RGB)
    cartoon_path = image_path.replace(".jpg", "_cartoon.jpg")
    cv2.imwrite(cartoon_path, cartoon)
    print(f"Saved cartoonized image: {cartoon_path}")



def process_screenshots(video_path, config):
    """Process screenshots and apply cartoon effect."""
    capture_screenshots(video_path, config)
    for time_sec in config["screenshot_times"]:
        screenshot_path = os.path.join(config["screenshots_dir"], f"screenshot_{time_sec}.jpg")
        cartoonize_image(screenshot_path, config)


# ==================================================
# MAIN EXECUTION
# ==================================================
if __name__ == "__main__":
    try:
        # Load app configuration
        app_config = load_app_config()
        logger = init_logging(app_config.get("logging", {}))

        # Add the `lib/python_utils` directory to sys.path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        lib_path = os.path.join(current_dir, "../lib/python_utils")
        sys.path.append(lib_path)
        logger.debug(f"Current sys.path: {sys.path}")

   

        # Validate input arguments
        if len(sys.argv) < 2:
            logger.error("Usage: python call_watermark.py <video_file_path>")
            sys.exit(1)

        input_video_path = sys.argv[1]
        if not os.path.isfile(input_video_path):
            logger.error(f"Input video file does not exist: {input_video_path}")
            sys.exit(1)

        logger.info(f"Processing video file: {input_video_path}")

        # Process screenshots and apply cartoonizing
        process_screenshots(input_video_path, config)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
