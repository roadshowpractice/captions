import os
import re
import json
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip


# Helper Function: Get codecs based on file extension
def get_codecs_by_extension(extension):
    codecs = {
        ".webm": {"video_codec": "libvpx", "audio_codec": "libvorbis"},
        ".mp4": {"video_codec": "libx264", "audio_codec": "aac"},
        ".ogv": {"video_codec": "libtheora", "audio_codec": "libvorbis"},
        ".mkv": {"video_codec": "libx264", "audio_codec": "aac"},
    }
    return codecs.get(extension, {"video_codec": "libx264", "audio_codec": "aac"})


# Helper Function: Replace newlines with spaces
def convert_newlines_to_spaces(text):
    return text.replace("\n", "                      ")


# Captioning Function
def add_captions(params, logger=None):
    try:
        if logger:
            logger.info("Initializing captioning process...")

        input_name = params["input_video_path"]
        download_path = params["download_path"]
        paragraph = convert_newlines_to_spaces(params["paragraph"])
        max_char_width = params.get("max_char_width", 65)
        next_line_pause = params.get("next_line", 1.7)
        overall_start = params.get("overall_start", 2)

        video_clip = VideoFileClip(input_name)

        # Split paragraph into readable lines
        lines = []
        words = re.split(r'(\s+)', paragraph)
        index = 0
        while index < len(words):
            line = words[index]
            next_index = index + 1
            while next_index < len(words) and len(line) + len(words[next_index]) + 1 <= max_char_width:
                line += ' ' + words[next_index]
                next_index += 1
            lines.append(line)
            index = next_index

        # Determine video dimensions and orientation
        video_width, video_height = video_clip.size
        current_top_position = (
            float(params.get("caption_top", "15%")[:-1]) / 100 * video_height
        )
        current_hor_offset = (
            float(params.get("hor_offset", "4%")[:-1]) / 100 * video_width
        )
        line_height = (
            float(params.get("line_width", "8%")[:-1]) / 100 * video_height
        )

        # Create caption clips
        caption_clips = []
        for line in lines:
            start_time = overall_start
            end_time = start_time + params.get("cap_length", 5)

            if end_time > video_clip.duration:
                end_time = video_clip.duration

            shadow_clip = (
                TextClip(
                    line,
                    fontsize=params["font_size"],
                    color=params.get("shadow", {}).get("color", "black"),
                    font=params["font"],
                )
                .set_position((
                    current_hor_offset + params.get("shadow", {}).get("offset", 5),
                    current_top_position + params.get("shadow", {}).get("offset", 5),
                ))
                .set_start(start_time)
                .set_duration(end_time - start_time)
                .set_opacity(params.get("shadow", {}).get("opacity", 0.6))
            )
            caption_clips.append(shadow_clip)

            caption_clip = (
                TextClip(
                    line,
                    fontsize=params["font_size"],
                    color=params["username_color"],
                    font=params["font"],
                )
                .set_position((current_hor_offset, current_top_position))
                .set_start(start_time)
                .set_duration(end_time - start_time)
            )
            caption_clips.append(caption_clip)

            overall_start += next_line_pause
            current_top_position += line_height

        final_video = CompositeVideoClip([video_clip] + caption_clips)
        filename, ext = os.path.splitext(os.path.basename(input_name))
        output_video_path = os.path.join(download_path, f"{filename}_captioned{ext}")
        codecs = get_codecs_by_extension(ext)

        final_video.write_videofile(
            output_video_path,
            codec=codecs["video_codec"],
            audio_codec=codecs["audio_codec"],
            fps=24,
        )

        if logger:
            logger.info(f"Captioning completed successfully. Output video saved at: {output_video_path}")

        return {"to_process": output_video_path}
    except Exception as e:
        if logger:
            logger.error(f"Error in adding captions: {e}")
        raise

