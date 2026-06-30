# Static Site Design System

This project uses a small, source-controlled design system instead of a CSS framework. The goal is to keep pages calm, fast, readable, and easy to extend without creating single-use styles for every page.

## CSS Organization

- Source CSS lives in `static/css/parts/` and is bundled into `docs/styles.css`.
- File names use numeric ordering because cascade order matters.
- Add a new CSS part when a feature has a clear ownership boundary, such as hero variants, FAQ, pricing, contact, or situation pages.
- Avoid large catch-all files. A CSS part should generally stay under 700 lines, and smaller focused files are preferred.
- Do not edit `docs/styles.css` directly; it is generated.

## Tokens And Components

- Global variables live in the earliest CSS parts and should be reused for color, spacing, shadows, type, and layout rhythm.
- Prefer existing component classes before adding new ones: `btn`, `card`, `section-*`, `content-*`, `guide-*`, `situation-*`, `pricing-*`, `faq-*`, and `contact-*`.
- Use Jinja macros for repeated HTML patterns such as buttons, icons, media, contact forms, cards, and situation sections.
- Avoid inline styles, inline event handlers, and raw icon markup outside the icon macro.

## Page Patterns

- `page` layout is for content-heavy guide pages with a hero, above-the-fold CTA, and readable Markdown body.
- `situation` layout is for problem-specific entry pages with first actions, how-we-help content, risks, costs, timeline, records, references, and a final CTA.
- Homepage sections should stay modular under `templates/sections/`.
- Site-specific content expectations belong in `tools/check_site_contracts.py`; generic framework expectations belong in `tools/check_content_contracts.py` and `tools/check_frontend_architecture.py`.

## Images

- Original images belong in `static/images/originals/`.
- Optimized public images are generated into `static/images/` and copied to `docs/images/`.
- Hero images should be unique across important pages unless there is a deliberate reason to repeat one.
- Every non-decorative image needs specific alt text in page frontmatter or template data.

## QA Rules

- Run `python site.py check` before committing.
- Run `python site.py check --lighthouse` before publishing meaningful visual, CSS, JS, or template changes.
- Keep Lighthouse scores at or above 90.
- Generated output belongs in `docs/`, but source changes should happen in `content/`, `templates/`, `static/`, or `tools/`.
