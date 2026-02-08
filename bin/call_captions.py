
import sys
import logging
import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import tempfile
import time
import speech_recognition as sr
from urllib.parse import urlparse


# ==================================================
# CLIPS CONFIGURATION 
# ==================================================
moviepy_config = {
    "clips_directory": "clips/",  # Directory where clips will be stored
    "width": 1280,  # Video width
    "height": 720,  # Video height
    "font": "Arial",  # Font file for text overlay
    "font_size": 32,  # Font size for overlay text
    "text_halign": "left",  # Horizontal alignment for overlay text (centered)
    "text_valign": "center",  # Vertical alignment for overlay text (centered)
    "output_format": "mp4",  # Output format
    "text_color": "white",  # Color of the text overlay
}

clips = [
    {
        "start": 3,  # Clip start time (in seconds)
        "end": 10,   # Clip end time (in seconds)
        "text": "First clip",  # Default text
        "name": "clip_1"  # Name of the clip file
    },
    {
        "start": 20,
        "end": 50,
        "text": "Bollocks",
        "name": "clip_2"
    },
    {
        "start": 120,
        "end": 170,
        "text": "Bollocks",
        "name": "treason_weasal"
    },
    {
        "start": 150.0,
        "end": 168.0,
        "text": "Bollocks",
        "name": "clip_4"
    }
]


# Mapping of known platforms to standard names
KNOWN_VENDORS = {
    "instagram.com": "instagram",
    "youtube.com": "youtube",
    "youtu.be": "youtube",
    "tiktok.com": "tiktok",
    "twitter.com": "twitter",
    "x.com": "twitter",
    "facebook.com": "facebook",
    "fb.watch": "facebook",
    "vimeo.com": "vimeo",
    "twitch.tv": "twitch"
}




# ==================================================
# LOGGING INITIALIZATION
# ==================================================
def initialize_logging():
    log_dir = "./logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "moviepy_clips.log")

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # File logging
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console logging
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(asctime)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    logger.info("Logging initialized.")
    return logger

# ==================================================
# AUDIO EXTRACTION AND TRANSCRIPTION
# ==================================================
def extract_audio_from_video(video_path, start_time, end_time, temp_audio_path):
    """Extracts audio from the video clip for the given time range."""
    try:
        video = VideoFileClip(video_path)
        video = video.subclip(start_time, end_time)
        audio_path = temp_audio_path
        video.audio.write_audiofile(audio_path)
        print(f"Audio extracted to {audio_path}")
        return audio_path
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return None

def transcribe_audio(audio_path):
    """Transcribe the audio using speech recognition."""
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        print(f"Transcription: {text}")
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None

def ensure_clips_directory(clips_directory):
    if not os.path.exists(clips_directory):
        os.makedirs(clips_directory)
        logger.info(f"Created clips directory: {clips_directory}")

# ==================================================
# VIDEO CLIPPING AND TEXT REPLACEMENT
# ==================================================
def process_video_for_clip_and_transcription(video_path, start_time, end_time, text_overlay):
    """Extract audio, transcribe it, replace original text, and prepare the clip."""
    # Create a temporary file for audio extraction
    with tempfile.NamedTemporaryFile(delete=False) as temp_audio_file:
        audio_path = temp_audio_file.name + ".wav"

        # Extract audio and transcribe it
        extracted_audio = extract_audio_from_video(video_path, start_time, end_time, audio_path)
        if extracted_audio:
            transcription = transcribe_audio(extracted_audio)

            # Clean up temporary audio file
            os.remove(extracted_audio)

            # Process the video clip with the transcription text
            video_clip = VideoFileClip(video_path).subclip(start_time, end_time)

            # If transcription exists, replace the original text with the transcribed text
            if transcription:
                text_overlay = transcription  # Replace the original text with transcription

            # Log the new text that would be used for overlay or replacement (just for verification)
            logger.info(f"Text overlay (or replacement) for {text_overlay}")

            # No writing or saving yet, just returning the video clip
            return video_clip, text_overlay
        else:
            return None, None

def get_user_confirmation(text):
    """Prompt the user to accept or change the transcription text."""
    print(f"Text detected: '{text}'")
    print("Accept this text? (y/n): ", end="", flush=True)

    # Set a timeout for user input
    start_time = time.time()
    user_input = ""
    while time.time() - start_time < 3:  # 3-second timer
        if user_input.lower() in ["y", "n"]:
            break
        if user_input == "":
            user_input = input()
        else:
            user_input = input()

    if user_input.lower() == "y":
        return text
    elif user_input.lower() == "n":
        print(f"Original text: {text}")
        changed_text = input("Enter new text (or press Enter to keep the original): ")
        return changed_text if changed_text else text
    else:
        return text  # Default to original text if no input or invalid input

def process_clips_moviepy(moviepy_config, clips, logger):
    input_video = sys.argv[1]  # Get input video path from command line argument
    clips_directory = moviepy_config["clips_directory"]
    
    # Log global config values
    logger.info(f"Processing video: {input_video}")
    logger.info(f"Output directory: {clips_directory}")
    
    # Ensure the clips directory exists
    ensure_clips_directory(clips_directory)
    
    # Load the input video using moviepy
    video_clip = VideoFileClip(input_video)
    
    # Iterate through clips and process each one
    for clip in clips:
        start, end, text, name = clip["start"], clip["end"], clip["text"], clip["name"]
        output_file = os.path.join(clips_directory, f"{name}.mp4")
        
        # Log the clip-specific values
        logger.info(f"Clip Name: {name}")
        logger.info(f"Clip Start Time: {start}")
        logger.info(f"Clip End Time: {end}")
        logger.info(f"Text to Overlay: {text}")
        logger.info(f"Output File: {output_file}")
        
        # Extract the clip
        clip = video_clip.subclip(start, end)

        # Create a TextClip for the overlay text
        txt_clip = TextClip(text, fontsize=moviepy_config["font_size"], font=moviepy_config["font"], color=moviepy_config["text_color"])
        
        # Set the position and duration of the text
        txt_clip = txt_clip.set_position((moviepy_config["text_halign"], moviepy_config["text_valign"])).set_duration(clip.duration)
        
        # Overlay the text on the video clip
        video_with_text = CompositeVideoClip([clip, txt_clip])

        # Write the result to the output file
        video_with_text.write_videofile(output_file, codec="libx264", audio_codec="aac")
        
        logger.info(f"Clip {name} processed successfully.")


def get_vendor(video_url):
    """Extracts and normalizes the vendor (host) from the video URL."""
    parsed_url = urlparse(video_url)
    domain = parsed_url.netloc.lower().lstrip("www.")  # Strip 'www.'

    # Return mapped vendor name or default to domain
    return KNOWN_VENDORS.get(domain, domain)



# ==================================================
# MAIN EXECUTION
# ==================================================

# Ensure the input file is provided as an argument
if len(sys.argv) < 2:
    print("Error: No input video file provided.")
    sys.exit(1)

# Initialize logger
logger = initialize_logging()

video_url = sys.argv[1]
vendor = get_vendor(video_url)

print(f"Vendor: {vendor}")

# Ensure clips directory exists
ensure_clips_directory(moviepy_config["clips_directory"])

# Iterate through clips
processed_clips = []
for clip in clips:
    start_time = clip["start"]
    end_time = clip["end"]
    text = clip["text"]
    
    # Process each clip
    processed_clip, updated_text = process_video_for_clip_and_transcription(
        sys.argv[1], start_time, end_time, text
    )
    
    # If transcribed text exists, confirm with the user
    if updated_text:
        updated_text = get_user_confirmation(updated_text)
        clip["text"] = updated_text
    processed_clips.append(clip)

# Process clips using moviepy
process_clips_moviepy(moviepy_config, processed_clips, logger)


