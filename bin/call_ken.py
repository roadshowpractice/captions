import os
import sys
import traceback
from PIL import Image, ImageEnhance
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, ColorClip, concatenate_videoclips
import logging

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




def clear_resize_directory(resize_dir):
    """Clear all files in the resize directory on startup."""
    try:
        if os.path.exists(resize_dir):
            for file in os.listdir(resize_dir):
                file_path = os.path.join(resize_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logger.info(f"Removed file: {file_path}")
            logger.info(f"Cleared all files in the resize directory: {resize_dir}")
        else:
            logger.info(f"Resize directory does not exist. Creating: {resize_dir}")
            os.makedirs(resize_dir, exist_ok=True)
    except Exception as e:
        logger.error(f"Error clearing resize directory: {e}")
        raise


def get_video_resolution(video_path):
    """Get the resolution of the video."""
    try:
        clip = VideoFileClip(video_path)
        resolution = clip.size
        clip.close()
        return resolution
    except Exception as e:
        logger.error(f"Error getting video resolution: {e}")
        return None


def resize_images(image_dir, output_dir, video_resolution, brightness=1.0, border=0.03):
    """
    Resize images to fit within the given video resolution while maintaining aspect ratio.
    Adjust brightness and add border if specified.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        video_width, video_height = video_resolution
        resized_images = []

        def extract_number(filename):
            try:
                return int(''.join(filter(str.isdigit, filename)) or 0)
            except ValueError:
                logger.warning(f"Filename '{filename}' does not contain valid numbers.")
                return 0

        images = [
            os.path.join(image_dir, f)
            for f in sorted(os.listdir(image_dir), key=extract_number)
            if f.endswith((".png", ".jpg", ".jpeg"))
        ]

        num_digits = len(str(len(images)))
        for idx, img_path in enumerate(images):
            with Image.open(img_path) as img:
                img_ratio = img.width / img.height
                video_ratio = video_width / video_height
                border_width = int(video_width * border)
                border_height = int(video_height * border)

                if img_ratio > video_ratio:
                    new_width = video_width - 2 * border_width
                    new_height = int(new_width / img_ratio)
                else:
                    new_height = video_height - 2 * border_height
                    new_width = int(new_height * img_ratio)

                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                canvas = Image.new("RGB", (video_width, video_height), (0, 0, 0))
                canvas.paste(img, ((video_width - new_width) // 2, (video_height - new_height) // 2))

                enhancer = ImageEnhance.Brightness(canvas)
                canvas = enhancer.enhance(brightness)

                padded_name = f"{str(idx + 1).zfill(num_digits)}.jpeg"
                output_path = os.path.join(output_dir, padded_name)
                canvas.save(output_path, format="JPEG")
                resized_images.append(output_path)

        return resized_images
    except Exception as e:
        logger.error(f"Error resizing images: {e}")
        return None



def create_slideshow(image_files, slide_length, video_resolution):
    """Create a slideshow from resized images."""
    try:
        clips = []
        for img_path in image_files:
            img_clip = ImageClip(img_path).set_duration(slide_length).set_position("center")
            canvas = ColorClip(video_resolution, color=(0, 0, 0)).set_duration(slide_length)
            composite = CompositeVideoClip([canvas, img_clip])
            clips.append(composite)

        return concatenate_videoclips(clips, method="compose")
    except Exception as e:
        logger.error(f"Error creating slideshow: {e}")
        return None


def overlay_images_on_video(video_path, image_dir, output_path, video_resolution):
    """
    Overlay resized images on the video.
    """
    try:
        resized_dir = "/tmp/resized_images"
        clear_resize_directory(resized_dir)

        images = resize_images(image_dir, resized_dir, video_resolution)
        if not images:
            logger.error("No resized images to overlay.")
            return

        slideshow = create_slideshow(images, slide_length, video_resolution=video_resolution)
        if not slideshow:
            logger.error("Failed to create slideshow.")
            return

        video = VideoFileClip(video_path)
        composite = CompositeVideoClip([video, slideshow.set_start(0)])
        composite.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)

        logger.info(f"Overlay process complete. Output saved to: {output_path}")
    except Exception as e:
        logger.error(f"Error overlaying images on video: {e}")

if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print("Usage: python script.py <input_video_path>")
            sys.exit(1)

        # Input parameters
        input_video_path = sys.argv[1]
        slide_length = 9  # Example slide duration
        brightness = 1.1  # Brightness adjustment
        border = 0.03  # 3% border
        image_dir = "/Users/mymac/Desktop/pics"
        resize_dir = "resized_images"  # Output resized images directory
        output_video_path = "/Users/mymac/Desktop/1.output_video.mp4"  # Output video

        # Clear the resize directory on startup
        clear_resize_directory(resize_dir)

        print("Determining video resolution...")
        video_resolution = get_video_resolution(input_video_path)
        if not video_resolution:
            print("Could not determine video resolution. Exiting.")
            sys.exit(1)

        # Resize images and check results
        resized_files = resize_images(image_dir, resize_dir, video_resolution, brightness, border)
        if not resized_files:
            print("No images resized. Exiting.")
            sys.exit(1)

        # Create slideshow and overlay
        logger.info("Starting slideshow creation...")
        slideshow = create_slideshow(resized_files, slide_length, video_resolution)
        if not slideshow:
            print("Slideshow creation failed. Exiting.")
            sys.exit(1)

        logger.info("Overlaying slideshow on video...")
        overlay_images_on_video(input_video_path, resize_dir, output_video_path, video_resolution)

        print(f"Video processing complete. Output saved to {output_video_path}")

    except Exception as e:
        print(f"Unexpected error: {e}")
        print(traceback.format_exc())

