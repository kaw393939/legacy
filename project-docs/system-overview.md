# System Overview

This repository contains a small reusable static-site framework. Legacy Defenders is the first active site profile implemented with the framework. The reusable engine, active site profile, content model, design system, and QA gates live together in one repo so the first site remains simple to deploy through GitHub Pages while the framework stays reusable for future sites.

## What The System Does

- Builds static HTML pages from Markdown, YAML, and Jinja templates.
- Publishes generated output to `docs/` for GitHub Pages.
- Keeps business content in `content/`.
- Selects an active site profile from `content/site-profile.yaml`.
- Keeps reusable rendering, validation, and QA logic in `build.py`, `site.py`, `validator.py`, and `tools/`.
- Bundles ordered CSS parts into one public stylesheet.
- Copies JavaScript modules and generated runtime config into `docs/modules/`.
- Optimizes original image assets into publishable derivatives.
- Validates source content, site-profile rules, generated HTML, links, assets, frontend architecture, and framework boundaries.
- Captures desktop and mobile QA screenshots for representative pages.
- Enforces Lighthouse scores of 90+.

## Framework Boundary

The project has two layers:

- Framework layer: generic build, scaffold, validation, CSS bundling, image optimization, Lighthouse, and visual QA tools.
- Site profile layer: active profile defaults, first-site content, service area, situation page expectations, compliance language, contact intake options, imagery, and public brand rules.

Keep reusable code free of Legacy Defenders assumptions unless it is in an allowed site-profile/template location. Site-specific checks belong in `tools/check_site_contracts.py`; generic checks belong in `tools/check_content_contracts.py`, `tools/check_frontend_architecture.py`, and `tools/check_framework_boundaries.py`.

## Configuration Boundary

- `content/config.yaml` is the public business/site configuration. It owns site title, URL, contact details, navigation-facing values, build paths, and public metadata.
- `content/compliance.yaml` owns compliance and cookie settings used by policy pages and runtime config.
- `content/site-profile.yaml` selects the active profile and profile directory.
- `content/profiles/*.yaml` stores site profiles. The current first-site profile is Legacy Defenders.
- `site.config.yaml` is local tooling configuration for `site.py`, including server port, logging, and Lighthouse budget.

Generated browser runtime config should include only values needed in the browser.

## Publishing Model

GitHub Pages serves the generated `docs/` directory. GitHub Actions rebuilds and validates the site before deploying.

First site profile live URL: [https://kaw393939.github.io/legacy/](https://kaw393939.github.io/legacy/)
