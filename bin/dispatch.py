#!/usr/bin/env python3
"""Run tasks defined in a metadata JSON file."""
import json
import os
import subprocess
import sys

TASK_SCRIPTS = {
    "perform_download": "bin/call_download.py",
    "apply_watermark": "bin/call_watermark.py",
    "make_clips": "bin/call_clips.py",
}


def run_script(script, arg):
    """Execute a Python script with the given argument and return its output."""
    cmd = [sys.executable, script, arg]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    return lines[-1] if lines else ""


def main(path):
    with open(path, "r") as fh:
        data = json.load(fh)

    url = data.get("url")
    tasks = data.get("tasks", {})
    last = tasks.get("perform_download") if isinstance(tasks.get("perform_download"), str) else None

    for task in ["perform_download", "apply_watermark", "make_clips"]:
        state = tasks.get(task)
        if state is True:
            if task != "perform_download" and not last:
                print(f"Skipping {task}: missing input file")
                continue
            script = os.path.join(os.path.dirname(__file__), os.pardir, TASK_SCRIPTS[task])
            script = os.path.normpath(script)
            arg = url if task == "perform_download" else last
            result_path = run_script(script, arg)
            tasks[task] = result_path
            last = result_path or last
        elif isinstance(state, str):
            last = state

    with open(path, "w") as fh:
        json.dump(data, fh, indent=4)
    print(f"Updated tasks in {path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: dispatch.py <metadata.json>")
        sys.exit(1)
    main(sys.argv[1])
