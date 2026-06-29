#!/usr/bin/env python3
"""Validate source content contracts before the static build runs."""

from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content"
PAGES_DIR = CONTENT_DIR / "pages"
TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"

MAX_TITLE_LENGTH = 75
MAX_DESCRIPTION_LENGTH = 160


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        return {}, raw

    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}, raw

    return yaml.safe_load(parts[1]) or {}, parts[2].strip()


def output_name(path: Path) -> str:
    return "index.html" if path.name == "home.md" else f"{path.stem}.html"


def check_required(errors: list[str], source: str, data: dict, keys: list[str]) -> None:
    for key in keys:
        if key not in data or data[key] in ("", None):
            errors.append(f"{source}: missing required field {key!r}")


def check_list_min(errors: list[str], source: str, data: dict, key: str, minimum: int) -> None:
    value = data.get(key)
    if not isinstance(value, list) or len(value) < minimum:
        errors.append(f"{source}: {key!r} must contain at least {minimum} items")


def check_image(errors: list[str], source: str, hero: dict | None) -> None:
    if not hero:
        errors.append(f"{source}: missing hero block")
        return

    image = hero.get("image")
    alt = hero.get("alt")

    if not image:
        errors.append(f"{source}: hero.image is required")
    elif image.startswith(("http://", "https://")):
        return
    else:
        candidate = STATIC_DIR / image
        if not candidate.exists():
            errors.append(f"{source}: hero.image does not exist in static/: {image}")

    if alt is None:
        errors.append(f"{source}: hero.alt is required; use an empty string only for decorative images")


def validate_config(errors: list[str]) -> None:
    config_path = CONTENT_DIR / "config.yaml"
    if not config_path.exists():
        errors.append("content/config.yaml is missing")
        return

    config = load_yaml(config_path)
    site = config.get("site", {})
    build = config.get("build", {})

    check_required(errors, "content/config.yaml site", site, ["title", "description", "url", "email", "phone_display"])

    parsed = urlparse(site.get("url", ""))
    if parsed.scheme != "https" or not parsed.netloc:
        errors.append("content/config.yaml: site.url must be an absolute https URL")

    for key in ("output_dir", "static_dir", "template_dir"):
        if not build.get(key):
            errors.append(f"content/config.yaml build: missing {key!r}")


def validate_pages(errors: list[str], warnings: list[str]) -> None:
    page_ids: dict[str, str] = {}

    for path in sorted(PAGES_DIR.glob("*.md")):
        page, body = parse_frontmatter(path)
        source = f"content/pages/{path.name}"

        check_required(errors, source, page, ["layout", "title", "description", "page_id"])

        title = str(page.get("title", ""))
        description = str(page.get("description", ""))
        layout = str(page.get("layout", ""))
        page_id = str(page.get("page_id", ""))

        if len(title) > MAX_TITLE_LENGTH:
            warnings.append(f"{source}: title is {len(title)} chars; consider keeping it under {MAX_TITLE_LENGTH}")

        if len(description) > MAX_DESCRIPTION_LENGTH:
            errors.append(f"{source}: description is {len(description)} chars; keep it under {MAX_DESCRIPTION_LENGTH}")

        if page_id:
            if page_id in page_ids:
                errors.append(f"{source}: duplicate page_id {page_id!r}; also used by {page_ids[page_id]}")
            page_ids[page_id] = source

        if layout and not (TEMPLATES_DIR / f"{layout}.html").exists():
            errors.append(f"{source}: layout template does not exist: templates/{layout}.html")

        if not body:
            warnings.append(f"{source}: body content is empty")

        if layout in {"page", "situation"}:
            check_image(errors, source, page.get("hero"))

        if layout == "page":
            check_list_min(errors, source, page, "hero_actions", 1)

        if layout == "situation":
            check_required(errors, source, page, ["contact_interest", "eyebrow", "boundary"])
            check_list_min(errors, source, page, "first_actions", 3)
            check_list_min(errors, source, page, "common_mistakes", 3)
            check_list_min(errors, source, page, "how_we_help", 3)
            check_list_min(errors, source, page, "costs", 3)
            check_list_min(errors, source, page, "timeline", 3)
            check_list_min(errors, source, page, "records", 2)
            check_list_min(errors, source, page, "related_links", 2)

        canonical = (page.get("seo") or {}).get("canonical")
        if canonical and canonical != f"/{output_name(path)}" and path.name != "home.md":
            errors.append(f"{source}: seo.canonical should be /{output_name(path)}")


def validate_data(errors: list[str]) -> None:
    situations_path = CONTENT_DIR / "data" / "situations.yaml"
    if not situations_path.exists():
        return

    situations = load_yaml(situations_path).get("situations", {})
    cards = situations.get("featured") or situations.get("cards") or []
    page_files = {output_name(path) for path in PAGES_DIR.glob("*.md")}

    if not isinstance(cards, list) or not cards:
        errors.append("content/data/situations.yaml: situations.featured must be a non-empty list")
        return

    for index, card in enumerate(cards, start=1):
        source = f"content/data/situations.yaml card {index}"
        check_required(errors, source, card, ["id", "title", "url", "description"])
        url = str(card.get("url", "")).split("#", 1)[0].split("?", 1)[0]
        if url and url not in page_files:
            errors.append(f"{source}: url does not match a source page output: {url}")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    validate_config(errors)
    validate_pages(errors, warnings)
    validate_data(errors)

    for warning in warnings:
        print(f"WARNING: {warning}")

    if errors:
        print("Content contract check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("OK content contracts passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
