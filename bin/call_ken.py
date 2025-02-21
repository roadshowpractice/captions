import os
import sys
import traceback
from PIL import Image, ImageEnhance
from moviepy.editor import (
    VideoFileClip,
    ImageClip,
    CompositeVideoClip,
    ColorClip,
    concatenate_videoclips,
)
import logging
import json
import platform


def initialize_logging(config):
    """Set up logging based on configuration."""
    log_dir = config["log_dir"]
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "call_ken.log")

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(asctime)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    logger.info("Logging setup complete.")
    return logger


def clear_resize_directory(resize_dir):
    """Clear all files in the resize directory."""
    try:
        if os.path.exists(resize_dir):
            for file in os.listdir(resize_dir):
                file_path = os.path.join(resize_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        else:
            os.makedirs(resize_dir, exist_ok=True)
    except Exception as e:
        raise RuntimeError(f"Error clearing resize directory: {e}")


def get_video_resolution(video_path):
    """Get the resolution of the video."""
    try:
        clip = VideoFileClip(video_path)
        resolution = clip.size
        clip.close()
        return resolution
    except Exception as e:
        raise RuntimeError(f"Error getting video resolution: {e}")


def resize_images(image_dir, output_dir, video_resolution, brightness, border):
    """Resize images to fit the video resolution."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        video_width, video_height = video_resolution
        resized_images = []

        images = [
            os.path.join(image_dir, f)
            for f in sorted(os.listdir(image_dir))
            if f.endswith((".png", ".jpg", ".jpeg"))
        ]

        for img_path in images:
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
                canvas.paste(
                    img,
                    ((video_width - new_width) // 2, (video_height - new_height) // 2),
                )

                enhancer = ImageEnhance.Brightness(canvas)
                canvas = enhancer.enhance(brightness)

                output_path = os.path.join(output_dir, os.path.basename(img_path))
                canvas.save(output_path, format="JPEG")
                resized_images.append(output_path)

        return resized_images
    except Exception as e:
        raise RuntimeError(f"Error resizing images: {e}")


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
        raise RuntimeError(f"Error creating slideshow: {e}")


def overlay_images_on_video(video_path, image_dir, output_path, video_resolution, brightness, border, slide_length):
    """Overlay resized images as a Ken Burns effect on the video."""
    try:
        resized_dir = "/tmp/resized_images"
        clear_resize_directory(resized_dir)

        images = resize_images(image_dir, resized_dir, video_resolution, brightness, border)
        if not images:
            raise RuntimeError("No resized images to overlay.")

        slideshow = create_slideshow(images, slide_length, video_resolution)
        if not slideshow:
            raise RuntimeError("Failed to create slideshow.")

        video = VideoFileClip(video_path)
        composite = CompositeVideoClip([video, slideshow.set_start(0)])
        composite.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)

    except Exception as e:
        raise RuntimeError(f"Error overlaying images on video: {e}")


def load_config():
    """Load platform-specific configuration."""
    config_path = os.path.join(os.path.dirname(__file__), "../conf/config.json")
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r") as f:
        config = json.load(f)

    platform_name = platform.system()
    platform_config = config.get(platform_name)
    if not platform_config:
        raise ValueError(f"Unsupported platform: {platform_name}.")
    return platform_config


if __name__ == "__main__":
    try:
        platform_config = load_config()
        logger = initialize_logging(platform_config)

        if len(sys.argv) < 2:
            logger.error("Usage: python call_ken.py <input_video_path>")
            sys.exit(1)

        input_video_path = sys.argv[1]
        output_video_path = os.path.splitext(input_video_path)[0] + "_kenburns.mp4"

        ken_burns_config = platform_config.get("ken_burns", {})
        slide_length = ken_burns_config.get("slide_length", 9)
        brightness = ken_burns_config.get("brightness", 1.3)
        border = ken_burns_config.get("border", 0.03)
        image_dir = platform_config["image_dir"]

        video_resolution = get_video_resolution(input_video_path)
        overlay_images_on_video(
            input_video_path, image_dir, output_video_path, video_resolution, brightness, border, slide_length
        )

        logger.info(f"Ken Burns effect applied. Output saved to {output_video_path}")
        print(output_video_path)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

