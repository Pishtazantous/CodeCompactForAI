#!/usr/bin/env python3
"""
session_summary.py — Print the last session's summary for a new chat.

Usage:
    python tools/session_summary.py
    python tools/session_summary.py --last 3
    python tools/session_summary.py --list

Requires Python 3.8+.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SESSIONS_DIR = Path(".ai/sessions")

SUMMARY_RE = re.compile(
    r"##\s+Summary for Next Session\s*\n(.*?)(?=\n##\s|\Z)",
    re.DOTALL,
)
GOAL_RE = re.compile(
    r"##\s+Goal\s*\n(.*?)(?=\n##\s|\Z)",
    re.DOTALL,
)
FILES_RE = re.compile(
    r"##\s+Files Modified\s*\n(.*?)(?=\n##\s|\Z)",
    re.DOTALL,
)


def clean_block(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    return text.strip()


def extract(text: str, pattern: re.Pattern) -> str:
    m = pattern.search(text)
    return clean_block(m.group(1)) if m else ""


def session_files() -> list[Path]:
    if not SESSIONS_DIR.exists():
        return []
    return sorted(SESSIONS_DIR.glob("[0-9][0-9]-*.md"))


def print_session(f: Path, verbose: bool) -> None:
    text = f.read_text(encoding="utf-8")
    summary = extract(text, SUMMARY_RE)
    goal = extract(text, GOAL_RE)

    print(f"# From {f.stem}")
    if goal:
        print(f"**Goal:** {goal}")
    if summary:
        print()
        print(summary)
    else:
        print("_(no summary filled in yet)_")
    if verbose:
        files = extract(text, FILES_RE)
        if files:
            print()
            print("**Files modified:**")
            for line in files.splitlines():
                if line.strip():
                    print(f"  {line.strip()}")
    print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print session summaries.")
    parser.add_argument("--last", type=int, default=1)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    files = session_files()
    if not files:
        print("No sessions found in .ai/sessions/", file=sys.stderr)
        return 1

    if args.list:
        print(f"Found {len(files)} session(s):")
        for f in files:
            first_line = f.read_text(encoding="utf-8").splitlines()[0]
            print(f"  {f.name}  —  {first_line.lstrip('# ').strip()}")
        return 0

    for f in files[-args.last:]:
        print_session(f, verbose=args.verbose)
    return 0


if __name__ == "__main__":
    sys.exit(main())
