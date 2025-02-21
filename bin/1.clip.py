import os
import logging
import traceback
import subprocess

logger = logging.getLogger(__name__)

def get_codecs_by_extension(extension):
    codecs = {
        ".webm": {"video_codec": "libvpx", "audio_codec": "libvorbis"},
        ".mp4": {"video_codec": "libx264", "audio_codec": "aac"},
        ".ogv": {"video_codec": "libtheora", "audio_codec": "libvorbis"},
        ".mkv": {"video_codec": "libx264", "audio_codec": "aac"},
    }
    return codecs.get(extension, {"video_codec": "libx264", "audio_codec": "aac"})
    
def process_clips(params, clips):
    try:
        input_video_path = params.get("input_video_path")
        download_path = params.get("download_path", os.getcwd())

        logger.info(f"Input video path: {input_video_path}")
        logger.info(f"Download path: {download_path}")

        if not os.path.exists(input_video_path):
            raise FileNotFoundError(f"Input video file not found: {input_video_path}")

        file_extension = os.path.splitext(input_video_path)[1]
        codecs = get_codecs_by_extension(file_extension)
        video_codec = codecs["video_codec"]
        audio_codec = codecs["audio_codec"]

        output_video_paths = []

        for idx, (start, end) in enumerate(clips, start=1):
            output_video_path = os.path.join(download_path, f"clip_{idx}.mp4")
            logger.info(f"Processing clip {idx} from {start}s to {end}s...")

            ffmpeg_command = [
                "ffmpeg", 
                "-i", input_video_path,
                "-ss", str(start), 
                "-to", str(end),
                "-c:v", video_codec, 
                "-c:a", audio_codec, 
                "-copyts",
                "-strict", "experimental", 
                output_video_path
            ]

            try:
                subprocess.run(ffmpeg_command, check=True)
                logger.info(f"Clip {idx} created: {output_video_path}")
                output_video_paths.append(output_video_path)
            except subprocess.CalledProcessError as e:
                logger.error(f"Error extracting clip {idx}: {e}")
                logger.info(traceback.format_exc())
                raise

        return {"output_video_paths": output_video_paths}

    except Exception as e:
        logger.error(f"Error in process_clips: {e}")
        logger.info(traceback.format_exc())
        raise

