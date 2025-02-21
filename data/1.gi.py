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

def run_gstreamer(input_file, start_time, end_time, output_file):
    # Create a GStreamer pipeline that copies the video and audio streams without re-encoding
    pipeline = Gst.parse_launch(f'filesrc location={input_file} ! decodebin name=dec '
                                f'! queue ! videoconvert ! video/x-raw ! mp4mux name=mux ! filesink location={output_file} '
                                f'dec. ! queue ! audioconvert ! audio/x-raw ! audioresample ! mux.')

    # Get the source element (filesrc) and set the start time
    source = pipeline.get_by_name('filesrc0')

    # Set the start time (in seconds)
    source.set_property('start-time', start_time * Gst.SECOND)
    
    # Set the end time (in seconds) by controlling the EOS event after the given duration
    pipeline.set_state(Gst.State.PLAYING)
    
    # Wait for the pipeline to finish or reach the end of the specified time range
    pipeline.get_bus().poll(Gst.MessageType.EOS, Gst.CLOCK_TIME_NONE)
    
    pipeline.set_state(Gst.State.NULL)


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
        clips_config = app_config.get("captions", {})
        clips_config["input_video_path"] = input_video_path
        clips_config["download_path"] = os.path.dirname(input_video_path)

        # Process clips using GStreamer
        for clip in clips:
            start_time, end_time = clip
            output_file = f"{os.path.splitext(input_video_path)[0]}_clip_{int(start_time)}_{int(end_time)}.mp4"
            logger.info(f"Processing clip: {start_time}-{end_time} to {output_file}")
            run_gstreamer(input_video_path, start_time, end_time, output_file)

        logger.info("Clips processing completed.")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        logger.debug(traceback.format_exc())
        sys.exit(1)
