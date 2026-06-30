#!/usr/bin/env python3
"""Validate the active site profile contracts."""

from __future__ import annotations

from tools.site_framework import (
    CONTENT_DIR,
    PAGES_DIR,
    ROOT,
    SITE_PROFILE_CONFIG,
    SITE_PROFILES_DIR,
    TEXT_ENCODING,
    active_site_profile,
    load_site_profile_config,
    load_site_profiles,
    load_yaml,
    output_name,
    page_sources,
)


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
COMPLIANCE_PAGES = (
    "privacy.html",
    "terms.html",
    "cookie-policy.html",
    "accessibility.html",
    "service-boundaries.html",
    "refund-cancellation.html",
    "provider-notice.html",
)
COMPLIANCE_SOURCE_FILES = {page_name.replace(".html", ".md") for page_name in COMPLIANCE_PAGES}
COMPLIANCE_REQUIRED_FIELDS = ("effective_date", "business_name", "service_area")


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
        if page.path.name in COMPLIANCE_SOURCE_FILES:
            continue

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
    if not SITE_PROFILE_CONFIG.exists():
        errors.append("content/site-profile.yaml is missing")
        return

    config = load_site_profile_config()
    active_id = config.get("active_profile")
    if not active_id:
        errors.append("content/site-profile.yaml: active_profile is required")
        return

    profiles_dir = CONTENT_DIR / str(config.get("profiles_dir", "profiles"))
    if not profiles_dir.exists():
        errors.append("content/site-profile.yaml: profiles_dir must point to an existing directory")
        return

    if profiles_dir != SITE_PROFILES_DIR and not profiles_dir.is_dir():
        errors.append("content/site-profile.yaml: profiles_dir must be a directory")
        return

    profiles = load_site_profiles()
    if active_id not in profiles:
        errors.append(f"content/site-profile.yaml: active_profile {active_id!r} has no matching profile file")
        return

    profile = active_site_profile()
    if not isinstance(profile, dict):
        errors.append("active site profile must be a mapping")
        return

    check_required(errors, f"active site profile {active_id}", profile, PROFILE_REQUIRED_FIELDS)

    primary_cta = profile.get("primary_cta")
    if not isinstance(primary_cta, dict):
        errors.append(f"active site profile {active_id}: primary_cta must be a mapping")
    else:
        check_required(errors, f"active site profile {active_id} primary_cta", primary_cta, ("text", "icon"))

    probate = ((profile.get("references") or {}).get("probate") or {}) if isinstance(profile.get("references"), dict) else {}
    if not isinstance(probate, dict) or not probate:
        errors.append(f"active site profile {active_id}: references.probate must be a mapping")
    else:
        check_required(errors, f"active site profile {active_id} references.probate", probate, ("title", "url"))


def compliance_data(errors: list[str]) -> dict:
    path = CONTENT_DIR / "compliance.yaml"
    if not path.exists():
        errors.append("content/compliance.yaml is missing")
        return {}

    compliance = load_yaml(path).get("compliance", {})
    if not isinstance(compliance, dict):
        errors.append("content/compliance.yaml: compliance must be a mapping")
        return {}

    check_required(errors, "content/compliance.yaml compliance", compliance, COMPLIANCE_REQUIRED_FIELDS)
    for key in ("contact", "data", "cookies", "terms", "visit_credit", "provider_notice", "accessibility"):
        if not isinstance(compliance.get(key), dict):
            errors.append(f"content/compliance.yaml: compliance.{key} must be a mapping")

    return compliance


def check_compliance_pages(errors: list[str]) -> None:
    outputs = {page.output_name for page in page_sources()}
    for output_name_value in COMPLIANCE_PAGES:
        if output_name_value not in outputs:
            errors.append(f"missing required compliance page source for {output_name_value}")


def check_footer_compliance_links(errors: list[str]) -> None:
    navigation = load_yaml(CONTENT_DIR / "data" / "navigation.yaml")
    footer_nav = navigation.get("footer_nav", {}) if isinstance(navigation, dict) else {}
    all_links = {
        str(link.get("url", ""))
        for section in footer_nav.values()
        if isinstance(section, dict)
        for link in section.get("links", [])
        if isinstance(link, dict)
    }

    for required_url in COMPLIANCE_PAGES:
        if required_url not in all_links:
            errors.append(f"content/data/navigation.yaml: footer missing compliance link {required_url}")

    footer = (ROOT / "templates" / "components" / "footer.html").read_text(encoding=TEXT_ENCODING)
    if "data-cookie-preferences" not in footer:
        errors.append("templates/components/footer.html: footer must expose Cookie Preferences")


def check_cookie_consent_contract(errors: list[str], compliance: dict) -> None:
    cookies = compliance.get("cookies") if isinstance(compliance.get("cookies"), dict) else {}
    base = (ROOT / "templates" / "base.html").read_text(encoding=TEXT_ENCODING)
    main_js = (ROOT / "static" / "js" / "main.js").read_text(encoding=TEXT_ENCODING)
    core_js = (ROOT / "static" / "js" / "modules" / "analytics" / "core.js").read_text(encoding=TEXT_ENCODING)
    consent_js_path = ROOT / "static" / "js" / "modules" / "cookies.js"

    if not consent_js_path.exists():
        errors.append("static/js/modules/cookies.js is required for cookie consent")
        return

    if "googletagmanager.com/gtag/js" in base:
        errors.append("templates/base.html: Google tag should not load directly before consent")

    if "components/cookie-consent.html" not in base:
        errors.append("templates/base.html: cookie consent component must be included")

    if "initCookieConsent" not in main_js:
        errors.append("static/js/main.js: cookie consent module must initialize")

    if "analyticsConsentGranted" not in core_js or "loadGtagScript" not in core_js:
        errors.append("static/js/modules/analytics/core.js: analytics must be consent-aware")

    if cookies.get("consent_required") and cookies.get("policy_url") != "cookie-policy.html":
        errors.append("content/compliance.yaml: cookies.policy_url should be cookie-policy.html")


def check_visit_credit_terms(errors: list[str]) -> None:
    has_visit_credit = False
    for page in page_sources():
        text = f"{page.body}\n{page.frontmatter}"
        if "$250" in text and "credit" in text.lower():
            has_visit_credit = True
            break

    if has_visit_credit and not (PAGES_DIR / "refund-cancellation.md").exists():
        errors.append("$250 visit-credit language exists but refund-cancellation.md is missing")


def main() -> int:
    errors: list[str] = []

    check_situation_depth(errors)
    check_required_page_ctas(errors)
    check_hero_image_uniqueness(errors)
    check_situation_cards(errors)
    check_contact_intake_contract(errors)
    check_page_size(errors)
    check_site_profile(errors)
    compliance = compliance_data(errors)
    check_compliance_pages(errors)
    check_footer_compliance_links(errors)
    check_cookie_consent_contract(errors, compliance)
    check_visit_credit_terms(errors)

    if errors:
        print("Site profile contract check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("OK site profile contracts passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
