#!/usr/bin/env python3
"""Guard against brand-specific assumptions in reusable framework files."""

from __future__ import annotations

from pathlib import Path

from tools.site_framework import ROOT, TEXT_ENCODING


BRAND_TERMS = (
    "Legacy Defenders",
    "Estate Math",
    "Allegheny County",
    "inherited-home estate",
    "legacy-site",
)
REUSABLE_PATHS = (
    "build.py",
    "site.py",
    "tools/__init__.py",
    "tools/check_content_contracts.py",
    "tools/check_frontend_architecture.py",
    "tools/optimize_images.py",
    "tools/run_lighthouse_budget.mjs",
    "tools/run_visual_qa.mjs",
    "tools/site_framework.py",
    "validator.py",
)
PROFILE_ALLOWED_PATHS = (
    "tools/check_site_contracts.py",
    "tools/new_page.py",
    "content/",
    "templates/",
    "static/",
    "README.md",
    "project-docs/",
    "site.config.yaml",
)


def project_file(relative_path: str) -> Path:
    return ROOT / relative_path


def check_reusable_files(errors: list[str]) -> None:
    for relative_path in REUSABLE_PATHS:
        path = project_file(relative_path)
        if not path.exists():
            continue

        text = path.read_text(encoding=TEXT_ENCODING)
        for term in BRAND_TERMS:
            if term in text:
                errors.append(f"{relative_path}: reusable framework file contains site-specific term {term!r}")


def check_profile_paths_exist(errors: list[str]) -> None:
    for relative_path in PROFILE_ALLOWED_PATHS:
        path = project_file(relative_path)
        if not path.exists():
            errors.append(f"profile boundary allowlist path does not exist: {relative_path}")


def main() -> int:
    errors: list[str] = []
    check_reusable_files(errors)
    check_profile_paths_exist(errors)

    if errors:
        print("Framework boundary check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("OK framework boundary checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
