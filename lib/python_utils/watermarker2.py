import os
import logging
import traceback
import re

try:
    # MoviePy v2 style imports
    from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ColorClip, VideoClip
except ImportError:
    try:
        # MoviePy v1 style fallback
        from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip, VideoClip
    except ImportError:
        VideoFileClip = None
        TextClip = None
        CompositeVideoClip = None
        ColorClip = None
        VideoClip = None

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
    stroke_color = params.get("stroke_color", "black")
    stroke_width = int(params.get("stroke_width", 4) or 0)
    common_kwargs = {
        "color": color,
        "font": params["font"],
        "stroke_color": stroke_color,
        "stroke_width": stroke_width,
    }

    try:
        # MoviePy v2 API
        clip = TextClip(text=text, font_size=params["font_size"], **common_kwargs)
    except TypeError:
        try:
            # Older MoviePy API
            clip = TextClip(text, fontsize=params["font_size"], **common_kwargs)
        except TypeError:
            # Gracefully fallback if stroke args are unsupported in an older install.
            fallback_kwargs = {"color": color, "font": params["font"]}
            try:
                clip = TextClip(text=text, font_size=params["font_size"], **fallback_kwargs)
            except TypeError:
                clip = TextClip(text, fontsize=params["font_size"], **fallback_kwargs)

    text_pad = int(params.get("text_pad", 8) or 0)
    pad = max(text_pad, stroke_width * 2)

    if pad > 0 and hasattr(clip, "margin"):
        margined_clip = None
        try:
            margined_clip = clip.margin(mar=pad, color=None, opacity=0)
        except TypeError:
            # Some versions have margin with positional-only arguments.
            try:
                margined_clip = clip.margin(pad)
            except Exception:
                margined_clip = None
        except Exception:
            margined_clip = None

        if margined_clip is not None:
            clip = margined_clip

    if pad > 0 and not hasattr(clip, "margin"):
        width, height = clip.size
        canvas = ColorClip(size=(width + 2 * pad, height + 2 * pad), color=(0, 0, 0))
        if hasattr(canvas, "with_opacity"):
            canvas = canvas.with_opacity(0)
        else:
            canvas = canvas.set_opacity(0)

        centered = mp_with_position(clip, ("center", "center"))
        clip = CompositeVideoClip([canvas, centered], size=canvas.size)

    video_w = int(params.get("video_w", 0) or 0)
    if video_w > 0:
        quarter = video_w * 0.25
        half = video_w * 0.50
        target = int((quarter + half) / 2)
        target = int(params.get("watermark_target_width", target) or target)
        if clip.w > target and clip.w > 0:
            factor = target / clip.w
            clip = mp_resized(clip, factor=factor)

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


def mp_resized(clip, factor=None, width=None, height=None):
    """Resize clips across MoviePy v1/v2 naming differences."""
    if hasattr(clip, "resized"):
        return clip.resized(factor=factor, width=width, height=height)
    if hasattr(clip, "resize"):
        if factor is not None:
            return clip.resize(factor)
        if width is not None and height is None:
            return clip.resize(width=width)
        if height is not None and width is None:
            return clip.resize(height=height)
        return clip.resize(newsize=(width, height))
    raise AttributeError(f"{type(clip).__name__} has neither resized nor resize")


def looks_like_filename(value):
    if not value:
        return False
    text = str(value).strip()
    lowered = text.lower()
    basename = os.path.basename(lowered)
    return (
        "/" in text
        or "\\" in text
        or lowered.endswith((".mp4", ".mov", ".mkv", ".webm", ".avi"))
        or (lowered.startswith("http") and "/" in lowered)
        or basename in {"download", "downloaded", "videoplayback", "video", "file"}
        or bool(re.match(r"^(download|video)[\s_\-(\[]*\d+", basename))
    )


def _normalize_axis_position(value, clip_size, video_size, min_margin, max_margin):
    """Resolve a MoviePy position token/number into a clamped pixel coordinate."""
    max_position = max(video_size - clip_size, 0)
    max_with_margin = max(max_position - max_margin, 0)
    min_with_margin = min(max(min_margin, 0), max_position)

    if isinstance(value, str):
        token = value.lower().strip()
        if token in {"left", "top"}:
            return min_with_margin
        if token in {"right", "bottom"}:
            return max_with_margin
        if token in {"center", "middle"}:
            centered = max((video_size - clip_size) / 2, 0)
            return min(max(centered, min_with_margin), max_with_margin)

    try:
        numeric = float(value)
    except (TypeError, ValueError):
        # Fallback to a safe default rather than risking off-frame clipping.
        numeric = min_with_margin

    return min(max(numeric, min_with_margin), max_with_margin)


def _resolve_position(position, clip_size, video_size, edge_padding, safe_margins=None):
    """Convert configured position into explicit coordinates to avoid edge clipping."""
    if not isinstance(position, (list, tuple)) or len(position) != 2:
        position = ("left", "top")

    safe_margins = safe_margins or {}
    safe_left = int(safe_margins.get("left", edge_padding) or 0)
    safe_right = int(safe_margins.get("right", edge_padding) or 0)
    safe_top = int(safe_margins.get("top", edge_padding) or 0)
    safe_bottom = int(safe_margins.get("bottom", edge_padding) or 0)

    x = _normalize_axis_position(
        position[0], clip_size[0], video_size[0], safe_left, safe_right
    )
    y = _normalize_axis_position(
        position[1], clip_size[1], video_size[1], safe_top, safe_bottom
    )
    return (x, y)


def _build_dynamic_timestamp_clip(params, video, video_size, edge_padding, safe_margins):
    """Use one clip that updates timestamp text over time instead of prebuilding each second."""
    if VideoClip is None:
        return None

    cache = {}
    timestamp_color = params["timestamp_color"]
    timestamp_position = params["timestamp_position"]

    def _clip_for_second(second):
        if second not in cache:
            timestamp = f"{second // 3600:02}:{(second % 3600) // 60:02}:{second % 60:02}"
            text_clip = _build_text_clip(timestamp, params, timestamp_color)
            text_position = _resolve_position(
                timestamp_position, text_clip.size, video_size, edge_padding, safe_margins
            )
            text_clip = mp_with_position(text_clip, text_position)
            cache[second] = text_clip.get_frame(0)
        return cache[second]

    frame_builder = lambda t: _clip_for_second(int(t))

    try:
        timestamp_clip = VideoClip(make_frame=frame_builder)
    except TypeError:
        try:
            timestamp_clip = VideoClip(frame_function=frame_builder)
        except TypeError:
            timestamp_clip = VideoClip(frame_builder)

    timestamp_clip = mp_with_duration(timestamp_clip, video.duration)
    return timestamp_clip


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

    if VideoFileClip is None:
        raise RuntimeError("moviepy is required to add watermarks")

    for key, value in params.items():
        logger.debug(f"{key}: {value}")

    input_video_path = params.get("input_video_path")
    if not input_video_path:
        raise ValueError("Missing required parameter: 'input_video_path'")

    try:
        logger.info(f"Processing video: {input_video_path}")
        video = VideoFileClip(input_video_path)
        params["video_w"] = int(getattr(video, "w", 0) or 0)
        video_size = (int(getattr(video, "w", 0) or 0), int(getattr(video, "h", 0) or 0))
        edge_padding = int(params.get("screen_edge_padding", 8) or 0)
        # Safe margins keep overlays away from app/video-player UI controls.
        safe_margins = {
            "left": int(params.get("safe_margin_left", 20) or 0),
            "right": int(params.get("safe_margin_right", 20) or 0),
            "top": int(params.get("safe_margin_top", 20) or 0),
            "bottom": int(params.get("safe_margin_bottom", 120) or 0),
        }
        enable_timestamp = bool(params.get("enable_timestamp", True))

        # Create watermark text clips
        username_text = params.get("username", "")
        if username_text and not looks_like_filename(username_text):
            username_clip = _build_text_clip(
                username_text, params, params["username_color"]
            )
            username_position = _resolve_position(
                params["username_position"],
                username_clip.size,
                video_size,
                edge_padding,
                safe_margins,
            )
            username_clip = mp_with_position(username_clip, username_position)
            username_clip = mp_with_duration(username_clip, video.duration)
        else:
            if username_text and looks_like_filename(username_text):
                logger.warning("Username '%s' looked like a filename/path; skipping username watermark.", username_text)
            username_clip = None

        date_clip = _build_text_clip(
            params["video_date"], params, params["date_color"]
        )
        date_position = _resolve_position(
            params["date_position"], date_clip.size, video_size, edge_padding, safe_margins
        )
        date_clip = mp_with_position(date_clip, date_position)
        date_clip = mp_with_duration(date_clip, video.duration)

        timestamp_clip = None
        if enable_timestamp:
            timestamp_clip = _build_dynamic_timestamp_clip(
                params, video, video_size, edge_padding, safe_margins
            )

        layers = [video]
        if username_clip is not None:
            layers.append(username_clip)
        layers.append(date_clip)
        if timestamp_clip is not None:
            layers.append(timestamp_clip)

        final = CompositeVideoClip(layers)
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
