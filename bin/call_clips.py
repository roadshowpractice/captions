import os
import sys
import logging
import subprocess


# Set the GST_DEBUG environment variable
os.environ['GST_DEBUG'] = '4'


# ==================================================
# CLIPS CONFIGURATION 
# ==================================================
# This dictionary contains all the necessary configuration.
# We define the input video, output directory, and clip settings directly.
# Global configuration for video processing with GStreamer
gstreamer_config = {
    "input_video_path": "data/Liberating_Humanity_Podcast_20241004_1_watermarked.mkv",  # Path to the input video
    "clips_directory": "clips/",  # Directory where clips will be stored
    "width": 1280,  # Video width
    "height": 720,  # Video height
    "font": "Arial",  # Font used for overlay text
    "font_size": 32,  # Font size for overlay text
    "alignment": {"horizontal": 1, "vertical": 1},  # Text alignment settings (1 = center)
    "encoder": "x264enc",  # GStreamer encoder
    "container_format": "mp4mux",  # Output format (e.g., MP4)
    "text_halign": "left",  # Horizontal alignment
    "text_valign": "center",  # Vertical alignment
}

# Clips: List of clips to process with individual properties
clips = [
    {
        "start": 3,  # Clip start time (in seconds)
        "end": 10,   # Clip end time (in seconds)
        "text": "First clip",  # Text to overlay on the video
        "name": "clip_1"  # Name of the clip file
    },
    {
        "start": 11,
        "end": 20,
        "text": "Second clip",
        "name": "clip_2"
    }
]

# ==================================================
# LOGGING INITIALIZATION
# ==================================================
# Sets up logging to both console and a log file.
# This helps track processing steps and errors.
def initialize_logging():
    log_dir = "./logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "call_clips.log")

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # File logging
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console logging
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(asctime)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    logger.info("Logging initialized.")
    return logger


# ==================================================
# PROCESSING CLIPS WITH GSTREAMER
# ==================================================
# Ensure the clips directory exists
def ensure_clips_directory(clips_directory):
    if not os.path.exists(clips_directory):
        os.makedirs(clips_directory)
        logger.info(f"Created clips directory: {clips_directory}")

# PROCESSING CLIPS WITH GSTREAMER
def process_clips_gstreamer(gstreamer_config, clips, logger):
    """Processes clips using GStreamer."""
    input_video = gstreamer_config["input_video_path"]
    clips_directory = gstreamer_config["clips_directory"]
    font = gstreamer_config["font"]
    font_size = gstreamer_config["font_size"]
    width = gstreamer_config["width"]
    height = gstreamer_config["height"]
    text_halign = gstreamer_config["text_halign"]
    text_valign = gstreamer_config["text_valign"]
    
    # Log global config values
    logger.info(f"Processing video: {input_video}")
    logger.info(f"Output directory: {clips_directory}")
    logger.info(f"Font: {font} (Size: {font_size})")
    logger.info(f"Video Resolution: {width}x{height}")
    
    # Ensure the clips directory exists
    ensure_clips_directory(clips_directory)
    
    # Iterate through clips and process each one
    for clip in clips:
        start, end, text, name = clip["start"], clip["end"], clip["text"], clip["name"]
        output_file = os.path.join(clips_directory, f"{name}.mp4")
        
        # Text alignment settings based on configuration
        halignment = text_halign  # left, center, right
        valignment = text_valign  # top, middle, bottom

        # Log the clip-specific values
        logger.info(f"Clip Name: {name}")
        logger.info(f"Clip Start Time: {start}")
        logger.info(f"Clip End Time: {end}")
        logger.info(f"Text to Overlay: {text}")
        logger.info(f"Output File: {output_file}")
        logger.info(f"Font: {font}, Font Size: {font_size}")
        logger.info(f"Text Alignment: Horizontal - {halignment}, Vertical - {valignment}")
        logger.info(f"Width: {width}, Height: {height}")
        
        # GStreamer command to process the clip
        gst_command = [
            "gst-launch-1.0",
            "filesrc", f"location={input_video}",
            "!", "decodebin",
            "!", "videoconvert",
            "!", "videoscale",
            "!", f'capsfilter', f'caps="video/x-raw,width={width},height={height}"',
            "!", "textoverlay",
            f"text={text}",
            f"font-desc={font} {font_size}",
            f"halignment={halignment}",
            f"valignment={valignment}",
            "!", gstreamer_config["encoder"],
            "!", gstreamer_config["container_format"],
            "!", "filesink", f"location={output_file}"
        ]
        
        # Log the GStreamer command being executed
        logger.info(f"GStreamer command: {' '.join(gst_command)}")

        # Run the GStreamer command inside a try-except block
        try:
            result = subprocess.run(gst_command, capture_output=True, text=True, check=True)
            
            # Print stdout and stderr
            logger.info("GStreamer command stdout:")
            logger.info(result.stdout)
            if result.stderr:
                logger.error("GStreamer command stderr:")
                logger.error(result.stderr)
            
            logger.info(f"Clip {name} processed successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error occurred while processing clip {name}.")
            logger.error(f"Return code: {e.returncode}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")


#main

# Initialize logger
logger = initialize_logging()

# Run the GStreamer processing routine
process_clips_gstreamer(gstreamer_config, clips, logger)
