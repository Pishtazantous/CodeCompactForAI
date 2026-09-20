#!/usr/bin/env python3
"""
log_metrics.py — Log session metrics to track AI workflow effectiveness.

Usage:
    python tools/log_metrics.py --task "feature" --files-changed 5 \
        --slop-count 1 --time-saved 45

    python tools/log_metrics.py --show        # show totals
    python tools/log_metrics.py --show --last 10
    python tools/log_metrics.py --reset

Requires Python 3.8+.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

METRICS_PATH = Path(".ai/metrics.json")


def load() -> dict:
    if METRICS_PATH.exists():
        try:
            return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"sessions": [], "totals": {}}


def save(data: dict) -> None:
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def recompute_totals(data: dict) -> None:
    sessions = data.get("sessions", [])
    data["totals"] = {
        "sessions": len(sessions),
        "files_changed": sum(s.get("files_changed", 0) for s in sessions),
        "slop_count": sum(s.get("slop_count", 0) for s in sessions),
        "time_saved": sum(s.get("time_saved", 0) for s in sessions),
        "slop_rate": 0.0,
    }
    if sessions:
        data["totals"]["slop_rate"] = (
            data["totals"]["slop_count"] / len(sessions)
        )


def show(data: dict, last: int) -> None:
    sessions = data.get("sessions", [])
    totals = data.get("totals", {})

    if not sessions:
        print("No sessions logged yet.")
        return

    print("========== Totals ==========")
    print(f"  Sessions:      {totals.get('sessions', 0)}")
    print(f"  Files changed: {totals.get('files_changed', 0)}")
    print(f"  Slop events:   {totals.get('slop_count', 0)}")
    print(f"  Time saved:    {totals.get('time_saved', 0)} min")
    print(f"  Slop rate:     {totals.get('slop_rate', 0):.2f} per session")

    if last > 0 and sessions:
        print()
        print(f"========== Last {min(last, len(sessions))} Sessions ==========")
        for s in sessions[-last:]:
            date = s.get("date", "?")
            task = s.get("task", "?")
            files = s.get("files_changed", 0)
            slop = s.get("slop_count", 0)
            saved = s.get("time_saved", 0)
            print(f"  {date}  [{task:10}]  "
                  f"files={files}  slop={slop}  saved={saved}min")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Log and inspect AI workflow metrics.",
    )
    parser.add_argument("--task", default=None,
                        help="Task type: bug-fix, feature, refactor, review")
    parser.add_argument("--files-changed", type=int, default=0)
    parser.add_argument("--slop-count", type=int, default=0)
    parser.add_argument("--time-saved", type=int, default=0,
                        help="Estimated minutes saved vs manual")
    parser.add_argument("--notes", default="")
    parser.add_argument("--show", action="store_true",
                        help="Show totals and recent sessions")
    parser.add_argument("--last", type=int, default=10,
                        help="Number of recent sessions to show (default: 10)")
    parser.add_argument("--reset", action="store_true",
                        help="Delete all metrics")
    args = parser.parse_args(argv)

    data = load()

    if args.reset:
        if METRICS_PATH.exists():
            METRICS_PATH.unlink()
            print(f"Deleted: {METRICS_PATH}")
        return 0

    if args.show:
        show(data, last=args.last)
        return 0

    if not args.task:
        print("Provide --task to log a session, or --show to inspect.",
              file=sys.stderr)
        return 2

    session = {
        "date": datetime.now().isoformat(timespec="seconds"),
        "task": args.task,
        "files_changed": args.files_changed,
        "slop_count": args.slop_count,
        "time_saved": args.time_saved,
        "notes": args.notes,
    }
    data.setdefault("sessions", []).append(session)
    recompute_totals(data)
    save(data)

    totals = data["totals"]
    print(f"Logged session #{totals['sessions']}")
    print(f"  Total files changed: {totals['files_changed']}")
    print(f"  Total slop events:   {totals['slop_count']}")
    print(f"  Total time saved:    {totals['time_saved']} min")
    print(f"  Slop rate:           {totals['slop_rate']:.2f} per session")

    return 0


if __name__ == "__main__":
    sys.exit(main())