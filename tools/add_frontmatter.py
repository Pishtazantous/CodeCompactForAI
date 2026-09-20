#!/usr/bin/env python3
"""Add YAML frontmatter to prompt markdown files.

Usage:
    python tools/add_frontmatter.py --dry-run
    python tools/add_frontmatter.py
    python tools/add_frontmatter.py --dir prompts/Expertise and Experience-FA
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# id -> (title, lang, category, depends_on)
META: dict[str, tuple[str, str, str, list[str]]] = {
    # Base layer
    "01-system": ("System Role and codemerge Tool", "fa", "base", []),
    "01-system-append-2": ("Editing Rules (append)", "en", "base", ["01-system"]),
    "02-manifest": ("Send Project Manifest", "fa", "base", ["01-system"]),
    # Task prompts
    "03-bug-fix": ("Task: Bug Fix", "fa", "task", []),
    "04-feature": ("Task: Add Feature", "fa", "task", []),
    "05-refactor": ("Task: Refactor", "fa", "task", []),
    "06-code-review": ("Task: Code Review", "fa", "task", []),
    "07-tests": ("Task: Write Tests", "fa", "task", []),
    "08-explain-code": ("Task: Explain Code", "fa", "task", []),
    "09-continue-session": ("Continue Session", "fa", "task", []),
    # Helpers
    "10-recovery": ("Recovery Prompt", "fa", "helper", []),
    "11-limit-files": ("Limit File Requests", "fa", "helper", []),
    "12-long-response": ("Manage Long Response", "fa", "helper", []),
    "13-final-summary": ("Final Summary", "fa", "helper", []),
    "14-checklist": ("Pre-Response Checklist", "fa", "helper", []),
    # Anti-slop
    "00-anti-slop-core": ("Core Anti-Slop Layer", "mixed", "expertise", []),
    "00-master-anti-slop": ("Master Anti-Slop Layer", "en", "expertise", []),
    # Expertise (EN)
    "01-frontend-architecture": ("Frontend Architect", "en", "expertise", []),
    "02-typescript": ("TypeScript Expert", "en", "expertise", []),
    "03-react-patterns": ("React Patterns Expert", "en", "expertise", []),
    "04-ui-design-system": ("UI & Design System Expert", "en", "expertise", []),
    "05-state-management": ("State Management Expert", "en", "expertise", []),
    "06-api-data-fetching": ("API & Data Fetching Expert", "en", "expertise", []),
    "07-security-auth": ("Security & Auth Expert", "en", "expertise", []),
    "08-performance": ("Performance Expert", "en", "expertise", []),
    "09-testing": ("Testing Expert", "en", "expertise", []),
    "10-devops-deployment": ("DevOps & Deployment Expert", "en", "expertise", []),
    "11-refactoring-legacy": ("Refactoring & Legacy Expert", "en", "expertise", []),
    "12-accessibility": ("Accessibility Expert", "en", "expertise", []),
}


def make_frontmatter(
    stem: str, lang_override: str | None = None,
) -> str:
    title, lang, category, deps = META.get(
        stem, (stem.replace("-", " ").title(), "en", "helper", []))
    if lang_override:
        lang = lang_override
    deps_str = "[" + ", ".join(deps) + "]"
    return (
        "---\n"
        f"id: {stem}\n"
        f'title: "{title}"\n'
        f"lang: {lang}\n"
        f"depends_on: {deps_str}\n"
        f"category: {category}\n"
        "version: 1\n"
        "---\n"
    )


def has_frontmatter(text: str) -> bool:
    return text.startswith("---\n")


def process_file(p: Path, dry_run: bool, lang_override: str | None) -> bool:
    text = p.read_text(encoding="utf-8")
    if has_frontmatter(text):
        print(f"  skip (already has frontmatter): {p}")
        return False

    fm = make_frontmatter(p.stem, lang_override)
    new_text = fm + "\n" + text

    if dry_run:
        print(f"  would add frontmatter to: {p}")
        print(f"    {fm.strip().replace(chr(10), ' | ')}")
    else:
        p.write_text(new_text, encoding="utf-8", newline="\n")
        print(f"  OK: {p}")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--dir", default="prompts",
                    help="Directory to scan (default: prompts)")
    ap.add_argument("--lang", choices=("fa", "en", "mixed"),
                    help="Force language for all files in this run")
    ap.add_argument("--include-readme", action="store_true",
                    help="Also add frontmatter to README.md files (default: skip)")
    args = ap.parse_args()

    root = Path(args.dir)
    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        return 1

    count = 0
    for p in sorted(root.rglob("*.md")):
        if not args.include_readme and p.name.lower() == "readme.md":
            continue
        if process_file(p, args.dry_run, args.lang):
            count += 1

    print()
    verb = "Would modify" if args.dry_run else "Modified"
    print(f"{verb} {count} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())