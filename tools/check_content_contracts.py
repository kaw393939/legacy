#!/usr/bin/env python3
"""Validate source content contracts before the static build runs."""

from __future__ import annotations

from urllib.parse import urlparse

from tools.site_framework import (
    CONTENT_DIR,
    PAGES_DIR,
    configured_static_dir,
    configured_templates_dir,
    load_yaml,
    output_name,
    page_sources,
)


MAX_TITLE_LENGTH = 75
MAX_DESCRIPTION_LENGTH = 160
PAGE_REQUIRED_FIELDS = ("layout", "title", "description", "page_id")
SITE_REQUIRED_FIELDS = ("title", "description", "url", "email", "phone_display")
BUILD_REQUIRED_FIELDS = ("output_dir", "static_dir", "template_dir")
SITUATION_REQUIRED_FIELDS = ("contact_interest", "eyebrow", "boundary")
SITUATION_REQUIRED_LISTS = {
    "first_actions": 3,
    "common_mistakes": 3,
    "how_we_help": 3,
    "costs": 3,
    "timeline": 3,
    "records": 2,
    "related_links": 2,
}


def check_required(errors: list[str], source: str, data: dict, keys: tuple[str, ...]) -> None:
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
    elif not image.startswith(("http://", "https://")) and not (configured_static_dir() / image).exists():
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

    check_required(errors, "content/config.yaml site", site, SITE_REQUIRED_FIELDS)
    check_required(errors, "content/config.yaml build", build, BUILD_REQUIRED_FIELDS)

    parsed = urlparse(site.get("url", ""))
    if parsed.scheme != "https" or not parsed.netloc:
        errors.append("content/config.yaml: site.url must be an absolute https URL")


def validate_pages(errors: list[str], warnings: list[str]) -> None:
    seen_page_ids: dict[str, str] = {}

    for page in page_sources():
        source = page.source_label
        frontmatter = page.frontmatter

        check_required(errors, source, frontmatter, PAGE_REQUIRED_FIELDS)
        check_title_length(warnings, source, frontmatter)
        check_description_length(errors, source, frontmatter)
        check_page_id(errors, source, frontmatter, seen_page_ids)
        check_layout(errors, source, frontmatter)
        check_body(warnings, source, page.body)
        check_layout_contracts(errors, page)
        check_canonical(errors, page)


def check_title_length(warnings: list[str], source: str, page: dict) -> None:
    title = str(page.get("title", ""))
    if len(title) > MAX_TITLE_LENGTH:
        warnings.append(f"{source}: title is {len(title)} chars; consider keeping it under {MAX_TITLE_LENGTH}")


def check_description_length(errors: list[str], source: str, page: dict) -> None:
    description = str(page.get("description", ""))
    if len(description) > MAX_DESCRIPTION_LENGTH:
        errors.append(f"{source}: description is {len(description)} chars; keep it under {MAX_DESCRIPTION_LENGTH}")


def check_page_id(errors: list[str], source: str, page: dict, seen_page_ids: dict[str, str]) -> None:
    page_id = str(page.get("page_id", ""))
    if not page_id:
        return

    if page_id in seen_page_ids:
        errors.append(f"{source}: duplicate page_id {page_id!r}; also used by {seen_page_ids[page_id]}")
    seen_page_ids[page_id] = source


def check_layout(errors: list[str], source: str, page: dict) -> None:
    layout = str(page.get("layout", ""))
    if layout and not (configured_templates_dir() / f"{layout}.html").exists():
        errors.append(f"{source}: layout template does not exist: templates/{layout}.html")


def check_body(warnings: list[str], source: str, body: str) -> None:
    if not body:
        warnings.append(f"{source}: body content is empty")


def check_layout_contracts(errors: list[str], page) -> None:
    layout = str(page.frontmatter.get("layout", ""))

    if layout in {"page", "situation"}:
        check_image(errors, page.source_label, page.frontmatter.get("hero"))

    if layout == "page":
        check_list_min(errors, page.source_label, page.frontmatter, "hero_actions", 1)

    if layout == "situation":
        check_required(errors, page.source_label, page.frontmatter, SITUATION_REQUIRED_FIELDS)
        for key, minimum in SITUATION_REQUIRED_LISTS.items():
            check_list_min(errors, page.source_label, page.frontmatter, key, minimum)


def check_canonical(errors: list[str], page) -> None:
    canonical = (page.frontmatter.get("seo") or {}).get("canonical")
    expected = f"/{page.output_name}"

    if canonical and canonical != expected and page.path.name != "home.md":
        errors.append(f"{page.source_label}: seo.canonical should be {expected}")


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
        check_required(errors, source, card, ("id", "title", "url", "description"))

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
