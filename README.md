# Legacy Defenders Website

Static website for Legacy Defenders, a care-led estate transition service for families, executors, and out-of-state decision makers handling inherited homes, belongings, local providers, costs, documentation, and urgent property work.

Live GitHub Pages site: [https://kaw393939.github.io/legacy/](https://kaw393939.github.io/legacy/)

Repository remote:

```bash
git@github.com:kaw393939/legacy.git
```

## What This Project Is

This is a content-driven static site. Source content lives in Markdown and YAML, templates are rendered with Jinja2, and the generated site is written to `docs/` for GitHub Pages.

The current public site is branded as Legacy Defenders. Some older helper files still use the original "Legs on the Ground" project name; treat that as legacy naming in tooling, not current site positioning.

## Tech Stack

- Python 3.12
- Jinja2 templates
- Markdown pages with YAML frontmatter
- YAML structured content
- Plain CSS split into ordered parts
- Plain JavaScript
- GitHub Actions
- GitHub Pages

## Project Structure

```text
.
|-- content/
|   |-- config.yaml              # Current site config: title, contact info, URLs, feature flags
|   |-- pages/                   # Markdown page content with frontmatter
|   `-- data/                    # Reusable YAML data used by templates
|-- templates/
|   |-- base.html                # Main HTML shell
|   |-- home.html                # Homepage layout
|   |-- page.html                # General content page layout
|   |-- services.html            # Services page layout
|   |-- situation.html           # Situation guide page layout
|   |-- components/              # Header, footer, top bar
|   |-- sections/                # Homepage and reusable page sections
|   `-- macros/                  # Reusable Jinja UI helpers
|-- static/
|   |-- css/
|   |   |-- parts/               # Ordered source CSS files
|   |   `-- styles.css           # Legacy/reference stylesheet; build uses parts when present
|   |-- js/main.js               # Source JavaScript
|   |-- images/                  # Source images copied to docs/images
|   |-- robots.txt
|   |-- sitemap.xml
|   `-- .nojekyll
|-- docs/                        # Generated site output for GitHub Pages
|-- build.py                     # Core static site generator
|-- validator.py                 # Output validation and quality checks
|-- site.py                      # Convenience CLI wrapper around build/serve/validate tasks
|-- requirements.txt             # Python dependencies
|-- .github/workflows/deploy.yml # GitHub Pages deployment workflow
`-- .github/workflows/preview.yml
```

## Live Pages

The build currently generates these public pages:

- `index.html`
- `services.html`
- `pricing.html`
- `free-guide.html`
- `diy-vs-us.html`
- `keith-story.html`
- `pa-probate.html`
- `single-decision-maker.html`
- `out-of-state-executor.html`
- `house-full-of-belongings.html`
- `urgent-bills-property-risk.html`
- `prearranged.html`
- `professional-referral-partners.html`
- `founder-plan.html`
- `thank-you.html`

## Local Setup

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If the virtual environment already exists, only install dependencies when `requirements.txt` changes.

## Common Commands

Build the site:

```powershell
.\.venv\Scripts\python.exe build.py
```

Build, minify bundled CSS, and validate output:

```powershell
.\.venv\Scripts\python.exe build.py --minify-css --validate
```

Serve the generated `docs/` site locally:

```powershell
.\.venv\Scripts\python.exe -m http.server 8000 --directory docs
```

Then open [http://localhost:8000/](http://localhost:8000/).

Run the JavaScript syntax check:

```powershell
node --check static\js\main.js
```

Run a Lighthouse check against the local site:

```powershell
npx --yes lighthouse@latest http://localhost:8000/index.html --quiet --chrome-flags="--headless=new --no-sandbox" --only-categories=performance,accessibility,best-practices,seo
```

Convenience commands also exist through `site.py` and `Makefile`, but `build.py --minify-css --validate` is the deployment source of truth.

## How The Build Works

`build.py` performs the static site build:

1. Loads `content/config.yaml`.
2. Loads all YAML files in `content/data/`.
3. Parses each Markdown page in `content/pages/`.
4. Converts Markdown body content to HTML.
5. Applies the page layout from frontmatter, such as `home`, `page`, `services`, or `situation`.
6. Renders Jinja templates with site config, page frontmatter, page HTML, current year, and all YAML data.
7. Writes generated pages to `docs/`.
8. Bundles CSS from `static/css/parts/*.css` into `docs/styles.css`.
9. Copies JavaScript, images, robots.txt, sitemap.xml, and `.nojekyll` into `docs/`.
10. Optionally validates the generated output when `--validate` is used.

The build cleans `docs/` by default before regenerating output. Do not edit generated files in `docs/` directly unless you are intentionally debugging output; source edits belong in `content/`, `templates/`, or `static/`.

## Content Editing Guide

Page content lives in `content/pages/*.md`.

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
---

Markdown body content goes here.
```

Use page frontmatter for:

- SEO title and meta description
- Layout selection
- Hero content
- CTA labels and destinations
- Situation-page fields such as first actions, mistakes, costs, and how-we-help lists

Structured content that appears across multiple pages lives in `content/data/*.yaml`.

Important data files:

- `navigation.yaml`: header/footer navigation
- `situations.yaml`: homepage and services-page situation cards
- `services.yaml`: services content
- `faq.yaml`: homepage FAQ content
- `prearranged-plan.yaml`: plan-ahead section content
- `proof-examples.yaml`: proof/result examples
- `technology-process.yaml`: process and inventory messaging
- `testimonials.yaml`, `value-props.yaml`, `why-choose.yaml`: supporting homepage sections

## Templates

Templates are in `templates/`.

Main layouts:

- `base.html`: shared document shell, metadata, header, footer, scripts
- `home.html`: homepage assembly
- `page.html`: standard content-page layout
- `services.html`: services overview layout
- `situation.html`: reusable guide layout for specific user situations

Reusable pieces:

- `templates/components/header.html`
- `templates/components/footer.html`
- `templates/sections/*.html`
- `templates/macros/*.html`

When adding a new page, prefer an existing layout before creating a new template.

## CSS

Source CSS is split into ordered files in `static/css/parts/`.

During build, files are sorted by filename and bundled into:

```text
docs/styles.css
```

The numeric prefixes control cascade order. Add new styles to the narrowest relevant part file instead of appending everything to the redesign file.

Current notable CSS areas:

- `00-1-css-variables.css`: tokens, colors, spacing, shadows
- `03-3-layout-system.css`: containers and layout primitives
- `05-5-header-navigation.css`: header and nav
- `06-6-buttons.css`: button system
- `11-11-forms.css`: forms
- `12-12-footer.css`: footer
- `15-15-media-queries-responsive-design.css`: responsive behavior
- `18-18-legacy-defenders-redesign.css`: broader redesign/page styles
- `19-19-situation-pages.css`: specific situation guide styles

For production builds, use `--minify-css` so the bundled output is smaller.

## JavaScript

Source JavaScript lives at:

```text
static/js/main.js
```

Build output copies it to:

```text
docs/main.js
```

The script handles:

- Mobile navigation
- Smooth anchor scrolling with fixed-header offset
- FAQ accordion behavior
- Contact intent handoff from CTA query parameters
- Form state helpers
- Back-to-top behavior
- WhatsApp floating-button visibility behavior
- Lightweight analytics/event hooks

Keep JavaScript dependency-free unless there is a strong reason to add a library.

## Images And Assets

Source images live in `static/images/` and are copied to `docs/images/`.

Use optimized web images where possible:

- Prefer `.webp` for page images.
- Keep meaningful `alt` text in templates/frontmatter.
- Avoid editing generated copies in `docs/images/`; update `static/images/` instead.

Social and logo assets are also under `static/images/`.

## Validation And QA

Primary validation command:

```powershell
.\.venv\Scripts\python.exe build.py --minify-css --validate
```

Additional useful checks:

```powershell
node --check static\js\main.js
git diff --check
```

Internal link and asset scan:

```powershell
@'
const fs = require('fs');
const path = require('path');
const root = path.resolve('docs');
const files = fs.readdirSync(root).filter(f => f.endsWith('.html'));
let failures = [];
for (const file of files) {
  const html = fs.readFileSync(path.join(root, file), 'utf8');
  const attrs = [...html.matchAll(/(?:href|src)=["']([^"']+)["']/gi)].map(m => m[1]);
  for (const raw of attrs) {
    if (!raw || raw.startsWith('#') || raw.startsWith('mailto:') || raw.startsWith('tel:') || raw.startsWith('http://') || raw.startsWith('https://') || raw.startsWith('data:') || raw.startsWith('javascript:')) continue;
    const target = raw.split('#')[0].split('?')[0];
    if (!target) continue;
    const resolved = path.resolve(root, target.startsWith('/') ? target.slice(1) : target);
    if (!resolved.startsWith(root) || !fs.existsSync(resolved)) failures.push(`${file}: missing ${raw}`);
  }
}
if (failures.length) {
  console.error(failures.join('\n'));
  process.exit(1);
}
console.log(`OK internal links/assets checked: ${files.length} pages`);
'@ | node -
```

Visual QA checklist:

- Desktop width around 1366px.
- Mobile width around 390px.
- Homepage hero, situation cards, contact form, FAQ, and footer.
- Each situation page hero, costs, common mistakes, related links, and final CTA.
- Pricing cards on mobile.
- Free guide worksheet section.
- Contact form prefill from links like `index.html?interest=Out-of-state%20executor%20help#contact`.
- No horizontal scrolling.
- No broken images.
- Anchor links land below the sticky header.

## GitHub Pages Deployment

The live site is deployed by `.github/workflows/deploy.yml`.

Deployment trigger:

- Push to `main`
- Manual `workflow_dispatch`

Deployment workflow:

1. Checkout repo.
2. Install Python 3.12.
3. Install `requirements.txt`.
4. Run `python build.py --validate --minify-css`.
5. Upload `docs/` as the Pages artifact.
6. Deploy with `actions/deploy-pages`.

Live URL:

[https://kaw393939.github.io/legacy/](https://kaw393939.github.io/legacy/)

Pull requests run `.github/workflows/preview.yml`, which builds, validates, uploads `validation-report.json`, and uploads the built `docs/` artifact for review.

## Typical Update Workflow

```powershell
git status --short --branch

# Edit source files in content/, templates/, or static/

.\.venv\Scripts\python.exe build.py --minify-css --validate
node --check static\js\main.js
git diff --check

git status --short
git add -A
git commit -m "Update site"
git push origin main
```

After pushing to `main`, GitHub Actions publishes the site.

## Environment Variables

The static build does not require secrets for normal operation.

Optional AI/image tooling may use:

```text
OPENAI_API_KEY
```

Use `.env.example` as a reference if working with optional tooling. Do not commit real secrets.

## Important Operational Notes

- `content/config.yaml` is the current site config used by `build.py`.
- `site.config.yaml` is used by the convenience `site.py` CLI and still includes older project labels.
- `docs/` is generated output. Commit it when you want the repository to include the current built site, but edit source files first.
- GitHub Actions rebuilds `docs/` before deploying, so source files must stay valid even if committed output appears correct.
- The founder plan is intentionally linked from the footer, not the main user path.
- `thank-you.html` should remain a utility page, not a primary landing page.

## Troubleshooting

Build fails with YAML errors:

```powershell
.\.venv\Scripts\python.exe -c "import yaml, pathlib; [yaml.safe_load(p.read_text(encoding='utf-8')) for p in pathlib.Path('content').rglob('*.yaml')]"
```

Generated page looks wrong:

- Check the page frontmatter in `content/pages/`.
- Confirm the expected layout exists in `templates/`.
- Check whether the page relies on a YAML data file in `content/data/`.
- Rebuild with `--validate`.

CSS change not showing:

- Edit `static/css/parts/*.css`, not `docs/styles.css`.
- Rebuild the site.
- Hard refresh the browser if cache-busted URLs did not change.

JavaScript behavior breaks:

- Run `node --check static\js\main.js`.
- Test locally at `http://localhost:8000/`.
- Check whether the generated copy in `docs/main.js` was rebuilt.

GitHub Pages does not update:

- Check the Actions tab for the latest `Deploy GitHub Pages` run.
- Confirm the push went to `main`.
- Confirm the workflow completed and deployed the `docs` artifact.

## License

Proprietary. All site content, branding, and assets are owned by the project owner unless otherwise noted.
