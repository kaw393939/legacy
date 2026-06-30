#!/usr/bin/env python3
"""Guardrails for keeping templates, CSS, and JS maintainable."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import re

from tools.site_framework import ROOT, TEXT_ENCODING


MAX_CSS_PART_LINES = 700
MAX_JS_MODULE_LINES = 350
REMOVED_FILES = (
    "static/css/parts/10-10-sections.css",
    "static/css/parts/07-7-hero-section.css",
    "static/css/parts/09-9-faq-accordion-components.css",
    "static/css/parts/17-17-contact-form-risd-design.css",
    "static/css/parts/18-01-hero-overrides.css",
    "static/css/parts/18-05-content-founder.css",
    "static/css/parts/18-18-legacy-defenders-redesign.css",
    "static/css/parts/18-07-diy-free-guide-pages.css",
    "static/css/styles.css",
)
REQUIRED_FILES = (
    "static/js/main.js",
    "static/js/modules/dom.js",
    "static/js/modules/analytics.js",
    "static/js/modules/analytics/core.js",
    "static/js/modules/analytics/cta.js",
    "static/js/modules/analytics/engagement.js",
    "static/js/modules/analytics/forms.js",
    "static/js/modules/assets.js",
    "static/js/modules/contact.js",
    "static/js/modules/faq.js",
    "static/js/modules/navigation.js",
    "static/js/modules/print.js",
    "static/js/modules/runtime-config.js",
)
DISALLOWED_PATTERNS = (
    ("inline event handler", re.compile(r"\bon[a-z]+\s*=", re.I)),
    ("inline style attribute", re.compile(r"(?<!\.)\bstyle\s*=", re.I)),
    ("inline style block", re.compile(r"<style\b", re.I)),
    ("transition all", re.compile(r"transition\s*:\s*all\b", re.I)),
)
RAW_ICON_PATTERN = re.compile(r"<i\s+class=", re.I)
CSS_SELECTOR_PATTERN = re.compile(r"^\s*([^@{}][^{]+?)\s*\{")
ALLOWED_DUPLICATE_SELECTOR_PREFIXES = (
    "*",
    ":root",
    "a",
    "body",
    "html",
    "img",
    ".btn",
    ".card-",
    ".category-",
    ".contact-",
    ".container",
    ".content-",
    ".cta",
    ".faq-",
    ".footer",
    ".form-",
    ".grid-",
    ".guide-",
    ".hero",
    ".ld-",
    ".logo",
    ".mobile-",
    ".nav",
    ".offer-",
    ".package",
    ".page-",
    ".phase-",
    ".prearranged-",
    ".pricing-",
    ".process-",
    ".proof-",
    ".psychological-",
    ".public-",
    ".scroll-",
    ".section-",
    ".service-",
    ".services-",
    ".situation-",
    ".stat-",
    ".tech-",
    ".testimonial-",
    ".text-",
    ".top-bar",
    ".trust-",
    ".value-",
    ".whatsapp-",
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


def check_raw_icon_markup(errors: list[str]) -> None:
    allowed = "templates/macros/ui.html"
    for source in source_files():
        if source.path.suffix != ".html" or source.label == allowed:
            continue

        for match in RAW_ICON_PATTERN.finditer(source.text):
            line_number = source.text.count("\n", 0, match.start()) + 1
            errors.append(f"{source.label}:{line_number}: use macros/ui.html icon() instead of raw <i> markup")


def duplicate_selector_allowed(selector: str) -> bool:
    stripped = selector.strip()
    return stripped.startswith(ALLOWED_DUPLICATE_SELECTOR_PREFIXES)


def check_duplicate_selectors(errors: list[str]) -> None:
    selectors: dict[str, list[tuple[str, int]]] = defaultdict(list)

    for path in sorted((ROOT / "static" / "css" / "parts").glob("*.css")):
        text = path.read_text(encoding=TEXT_ENCODING)
        for line_number, line in enumerate(text.splitlines(), start=1):
            match = CSS_SELECTOR_PATTERN.match(line)
            if not match:
                continue

            selector = match.group(1).strip()
            if selector in {"from", "to"} or selector.endswith("%"):
                continue
            selectors[selector].append((path.relative_to(ROOT).as_posix(), line_number))

    for selector, locations in sorted(selectors.items()):
        files = {filename for filename, _line in locations}
        if len(locations) < 2 or len(files) < 2 or duplicate_selector_allowed(selector):
            continue

        detail = ", ".join(f"{filename}:{line}" for filename, line in locations[:4])
        errors.append(f"duplicate selector without allowlist: {selector} ({detail})")


def check_module_entry(errors: list[str]) -> None:
    base = (ROOT / "templates" / "base.html").read_text(encoding=TEXT_ENCODING)
    main = (ROOT / "static" / "js" / "main.js").read_text(encoding=TEXT_ENCODING)

    if '<script type="module" src="main.js?v={{ asset_version }}"></script>' not in base:
        errors.append("templates/base.html: runtime script should be loaded as a versioned ES module")

    if "import " not in main or "ready(() =>" not in main:
        errors.append("static/js/main.js: expected a small ES module entry point")


def check_runtime_config_contract(errors: list[str]) -> None:
    base = (ROOT / "templates" / "base.html").read_text(encoding=TEXT_ENCODING)
    build = (ROOT / "build.py").read_text(encoding=TEXT_ENCODING)
    core = (ROOT / "static" / "js" / "modules" / "analytics" / "core.js").read_text(encoding=TEXT_ENCODING)
    contact = (ROOT / "static" / "js" / "modules" / "contact.js").read_text(encoding=TEXT_ENCODING)

    disallowed_globals = ("window.CONVERSION_VALUES", "window.CONTACT_INTENT_OPTIONS", "window.ldAnalyticsEnabled")
    for global_name in disallowed_globals:
        if global_name in base:
            errors.append(f"templates/base.html: runtime config should not define {global_name} inline")

    if "write_runtime_config" not in build or "modules/runtime-config.js" not in build:
        errors.append("build.py: should generate modules/runtime-config.js from source data")

    if "runtimeConfig" not in core or "runtimeConfig" not in contact:
        errors.append("JS runtime modules should consume runtimeConfig instead of window globals")


def main() -> int:
    errors: list[str] = []

    check_expected_files(errors)
    check_css_part_size(errors)
    check_js_module_size(errors)
    check_disallowed_patterns(errors)
    check_raw_icon_markup(errors)
    check_duplicate_selectors(errors)
    check_module_entry(errors)
    check_runtime_config_contract(errors)

    if errors:
        print("Frontend architecture check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("OK frontend architecture checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
