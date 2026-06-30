#!/usr/bin/env python3
"""Create a consistent Markdown scaffold for a new site page."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from urllib.parse import quote

from tools.site_framework import CONTENT_DIR, PAGES_DIR, ROOT, TEXT_ENCODING, load_yaml, slugify


@dataclass(frozen=True)
class SiteProfile:
    name: str
    default_hero_image: str
    page_eyebrow: str
    situation_eyebrow: str
    primary_cta_text: str
    primary_cta_icon: str
    situation_boundary: str
    probate_reference_title: str
    probate_reference_url: str


DEFAULT_PROFILE = "legacy_defenders"


def profile_from_data(data: dict) -> SiteProfile:
    profile = data.get("profile") if isinstance(data.get("profile"), dict) else {}
    primary_cta = profile.get("primary_cta") if isinstance(profile.get("primary_cta"), dict) else {}
    references = profile.get("references") if isinstance(profile.get("references"), dict) else {}
    probate = references.get("probate") if isinstance(references.get("probate"), dict) else {}

    return SiteProfile(
        name=str(profile.get("id") or DEFAULT_PROFILE),
        default_hero_image=str(profile.get("default_hero_image") or ""),
        page_eyebrow=str(profile.get("page_eyebrow") or "Guide"),
        situation_eyebrow=str(profile.get("situation_eyebrow") or "Situation guide"),
        primary_cta_text=str(primary_cta.get("text") or "Start With A Free Call"),
        primary_cta_icon=str(primary_cta.get("icon") or "fa-phone"),
        situation_boundary=str(profile.get("situation_boundary") or ""),
        probate_reference_title=str(probate.get("title") or "Official probate reference"),
        probate_reference_url=str(probate.get("url") or ""),
    )


def load_profiles() -> dict[str, SiteProfile]:
    profile = profile_from_data(load_yaml(CONTENT_DIR / "site-profile.yaml"))
    return {profile.name: profile}


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def contact_interest(slug: str) -> str:
    return quote(slug.replace("-", " ").title())


def page_template(profile: SiteProfile, slug: str, title: str, description: str) -> str:
    page_id = slug.replace("-", "_")
    return f"""---
layout: page
title: {yaml_quote(title)}
description: {yaml_quote(description)}
page_id: {yaml_quote(page_id)}
eyebrow: {yaml_quote(profile.page_eyebrow)}
hero:
  image: {yaml_quote(profile.default_hero_image)}
  alt: ""
  caption: ""
hero_actions:
  - text: {yaml_quote(profile.primary_cta_text)}
    url: "index.html?interest={contact_interest(slug)}#contact"
    icon: {yaml_quote(profile.primary_cta_icon)}
    style: "btn-primary"
seo:
  canonical: "/{slug}.html"
  og_type: "website"
---

## Start Here

Write the page around one clear reader problem, the first useful step, and the next decision they need to make.
"""


def situation_template(profile: SiteProfile, slug: str, title: str, description: str) -> str:
    page_id = slug.replace("-", "_")
    return f"""---
layout: situation
title: {yaml_quote(title)}
description: {yaml_quote(description)}
page_id: {yaml_quote(page_id)}
eyebrow: {yaml_quote(profile.situation_eyebrow)}
contact_interest: {yaml_quote(title)}
hero:
  image: {yaml_quote(profile.default_hero_image)}
  alt: ""
  caption: ""
stats:
  - number: "Free"
    label: "1-hour estate call"
  - number: "$250"
    label: "Credited home visit"
  - number: "Clear"
    label: "First plan"
first_actions:
  - title: "Confirm authority"
    text: "Clarify who can approve access, spending, provider work, and next decisions."
  - title: "Map the situation"
    text: "Document urgent risks, important assets, access issues, and likely provider needs."
  - title: "Choose the first bottleneck"
    text: "Decide what must happen first so the project can move without confusion or waste."
common_mistakes:
  - "Starting work before authority, access, and records are clear."
  - "Discarding important items before papers, photos, valuables, and memory items are protected."
  - "Hiring providers without a written scope, budget, photo record, and decision log."
how_we_help:
  - "Turn the situation, risks, provider needs, and next options into a practical plan."
  - "Coordinate local work so the family has fewer separate calls, quotes, and follow-ups."
  - "Create photos, notes, receipts, scopes, and item records the decision maker can keep."
cost_intro: "These are planning ranges, not quotes. Exact pricing depends on condition, access, volume, urgency, provider availability, authority, and approved scope."
costs:
  - category: "Free first call"
    range: "$0"
    notes: "A calm first conversation about the situation, authority, deadlines, and pressure points."
  - category: "Planning visit"
    range: "$250 credit"
    notes: "Walkthrough of the property, belongings, obvious risks, provider needs, and first budget categories."
  - category: "First coordination sprint"
    range: "$8,500-$12,000 typical"
    notes: "A scoped first project to clear the first bottleneck and provide documented next steps."
timeline:
  - period: "First 48 hours"
    text: "Protect access, records, utilities, obvious risks, and high-value or sentimental items."
  - period: "First week"
    text: "Complete the visit, document the situation, and choose the first approved scope."
  - period: "First 30 days"
    text: "Move approved work forward with photos, receipts, provider scopes, and family-ready updates."
records:
  - title: "Planning snapshot"
    text: "A practical view of risks, costs, provider needs, timing, and next decisions."
  - title: "Decision-ready packet"
    text: "Scopes, receipts, invoices, photos, provider notes, budget categories, and open questions."
boundary: {yaml_quote(profile.situation_boundary)}
official_references:
  - title: {yaml_quote(profile.probate_reference_title)}
    url: {yaml_quote(profile.probate_reference_url)}
    note: "Check current filing and administration fee schedules."
related_links:
  - label: "Costs"
    title: "Pricing Examples"
    url: "pricing.html"
  - label: "Worksheet"
    title: "Free Inherited Home Guide"
    url: "free-guide.html"
seo:
  canonical: "/{slug}.html"
  og_type: "website"
---

## Write the human situation first

Describe what the reader is facing in plain language before listing services. Keep it specific, practical, and calming.
"""


def render_template(profile: SiteProfile, kind: str, slug: str, title: str, description: str) -> str:
    if kind == "situation":
        return situation_template(profile, slug, title, description)
    return page_template(profile, slug, title, description)


def parse_args() -> argparse.Namespace:
    profiles = load_profiles()
    parser = argparse.ArgumentParser(
        prog="python -m tools.new_page",
        description="Create a static-site page scaffold",
    )
    parser.add_argument("--kind", choices=["page", "situation"], default="page")
    parser.add_argument("--profile", choices=sorted(profiles), default=DEFAULT_PROFILE)
    parser.add_argument("--slug", help="URL slug, for example out-of-state-executor")
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--force", action="store_true", help="Overwrite an existing page")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    profile = load_profiles()[args.profile]
    slug = slugify(args.slug or args.title)

    if not slug:
        raise SystemExit("Could not create a slug from the provided input")

    target = PAGES_DIR / f"{slug}.md"
    if target.exists() and not args.force:
        print(f"Refusing to overwrite existing page: {target}")
        return 1

    target.write_text(render_template(profile, args.kind, slug, args.title, args.description), encoding=TEXT_ENCODING)
    print(f"Created {target.relative_to(ROOT)}")
    print("Next steps:")
    print("- Replace empty hero alt/caption values with specific copy.")
    print("- Add the page to navigation or situations.yaml if it should be discoverable.")
    print("- Run python site.py validate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
