#!/usr/bin/env python3
"""Extract the key validation series from a preserved veRL console log."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


FIELDS = {
    "step": "training/global_step",
    "training_score": "val-aux/MATH-TTT/score/mean@16",
    "format_score": "val-aux/MATH-TTT/format_score/mean@16",
    "accuracy": "val-core/MATH-TTT/acc/mean@16",
}


def extract(log_path: Path) -> list[dict[str, float]]:
    patterns = {
        output: re.compile(re.escape(metric) + r":(-?[0-9]+(?:\.[0-9]+)?)")
        for output, metric in FIELDS.items()
    }
    rows = []
    with log_path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            values = {
                output: float(match.group(1))
                for output, pattern in patterns.items()
                if (match := pattern.search(line))
            }
            if len(values) == len(patterns):
                rows.append(values)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = extract(args.log)
    if not rows:
        raise SystemExit(f"No complete validation records found in {args.log}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
