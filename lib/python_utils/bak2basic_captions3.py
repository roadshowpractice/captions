import os
import re
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

def add_captions(params, logger=None):
    try:
        input_name = params["input_video_path"]
        download_path = params["download_path"]
        paragraph = params["paragraph"].replace("\n", " ")

        video_clip = VideoFileClip(input_name)
        video_width, video_height = video_clip.size
        current_top_position = float(params.get("caption_top", "15%")[:-1]) / 100 * video_height

        lines = [paragraph]  # Simplified line handling

        caption_clips = []
        for line in lines:
            start_time = params.get("overall_start", 2)
            end_time = min(start_time + params.get("cap_length", 5), video_clip.duration)

            caption_clip = TextClip(
                line,
                fontsize=params["font_size"],
                color=params["username_color"],
                font=params["font"]
            ).set_position((float(params.get("hor_offset", "4%")[:-1]) / 100 * video_width, current_top_position))
            caption_clip = caption_clip.set_start(start_time).set_duration(end_time - start_time)
            caption_clips.append(caption_clip)

        final_video = CompositeVideoClip([video_clip] + caption_clips)
        output_video_path = os.path.join(download_path, os.path.splitext(os.path.basename(input_name))[0] + "_captioned.mp4")
        final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac", fps=24)

        if logger:
            logger.info(f"Captioning completed: {output_video_path}")
        return {"to_process": output_video_path}

    except Exception as e:
        if logger:
            logger.error(f"Error: {e}")
        raise



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

