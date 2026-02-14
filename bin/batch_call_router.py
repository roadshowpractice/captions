#!/usr/bin/env python
"""Process a batch of URLs by invoking call_router.py for each entry."""

import argparse
import subprocess
import sys
import time
from pathlib import Path


def load_urls(path: Path) -> list[str]:
    """Read non-empty, non-comment URLs from a text file."""
    urls: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        urls.append(line)
    return urls


def run_batch(
    urls: list[str],
    dry_run: bool,
    stop_on_error: bool,
    heartbeat_seconds: int,
) -> int:
    """Run call_router.py for each URL and return final exit code."""
    repo_root = Path(__file__).resolve().parent.parent
    call_router = repo_root / "bin" / "call_router.py"

    failures = 0

    for index, url in enumerate(urls, start=1):
        cmd = [sys.executable, str(call_router), url]
        if dry_run:
            cmd.append("--dry-run")

        print(f"[{index}/{len(urls)}] Running: {' '.join(cmd)}")
        process = subprocess.Popen(cmd)
        started_at = time.time()
        next_heartbeat = started_at + heartbeat_seconds

        while True:
            returncode = process.poll()
            if returncode is not None:
                break

            now = time.time()
            if now >= next_heartbeat:
                elapsed = int(now - started_at)
                print(
                    f"  🔄 Still processing URL {index}/{len(urls)} "
                    f"({elapsed}s elapsed)"
                )
                next_heartbeat = now + heartbeat_seconds

            time.sleep(1)

        if returncode != 0:
            failures += 1
            print(f"  ❌ Failed for URL: {url} (exit {returncode})")
            if stop_on_error:
                return returncode
        else:
            print(f"  ✅ Completed for URL: {url}")

    if failures:
        print(f"Batch finished with {failures} failure(s).")
        return 1

    print("Batch finished successfully.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run call_router.py for each URL in a text file."
    )
    parser.add_argument(
        "url_file",
        nargs="?",
        default="tests/1.test.txt",
        help="Path to a newline-delimited URL file (default: tests/1.test.txt)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Pass --dry-run to call_router.py for each URL.",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop immediately if any URL processing fails.",
    )
    parser.add_argument(
        "--heartbeat-seconds",
        type=int,
        default=60,
        help="Emit a keepalive status line every N seconds while processing (default: 60).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    url_file = Path(args.url_file)

    if not url_file.exists():
        print(f"URL file not found: {url_file}", file=sys.stderr)
        return 1

    urls = load_urls(url_file)
    if not urls:
        print(f"No valid URLs found in: {url_file}", file=sys.stderr)
        return 1

    if args.heartbeat_seconds < 1:
        print("--heartbeat-seconds must be >= 1", file=sys.stderr)
        return 1

    return run_batch(
        urls,
        dry_run=args.dry_run,
        stop_on_error=args.stop_on_error,
        heartbeat_seconds=args.heartbeat_seconds,
    )


if __name__ == "__main__":
    raise SystemExit(main())
