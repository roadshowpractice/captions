###############################################################################
#                                                                             #
#                               task_lib.py                                   #
#                                                                             #
#   Description:                                                              #
#   ------------------------------------------------------------------------  #
#   This module provides task-aware utilities for managing operations such    #
#   as video downloading, metadata handling, and task status tracking.        #
#                                                                             #
#   Functions Included:                                                       #
#   ------------------------------------------------------------------------  #
#   - load_default_tasks(config_path="conf/default_tasks.json")              #
#     --> Load default task flags from JSON config                            #
#                                                                             #
#   - should_perform_task(task: str, task_config: dict)                       #
#     --> Check if a task should be performed based on config                 #
#                                                                             #
#   - copy_metadata_to_backup(params: dict)                                   #
#     --> Copy metadata JSON to backup directory                              #
#                                                                             #
#   - extend_metadata_with_task_output(params: dict)                          #
#     --> Update metadata with task output path                               #
#                                                                             #
#   - find_url_json(url, metadata_dir="./metadata")                           #
#     --> Locate metadata JSON that contains the given URL                    #
#                                                                             #
#   - get_existing_task_output(task: str, task_config: dict)                  #
#     --> Retrieve output path for a completed task                           #
#                                                                             #
#   - add_default_tasks_to_metadata(metadata_path: str, config_path=...)      #
#     --> Insert default task flags into a metadata file                      #
#                                                                             #
#   - update_task_output_path(metadata_path: str, task: str, output_path: str)#
#     --> Replace boolean task flag with actual output path                   #
#                                                                             #
#   - get_task_states(url, metadata_dir="./metadata")                         #
#     --> Return all task states from metadata for a given URL                #
#                                                                             #
#   Author:        Aldebaran                                                  #
#   Created:       2025-03-18                                                 #
#   Last Modified: 2025-03-25                                                 #
#                                                                             #
###############################################################################


import os
import json
import logging
import shutil
import traceback

# Initialize the logger
logger = logging.getLogger(__name__)
logger.info(f"📦 {__name__} imported into {__file__}")


def load_default_tasks(config_path="conf/default_tasks.json"):
    """
    Loads the task flags from the default_tasks JSON configuration file.
    """
    logger.info("🔴 Entering load_default_tasks routine... 🚀")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Task config file not found: {config_path}")

    with open(config_path, "r") as f:
        config = json.load(f)

    return config.get("default_tasks", {})


def should_perform_task(task: str, task_config: dict) -> bool:
    """
    Checks if a task should be performed based on the provided task configuration.
    """
    logger.info(f"🔵 Checking if task '{task}' should be performed...")

    # Log the entire task config for better visibility
    logger.debug(f"Task Config: {task_config}")

    # Retrieve the task flag from the config
    val = task_config.get("default_tasks", {}).get(task)
    logger.info(
        f"🔑 Task '{task}' value from config: {val}"
    )  # Log the exact value fetched

    if val is None:
        logger.warning(f"⚠️ Task '{task}' not found in config.")

    return val is True


def copy_metadata_to_backup(params: dict) -> dict:
    """
    Copies the original metadata JSON to the backup directory after a task is completed.
    """
    logger.info("🟢 Entering copy_metadata_to_backup routine... 💾")

    config_json_path = params.get("config_json")
    app_config = params.get("app_config", {})
    metadata_dir = app_config.get("video_download", {}).get(
        "metadata_backup_path", "./metadata"
    )

    if not config_json_path or not os.path.exists(config_json_path):
        logger.warning("Original config JSON not found. Skipping copy.")
        return {"full_metadata_json": None}

    os.makedirs(metadata_dir, exist_ok=True)
    base_name = os.path.basename(config_json_path)
    target_path = os.path.join(metadata_dir, base_name)

    shutil.copy2(config_json_path, target_path)
    logger.info(f"Metadata copied to: {target_path}")

    return {"full_metadata_json": target_path}


def extend_metadata_with_task_output(params: dict) -> dict:
    """
    Updates the metadata JSON to mark the task as completed with the final output path.
    """
    logger.info("🟠 Entering extend_metadata_with_task_output routine... ✅")

    task = params.get("task")
    json_path = params.get("full_metadata_json")
    output_path = (
        params.get(f"{task}_output_path")
        or params.get("original_filename")
        or params.get("to_process")
    )

    if not json_path or not os.path.exists(json_path):
        logger.warning("Metadata file not found for extension.")
        return {"updated_metadata": None}

    try:
        with open(json_path, "r") as f:
            data = json.load(f)

        if "default_tasks" in data and task in data["default_tasks"] and output_path:
            data["default_tasks"][task] = output_path
            logger.info(f"Marked task '{task}' as completed: {output_path}")
        else:
            logger.warning(f"Task '{task}' not found or no output to record.")

        # Save the updated data back to the JSON file
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)

        return {"updated_metadata": json_path}
    except Exception as e:
        logger.error(f"Failed to extend metadata for task '{task}': {e}")
        logger.debug(traceback.format_exc())
        return {"updated_metadata": None}


def find_url_json(url, metadata_dir="./metadata"):
    """
    Search for a JSON file in the metadata directory that contains the given URL.
    """
    logger.info(f"🔍 Searching for URL '{url}' in {metadata_dir}")

    if not os.path.exists(metadata_dir):
        logger.warning(f"Metadata directory not found: {metadata_dir}")
        return None, None

    for filename in os.listdir(metadata_dir):
        if filename.endswith(".json"):
            json_path = os.path.join(metadata_dir, filename)
            try:
                with open(json_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    if isinstance(data, dict) and "url" in data and data["url"] == url:
                        logger.info(f"✅ URL found in: {json_path}")
                        return json_path, data
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error reading {json_path}: {e}")

    logger.warning(f"⚠️ URL not found in metadata directory.")
    return None, None


# def get_existing_task_output(task: str, task_config: dict) -> str | None:
#  ^^^ don't let this happen easily the bar is trouble, breaks things
from typing import Optional


def get_existing_task_output(task: str, task_config: dict) -> Optional[str]:

    """
    Checks if there is an existing output for the given task in the task configuration.

    Args:
        task (str): The task name (e.g., "perform_download").
        task_config (dict): The task configuration containing task-specific outputs.

    Returns:
        str | None: The output path of the completed task, or None if no output is found.
    """
    logger.info(f"🔎 Entering get_existing_task_output routine... 📝")

    # Retrieve the task output value from the config
    val = task_config.get(task)
    logger.info(f"🔑 Retrieved value for task '{task}': {val}")

    # Return the output path if it's a valid string, else None
    if isinstance(val, str):
        logger.info(f"✅ Found existing output for task '{task}': {val}")
        return val
    else:
        logger.warning(
            f"❌ No output found for task '{task}' or output is not a valid string."
        )
        return None


def extend_metadata_with_task_output(params: dict) -> dict:
    """
    Updates the metadata JSON to mark the task as completed with the final output path.
    """
    logger.info("🟠 Entering extend_metadata_with_task_output routine... ✅")

    task = params.get("task")
    json_path = params.get("full_metadata_json")
    output_path = (
        params.get(f"{task}_output_path")
        or params.get("original_filename")
        or params.get("to_process")
    )

    logger.debug(
        f"extend_metadata_with_task_output: task={task}, output_path={output_path}, json_path={json_path}"
    )

    if not json_path or not os.path.exists(json_path):
        logger.warning("⚠️ Metadata file not found for extension.")
        return {"updated_metadata": None}

    try:
        with open(json_path, "r") as f:
            data = json.load(f)

        # DEBUG: Show what's in default_tasks
        logger.debug(
            f"default_tasks BEFORE update: {json.dumps(data.get('default_tasks', {}), indent=2)}"
        )

        if "default_tasks" in data and task and output_path:
            data["default_tasks"][task] = output_path
            logger.info(f"✅ Marked task '{task}' as completed: {output_path}")
        else:
            logger.warning(
                f"⚠️ Task '{task}' not found in metadata OR output_path missing.\n"
                f"  task in default_tasks: {task in data.get('default_tasks', {})}\n"
                f"  output_path: {output_path}"
            )

        # DEBUG: Show what's going to be saved
        logger.debug(f"📝 Final metadata before save:\n{json.dumps(data, indent=2)}")

        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)

        return {"updated_metadata": json_path}
    except Exception as e:
        logger.error(f"❌ Failed to extend metadata for task '{task}': {e}")
        logger.debug(traceback.format_exc())
        return {"updated_metadata": None}


def add_default_tasks_to_metadata(
    metadata_path: str, config_path="conf/default_tasks.json"
):
    """
    Adds the default tasks from the configuration file to the metadata JSON file.

    Args:
        metadata_path (str): Path to the metadata JSON file.
        config_path (str): Path to the default_tasks JSON file.

    Returns:
        dict: The updated metadata JSON file path.
    """
    logger.info(f"🔎 Entering add_default_tasks_to_metadata... 📝")

    # Load default tasks from the configuration file
    if not os.path.exists(config_path):
        logger.error(f"❌ Configuration file not found: {config_path}")
        return {"updated_metadata": None}

    try:
        with open(config_path, "r") as f:
            default_tasks = json.load(f).get("default_tasks", {})
    except json.JSONDecodeError as e:
        logger.error(f"❌ Error parsing {config_path}: {e}")
        return {"updated_metadata": None}

    if not os.path.exists(metadata_path):
        logger.error(f"❌ Metadata file not found: {metadata_path}")
        return {"updated_metadata": None}

    try:
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"❌ Error parsing {metadata_path}: {e}")
        return {"updated_metadata": None}

    # Add the default tasks to the metadata if they're not already there
    if "default_tasks" not in metadata:
        metadata["default_tasks"] = {}

    for task, status in default_tasks.items():
        if task not in metadata["default_tasks"]:
            metadata["default_tasks"][task] = status
            logger.info(f"➕ Added task '{task}' to metadata with status: {status}")

    # Save the updated metadata back to the file
    try:
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=4)
        logger.info(f"✅ Metadata updated with default tasks. Saved to: {metadata_path}")
        return {"updated_metadata": metadata_path}
    except Exception as e:
        logger.error(f"❌ Failed to save updated metadata: {e}")
        return {"updated_metadata": None}


def write_masked_metadata_with_tasks(
    params: dict, config_path="conf/default_tasks.json"
) -> dict:
    """
    Writes masked metadata fields and default task flags into the metadata JSON file.

    Args:
        params (dict): Parameters including masked metadata fields and paths.
        config_path (str): Path to the default_tasks JSON file.

    Returns:
        dict: The updated metadata file path, or None if failed.
    """
    metadata_path = params.get("metadata_path") or params.get("config_json")
    if not metadata_path:
        logger.warning("⚠️ No metadata_path or config_json found in params.")
        return {"updated_metadata": None}

    metadata_dir = os.path.dirname(metadata_path)
    if metadata_dir:
        os.makedirs(metadata_dir, exist_ok=True)

    try:
        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        else:
            metadata = {}
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"❌ Failed to read metadata file: {e}")
        metadata = {}

    masked_keys = [
        "video_title",
        "video_date",
        "uploader",
        "file_path",
        "duration",
        "width",
        "height",
        "id",
        "ext",
        "resolution",
        "fps",
        "channels",
        "filesize",
        "tbr",
        "protocol",
        "vcodec",
        "vbr",
        "acodec",
        "abr",
        "asr",
    ]

    for key in masked_keys:
        if key in params:
            metadata[key] = params[key]

    if params.get("url"):
        metadata["url"] = params["url"]

    try:
        default_tasks = load_default_tasks(config_path)
    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
        default_tasks = {}

    if "default_tasks" not in metadata:
        metadata["default_tasks"] = {}

    for task, status in default_tasks.items():
        metadata["default_tasks"].setdefault(task, status)

    output_path = params.get("to_process") or params.get("original_filename")
    if output_path:
        metadata["default_tasks"]["perform_download"] = output_path

    try:
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)
        logger.info(f"✅ Masked metadata updated at: {metadata_path}")
        return {"updated_metadata": metadata_path}
    except OSError as e:
        logger.error(f"❌ Failed to save metadata: {e}")
        logger.debug(traceback.format_exc())
        return {"updated_metadata": None}


def update_task_output_path(metadata_path: str, task: str, output_path: str) -> dict:
    """
    Updates the given task in the metadata JSON to store the actual output path
    instead of just 'true'.

    Args:
        metadata_path (str): Path to the metadata JSON file.
        task (str): The task name to update (e.g., "perform_download").
        output_path (str): The actual output path to store.

    Returns:
        dict: The updated metadata file path, or None if failed.
    """
    logger.info(f"🛠 Updating task output path for '{task}' in: {metadata_path}")

    if not metadata_path or not os.path.exists(metadata_path):
        logger.error(f"❌ Metadata file not found: {metadata_path}")
        return {"updated_metadata": None}

    if not output_path:
        logger.warning("⚠️ No output path provided — cannot update metadata.")
        return {"updated_metadata": None}

    try:
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        if "default_tasks" in metadata:
            metadata["default_tasks"][task] = output_path
            logger.info(f"✅ Task '{task}' updated to: {output_path}")
        else:
            logger.warning(f"⚠️ No 'default_tasks' section found in metadata.")

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=4)

        return {"updated_metadata": metadata_path}
    except Exception as e:
        logger.error(f"❌ Failed to update task output path: {e}")
        logger.debug(traceback.format_exc())
        return {"updated_metadata": None}


def get_task_states(url, metadata_dir="./metadata"):
    """
    Given a URL, this function looks for the metadata file in the specified directory
    and returns the state of the tasks in the 'default_tasks' section.

    Args:
        url (str): The URL to search for.
        metadata_dir (str): The directory where metadata JSON files are stored.

    Returns:
        dict: Task states if the metadata is found, or None if not.
    """
    # Find the metadata file and its content
    metadata_file, metadata_data = find_url_json(url, metadata_dir)

    if metadata_data is None:
        return None

    # Retrieve the state of tasks from the 'default_tasks' section
    default_tasks = metadata_data.get("default_tasks", {})

    if not default_tasks:
        logger.warning(f"⚠️ No 'default_tasks' found in metadata for URL: {url}")
        return None

    # Return the task states
    logger.info(f"🛠 Task states for {url}: {default_tasks}")
    return default_tasks
