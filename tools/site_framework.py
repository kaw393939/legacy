"""Shared primitives for the Legacy Defenders static site framework."""

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
TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"
DOCS_DIR = ROOT / "docs"

HOME_SOURCE = "home.md"
HOME_OUTPUT = "index.html"
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


def parse_frontmatter(path: str | Path) -> PageSource:
    path = project_path(path)
    raw = path.read_text(encoding=TEXT_ENCODING)

    if not raw.startswith("---"):
        return PageSource(path=path, frontmatter={}, body=raw)

    parts = raw.split("---", 2)
    if len(parts) < 3:
        return PageSource(path=path, frontmatter={}, body=raw)

    frontmatter = yaml.safe_load(parts[1]) or {}
    return PageSource(path=path, frontmatter=frontmatter, body=parts[2].strip())


def output_name(path: str | Path) -> str:
    path = Path(path)
    return HOME_OUTPUT if path.name == HOME_SOURCE else f"{path.stem}.html"


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def page_sources() -> list[PageSource]:
    return [parse_frontmatter(path) for path in sorted(PAGES_DIR.glob("*.md"))]


def generated_html_files(output_dir: str | Path = DOCS_DIR) -> list[Path]:
    return sorted(project_path(output_dir).glob("*.html"))
