import os
import sys
import json
import logging
import traceback
from datetime import datetime
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip

#########

# Define log directory and ensure it exists
current_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(current_dir, "../log")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Log file path
log_file = os.path.join(log_dir, "call_captions.log")

# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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

logger.info("Logging setup complete.")

########

def analyze_video(video_path):
    """Analyze video attributes using MoviePy."""
    try:
        video = VideoFileClip(video_path)
        attributes = {
            "duration": video.duration,
            "fps": video.fps,
            "resolution": (video.w, video.h),
            "audio": video.audio is not None,
        }
        video.close()
        logger.debug(f"Video analysis complete: {attributes}")
        return attributes
    except Exception as e:
        logger.error(f"Error analyzing video: {e}")
        return {"error": str(e)}

def find_matching_json(video_path):
    """Find a JSON file with the same name as the video file."""
    json_path = os.path.splitext(video_path)[0] + ".json"
    if os.path.exists(json_path):
        logger.info(f"Matching JSON file found: {json_path}")
        return json_path
    else:
        logger.warning(f"No matching JSON file found for: {video_path}")
        return None

def parse_json(json_path):
    """Extract details from the JSON file."""
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        logger.info(f"Parsed JSON data for {json_path}: {json.dumps(data, indent=2)}")
        return data
    except Exception as e:
        logger.error(f"Error parsing JSON file: {e}")
        return {"error": str(e)}

def create_canvas(image_clip, canvas_size):
    """Center an image on a canvas matching the video resolution."""
    try:
        canvas = CompositeVideoClip([image_clip.set_position("center")], size=canvas_size)
        return canvas
    except Exception as e:
        logger.error(f"Error creating canvas for image: {e}")
        return None

def sequence_images(image_dir, video_resolution, video_duration):
    """Sequence images lexicographically and create a clip with canvases for mismatched sizes."""
    try:
        images = sorted([os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith((".png", ".jpg", ".jpeg"))])
        if not images:
            logger.error("No images found in the specified directory.")
            return None
        logger.info(f"Sequencing images: {images}")
        
        clips = []
        clip_duration = video_duration / len(images)
        for img in images:
            image_clip = ImageClip(img).set_duration(clip_duration)
            canvas = create_canvas(image_clip, video_resolution)
            clips.append(canvas)
        
        # Concatenate the canvas clips
        return CompositeVideoClip(clips).set_duration(video_duration)
    except Exception as e:
        logger.error(f"Error creating image sequence: {e}")
        return None

def overlay_images_on_video(video_path, image_dir, output_path):
    """Overlay sequenced images on the video."""
    try:
        video = VideoFileClip(video_path)
        video_resolution = (video.w, video.h)
        image_clip = sequence_images(image_dir, video_resolution, video.duration)
        if not image_clip:
            logger.error("Failed to create image sequence. Exiting overlay process.")
            return None
        # Composite the video and image sequence
        composite = CompositeVideoClip([video, image_clip])
        composite.write_videofile(output_path, codec="libx264", audio_codec="aac")
        logger.info(f"Overlay process complete. Output saved to: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error overlaying images on video: {e}")
        logger.debug(traceback.format_exc())
        return None

if __name__ == "__main__":
    try:
        # Validate input arguments
        if len(sys.argv) < 3:
            logger.error("Usage: python call_captions.py <video_file_path> <image_directory>")
            sys.exit(1)

        input_video_path = sys.argv[1]
        image_directory = sys.argv[2]

        if not os.path.isfile(input_video_path):
            logger.error(f"Input video file does not exist: {input_video_path}")
            sys.exit(1)

        if not os.path.isdir(image_directory):
            logger.error(f"Image directory does not exist: {image_directory}")
            sys.exit(1)

        logger.info(f"Processing video file: {input_video_path}")
        logger.info(f"Using image directory: {image_directory}")

        # Analyze video
        video_attributes = analyze_video(input_video_path)

        # Find and parse matching JSON file
        json_path = find_matching_json(input_video_path)
        json_data = parse_json(json_path) if json_path else None

        # Overlay images on the video
        output_video_path = os.path.join(os.path.dirname(input_video_path), "output_video.mp4")
        result = overlay_images_on_video(input_video_path, image_directory, output_video_path)

        if result:
            logger.info(f"Process completed successfully. Output video: {result}")
            print(result)
        else:
            logger.error("Overlay process failed.")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

