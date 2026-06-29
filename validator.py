"""Generated-site validation for the Legacy Defenders static framework."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urldefrag, urlparse

import cssutils
import html5lib
from bs4 import BeautifulSoup

from tools.site_framework import DOCS_DIR, load_yaml


MAX_META_DESCRIPTION_LENGTH = 160
CRITICAL_OUTPUT_FILES = ("index.html", "styles.css")
LOCAL_PROTOCOLS = {"", None}
SKIPPED_PROTOCOLS = {"mailto", "tel", "javascript", "data"}


@dataclass
class ValidationResult:
    name: str
    errors: list[str]
    warnings: list[str]


class SiteValidator:
    """Validate the generated static output directory."""

    def __init__(self, output_dir: Path | str = DOCS_DIR):
        self.output_dir = Path(output_dir)
        self.site_url = self._load_site_url()
        self.site_base_path = self._site_base_path()
        cssutils.log.setLevel("FATAL")

    @staticmethod
    def _load_site_url() -> str:
        config = load_yaml("content/config.yaml")
        return str((config.get("site") or {}).get("url") or "")

    def _site_base_path(self) -> str:
        parsed = urlparse(self.site_url)
        path = parsed.path.strip("/")
        return f"/{path}/" if path else "/"

    def validate_all(self) -> list[ValidationResult]:
        return [
            self._validate_required_files(),
            self._validate_html(),
            self._validate_links(),
            self._validate_css(),
        ]

    def _validate_required_files(self) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        if not self.output_dir.exists():
            errors.append(f"Output directory does not exist: {self.output_dir}")
            return ValidationResult("required-files", errors, warnings)

        for filename in CRITICAL_OUTPUT_FILES:
            if not (self.output_dir / filename).exists():
                errors.append(f"Missing critical output file: {filename}")

        return ValidationResult("required-files", errors, warnings)

    def _validate_html(self) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []
        html_files = sorted(self.output_dir.glob("*.html"))

        if not html_files:
            errors.append("No HTML files found in output directory")
            return ValidationResult("html", errors, warnings)

        for html_path in html_files:
            raw = html_path.read_text(encoding="utf-8", errors="replace")

            try:
                document = html5lib.parse(raw, treebuilder="etree")
                if document is None:
                    errors.append(f"{html_path.name}: html5lib returned no document")
            except Exception as exc:
                errors.append(f"{html_path.name}: HTML parse error: {exc}")
                continue

            soup = BeautifulSoup(raw, "html.parser")
            self._validate_page_metadata(soup, html_path.name, errors, warnings)
            self._validate_images(soup, html_path.name, warnings)

        return ValidationResult("html", errors, warnings)

    @staticmethod
    def _validate_page_metadata(
        soup: BeautifulSoup,
        page_name: str,
        errors: list[str],
        warnings: list[str],
    ) -> None:
        title = soup.find("title")
        if not title or not title.get_text(strip=True):
            errors.append(f"{page_name}: missing or empty <title>")

        description = soup.find("meta", attrs={"name": "description"})
        description_text = str(description.get("content", "")).strip() if description else ""

        if not description_text:
            errors.append(f"{page_name}: missing meta description")
        elif len(description_text) > MAX_META_DESCRIPTION_LENGTH:
            warnings.append(
                f"{page_name}: meta description is {len(description_text)} characters; "
                f"keep it under {MAX_META_DESCRIPTION_LENGTH}"
            )

    @staticmethod
    def _validate_images(soup: BeautifulSoup, page_name: str, warnings: list[str]) -> None:
        for img in soup.find_all("img"):
            if not img.has_attr("alt"):
                warnings.append(f"{page_name}: <img> missing alt attribute")

    def _validate_links(self) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []
        html_files = sorted(self.output_dir.glob("*.html"))
        existing_files = self._existing_output_files()
        page_ids = self._page_ids(html_files)

        for html_path in html_files:
            page_name = html_path.relative_to(self.output_dir).as_posix()
            soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="replace"), "html.parser")

            for tag_name, attr_name, raw_value in self._iter_asset_references(soup):
                self._validate_reference(
                    errors=errors,
                    page_name=page_name,
                    tag_name=tag_name,
                    attr_name=attr_name,
                    raw_value=raw_value,
                    existing_files=existing_files,
                    page_ids=page_ids,
                )

        return ValidationResult("links", errors, warnings)

    def _existing_output_files(self) -> set[str]:
        return {
            path.relative_to(self.output_dir).as_posix()
            for path in self.output_dir.rglob("*")
            if path.is_file()
        }

    def _page_ids(self, html_files: list[Path]) -> dict[str, set[str]]:
        page_ids: dict[str, set[str]] = {}

        for html_path in html_files:
            page_name = html_path.relative_to(self.output_dir).as_posix()
            soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="replace"), "html.parser")
            ids = {
                value
                for element in soup.find_all(attrs={"id": True})
                if (value := element.get("id"))
            }
            ids.update(
                value
                for element in soup.find_all(attrs={"name": True})
                if (value := element.get("name"))
            )
            page_ids[page_name] = ids

        return page_ids

    @staticmethod
    def _iter_asset_references(soup: BeautifulSoup):
        for element in soup.find_all(["a", "link", "script", "img", "source"]):
            for attr in ("href", "src"):
                if element.has_attr(attr):
                    yield element.name or "element", attr, str(element[attr])

    def _validate_reference(
        self,
        *,
        errors: list[str],
        page_name: str,
        tag_name: str,
        attr_name: str,
        raw_value: str,
        existing_files: set[str],
        page_ids: dict[str, set[str]],
    ) -> None:
        value = raw_value.strip()
        if not value:
            errors.append(f"{page_name}: empty {tag_name}[{attr_name}] value")
            return

        if attr_name == "href" and value == "#":
            errors.append(f"{page_name}: placeholder href '#' should point to a real section or page")
            return

        base_url, fragment = urldefrag(value)
        parsed = urlparse(base_url)

        if parsed.scheme in SKIPPED_PROTOCOLS:
            return

        if parsed.scheme in {"http", "https"}:
            target = self._local_target_from_absolute_url(parsed)
            if target:
                self._validate_local_target(errors, page_name, value, target, fragment, existing_files, page_ids)
            return

        if parsed.scheme not in LOCAL_PROTOCOLS:
            return

        target = self._local_target_from_relative_url(errors, page_name, tag_name, attr_name, base_url, value)
        if target is None:
            return

        self._validate_local_target(errors, page_name, value, target, fragment, existing_files, page_ids)

    def _local_target_from_absolute_url(self, parsed) -> str | None:
        site = urlparse(self.site_url)
        if not site.netloc or parsed.netloc != site.netloc:
            return None

        if parsed.path.rstrip("/") == self.site_base_path.rstrip("/"):
            return "index.html"

        if not parsed.path.startswith(self.site_base_path):
            return None

        local_path = parsed.path.removeprefix(self.site_base_path).lstrip("/")
        return unquote(local_path or "index.html")

    def _local_target_from_relative_url(
        self,
        errors: list[str],
        page_name: str,
        tag_name: str,
        attr_name: str,
        base_url: str,
        link_value: str,
    ) -> str | None:
        if base_url.startswith("/"):
            if base_url.rstrip("/") == self.site_base_path.rstrip("/"):
                return "index.html"

            if base_url.startswith(self.site_base_path):
                return unquote(base_url.removeprefix(self.site_base_path)) or "index.html"

            errors.append(
                f"{page_name}: {tag_name}[{attr_name}] uses root-relative link {link_value!r}; "
                "use a relative path so GitHub Pages subpath deployment works"
            )
            return None

        if base_url:
            clean_url = base_url.split("?", 1)[0]
            return (Path(page_name).parent / unquote(clean_url)).as_posix()

        return page_name

    @staticmethod
    def _validate_local_target(
        errors: list[str],
        page_name: str,
        link_value: str,
        target: str,
        fragment: str,
        existing_files: set[str],
        page_ids: dict[str, set[str]],
    ) -> None:
        if target in {"", "."}:
            target = "index.html"
        if target.endswith("/"):
            target = f"{target}index.html"

        target = target.removeprefix("./")

        if target not in existing_files:
            errors.append(f"{page_name}: broken local link {link_value!r} -> {target}")
            return

        if fragment and target.endswith(".html") and fragment not in page_ids.get(target, set()):
            errors.append(f"{page_name}: broken anchor {link_value!r} -> {target}#{fragment}")

    def _validate_css(self) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        css_path = self.output_dir / "styles.css"
        if not css_path.exists():
            errors.append("Missing styles.css in output")
            return ValidationResult("css", errors, warnings)

        try:
            cssutils.parseString(css_path.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:
            errors.append(f"styles.css: CSS parse error: {exc}")

        return ValidationResult("css", errors, warnings)

    def generate_report(self, results: list[ValidationResult] | None = None) -> str:
        results = results or self.validate_all()
        total_errors = sum(len(result.errors) for result in results)
        total_warnings = sum(len(result.warnings) for result in results)
        lines = [f"Results: {total_errors} errors, {total_warnings} warnings"]

        for result in results:
            if result.errors:
                lines.append(f"\n[{result.name}] Errors:")
                lines.extend(f"- {error}" for error in result.errors)
            if result.warnings:
                lines.append(f"\n[{result.name}] Warnings:")
                lines.extend(f"- {warning}" for warning in result.warnings)

        return "\n".join(lines).strip() + "\n"

    def save_report(self, path: Path | str, results: list[ValidationResult] | None = None) -> None:
        results = results or self.validate_all()
        payload: dict[str, Any] = {
            "output_dir": str(self.output_dir),
            "results": [
                {"name": result.name, "errors": result.errors, "warnings": result.warnings}
                for result in results
            ],
        }

        Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
