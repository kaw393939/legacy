"""Shared primitives for the static site framework."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content"
PAGES_DIR = CONTENT_DIR / "pages"
DATA_DIR = CONTENT_DIR / "data"
SITE_PROFILE_CONFIG = CONTENT_DIR / "site-profile.yaml"
SITE_PROFILES_DIR = CONTENT_DIR / "profiles"
TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"
DOCS_DIR = ROOT / "docs"
CONTENT_CONFIG = CONTENT_DIR / "config.yaml"

HOME_SOURCE = "home.md"
HOME_OUTPUT = "index.html"
OUTPUT_STYLESHEET = "styles.css"
CRITICAL_OUTPUT_FILES = (HOME_OUTPUT, OUTPUT_STYLESHEET)
VALIDATION_REPORT = "validation-report.json"
VALIDATION_REPORT_PATH = ROOT / VALIDATION_REPORT
MARKDOWN_EXTENSIONS = ["meta", "extra", "codehilite", "toc"]
TEXT_ENCODING = "utf-8"


@dataclass(frozen=True)
class PageSource:
    path: Path
    frontmatter: dict[str, Any]
    body: str

    @property
    def output_name(self) -> str:
        return output_name(self.path)

    @property
    def source_label(self) -> str:
        return self.path.relative_to(ROOT).as_posix()


def project_path(path: str | Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else ROOT / path


def read_text(path: str | Path) -> str:
    return project_path(path).read_text(encoding=TEXT_ENCODING)


def write_text(path: str | Path, value: str) -> None:
    project_path(path).write_text(value, encoding=TEXT_ENCODING)


def load_yaml(path: str | Path) -> Any:
    return yaml.safe_load(read_text(path)) or {}


def load_content_config() -> dict[str, Any]:
    config = load_yaml(CONTENT_CONFIG)
    return config if isinstance(config, dict) else {}


def load_site_profile_config() -> dict[str, Any]:
    config = load_yaml(SITE_PROFILE_CONFIG) if SITE_PROFILE_CONFIG.exists() else {}
    return config if isinstance(config, dict) else {}


def load_site_profiles() -> dict[str, dict[str, Any]]:
    config = load_site_profile_config()
    profiles: dict[str, dict[str, Any]] = {}

    inline_profile = config.get("profile")
    if isinstance(inline_profile, dict):
        profile_id = str(inline_profile.get("id") or "default")
        profiles[profile_id] = inline_profile

    profiles_dir_value = config.get("profiles_dir", SITE_PROFILES_DIR.relative_to(CONTENT_DIR).as_posix())
    profiles_dir = CONTENT_DIR / str(profiles_dir_value)
    if profiles_dir.exists():
        for path in sorted(profiles_dir.glob("*.yaml")):
            loaded = load_yaml(path)
            profile = loaded.get("profile") if isinstance(loaded, dict) else None
            if not isinstance(profile, dict):
                continue

            profile_id = str(profile.get("id") or path.stem)
            profiles[profile_id] = profile

    return profiles


def active_site_profile() -> dict[str, Any]:
    config = load_site_profile_config()
    profiles = load_site_profiles()
    active_id = str(config.get("active_profile") or next(iter(profiles), ""))
    return profiles.get(active_id, {})


def build_config(config: dict[str, Any] | None = None) -> dict[str, Any]:
    value = (load_content_config() if config is None else config).get("build") or {}
    return value if isinstance(value, dict) else {}


def configured_output_dir(config: dict[str, Any] | None = None) -> Path:
    return project_path(build_config(config).get("output_dir", DOCS_DIR.relative_to(ROOT)))


def configured_static_dir(config: dict[str, Any] | None = None) -> Path:
    return project_path(build_config(config).get("static_dir", STATIC_DIR.relative_to(ROOT)))


def configured_templates_dir(config: dict[str, Any] | None = None) -> Path:
    return project_path(build_config(config).get("template_dir", TEMPLATES_DIR.relative_to(ROOT)))


def parse_frontmatter(path: str | Path) -> PageSource:
    path = project_path(path)
    raw = read_text(path)
    normalized = raw.replace("\r\n", "\n").replace("\r", "\n")

    if not normalized.startswith("---\n"):
        return PageSource(path=path, frontmatter={}, body=raw)

    lines = normalized.split("\n")
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() != "---":
            continue

        loaded = yaml.safe_load("\n".join(lines[1:index])) or {}
        frontmatter = loaded if isinstance(loaded, dict) else {}
        body = "\n".join(lines[index + 1 :]).strip()
        return PageSource(path=path, frontmatter=frontmatter, body=body)

    return PageSource(path=path, frontmatter={}, body=raw)


def output_name(path: str | Path) -> str:
    path = Path(path)
    return HOME_OUTPUT if path.name == HOME_SOURCE else f"{path.stem}.html"


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def page_sources() -> list[PageSource]:
    return [parse_frontmatter(path) for path in sorted(PAGES_DIR.glob("*.md"))]


def generated_html_files(output_dir: str | Path | None = None) -> list[Path]:
    return sorted((project_path(output_dir) if output_dir else configured_output_dir()).glob("*.html"))
