# Architecture

## Directory Map

```text
.
|-- content/
|   |-- config.yaml        # Public site configuration
|   |-- compliance.yaml    # Compliance/cookie source of truth
|   |-- site-profile.yaml  # Active profile selector
|   |-- profiles/          # Site profile registry
|   |-- pages/             # Markdown pages with YAML frontmatter
|   `-- data/              # Structured reusable content
|-- templates/
|   |-- base.html          # Shared HTML shell
|   |-- home.html          # Homepage layout
|   |-- page.html          # General content-page layout
|   |-- services.html      # Services overview layout
|   |-- situation.html     # Situation guide layout
|   |-- components/        # Header, footer, cookie consent, reusable components
|   |-- sections/          # Homepage and page sections
|   `-- macros/            # Jinja UI helpers
|-- static/
|   |-- css/parts/         # Ordered source CSS parts
|   |-- js/                # Source JavaScript modules
|   |-- images/            # Optimized source assets
|   `-- images/originals/  # High-resolution originals, not published
|-- docs/                  # Generated GitHub Pages output
|-- tools/                 # Framework helpers, validators, QA tools
|-- project-docs/          # Current docs and archived notes
|-- build.py               # Static site generator
|-- site.py                # Developer CLI
|-- validator.py           # Generated-site validation
`-- site.config.yaml       # Local CLI config
```

## Build Pipeline

`build.py` performs the static site build:

1. Loads `content/config.yaml`.
2. Optimizes image originals from `static/images/originals/`.
3. Loads structured YAML data from `content/data/`.
4. Loads compliance data from `content/compliance.yaml`.
5. Loads the active site profile from `content/site-profile.yaml` and `content/profiles/`.
6. Parses Markdown pages from `content/pages/`.
7. Converts Markdown body content to HTML.
8. Selects the Jinja layout named in page frontmatter.
9. Renders pages with site config, active site profile, page data, Markdown HTML, current year, YAML data, compliance data, and generated runtime values.
10. Writes generated pages to `docs/`.
11. Bundles `static/css/parts/*.css` into `docs/styles.css`.
12. Copies JavaScript, images, robots.txt, sitemap.xml, and `.nojekyll`.
13. Runs validation when requested.

The build cleans `docs/` before regenerating output.

## Templates

Use an existing layout before creating a new one.

- `base.html`: metadata, header, footer, cookie consent, scripts, shared shell.
- `home.html`: homepage assembly from section templates.
- `page.html`: general public content pages.
- `services.html`: services overview.
- `situation.html`: reusable guide layout for specific user situations.
- `internal.html`: internal or special-purpose pages.

Reusable UI should live in `templates/components/`, `templates/sections/`, or `templates/macros/`.

## CSS

Source CSS lives in `static/css/parts/` and is bundled in filename order. Numeric prefixes control cascade order. Generated output is `docs/styles.css`.

Important CSS areas:

- `00-*`: variables and base tokens.
- `03-*`: layout primitives.
- `05-*`: header and navigation.
- `06-*`: buttons.
- `11-*`: forms.
- `12-*`: footer.
- `18-*`: content page and redesign layers.
- `19-*`: situation pages.
- `20-*`: cookie consent.
- `21-*`: restraint/typography consolidation layer.

Do not edit `docs/styles.css` directly.

## JavaScript

Source JavaScript lives in `static/js/` and is copied to `docs/`. The site uses plain browser JavaScript modules for navigation, contact intent handling, FAQ behavior, cookie consent, analytics hooks, print helpers, asset loading, and runtime config.

Keep JavaScript dependency-free unless there is a strong reason to add a library.

## Validation Layers

- `tools/check_content_contracts.py`: generic source content rules.
- `tools/check_site_contracts.py`: active site-profile rules.
- `tools/check_frontend_architecture.py`: CSS, template, and JavaScript architecture guardrails.
- `tools/check_framework_boundaries.py`: reusable framework versus site-profile boundary checks.
- `tools/check_site_integrity.py`: generated HTML, links, assets, metadata, and placeholder validation.
- `validator.py`: generated-site validation primitives.
