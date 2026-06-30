# Assets And Images

## Source And Generated Assets

High-resolution originals live in:

```text
static/images/originals/
```

Optimized public assets live under:

```text
static/images/
```

Generated assets are copied to:

```text
docs/images/
```

Do not edit `docs/images/` directly. Update source assets and rebuild.

## Image Optimization

The optimizer reads originals and creates publishable derivatives such as `.webp`, `.jpg`, and responsive width variants.

Example source:

```text
static/images/originals/hero/free-guide-cost-worksheet.png
```

Example derivatives:

```text
static/images/hero/free-guide-cost-worksheet.webp
static/images/hero/free-guide-cost-worksheet.jpg
static/images/hero/free-guide-cost-worksheet_600w.webp
static/images/hero/free-guide-cost-worksheet_900w.webp
static/images/hero/free-guide-cost-worksheet_1200w.webp
```

Optimization runs during:

```powershell
.\.venv\Scripts\python.exe site.py check
.\.venv\Scripts\python.exe site.py validate
.\.venv\Scripts\python.exe site.py optimize-images
```

## Image Rules

- Prefer `.webp` for page images.
- Keep meaningful alt text in frontmatter or template data.
- Use a unique hero image for each important public page where practical.
- Keep images specific to the page topic.
- Avoid stock-like images that do not help the user understand the service.
- Keep original large files out of generated output.

## Logos And Social Assets

Logo, favicon, Open Graph, and Twitter card assets live under `static/images/`. Generated pages reference these assets through template metadata.

When updating brand assets, rebuild and run:

```powershell
.\.venv\Scripts\python.exe site.py check --lighthouse
```
