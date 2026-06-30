# Troubleshooting

## Build Fails With YAML Errors

Validate YAML files:

```powershell
.\.venv\Scripts\python.exe -c "import yaml, pathlib; [yaml.safe_load(p.read_text(encoding='utf-8')) for p in pathlib.Path('content').rglob('*.yaml')]"
```

Check recent edits in `content/config.yaml`, `content/compliance.yaml`, and `content/data/*.yaml`.

## Generated Page Looks Wrong

- Check the page frontmatter in `content/pages/`.
- Confirm the `layout` exists in `templates/`.
- Check whether the page relies on a YAML data file in `content/data/`.
- Rebuild with:

```powershell
.\.venv\Scripts\python.exe site.py build
```

## CSS Change Not Showing

- Edit `static/css/parts/*.css`, not `docs/styles.css`.
- Confirm the CSS part filename sorts after the rules it needs to override.
- Rebuild the site.
- Hard refresh the browser.

## JavaScript Behavior Breaks

Run syntax checks:

```powershell
.\.venv\Scripts\python.exe site.py validate
```

Or check one file directly:

```powershell
node --check static\js\main.js
```

Then test locally:

```powershell
.\.venv\Scripts\python.exe site.py serve
```

## Lighthouse Drops Below 90

- Check image size and format.
- Confirm CSS and JS are still bundled/minified as expected.
- Avoid adding render-blocking third-party scripts.
- Keep analytics consent-gated.
- Run Lighthouse against the local homepage:

```powershell
.\.venv\Scripts\python.exe site.py check --lighthouse
```

## Visual QA Screenshots Look Polluted

`site.py visual-qa` suppresses the cookie banner by setting a local consent value before screenshots. If screenshots still show the banner, inspect `tools/run_visual_qa.mjs` and rerun:

```powershell
.\.venv\Scripts\python.exe site.py visual-qa
```

## GitHub Pages Does Not Update

- Confirm the push went to `main`.
- Check the Actions tab for the latest deployment.
- Confirm `Deploy GitHub Pages` completed.
- Confirm the workflow deployed the `docs/` artifact.
- Wait a few minutes and hard refresh the live URL.

## Validation Report

`site.py check` writes:

```text
validation-report.json
```

Use it to inspect generated-site issues when a check fails.
