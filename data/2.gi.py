import os
import sys
import json
import traceback
import logging
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

# Initialize GStreamer
Gst.init(None)

def initialize_logging(config):
    log_dir = config.get("log_dir", "./logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "call_gstreamer.log")
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

def load_app_config():
    """Load configuration from app_config.json."""
    try:
        config_path = "../conf/app_config.json"
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found at {config_path}")
        with open(config_path, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

def run_gstreamer(input_file, start_time, end_time, output_file, logger):
    try:
        # Create the GStreamer pipeline for video and audio processing
        pipeline = Gst.parse_launch(f'filesrc location={input_file} ! decodebin name=dec '
                                    f'! queue ! videoconvert ! x264enc ! video/x-h264 ! mp4mux name=mux ! filesink location={output_file} '
                                    f'dec. ! queue ! audioconvert ! audio/x-raw ! audioresample ! faac ! mux.')

        # Get the bus for the pipeline to interact with GStreamer
        bus = pipeline.get_bus()

        # Start the pipeline in the PAUSED state
        pipeline.set_state(Gst.State.PAUSED)

        # Wait for preroll (initial buffering)
        pipeline.get_state(Gst.CLOCK_TIME_NONE)

        # Seek the pipeline to the start_time (in seconds)
        success = pipeline.seek(1.0, Gst.Format.TIME, Gst.SeekFlags.FLUSH, Gst.SeekType.SET, start_time * Gst.SECOND, end_time * Gst.SECOND)
        if not success:
            logger.error(f"Failed to seek to {start_time} seconds.")
        else:
            logger.info(f"Sent seek event to start at {start_time} seconds.")

        # Set the pipeline to playing state to start processing
        pipeline.set_state(Gst.State.PLAYING)

        # Wait until the specified end time is reached or the end of stream (EOS) is received
        bus.poll(Gst.MessageType.EOS, Gst.CLOCK_TIME_NONE)

        # Set the pipeline to NULL after processing
        pipeline.set_state(Gst.State.NULL)

    except Exception as e:
        logger.error(f"Error processing video clip: {e}")
        logger.debug(traceback.format_exc())

if __name__ == "__main__":
    try:
        app_config = load_app_config()
        logger = initialize_logging(app_config)

        # Extract clips from the configuration
        clips = app_config.get("captions", {}).get("clips", [])
        logger.info(f"Clips found in configuration: {clips}")

        if not clips:
            logger.warning("No clips found in the configuration.")
        else:
            logger.info(f"Clips extracted from configuration: {clips}")
            logger.debug(f"Detailed clips info: {json.dumps(clips, indent=2)}")

        if len(sys.argv) < 2:
            logger.error("Usage: python caller.py <video_file_path>")
            sys.exit(1)

        input_video_path = sys.argv[1]
        clips_config = app_config.get("captions", 
