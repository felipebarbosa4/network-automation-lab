#!/usr/bin/env python3
"""Compare two configuration files after conservative whitespace normalization."""

from __future__ import annotations

import argparse
import difflib
from pathlib import Path


def normalized_lines(path: Path) -> list[str]:
    lines: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines


def compare(expected: Path, observed: Path) -> tuple[bool, str]:
    expected_lines = normalized_lines(expected)
    observed_lines = normalized_lines(observed)
    if expected_lines == observed_lines:
        return True, "Configurations match after normalization."

    diff = "\n".join(
        difflib.unified_diff(
            expected_lines,
            observed_lines,
            fromfile=str(expected),
            tofile=str(observed),
            lineterm="",
        )
    )
    return False, diff


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("expected", type=Path)
    parser.add_argument("observed", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        equal, report = compare(args.expected, args.observed)
    except OSError as exc:
        print(f"ERROR: {exc}")
        return 2

    print(report)
    return 0 if equal else 1


if __name__ == "__main__":
    raise SystemExit(main())
