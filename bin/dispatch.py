#!/usr/bin/env python3
"""Run tasks defined in a metadata JSON file."""
import json
import os
import subprocess
import sys
import logging

TASK_SCRIPTS = {
    "perform_download": "bin/call_download.py",
    "apply_watermark": "bin/call_watermark.py",
    "make_clips": "bin/call_clips.py",
}


def setup_logging(verbose: bool = False) -> None:
    """Configure basic logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(message)s")


def run_script(script: str, arg: str, verbose: bool = False) -> str:
    """Execute a Python script with the given argument and return its output."""
    cmd = [sys.executable, script, arg]
    if verbose:
        logging.info("Running: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if verbose and result.stdout:
        logging.info(result.stdout.strip())
    if verbose and result.stderr:
        logging.warning(result.stderr.strip())
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    return lines[-1] if lines else ""


def main(path: str, verbose: bool = False) -> None:
    setup_logging(verbose)
    logging.info("Reading metadata from %s", path)
    with open(path, "r") as fh:
        data = json.load(fh)

    url = data.get("url")
    tasks = data.get("tasks", {})
    last = tasks.get("perform_download") if isinstance(tasks.get("perform_download"), str) else None

    for task in ["perform_download", "apply_watermark", "make_clips"]:
        state = tasks.get(task)
        if state is True:
            if task != "perform_download" and not last:
                logging.info("Skipping %s: missing input file", task)
                continue
            script = os.path.join(os.path.dirname(__file__), os.pardir, TASK_SCRIPTS[task])
            script = os.path.normpath(script)
            arg = url if task == "perform_download" else last
            logging.info("Running task %s", task)
            result_path = run_script(script, arg, verbose)
            tasks[task] = result_path
            last = result_path or last
            logging.info("%s result: %s", task, result_path)
        elif isinstance(state, str):
            logging.info("Using existing result for %s: %s", task, state)
            last = state
        else:
            logging.info("Skipping %s", task)

    with open(path, "w") as fh:
        json.dump(data, fh, indent=4)
    logging.info("Updated tasks in %s", path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run tasks defined in a metadata JSON file")
    parser.add_argument("metadata", help="Path to metadata JSON")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
    args = parser.parse_args()

    main(args.metadata, verbose=args.verbose)
