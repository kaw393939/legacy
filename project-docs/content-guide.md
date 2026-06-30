# Content Guide

## Where Content Lives

- Page content: `content/pages/*.md`
- Public site configuration: `content/config.yaml`
- Active profile selector: `content/site-profile.yaml`
- Site profile files: `content/profiles/*.yaml`
- Compliance and cookie settings: `content/compliance.yaml`
- Reusable structured content: `content/data/*.yaml`

Generated HTML lives in `docs/`, but source edits should happen in `content/`, `templates/`, or `static/`.

## Page Frontmatter

Each page starts with YAML frontmatter:

```markdown
---
layout: page
title: "Pricing Examples"
description: "Plain-language estate support pricing examples."
page_id: "pricing"
hero:
  eyebrow: "Pricing"
  title: "Know what the estate work may cost before it gets away from you."
  cta:
    label: "Start With A Free Call"
    href: "index.html#contact"
---

Markdown body content goes here.
```

Use frontmatter for:

- Layout selection.
- SEO title and meta description.
- Canonical path and robots rules.
- Hero eyebrow, title, description, image, image alt text, caption, and CTA.
- Page-specific CTA labels and destinations.
- Situation-page fields such as first actions, mistakes, costs, records, timeline, references, and related links.

## Layouts

- `home`: homepage.
- `page`: general content, compliance, guide, pricing, and story pages.
- `services`: services overview.
- `situation`: problem-specific situation guide.
- `internal`: internal or special-purpose pages.

## Structured Data

Important YAML data files:

- `navigation.yaml`: header/footer navigation.
- `situations.yaml`: situation cards and routing.
- `services.yaml`: service categories and service details.
- `contact_intake.yaml`: visible contact form options and intent mapping.
- `faq.yaml`: FAQ content.
- `prearranged_plan.yaml`: plan-ahead section content.
- `proof_examples.yaml`: proof/result examples.
- `technology_process.yaml`: process and inventory messaging.
- `testimonials.yaml`, `value_props.yaml`, `why_choose.yaml`: homepage support sections.

Keep repeated content in YAML data when it appears across multiple pages.

## Compliance Content

`content/compliance.yaml` is the source of truth for:

- Business name and public contact details.
- Service area.
- Effective date.
- Form/data collection categories.
- Cookie and analytics settings.
- Refund and cancellation language.
- Professional service boundary language.
- Contractor/provider notice language.
- Accessibility contact language.
- Children under 13 note.

Compliance pages live in `content/pages/` and should remain plain-language. They are practical templates, not legal advice.

## Content Style

Legacy Defenders content should sound calm, useful, and protective. Prefer:

- Shorter sections.
- Clear headings.
- Specific first steps.
- Realistic cost ranges.
- Concrete examples.
- Gentle language for bereavement and executor stress.
- Direct calls to action that reduce uncertainty.

Avoid overwhelming users with too many equal-weight options. Use the page narrative to answer: what is happening, what matters first, what it may cost, what the user can do alone, and when Legacy Defenders can help.

## SEO And Metadata

- Keep meta descriptions under about 160 characters.
- Use one clear page purpose per page.
- Keep `thank-you.html` and `founder-plan.html` as `noindex, follow` unless strategy changes.
- Use unique hero images for public pages where practical.
- Keep internal founder/business-planning content out of primary user navigation.
