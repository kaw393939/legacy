# Static Site Framework

Reusable static-site framework with Legacy Defenders as the first active site profile. Legacy Defenders is a care-led estate transition service for families, executors, and out-of-state decision makers handling inherited homes, belongings, local providers, costs, documentation, and urgent property work.

Live site: [https://kaw393939.github.io/legacy/](https://kaw393939.github.io/legacy/)

Repository remote:

```bash
git@github.com:kaw393939/legacy.git
```

## Start Here

This repo is a greenfield framework for building content-driven service sites. Legacy Defenders is the first site implemented on top of the framework, not a single-purpose codebase.

- Source content lives in `content/`.
- Jinja templates live in `templates/`.
- CSS, JavaScript, and images live in `static/`.
- Generated GitHub Pages output lives in `docs/`.
- Local framework and QA tools live in `tools/`.

Do not edit generated files in `docs/` as the source of truth. Edit `content/`, `templates/`, `static/`, or `tools/`, then rebuild.

## Quick Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Build the generated site:

```powershell
.\.venv\Scripts\python.exe site.py build
```

Run the full local quality gate:

```powershell
.\.venv\Scripts\python.exe site.py check
```

Run the full gate with Lighthouse:

```powershell
.\.venv\Scripts\python.exe site.py check --lighthouse
```

Serve locally:

```powershell
.\.venv\Scripts\python.exe site.py serve
```

Then open [http://localhost:8000/](http://localhost:8000/).

## Documentation Index

- [Project Docs Index](project-docs/README.md): full documentation map.
- [System Overview](project-docs/system-overview.md): what the project is, how the framework is separated from the site, and what it can do.
- [Architecture](project-docs/architecture.md): source directories, build pipeline, templates, CSS, JS, and validation layers.
- [Commands](project-docs/commands.md): all `site.py`, image, Lighthouse, visual QA, and scaffold commands.
- [Site Profiles](project-docs/site-profiles.md): active profile selection, profile files, and how to prepare the system for another site.
- [Content Guide](project-docs/content-guide.md): editing Markdown pages, YAML data, compliance copy, and page frontmatter.
- [Page Inventory](project-docs/page-inventory.md): generated public pages and their role in the site narrative.
- [Design System](project-docs/design-system.md): tokens, CSS ordering, component rules, image rules, and visual QA standards.
- [Assets And Images](project-docs/assets-and-images.md): original images, optimized derivatives, hero image rules, and asset workflow.
- [Validation And QA](project-docs/validation-and-qa.md): source checks, generated-site integrity, Lighthouse, visual QA, and release checklist.
- [Deployment](project-docs/deployment.md): GitHub Pages deployment, Actions workflows, and publishing flow.
- [Troubleshooting](project-docs/troubleshooting.md): common build, CSS, JS, YAML, and GitHub Pages issues.

Historical notes and superseded implementation artifacts are preserved under [project-docs/archive/](project-docs/archive/). Treat the files linked above as the current source of truth.

## Capabilities

The system currently supports:

- Markdown pages with YAML frontmatter.
- Structured YAML data for reusable content.
- Jinja layouts, sections, components, and macros.
- Situation-guide page scaffolding.
- Public compliance pages and cookie consent controls.
- Consent-gated analytics runtime configuration.
- Ordered CSS parts bundled into `docs/styles.css`.
- Plain JavaScript modules copied to generated output.
- Automatic image optimization from source originals.
- Generated-site link, asset, meta, and integrity validation.
- Content and site-profile contract checks.
- Active site profile registry for page scaffolding and site-specific defaults.
- Frontend architecture and framework-boundary checks.
- Lighthouse budgets of 90+.
- Desktop and mobile visual QA screenshots.
- GitHub Pages deployment from `docs/`.

## Common Workflow

```powershell
git status --short --branch

# Edit source files in content/, templates/, static/, or tools/

.\.venv\Scripts\python.exe site.py check
.\.venv\Scripts\python.exe site.py check --lighthouse
.\.venv\Scripts\python.exe site.py visual-qa

git status --short
git add -A
git commit -m "Update site"
git push origin main
```

## License

Proprietary. All site content, branding, and assets are owned by the project owner unless otherwise noted.
