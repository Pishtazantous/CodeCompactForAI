#!/usr/bin/env python3
"""
estimate.py — Estimate tokens and cost of a file before sending to AI.

Usage:
    python tools/estimate.py bundle.txt
    python tools/estimate.py bundle.txt --model gpt-4o
    python tools/estimate.py bundle.txt --model claude-3.5-sonnet

Requires Python 3.8+. Uses tiktoken if installed for exact token counts;
falls back to a rough 4-chars-per-token heuristic otherwise.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Prices per 1M tokens (USD). Update as pricing changes.
PRICING = {
    "gpt-4o":            {"in": 2.50,  "out": 10.00},
    "gpt-4o-mini":       {"in": 0.15,  "out": 0.60},
    "gpt-4-turbo":       {"in": 10.00, "out": 30.00},
    "claude-3.5-sonnet": {"in": 3.00,  "out": 15.00},
    "claude-3.5-haiku":  {"in": 0.80,  "out": 4.00},
    "claude-3-opus":     {"in": 15.00, "out": 75.00},
    "deepseek-chat":     {"in": 0.14,  "out": 0.28},
    "deepseek-reasoner": {"in": 0.55,  "out": 2.19},
}


def estimate_tokens(text: str) -> tuple[int, str]:
    """Return (token_count, method_used)."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text)), "tiktoken (exact)"
    except Exception:
        return max(1, len(text) // 4), "heuristic (~4 chars/token)"


def human_size(n: int) -> str:
    for unit in ("B", "K", "M", "G"):
        if n < 1024:
            return f"{n:.1f}{unit}" if unit != "B" else f"{n}{unit}"
        n /= 1024  # type: ignore
    return f"{n:.1f}T"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Estimate tokens and cost of a file.",
    )
    parser.add_argument("file", help="File to estimate")
    parser.add_argument(
        "--model", default="gpt-4o",
        choices=sorted(PRICING.keys()),
        help="Model to estimate cost for",
    )
    parser.add_argument(
        "--output-tokens", type=int, default=2000,
        help="Expected output tokens (default: 2000)",
    )
    args = parser.parse_args(argv)

    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8", errors="replace")
    tokens, method = estimate_tokens(text)
    pricing = PRICING[args.model]

    input_cost = tokens / 1_000_000 * pricing["in"]
    output_cost = args.output_tokens / 1_000_000 * pricing["out"]
    total = input_cost + output_cost

    print(f"File:           {args.file}")
    print(f"Size:           {human_size(len(text.encode('utf-8')))}")
    print(f"Tokens (in):    {tokens:,}  [{method}]")
    print(f"Model:          {args.model}")
    print(f"Output (est.):  {args.output_tokens:,} tokens")
    print()
    print(f"Input cost:     ${input_cost:.4f}")
    print(f"Output cost:    ${output_cost:.4f}")
    print(f"Total:          ${total:.4f}")

    # Warnings
    if tokens > 50_000:
        print()
        print("Warning: input exceeds 50k tokens. Consider:")
        print("  python codemerge.py manifest --no-symbols --no-imports")

    return 0


if __name__ == "__main__":
    sys.exit(main())