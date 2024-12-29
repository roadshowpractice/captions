# utilities1.py

import os
import time
import traceback
import logging
import json


####################
# Logger setup
# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
###########################


# Function to store params as a JSON file in the output directory
def store_params_as_json(params):
    """
    Stores the params dictionary as a JSON file in the output directory.
    The filename should match the video file, but with a .json extension.

    Args:
        params (dict): The parameters dictionary to store.

    Returns:
        dict: A dictionary with key 'config_json' and value as the path of the JSON file.
    """
    try:
        original_filename = params.get("original_filename")
        if original_filename:
            json_filename = os.path.splitext(original_filename)[0] + ".json"
            with open(json_filename, "w") as json_file:
                json.dump(params, json_file, indent=4)
            logger.info(f"Params saved to JSON file: {json_filename}")
            return {"config_json": json_filename}
        else:
            logger.warning("No original filename found in params to create JSON file.")
            return {"config_json": None}
    except Exception as e:
        logger.error(f"Failed to save params to JSON: {e}")
        logger.debug(traceback.format_exc())
        return {"config_json": None}


def unique_output_path(path, filename):
    """
    Generates a unique output file path by appending a counter to the filename if it already exists.

    Args:
        path (str): Directory path.
        filename (str): Original filename.

    Returns:
        str: A unique file path.
    """
    base, ext = os.path.splitext(filename)
    counter = 1
    unique_filename = filename
    while os.path.exists(os.path.join(path, unique_filename)):
        unique_filename = f"{base}_{counter}{ext}"
        counter += 1
    return os.path.join(path, unique_filename)


def print_params(params):
    """
    Prints parameters for diagnostic purposes.

    Args:
        params (dict): Parameters to print.
    """
    print("Received parameters:")
    for key, value in params.items():
        print(f"{key}: {value}")


def handle_exception(e):
    """
    Handles exceptions by printing the error message and traceback.

    Args:
        e (Exception): The exception to handle.
    """
    print(f"Error: {e}")
    traceback.print_exc()


def current_timestamp():
    """
    Returns the current timestamp in a readable format.

    Returns:
        str: Current timestamp as a formatted string.
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def on_progress(stream, chunk, bytes_remaining):
    """
    Callback function to report download progress.

    Args:
        stream: The stream being downloaded.
        chunk: The chunk of data that has been downloaded.
        bytes_remaining (int): Number of bytes remaining to download.
    """
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    print(f"Download progress: {percentage_of_completion:.2f}%")


def on_complete(stream, file_path):
    """
    Callback function when a download is complete.

    Args:
        stream: The stream that was downloaded.
        file_path (str): Path to the downloaded file.
    """
    print(f"Download complete: {file_path}")


if __name__ == "__main__":
    main()
