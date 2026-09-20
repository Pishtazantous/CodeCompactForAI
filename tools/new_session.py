#!/usr/bin/env python3
"""
new_session.py — Start a new AI session with a proper scaffold.

Usage:
    python tools/new_session.py "auth refactor"
    python tools/new_session.py "payment bug" --prev 02

Requires Python 3.8+.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

SESSIONS_DIR = Path(".ai/sessions")
INDEX_PATH = SESSIONS_DIR / "index.json"

TEMPLATE = """# Session {num} — {title}

**Started:** {date}
**Previous:** {prev}
**Status:** In Progress

## Goal

<!-- What are we trying to accomplish? One sentence. -->


## Context

<!-- What was done before? Paste the previous session's summary here. -->


## Files Fetched

<!-- List of files fetched via codemerge-fetch in this session. -->


## Files Modified

<!-- What was changed, in which files. -->


## Decisions

<!-- Key decisions made and the reason behind them. -->


## Slop Incidents

<!-- Any AI slop that had to be corrected. Note what was wrong. -->


## Follow-ups

<!-- Things left for the next session. -->


## Summary for Next Session

<!-- A short paragraph the next session can start from. Keep it under
100 words and focus on state, not process. -->
"""


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:40].strip("-") or "session"


def load_index() -> dict:
    if INDEX_PATH.exists():
        try:
            return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"sessions": []}


def save_index(data: dict) -> None:
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Start a new AI session with a proper scaffold.",
    )
    parser.add_argument("title", help="Short session title")
    parser.add_argument("--prev", default=None)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    index = load_index()
    next_num = len(index["sessions"]) + 1
    num_str = f"{next_num:02d}"

    slug = slugify(args.title)
    filename = f"{num_str}-{slug}.md"
    target = SESSIONS_DIR / filename

    if target.exists() and not args.force:
        print(f"Session file already exists: {target}", file=sys.stderr)
        print("Use --force to overwrite.", file=sys.stderr)
        return 1

    content = TEMPLATE.format(
        num=next_num,
        title=args.title,
        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
        prev=args.prev or "—",
    )
    target.write_text(content, encoding="utf-8", newline="\n")

    index["sessions"].append({
        "num": num_str,
        "title": args.title,
        "file": filename,
        "created": datetime.now().isoformat(timespec="seconds"),
        "prev": args.prev,
        "status": "in_progress",
    })
    save_index(index)

    print(f"Session created: {target}")
    print()
    print("Next steps:")
    print(f"  1. Fill in 'Goal' and 'Context' in {target}")
    print("  2. Start your AI chat with the standard prompt order")
    print("  3. When done, fill in 'Summary for Next Session'")
    print("  4. Run: python tools/session_summary.py --last 1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
