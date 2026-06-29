#!/usr/bin/env python3
"""One-time CSS refactor helper.

Splits static/css/styles.css into ordered parts under static/css/parts/
using the existing section header markers.

This is intended to be run manually when migrating the repo; afterwards,
edit the files in static/css/parts/ and the build will bundle them.
"""

from __future__ import annotations

import re
from pathlib import Path


SECTION_RE = re.compile(r"^/\*\s*=+\s*(?P<title>[^*]+?)\s*=+\s*\*/\s*$")


def _slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "section"


def split_stylesheet(source_path: Path, parts_dir: Path) -> list[Path]:
    css = source_path.read_text(encoding="utf-8")
    lines = css.splitlines(keepends=True)

    # Identify indices of major section headers.
    headers: list[tuple[int, str]] = []
    for idx, line in enumerate(lines):
        match = SECTION_RE.match(line)
        if match:
            title = match.group("title")
            # Skip very small decorative markers; keep the big numbered ones.
            if "LEGS ON THE GROUND" in title:
                continue
            if re.search(r"\b\d+\.", title):
                headers.append((idx, title))

    # Fallback: if regex didn't catch anything, just write a single part.
    if not headers:
        parts_dir.mkdir(parents=True, exist_ok=True)
        out = parts_dir / "00-styles.css"
        out.write_text(css, encoding="utf-8")
        return [out]

    # Add end sentinel.
    headers.append((len(lines), "END"))

    parts_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for part_idx in range(len(headers) - 1):
        start, title = headers[part_idx]
        end, _ = headers[part_idx + 1]

        chunk = "".join(lines[start:end]).strip("\n") + "\n"
        if not chunk.strip():
            continue

        # Prefix keeps lexical ordering stable even if numbers repeat.
        filename = f"{part_idx:02d}-{_slugify(title)[:60]}.css"
        out_path = parts_dir / filename
        out_path.write_text(chunk, encoding="utf-8")
        written.append(out_path)

    return written


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    source = repo_root / "static" / "css" / "styles.css"
    parts = repo_root / "static" / "css" / "parts"

    if not source.exists():
        raise SystemExit(f"Source stylesheet not found: {source}")

    written = split_stylesheet(source, parts)
    print(f"Wrote {len(written)} part files to {parts}")


if __name__ == "__main__":
    main()
