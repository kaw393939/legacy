# Validation And QA

## Primary Gates

Run before committing meaningful changes:

```powershell
.\.venv\Scripts\python.exe site.py check
```

Run before publishing frontend, visual, template, image, JS, or performance-sensitive changes:

```powershell
.\.venv\Scripts\python.exe site.py check --lighthouse
```

Capture desktop and mobile screenshots:

```powershell
.\.venv\Scripts\python.exe site.py visual-qa
```

## What `site.py check` Does

- Compiles Python source.
- Optimizes source images.
- Runs source content contract checks.
- Runs site-profile contract checks.
- Runs frontend architecture checks.
- Runs framework boundary checks.
- Builds generated output.
- Validates generated HTML, links, assets, titles, metadata, and placeholder links.
- Checks JavaScript syntax.
- Writes `validation-report.json`.
- Runs `git diff --check`.

`site.py check --lighthouse` also starts a temporary local server and enforces Lighthouse scores of 90+.

## Visual QA Checklist

Inspect both desktop and mobile screenshots for:

- No horizontal scrolling.
- No clipped text.
- No overlapping floating elements.
- Header and mobile menu behave correctly.
- Cookie consent is readable and does not obscure core actions.
- Footer is balanced and useful.
- Hero sections have clear hierarchy and readable images.
- Situation cards link to sensible pages.
- Pricing examples fit on mobile.
- FAQ expanded answers have good spacing.
- Contact form options match CTA intent handoff.
- WhatsApp bubble does not cover important content.

## Cognitive Load QA

For each page, ask:

- Does the page immediately say who it is for?
- Does it tell the user what matters first?
- Are there too many equally loud cards or buttons?
- Is the CTA obvious but not aggressive?
- Can a grieving or overwhelmed user scan the page?
- Are costs, limits, and next steps concrete?
- Does the page avoid repeating what another page already explains better?

## Release Checklist

Before pushing to `main`:

```powershell
.\.venv\Scripts\python.exe site.py check
.\.venv\Scripts\python.exe site.py check --lighthouse
.\.venv\Scripts\python.exe site.py visual-qa
git status --short
```

Review `qa-screenshots/` for the affected pages.
