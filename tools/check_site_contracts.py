#!/usr/bin/env python3
"""Validate the Legacy Defenders site profile contracts."""

from __future__ import annotations

from tools.site_framework import CONTENT_DIR, PAGES_DIR, ROOT, TEXT_ENCODING, load_yaml, output_name, page_sources


SITUATION_REQUIRED_LISTS = {
    "first_actions": 3,
    "common_mistakes": 3,
    "how_we_help": 3,
    "costs": 3,
    "timeline": 3,
    "records": 2,
    "related_links": 2,
}
PAGE_REQUIRED_CTA_LAYOUTS = {"internal", "page", "services"}
MAX_LONG_PAGE_LINES = 180
LONG_PAGE_ALLOWLIST = {"founder-plan.md"}
PROFILE_REQUIRED_FIELDS = ("id", "page_eyebrow", "situation_eyebrow", "default_hero_image", "situation_boundary")


def check_required(errors: list[str], source: str, data: dict, keys: tuple[str, ...]) -> None:
    for key in keys:
        if key not in data or data[key] in ("", None):
            errors.append(f"{source}: missing required field {key!r}")


def check_list_min(errors: list[str], source: str, data: dict, key: str, minimum: int) -> None:
    value = data.get(key)
    if not isinstance(value, list) or len(value) < minimum:
        errors.append(f"{source}: {key!r} must contain at least {minimum} items")


def check_situation_depth(errors: list[str]) -> None:
    for page in page_sources():
        if page.frontmatter.get("layout") != "situation":
            continue

        for key, minimum in SITUATION_REQUIRED_LISTS.items():
            check_list_min(errors, page.source_label, page.frontmatter, key, minimum)


def check_required_page_ctas(errors: list[str]) -> None:
    for page in page_sources():
        layout = str(page.frontmatter.get("layout", ""))
        if layout in PAGE_REQUIRED_CTA_LAYOUTS:
            check_list_min(errors, page.source_label, page.frontmatter, "hero_actions", 1)


def check_hero_image_uniqueness(errors: list[str]) -> None:
    seen: dict[str, str] = {}
    for page in page_sources():
        image = ((page.frontmatter.get("hero") or {}).get("image") or "").strip()
        if not image:
            continue

        if image in seen:
            errors.append(f"{page.source_label}: duplicate hero.image {image!r}; also used by {seen[image]}")
            continue

        seen[image] = page.source_label


def check_situation_cards(errors: list[str]) -> None:
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


def check_contact_intake_contract(errors: list[str]) -> None:
    data_path = ROOT / "content" / "data" / "contact-intake.yaml"
    form_path = ROOT / "templates" / "sections" / "contact-form.html"
    macro_path = ROOT / "templates" / "macros" / "contact.html"
    contact_js_path = ROOT / "static" / "js" / "modules" / "contact.js"

    data = load_yaml(data_path).get("contact_intake", {})
    required_lists = ("situations", "roles", "vacancy_statuses", "urgent_issues", "intent_options")
    for key in required_lists:
        if not isinstance(data.get(key), list) or not data[key]:
            errors.append(f"content/data/contact-intake.yaml: contact_intake.{key} must be a non-empty list")

    form = form_path.read_text(encoding=TEXT_ENCODING)
    macros = macro_path.read_text(encoding=TEXT_ENCODING)
    if "care_intake_form(site, contact_intake)" not in form or "contact_methods(site)" not in form:
        errors.append("templates/sections/contact-form.html: contact section should delegate to contact macros")

    for key in ("situations", "roles", "vacancy_statuses", "urgent_issues"):
        if f"contact_intake.{key}" not in macros:
            errors.append(f"templates/macros/contact.html: {key} should be generated from contact_intake data")

    contact_js = contact_js_path.read_text(encoding=TEXT_ENCODING)
    if "runtimeConfig.contactIntentOptions" not in contact_js or "const contactIntentOptions = [" in contact_js:
        errors.append("static/js/modules/contact.js: contact intent options should come from runtimeConfig.contactIntentOptions")


def check_page_size(errors: list[str]) -> None:
    for path in sorted(PAGES_DIR.glob("*.md")):
        if path.name in LONG_PAGE_ALLOWLIST:
            continue

        lines = len(path.read_text(encoding=TEXT_ENCODING).splitlines())
        if lines > MAX_LONG_PAGE_LINES:
            errors.append(
                f"{path.relative_to(ROOT).as_posix()}: {lines} lines exceeds {MAX_LONG_PAGE_LINES}; split or tighten the page"
            )


def check_site_profile(errors: list[str]) -> None:
    profile_path = CONTENT_DIR / "site-profile.yaml"
    if not profile_path.exists():
        errors.append("content/site-profile.yaml is missing")
        return

    profile = load_yaml(profile_path).get("profile", {})
    if not isinstance(profile, dict):
        errors.append("content/site-profile.yaml: profile must be a mapping")
        return

    check_required(errors, "content/site-profile.yaml profile", profile, PROFILE_REQUIRED_FIELDS)

    primary_cta = profile.get("primary_cta")
    if not isinstance(primary_cta, dict):
        errors.append("content/site-profile.yaml: profile.primary_cta must be a mapping")
    else:
        check_required(errors, "content/site-profile.yaml profile.primary_cta", primary_cta, ("text", "icon"))

    probate = ((profile.get("references") or {}).get("probate") or {}) if isinstance(profile.get("references"), dict) else {}
    if not isinstance(probate, dict) or not probate:
        errors.append("content/site-profile.yaml: profile.references.probate must be a mapping")
    else:
        check_required(errors, "content/site-profile.yaml profile.references.probate", probate, ("title", "url"))


def main() -> int:
    errors: list[str] = []

    check_situation_depth(errors)
    check_required_page_ctas(errors)
    check_hero_image_uniqueness(errors)
    check_situation_cards(errors)
    check_contact_intake_contract(errors)
    check_page_size(errors)
    check_site_profile(errors)

    if errors:
        print("Site profile contract check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("OK site profile contracts passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
