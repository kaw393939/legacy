# Site Profiles

Site profiles are the bridge between the reusable static-site framework and the specific business or brand using it.

## Files

The active profile is selected here:

```yaml
active_profile: "legacy_defenders"
profiles_dir: "profiles"
```

File:

```text
content/site-profile.yaml
```

Profile files live here:

```text
content/profiles/
```

Current first-site profile:

```text
content/profiles/legacy-defenders.yaml
```

## What A Profile Controls

A profile stores defaults and site-specific assumptions used by scaffolding, validation, and templates:

- profile id and label
- brand archetype
- default page eyebrow
- default situation eyebrow
- default hero image
- primary CTA text and icon
- standard service-boundary language
- official reference links used by situation scaffolds

Example:

```yaml
profile:
  id: "legacy_defenders"
  label: "Legacy Defenders"
  archetype: "bereavement caregiver"
  page_eyebrow: "Guide"
  situation_eyebrow: "Situation guide"
  default_hero_image: "images/hero/legacy-defenders-care-hero.webp"
  primary_cta:
    text: "Start With A Free Call"
    icon: "fa-phone"
```

## How The Framework Uses Profiles

- `tools/site_framework.py` loads all profiles and exposes the active profile.
- `build.py` makes the active profile available to templates as `site_profile`.
- `tools/new_page.py` uses the active profile for new page and situation scaffolds.
- `tools/check_site_contracts.py` validates that the selected active profile exists and contains required fields.

## Creating Another Site Profile

1. Add a profile file under `content/profiles/`, such as `content/profiles/example-service.yaml`.
2. Give it a unique `profile.id`.
3. Update `content/site-profile.yaml`:

```yaml
active_profile: "example_service"
profiles_dir: "profiles"
```

4. Update `content/config.yaml`, `content/compliance.yaml`, `content/data/`, page content, images, and navigation for the new business.
5. Run:

```powershell
.\.venv\Scripts\python.exe site.py check
```

6. Scaffold new pages from the active profile:

```powershell
.\.venv\Scripts\python.exe site.py new-page --kind page --title "Example Guide" --description "Short description."
```

## Boundary Rule

Reusable framework files should not know about Legacy Defenders. First-site assumptions belong in:

- `content/`
- `content/profiles/`
- `templates/` when rendering public site copy
- `static/` when styling the active site profile
- `tools/check_site_contracts.py` when enforcing active site-profile contracts

Generic framework rules belong in:

- `tools/site_framework.py`
- `tools/check_content_contracts.py`
- `tools/check_frontend_architecture.py`
- `tools/check_framework_boundaries.py`
- `tools/new_page.py`
