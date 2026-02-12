import os
import logging
import traceback

try:
    # MoviePy v2 style imports
    from moviepy import VideoFileClip, TextClip, CompositeVideoClip
except ImportError:
    # MoviePy v1 style fallback
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

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

def _build_text_clip(text, params, color):
    # Build TextClip with padding to prevent font clipping
    common_kwargs = {"color": color, "font": params["font"]}

    try:
        # MoviePy v2 API
        clip = TextClip(text=text, font_size=params["font_size"], **common_kwargs)
    except TypeError:
        # Older MoviePy API
        clip = TextClip(text, fontsize=params["font_size"], **common_kwargs)

    # Transparent padding (fixes clipped ascenders)
    pad = int(params.get("text_pad", 8))

    if pad > 0:
        # Prefer built-in margin helpers when available.
        if hasattr(clip, "margin"):
            clip = clip.margin(top=pad, bottom=pad, left=pad, right=pad, opacity=0)
        elif hasattr(clip, "with_margin"):
            clip = clip.with_margin(top=pad, bottom=pad, left=pad, right=pad, opacity=0)
        else:
            # MoviePy 2.1.x can expose TextClip without margin helpers.
            # Fall back to wrapping in a transparent canvas to emulate padding.
            width, height = clip.size
            clip = clip.on_color(
                size=(width + 2 * pad, height + 2 * pad),
                color=(0, 0, 0),
                col_opacity=0,
                pos=("center", "center"),
            )

    return clip


def mp_call(obj, old, new, *args, **kwargs):
    """Call a MoviePy method across v1 (old) and v2 (new) APIs."""
    if hasattr(obj, new):
        return getattr(obj, new)(*args, **kwargs)
    if hasattr(obj, old):
        return getattr(obj, old)(*args, **kwargs)
    raise AttributeError(
        f"Object of type {type(obj).__name__} has neither '{new}' nor '{old}'"
    )


def mp_with_position(clip, position):
    return mp_call(clip, "set_position", "with_position", position)


def mp_with_duration(clip, duration):
    return mp_call(clip, "set_duration", "with_duration", duration)


def mp_with_start(clip, start):
    return mp_call(clip, "set_start", "with_start", start)


def mp_with_audio(clip, audio):
    return mp_call(clip, "set_audio", "with_audio", audio)


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
        username_clip = _build_text_clip(
            params["username"], params, params["username_color"]
        )
        username_clip = mp_with_position(username_clip, params["username_position"])
        username_clip = mp_with_duration(username_clip, video.duration)

        date_clip = _build_text_clip(
            params["video_date"], params, params["date_color"]
        )
        date_clip = mp_with_position(date_clip, params["date_position"])
        date_clip = mp_with_duration(date_clip, video.duration)

        # Generate timestamp clips
        timestamp_clips = []
        for t in range(int(video.duration)):
            timestamp = f"{t // 3600:02}:{(t % 3600) // 60:02}:{t % 60:02}"
            timestamp_clip = _build_text_clip(
                timestamp, params, params["timestamp_color"]
            )
            timestamp_clip = mp_with_position(
                timestamp_clip, params["timestamp_position"]
            )
            timestamp_clip = mp_with_start(timestamp_clip, t)
            timestamp_clip = mp_with_duration(timestamp_clip, 1)
            timestamp_clips.append(timestamp_clip)

        final = CompositeVideoClip([video, username_clip, date_clip] + timestamp_clips)
        final = mp_with_audio(final, video.audio)

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
