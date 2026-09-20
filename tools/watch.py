#!/usr/bin/env python3
"""
watch.py — Watch project for changes and auto-run codemerge diff.

Usage:
    python tools/watch.py
    python tools/watch.py --interval 5
    python tools/watch.py -o .ai/changes.txt

Press Ctrl+C to stop.

Requires Python 3.8+.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

EXCLUDE_DIRS = {
    ".git", "node_modules", ".next", ".ai", "dist", "build",
    ".turbo", "coverage", "venv", ".venv", "__pycache__",
    ".idea", ".vscode", "out", "target", ".cache",
}


def should_skip(path: Path) -> bool:
    return any(part in EXCLUDE_DIRS for part in path.parts)


def latest_mtime(root: Path) -> float:
    """Return latest mtime among all source files."""
    latest = 0.0
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        try:
            rel = p.relative_to(root)
        except ValueError:
            continue
        if should_skip(rel):
            continue
        try:
            latest = max(latest, p.stat().st_mtime)
        except OSError:
            pass
    return latest


def run_diff(
    codemerge: str,
    output: Path,
    root: Path,
    quiet: bool,
) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    if not quiet:
        print(f"[{ts}] Running diff...")
    try:
        result = subprocess.run(
            [sys.executable, codemerge, "diff", "-o", str(output), "--quiet"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=180,
        )
        if not quiet:
            if result.stdout.strip():
                print(result.stdout.strip())
            if result.stderr.strip():
                print(result.stderr.strip(), file=sys.stderr)
    except subprocess.TimeoutExpired:
        print("  ! diff timed out", file=sys.stderr)
    except FileNotFoundError:
        print(f"  ! codemerge not found at: {codemerge}", file=sys.stderr)
        sys.exit(2)


def watch_loop(
    interval: int,
    output: Path,
    codemerge: str,
    root: Path,
    quiet: bool,
) -> None:
    print(f"Watching:   {root}")
    print(f"Interval:   {interval}s")
    print(f"Output:     {output}")
    print(f"Press Ctrl+C to stop.")
    print()

    last_mtime = 0.0

    # Initial run
    run_diff(codemerge, output, root, quiet)
    last_mtime = latest_mtime(root)

    while True:
        try:
            time.sleep(interval)
            mtime = latest_mtime(root)
            if mtime > last_mtime:
                last_mtime = mtime
                run_diff(codemerge, output, root, quiet)
        except KeyboardInterrupt:
            print("\nStopped.")
            return


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Watch project and auto-run codemerge diff.",
    )
    parser.add_argument("-r", "--root", default=".",
                        help="Project root (default: cwd)")
    parser.add_argument("-i", "--interval", type=int, default=15,
                        help="Check interval in seconds (default: 15)")
    parser.add_argument("-o", "--output", default=".ai/changes.txt",
                        help="Output file for diff (default: .ai/changes.txt)")
    parser.add_argument("--codemerge", default="codemerge.py",
                        help="Path to codemerge.py (default: codemerge.py)")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Suppress per-run messages")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = root / output
    output.parent.mkdir(parents=True, exist_ok=True)

    try:
        watch_loop(args.interval, output, args.codemerge, root, args.quiet)
    except KeyboardInterrupt:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())