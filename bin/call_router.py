#!/usr/bin/env python
import sys
import os
import json
import logging
import traceback
import subprocess
from datetime import datetime

# Add lib path to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
lib_path = os.path.join(root_dir, "lib")
sys.path.append(lib_path)

# Import utilities
from teton_utils import initialize_logging, load_config, load_app_config
from python_utils.tasks_lib import find_url_json

# Map tasks to their respective scripts
TASK_DISPATCH = {
    "perform_download": "bin/call_download.py",
    "apply_watermark": "bin/call_watermark.py",
    "make_clips": "bin/call_clips.py",
    "extract_audio": "bin/call_extract_audio.py",
    "generate_captions": "bin/call_captions.py",
    # Convert screenshot timestamps after all other tasks
    "post_process": "bin/convert_screenshots.py"
}

def execute_tasks(task_config, url, to_process, dry_run=False):
    """Run appropriate script for each task based on its config."""
    for task, status in task_config.items():
        script = TASK_DISPATCH.get(task)

        if not script:
            logging.warning(f"No script defined for task: {task}")
            continue

        # Use URL for download; use file path for all others
        task_input = url if task == "perform_download" else to_process

        if status is True:
            logging.info(f"🚀 Running task: {task} -> {script}")
            script_path = os.path.join(root_dir, script)
            if dry_run:
                logging.info(f"[Dry Run] Would run: python {script_path} {task_input}")
            else:
                subprocess.run(["python", script_path, task_input])
        elif isinstance(status, str):
            logging.info(f"✅ Task already completed: {task} @ {status}")
        else:
            logging.info(f"⏭️  Skipping task: {task}")


def run_my_existing_downloader(url, logger):
    """Calls the known-good downloader script for the given URL."""
    logger.info(f"📥 Initiating download for: {url}")

    script_path = os.path.join(root_dir, "bin/call_download.py")
    result = subprocess.run(
        ["python", script_path, url],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        logger.error(f"Download script failed:\n{result.stderr}")
    else:
        logger.info(f"Download stdout:\n{result.stdout}")

def main():
    try:
        dry_run = "--dry-run" in sys.argv
        url_args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

        if len(url_args) < 1:
            print("Usage: python call_router.py <url> [--dry-run]")
            sys.exit(1)

        url = url_args[0].strip()

        config = load_config()
        logger = initialize_logging()
        app_config = load_app_config()
        logger.info("🔁 Task Router Started")

        found_file, found_data = find_url_json(url, metadata_dir="./metadata")

        perform_download_done = (
            found_data.get("default_tasks", {}).get("perform_download")
            if found_data
            else None
        )

        if not found_file or not perform_download_done:
            logger.info("📥 No completed download or metadata found — running downloader...")
            run_my_existing_downloader(url, logger)
            found_file, found_data = find_url_json(url, metadata_dir="./metadata")
            perform_download_done = (
                found_data.get("default_tasks", {}).get("perform_download")
                if found_data
                else None
            )

        if not found_data:
            logger.error("❌ No metadata found after attempted download.")
            return

        print(f"Found in: {found_file}")
        print(json.dumps(found_data, indent=2))

        if isinstance(perform_download_done, str):
            to_process = perform_download_done
        else:
            logger.error("Download task not completed and no output path recorded.")
            return

        if not os.path.exists(to_process):
            logger.error(f"Input file does not exist: {to_process}")
            return

        default_tasks = found_data.get("default_tasks", {})
        if not default_tasks:
            logger.warning("No 'default_tasks' section found in metadata.")
            return

        logger.info(f"🛠 Tasks to evaluate: {list(default_tasks.keys())}")
        execute_tasks(default_tasks, url, to_process, dry_run)

    except Exception as e:
        logging.error(f"Unexpected error in main(): {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
