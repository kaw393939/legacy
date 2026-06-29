#!/usr/bin/env python3
"""Create a consistent Markdown scaffold for a new site page."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES_DIR = ROOT / "content" / "pages"


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def page_template(slug: str, title: str, description: str) -> str:
    page_id = slug.replace("-", "_")
    return f"""---
layout: page
title: "{title}"
description: "{description}"
page_id: "{page_id}"
eyebrow: "Guide"
hero:
  image: "images/hero/legacy-defenders-care-hero.webp"
  alt: ""
  caption: ""
hero_actions:
  - text: "Start With A Free Call"
    url: "index.html?interest={slug.replace('-', '%20').title()}#contact"
    icon: "fa-phone"
    style: "btn-primary"
seo:
  canonical: "/{slug}.html"
  og_type: "website"
---

## Start Here

Write the page around one clear reader problem, the first useful step, and the next decision they need to make.
"""


def situation_template(slug: str, title: str, description: str) -> str:
    page_id = slug.replace("-", "_")
    contact_interest = title
    return f"""---
layout: situation
title: "{title}"
description: "{description}"
page_id: "{page_id}"
eyebrow: "Situation guide"
contact_interest: "{contact_interest}"
hero:
  image: "images/hero/legacy-defenders-care-hero.webp"
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
    text: "Clarify who can approve access, spending, belongings movement, provider work, and next decisions."
  - title: "Map the house"
    text: "Document rooms, belongings, urgent risks, bills, access issues, and likely provider needs."
  - title: "Choose the first bottleneck"
    text: "Decide what must happen first so the estate can move without confusion or waste."
common_mistakes:
  - "Starting work before authority, access, and records are clear."
  - "Throwing away belongings before papers, photos, titles, valuables, and memory items are protected."
  - "Hiring providers without a written scope, budget, photo record, and decision log."
how_we_help:
  - "Turn the house, belongings, risks, provider needs, and next options into a practical plan."
  - "Coordinate the local work so the family has fewer separate calls, quotes, and follow-ups."
  - "Create photos, notes, receipts, scopes, and item records the executor can keep."
cost_intro: "These are planning ranges, not quotes. Exact pricing depends on condition, access, volume, urgency, provider availability, authority, and approved scope."
costs:
  - category: "Free estate call"
    range: "$0"
    notes: "A calm first conversation about the home, authority, belongings, deadlines, and pressure points."
  - category: "Estate Math Home Visit"
    range: "$250 credit"
    notes: "Walkthrough of the property, belongings, obvious risks, provider needs, and first budget categories."
  - category: "First coordination sprint"
    range: "$8,500-$12,000 typical"
    notes: "A scoped first project to clear the first bottleneck and give the executor documented next steps."
timeline:
  - period: "First 48 hours"
    text: "Protect access, records, utilities, mail, obvious risks, and high-value or sentimental items."
  - period: "First week"
    text: "Complete the home visit, document the situation, and choose the first approved scope."
  - period: "First 30 days"
    text: "Move approved work forward with photos, receipts, provider scopes, and family-ready updates."
records:
  - title: "Estate Math Snapshot"
    text: "A practical view of risks, costs, belongings, provider needs, timing, and next decisions."
  - title: "Executor-ready packet"
    text: "Scopes, receipts, invoices, photos, provider notes, budget categories, and open questions."
boundary: "Legacy Defenders does not provide legal, tax, appraisal, lending, insurance, real estate brokerage, or licensed trade advice."
official_references:
  - title: "Allegheny County Probate Fees"
    url: "https://www.alleghenycounty.us/Government/Court-Related/Wills-and-Orphans/Probating-Wills/Probate-Fees"
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Legacy Defenders page scaffold")
    parser.add_argument("--kind", choices=["page", "situation"], default="page")
    parser.add_argument("--slug", help="URL slug, for example out-of-state-executor")
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--force", action="store_true", help="Overwrite an existing page")
    args = parser.parse_args()

    slug = slugify(args.slug or args.title)
    if not slug:
        parser.error("Could not create a slug from the provided input")

    target = PAGES_DIR / f"{slug}.md"
    if target.exists() and not args.force:
        print(f"Refusing to overwrite existing page: {target}")
        return 1

    content = (
        situation_template(slug, args.title, args.description)
        if args.kind == "situation"
        else page_template(slug, args.title, args.description)
    )

    target.write_text(content, encoding="utf-8")
    print(f"Created {target.relative_to(ROOT)}")
    print("Next steps:")
    print("- Replace empty hero alt/caption values with specific copy.")
    print("- Add the page to navigation or situations.yaml if it should be discoverable.")
    print("- Run python site.py validate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
