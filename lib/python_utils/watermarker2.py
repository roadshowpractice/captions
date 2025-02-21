import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
import logging
import traceback

# Use the logger configured in the caller
logger = logging.getLogger(__name__)

def get_codecs_by_extension(extension):
    """Determine codecs based on file extension."""
    codecs = {
        ".webm": {"video_codec": "libvpx", "audio_codec": "libvorbis"},
        ".mp4": {"video_codec": "libx264", "audio_codec": "aac"},
        ".ogv": {"video_codec": "libtheora", "audio_codec": "libvorbis"},
        ".mkv": {"video_codec": "libx264", "audio_codec": "aac"},
    }
    return codecs.get(extension, {"video_codec": "libx264", "audio_codec": "aac"})

def add_watermark(params):
    """
    Adds watermark text overlays to a video file.

    Args:
        params (dict): Parameters for adding watermark, including:
            - input_video_path (str): Path to the input video.
            - download_path (str): Directory to save the watermarked video.
            - username (str): Username to add as a watermark.
            - video_date (str): Date to add as a watermark.
            - font (str): Font type for watermark text.
            - font_size (int): Font size for watermark text.
            - username_color (str): Color of the username watermark text.
            - date_color (str): Color of the date watermark text.
            - timestamp_color (str): Color of the timestamp watermark text.
            - username_position (tuple): Position for username watermark.
            - date_position (tuple): Position for date watermark.
            - timestamp_position (tuple): Position for timestamp watermark.

    Returns:
        dict: A dictionary with the path to the watermarked video under 'to_process',
              or None if an error occurs.
    """
    logger.debug("Received parameters for watermarking.")
    for key, value in params.items():
        logger.debug(f"{key}: {value}")

    input_video_path = params.get("input_video_path")
    if not input_video_path:
        raise ValueError("Missing required parameter: 'input_video_path'")

    try:
        logger.info(f"Processing video: {input_video_path}")
        video = VideoFileClip(input_video_path)

        # Create watermark text clips
        username_clip = TextClip(
            params["username"],
            fontsize=params["font_size"],
            color=params["username_color"],
            font=params["font"],
        ).set_position(params["username_position"]).set_duration(video.duration)

        date_clip = TextClip(
            params["video_date"],
            fontsize=params["font_size"],
            color=params["date_color"],
            font=params["font"],
        ).set_position(params["date_position"]).set_duration(video.duration)

        # Generate timestamp clips
        timestamp_clips = []
        for t in range(int(video.duration)):
            timestamp = f"{t // 3600:02}:{(t % 3600) // 60:02}:{t % 60:02}"
            timestamp_clip = TextClip(
                timestamp,
                fontsize=params["font_size"],
                color=params["timestamp_color"],
                font=params["font"],
            ).set_position(params["timestamp_position"]).set_start(t).set_duration(1)
            timestamp_clips.append(timestamp_clip)

        final = CompositeVideoClip([video, username_clip, date_clip] + timestamp_clips)
        final = final.set_audio(video.audio)

        # Save the watermarked video
        filename, ext = os.path.splitext(os.path.basename(input_video_path))
        watermarked_video_path = os.path.join(
            params["download_path"], f"{filename}_watermarked{ext}"
        )
        codecs = get_codecs_by_extension(ext)
        logger.info(f"Exporting watermarked video to: {watermarked_video_path}")
        final.write_videofile(
            watermarked_video_path, codec=codecs["video_codec"], audio_codec=codecs["audio_codec"]
        )

        logger.info(f"Watermarked video saved to: {watermarked_video_path}")
        return {"to_process": watermarked_video_path}

    except Exception as e:
        logger.error(f"Error in add_watermark: {e}")
        logger.debug(traceback.format_exc())
        return None

