import os
import logging
import traceback
import subprocess



logger = logging.getLogger(__name__)

# Helper Function: Get codecs based on file extension
def get_codecs_by_extension(extension):
    codecs = {
        ".webm": {"video_codec": "libvpx", "audio_codec": "libvorbis"},
        ".mp4": {"video_codec": "libx264", "audio_codec": "aac"},
        ".ogv": {"video_codec": "libtheora", "audio_codec": "libvorbis"},
        ".mkv": {"video_codec": "libx264", "audio_codec": "aac"},
    }
    return codecs.get(extension, {"video_codec": "libx264", "audio_codec": "aac"})

def process_clips_ffmpeg(params, clips):
    try:
        input_video_path = params.get("input_video_path")
        download_path = params.get("download_path", os.getcwd())
        
        logger.info(f"Input video path: {input_video_path}")
        logger.info(f"Download path: {download_path}")
        
        if not os.path.exists(input_video_path):
            raise FileNotFoundError(f"Input video file not found: {input_video_path}")

        # Get file extension to determine appropriate codecs
        file_extension = os.path.splitext(input_video_path)[1]
        codecs = get_codecs_by_extension(file_extension)
        video_codec = codecs["video_codec"]
        audio_codec = codecs["audio_codec"]
        
        output_video_paths = []
        
        # Process each clip
        for idx, (start, end, text) in enumerate(clips, start=1):
            output_video_path = os.path.join(download_path, f"clip_{idx}.mp4")
            logger.info(f"Processing clip {idx} from {start}s to {end}s...")
            
            # FFmpeg command to extract clips
            ffmpeg_command = [
                "ffmpeg", 
                "-i", input_video_path, 
                "-ss", str(start), 
                "-to", str(end), 
                "-c:v", video_codec, 
                "-c:a", audio_codec, 
                "-strict", "experimental"
            ]
            
            if text:
                # Adding overlay text if present
                ffmpeg_command.extend([
                    "-vf", f"drawtext=text='{text}':x=10:y=10:fontsize=24:fontcolor=yellow"
                ])
            
            ffmpeg_command.append(output_video_path)

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
        logger.error(f"Error in process_clips_ffmpeg: {e}")
        logger.info(traceback.format_exc())
        raise



def process_clips_gstreamer(params, clips):
    try:
        input_video_path = params.get("input_video_path")
        download_path = params.get("download_path", os.getcwd())

        logger.info(f"Input video path: {input_video_path}")
        logger.info(f"Download path: {download_path}")
        
        if not os.path.exists(input_video_path):
            raise FileNotFoundError(f"Input video file not found: {input_video_path}")
        
        output_video_paths = []
        
        # Process each clip
        for idx, (start, end, text) in enumerate(clips, start=1):
            output_video_path = os.path.join(download_path, f"clip_{idx}.mp4")
            logger.info(f"Processing clip {idx} from {start}s to {end}s...")

            # GStreamer command to extract clips
            gstreamer_command = [
                "gst-launch-1.0", 
                "filesrc", f"location={input_video_path}", 
                "decodebin", 
                "videoconvert", 
                "x264enc", 
                "mp4mux", 
                f"filesink location={output_video_path}"
            ]
            
            if text:
                # Adding text overlay if present
                gstreamer_command.extend([
                    "textoverlay", f"text={text}:font-desc='Arial, 24':halign=left:valign=top"
                ])
            
            try:
                subprocess.run(gstreamer_command, check=True)
                logger.info(f"Clip {idx} created: {output_video_path}")
                output_video_paths.append(output_video_path)
            except subprocess.CalledProcessError as e:
                logger.error(f"Error extracting clip {idx}: {e}")
                logger.info(traceback.format_exc())
                raise

        return {"output_video_paths": output_video_paths}

    except Exception as e:
        logger.error(f"Error in process_clips_gstreamer: {e}")
        logger.info(traceback.format_exc())
        raise
