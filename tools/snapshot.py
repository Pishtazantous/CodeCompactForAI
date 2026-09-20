#!/usr/bin/env python3
"""
snapshot.py — Take timestamped snapshots of the project's source files.

Usage:
    python tools/snapshot.py                     # create snapshot
    python tools/snapshot.py --label before-ai
    python tools/snapshot.py --list              # list snapshots
    python tools/snapshot.py --restore <name>    # restore
    python tools/snapshot.py --clean             # keep only latest N

Requires Python 3.8+.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

SNAPSHOT_ROOT = Path(".ai/snapshots")
KEEP_LAST = 10

EXCLUDE_DIRS = {
    ".git", "node_modules", "venv", ".venv", "__pycache__",
    ".next", "dist", "build", ".ai", ".turbo", "coverage",
    "target", "out", ".idea", ".vscode", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", ".cache", ".tox",
}

EXCLUDE_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "poetry.lock", "Pipfile.lock", "Cargo.lock",
    "go.sum", "bun.lockb", "tsconfig.tsbuildinfo",
}

EXCLUDE_SUFFIXES = {".min.js", ".min.css", ".map"}


def should_skip(path: Path) -> bool:
    if any(part in EXCLUDE_DIRS for part in path.parts):
        return True
    if path.name in EXCLUDE_FILES:
        return True
    if path.suffix in EXCLUDE_SUFFIXES:
        return True
    return False


def iter_source_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if should_skip(rel):
            continue
        out.append(p)
    return out


def create_snapshot(root: Path, label: str | None = None) -> Path:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    name = f"{ts}-{label}" if label else ts
    target = SNAPSHOT_ROOT / name
    target.mkdir(parents=True, exist_ok=True)

    files = iter_source_files(root)
    manifest = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "label": label,
        "root": str(root),
        "file_count": len(files),
        "files": [],
    }

    for f in files:
        rel = f.relative_to(root)
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(f, dest)
            manifest["files"].append(str(rel))
        except OSError as e:
            print(f"  ! skip {rel}: {e}", file=sys.stderr)

    (target / "_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return target


def list_snapshots() -> list[Path]:
    if not SNAPSHOT_ROOT.exists():
        return []
    return sorted(
        [p for p in SNAPSHOT_ROOT.iterdir() if p.is_dir()],
        reverse=True,
    )


def find_snapshot(name: str) -> Path | None:
    exact = SNAPSHOT_ROOT / name
    if exact.exists():
        return exact
    matches = [s for s in list_snapshots() if s.name.startswith(name)]
    return matches[0] if matches else None


def restore_snapshot(root: Path, name: str) -> int:
    target = find_snapshot(name)
    if target is None:
        print(f"Snapshot not found: {name}", file=sys.stderr)
        for s in list_snapshots():
            print(f"  {s.name}")
        return 1

    manifest_path = target / "_manifest.json"
    if not manifest_path.exists():
        print(f"Invalid snapshot (missing manifest): {target}", file=sys.stderr)
        return 1

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    restored = 0
    for rel in manifest["files"]:
        src = target / rel
        dest = root / rel
        if not src.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        restored += 1

    print(f"Restored {restored} file(s) from {target.name}")
    return 0


def clean_old_snapshots(keep: int = KEEP_LAST) -> int:
    snapshots = list_snapshots()
    to_remove = snapshots[keep:]
    for s in to_remove:
        shutil.rmtree(s, ignore_errors=True)
    return len(to_remove)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Snapshot project source files.")
    parser.add_argument("-r", "--root", default=".")
    parser.add_argument("-l", "--label", default=None)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--restore", metavar="NAME")
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()

    if args.list:
        snapshots = list_snapshots()
        if not snapshots:
            print("No snapshots found.")
            return 0
        print(f"Snapshots ({len(snapshots)}):")
        for s in snapshots:
            mp = s / "_manifest.json"
            count = "?"
            if mp.exists():
                try:
                    m = json.loads(mp.read_text(encoding="utf-8"))
                    count = m.get("file_count", "?")
                except Exception:
                    pass
            print(f"  {s.name}  ({count} files)")
        return 0

    if args.restore:
        return restore_snapshot(root, args.restore)

    if args.clean:
        removed = clean_old_snapshots()
        print(f"Removed {removed} old snapshot(s).")
        return 0

    target = create_snapshot(root, args.label)
    manifest = json.loads((target / "_manifest.json").read_text("utf-8"))
    print(f"Snapshot created: {target}")
    print(f"  Files: {manifest['file_count']}")
    print(f"  Label: {manifest.get('label') or '(none)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
