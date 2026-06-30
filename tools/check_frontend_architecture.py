#!/usr/bin/env python3
"""Guardrails for keeping templates, CSS, and JS maintainable."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from tools.site_framework import ROOT, TEXT_ENCODING


MAX_CSS_PART_LINES = 1_800
MAX_JS_MODULE_LINES = 350
REMOVED_FILES = (
    "static/css/parts/18-18-legacy-defenders-redesign.css",
)
REQUIRED_FILES = (
    "static/js/main.js",
    "static/js/modules/dom.js",
    "static/js/modules/analytics.js",
    "static/js/modules/assets.js",
    "static/js/modules/contact.js",
    "static/js/modules/faq.js",
    "static/js/modules/navigation.js",
    "static/js/modules/print.js",
)
DISALLOWED_PATTERNS = (
    ("inline event handler", re.compile(r"\bon[a-z]+\s*=", re.I)),
    ("inline style block", re.compile(r"<style\b", re.I)),
    ("transition all", re.compile(r"transition\s*:\s*all\b", re.I)),
)


@dataclass(frozen=True)
class SourceFile:
    path: Path

    @property
    def label(self) -> str:
        return self.path.relative_to(ROOT).as_posix()

    @property
    def text(self) -> str:
        return self.path.read_text(encoding=TEXT_ENCODING)


def line_count(path: Path) -> int:
    return len(path.read_text(encoding=TEXT_ENCODING).splitlines())


def source_files() -> list[SourceFile]:
    roots = (ROOT / "templates", ROOT / "static" / "css", ROOT / "static" / "js")
    extensions = {".html", ".css", ".js"}
    files: list[SourceFile] = []

    for source_root in roots:
        if not source_root.exists():
            continue
        for path in sorted(source_root.rglob("*")):
            if path.is_file() and path.suffix in extensions:
                files.append(SourceFile(path))

    return files


def check_expected_files(errors: list[str]) -> None:
    for relative_path in REQUIRED_FILES:
        if not (ROOT / relative_path).exists():
            errors.append(f"missing required frontend module: {relative_path}")

    for relative_path in REMOVED_FILES:
        if (ROOT / relative_path).exists():
            errors.append(f"removed legacy frontend file still exists: {relative_path}")


def check_css_part_size(errors: list[str]) -> None:
    for path in sorted((ROOT / "static" / "css" / "parts").glob("*.css")):
        lines = line_count(path)
        if lines > MAX_CSS_PART_LINES:
            errors.append(f"{path.relative_to(ROOT).as_posix()}: {lines} lines exceeds {MAX_CSS_PART_LINES}")


def check_js_module_size(errors: list[str]) -> None:
    for path in sorted((ROOT / "static" / "js").rglob("*.js")):
        lines = line_count(path)
        if lines > MAX_JS_MODULE_LINES:
            errors.append(f"{path.relative_to(ROOT).as_posix()}: {lines} lines exceeds {MAX_JS_MODULE_LINES}")


def check_disallowed_patterns(errors: list[str]) -> None:
    for source in source_files():
        text = source.text
        for label, pattern in DISALLOWED_PATTERNS:
            for match in pattern.finditer(text):
                line_number = text.count("\n", 0, match.start()) + 1
                errors.append(f"{source.label}:{line_number}: avoid {label}")


def check_module_entry(errors: list[str]) -> None:
    base = (ROOT / "templates" / "base.html").read_text(encoding=TEXT_ENCODING)
    main = (ROOT / "static" / "js" / "main.js").read_text(encoding=TEXT_ENCODING)

    if '<script type="module" src="main.js?v={{ asset_version }}"></script>' not in base:
        errors.append("templates/base.html: runtime script should be loaded as a versioned ES module")

    if "import " not in main or "ready(() =>" not in main:
        errors.append("static/js/main.js: expected a small ES module entry point")


def main() -> int:
    errors: list[str] = []

    check_expected_files(errors)
    check_css_part_size(errors)
    check_js_module_size(errors)
    check_disallowed_patterns(errors)
    check_module_entry(errors)

    if errors:
        print("Frontend architecture check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("OK frontend architecture checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
