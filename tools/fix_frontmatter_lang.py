#!/usr/bin/env python3
"""Fix the `lang:` field in YAML frontmatter based on file location.

Problem:
    Running `add_frontmatter.py --dir prompts --lang fa` recurses into
    subdirectories and forces `lang: fa` on English files too.

Usage:
    python tools/fix_frontmatter_lang.py --dry-run
    python tools/fix_frontmatter_lang.py
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Path prefix -> correct lang. Longest match wins.
RULES: list[tuple[str, str]] = [
    ("prompts/Anti-AI-Slop", "en"),
    ("prompts/Expertise and Experience-FA", "fa"),
    ("prompts/Expertise and Experience", "en"),
    # Files directly in prompts/ stay as-is (default: fa).
]

LANG_RE = re.compile(r"^(lang:\s*)(\S+)\s*$", re.M)


def correct_lang_for(rel_path: str) -> str | None:
    """Return the correct lang for a project-relative posix path, or None."""
    # Try longest prefix first
    for prefix, lang in sorted(RULES, key=lambda x: -len(x[0])):
        if rel_path.startswith(prefix + "/"):
            return lang
    return None


def fix_file(p: Path, project_root: Path, dry_run: bool) -> bool:
    text = p.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return False

    rel = p.relative_to(project_root).as_posix()
    expected = correct_lang_for(rel)
    if expected is None:
        return False

    m = LANG_RE.search(text)
    if not m:
        return False

    current = m.group(2)
    if current == expected:
        return False

    new_text = LANG_RE.sub(rf"\g<1>{expected}", text, count=1)
    if dry_run:
        print(f"  would fix: {rel}  {current} -> {expected}")
    else:
        p.write_text(new_text, encoding="utf-8", newline="\n")
        print(f"  fixed:     {rel}  {current} -> {expected}")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--root", default=".", help="Project root (default: .)")
    args = ap.parse_args()

    project_root = Path(args.root).resolve()
    if not project_root.is_dir():
        print(f"Error: {project_root} is not a directory", file=sys.stderr)
        return 1

    prompts_dir = project_root / "prompts"
    if not prompts_dir.is_dir():
        print(f"Error: {prompts_dir} not found", file=sys.stderr)
        return 1

    count = 0
    for p in sorted(prompts_dir.rglob("*.md")):
        if fix_file(p, project_root, args.dry_run):
            count += 1

    verb = "Would fix" if args.dry_run else "Fixed"
    print(f"\n{verb} {count} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())