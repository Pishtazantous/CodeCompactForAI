#!/usr/bin/env python3
"""
apply_ai_output.py — Parse and apply AI-generated file blocks.

Reads an AI response file (or stdin) and extracts blocks like:

    ```file:path/to/file.ts
    <content>
    ```

For each block:
  * If the target file exists, a timestamped backup is made
    under .ai/backups/<timestamp>/<path> before overwriting.
  * If the target file does not exist and --force is not set, the block
    is skipped (safety).
  * Paths outside the project root are rejected.

Usage:
    python tools/apply_ai_output.py ai_response.md
    python tools/apply_ai_output.py ai_response.md --dry-run
    python tools/apply_ai_output.py ai_response.md --force
    cat ai_response.md | python tools/apply_ai_output.py --from-stdin

Requires Python 3.8+.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

BLOCK_RE = re.compile(
    r"```file:([^\s`]+)\s*\n(.*?)\n```",
    re.DOTALL,
)

BACKUP_DIR_NAME = ".ai/backups"


def parse_blocks(text: str) -> list[tuple[str, str]]:
    """Return list of (path, content) tuples from AI response."""
    blocks: list[tuple[str, str]] = []
    for m in BLOCK_RE.finditer(text):
        path = m.group(1).strip()
        content = m.group(2)
        if not content.endswith("\n"):
            content += "\n"
        blocks.append((path, content))
    return blocks


def make_backup(path: Path, backup_root: Path) -> Path | None:
    """Copy the existing file into a timestamped backup directory."""
    if not path.exists():
        return None
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = backup_root / ts / path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup_path)
    return backup_path


def apply_block(
    rel_path: str,
    content: str,
    root: Path,
    backup_root: Path,
    dry_run: bool,
    force: bool,
    no_backup: bool,
) -> tuple[str, str]:
    """Apply a single block. Returns (status, detail)."""
    try:
        target = (root / rel_path).resolve()
    except OSError:
        return ("REJECTED", f"{rel_path} (invalid path)")

    if not str(target).startswith(str(root.resolve())):
        return ("REJECTED", f"{rel_path} (outside project root)")

    existed = target.exists()

    if not existed and not force:
        return ("SKIPPED",
                f"{rel_path} (file does not exist; use --force to create)")

    if dry_run:
        action = "WOULD UPDATE" if existed else "WOULD CREATE"
        return (action, rel_path)

    if existed and not no_backup:
        make_backup(target.relative_to(root), backup_root)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8", newline="\n")
    return ("WROTE" if existed else "CREATED", rel_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Parse AI-generated ```file:...``` blocks and apply them.",
    )
    parser.add_argument("source", nargs="?",
                        help="Path to AI response file (.md, .txt)")
    parser.add_argument("--from-stdin", action="store_true",
                        help="Read AI response from stdin")
    parser.add_argument("-r", "--root", default=".",
                        help="Project root (default: cwd)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done, do not write anything")
    parser.add_argument("--force", action="store_true",
                        help="Allow creating new files")
    parser.add_argument("--no-backup", action="store_true",
                        help="Skip creating backups")
    args = parser.parse_args(argv)

    if args.from_stdin:
        text = sys.stdin.read()
    elif args.source:
        source_path = Path(args.source)
        if not source_path.exists():
            print(f"Error: file not found: {source_path}", file=sys.stderr)
            return 2
        text = source_path.read_text(encoding="utf-8")
    else:
        print("Provide a source file or use --from-stdin.", file=sys.stderr)
        return 2

    blocks = parse_blocks(text)
    if not blocks:
        print("No ```file:path``` blocks found in the input.", file=sys.stderr)
        return 1

    root = Path(args.root).resolve()
    backup_root = root / BACKUP_DIR_NAME

    print(f"Found {len(blocks)} file block(s) in AI response.")
    if args.dry_run:
        print("(dry-run mode: no changes will be written)")
    print()

    results: list[tuple[str, str]] = []
    for rel_path, content in blocks:
        status, detail = apply_block(
            rel_path, content, root, backup_root,
            dry_run=args.dry_run, force=args.force,
            no_backup=args.no_backup,
        )
        results.append((status, detail))
        print(f"  [{status:14}] {detail}")

    written = sum(1 for s, _ in results if s in ("WROTE", "CREATED"))
    skipped = sum(1 for s, _ in results if s == "SKIPPED")
    rejected = sum(1 for s, _ in results if s == "REJECTED")

    print()
    print(f"Applied: {written}  |  Skipped: {skipped}  |  Rejected: {rejected}")

    if not args.no_backup and not args.dry_run and written:
        print(f"Backups saved in: {backup_root}")

    if skipped and not args.force:
        print("\nHint: use --force to create skipped files.", file=sys.stderr)

    return 0 if rejected == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
