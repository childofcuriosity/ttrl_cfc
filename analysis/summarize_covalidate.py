#!/usr/bin/env python3
"""Summarize TTRL co-validation CSV files without loading responses into RAM."""

from __future__ import annotations

import argparse
import ast
import csv
import sys
from pathlib import Path


def as_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def summarize(path: Path) -> dict[str, str | int | float]:
    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    rows = greedy_correct = pseudo_correct = vote_count = vote_correct = 0
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"greedy_correct", "pseudo_correct", "votes_correct"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path}: missing columns {sorted(missing)}")
        for row in reader:
            rows += 1
            greedy_correct += as_bool(row["greedy_correct"])
            pseudo_correct += as_bool(row["pseudo_correct"])
            votes = ast.literal_eval(row["votes_correct"])
            if not isinstance(votes, list) or not all(isinstance(item, bool) for item in votes):
                raise ValueError(f"{path}: votes_correct must be a list of booleans")
            vote_count += len(votes)
            vote_correct += sum(votes)
    if rows == 0 or vote_count == 0:
        raise ValueError(f"{path}: no evaluation rows")
    return {
        "file": str(path),
        "rows": rows,
        "votes": vote_count,
        "vote_accuracy": vote_correct / vote_count,
        "greedy_accuracy": greedy_correct / rows,
        "pseudo_label_accuracy": pseudo_correct / rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path, nargs="+")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    summaries = [summarize(path) for path in args.csv]
    fields = list(summaries[0])
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        handle = args.output.open("w", encoding="utf-8", newline="")
    else:
        handle = sys.stdout
    try:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(summaries)
    finally:
        if args.output:
            handle.close()


if __name__ == "__main__":
    main()
