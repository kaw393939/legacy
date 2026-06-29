#!/usr/bin/env python3
"""Run generated-site integrity checks through the shared validator."""

from __future__ import annotations

import argparse
from pathlib import Path

from validator import SiteValidator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate generated static site output")
    parser.add_argument("output_dir", nargs="?", default="docs")
    parser.add_argument("--report", help="Optional path for a JSON validation report")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validator = SiteValidator(Path(args.output_dir))
    results = validator.validate_all()
    report = validator.generate_report(results)
    print(report, end="")
    if args.report:
        validator.save_report(Path(args.report), results)

    total_errors = sum(len(result.errors) for result in results)
    if total_errors:
        return 1

    html_count = len(list(Path(args.output_dir).glob("*.html")))
    print(f"OK generated site integrity passed: {html_count} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
