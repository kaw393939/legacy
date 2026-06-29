#!/usr/bin/env python3
"""Build the Legacy Defenders static site."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import re
import shutil
import sys
import time
from typing import Any

import markdown
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape

from tools.site_framework import (
    CRITICAL_OUTPUT_FILES,
    DATA_DIR,
    MARKDOWN_EXTENSIONS,
    OUTPUT_STYLESHEET,
    ROOT,
    TEXT_ENCODING,
    VALIDATION_REPORT_PATH,
    configured_output_dir,
    configured_static_dir,
    configured_templates_dir,
    load_yaml,
    page_sources,
)


SEO_FILES = ("robots.txt", "sitemap.xml", "CNAME", ".nojekyll")
ASSET_SUFFIXES = {".css", ".js"}


def minify_css_conservative(css: str) -> str:
    """Remove comments and excess whitespace without changing CSS semantics."""

    css = css.replace("\r\n", "\n").replace("\r", "\n")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,>+~])\s*", r"\1", css)
    css = css.replace(";}", "}")
    return css.strip() + "\n"


def enhance_responsive_tables(html: str) -> str:
    """Add mobile table labels at build time to avoid client-side layout shifts."""

    soup = BeautifulSoup(html, "html.parser")

    for table in soup.find_all("table"):
        headers = [
            cell.get_text(" ", strip=True)
            for cell in table.select("thead th")
            if cell.get_text(" ", strip=True)
        ]
        if not headers:
            continue

        classes = table.get("class", [])
        if "responsive-table-ready" not in classes:
            table["class"] = [*classes, "responsive-table-ready"]

        tbody = table.find("tbody")
        rows = tbody.find_all("tr", recursive=False) if tbody else table.find_all("tr")

        for row in rows:
            for index, cell in enumerate(row.find_all(["td", "th"], recursive=False)):
                if cell.name == "th" and cell.find_parent("thead"):
                    continue

                fallback = "Item" if index == 0 else f"Detail {index + 1}"
                cell["data-label"] = headers[index] if index < len(headers) else fallback

                if not cell.get_text(" ", strip=True):
                    cell_classes = cell.get("class", [])
                    if "table-cell-empty" not in cell_classes:
                        cell["class"] = [*cell_classes, "table-cell-empty"]

    return "".join(str(child) for child in soup.contents)


class SiteBuilder:
    """Render Markdown/YAML/Jinja source files into the static output directory."""

    def __init__(self, config_path: str = "content/config.yaml") -> None:
        self.project_root = ROOT
        self.config = load_yaml(config_path)
        self.content_dir = self.project_root / "content"
        self.template_dir = configured_templates_dir(self.config)
        self.static_dir = configured_static_dir(self.config)
        self.output_dir = configured_output_dir(self.config)
        self.asset_version = self.compute_asset_version()
        self.jinja_env = self.create_jinja_environment()

        print("Legacy Defenders - Site Builder")
        print("=" * 50)

    def create_jinja_environment(self) -> Environment:
        return Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def compute_asset_version(self) -> str:
        """Create a stable cache-busting token from source CSS and JS."""

        digest = hashlib.sha256()

        for asset_root in (self.static_dir / "css", self.static_dir / "js"):
            if not asset_root.exists():
                continue

            for path in sorted(asset_root.rglob("*")):
                if not path.is_file() or path.suffix not in ASSET_SUFFIXES:
                    continue

                digest.update(path.relative_to(self.project_root).as_posix().encode("utf-8"))
                digest.update(b"\0")
                digest.update(path.read_bytes())
                digest.update(b"\0")

        return digest.hexdigest()[:12]

    def load_all_data(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        print("\nLoading content data...")

        for yaml_file in sorted(DATA_DIR.glob("*.yaml")):
            key = yaml_file.stem
            key_normalized = key.replace("-", "_")
            content = load_yaml(yaml_file)

            if isinstance(content, dict) and key in content:
                data[key_normalized] = content[key]
            elif isinstance(content, dict) and key_normalized in content:
                data[key_normalized] = content[key_normalized]
            else:
                data[key_normalized] = content

            print(f"   OK Loaded {key_normalized}")

        return data

    def render_markdown(self, markdown_content: str) -> str:
        md = markdown.Markdown(extensions=MARKDOWN_EXTENSIONS)
        return enhance_responsive_tables(md.convert(markdown_content))

    def build_page(self, page, data: dict[str, Any]) -> None:
        print(f"   Building {page.path.name}...")

        layout = page.frontmatter.get("layout", "page")
        template = self.jinja_env.get_template(f"{layout}.html")
        content = self.render_markdown(page.body)

        context = {
            "site": self.config["site"],
            "features": self.config.get("features", {}),
            "page": page.frontmatter,
            "content": content,
            "asset_version": self.asset_version,
            "current_year": datetime.now().year,
            "section": page.frontmatter,
            **data,
        }

        html = template.render(**context)
        (self.output_dir / page.output_name).write_text(html, encoding=TEXT_ENCODING)
        print(f"      OK Generated {page.output_name}")

    def bundle_css(self, *, minify_css: bool) -> None:
        css_src = self.static_dir / "css"
        if not css_src.exists():
            return

        parts_dir = css_src / "parts"
        part_files = sorted(parts_dir.glob("*.css")) if parts_dir.exists() else []

        if not part_files:
            for css_file in sorted(css_src.glob("*.css")):
                shutil.copy2(css_file, self.output_dir / css_file.name)
                print(f"   OK Copied {css_file.name}")
            return

        bundled = "\n".join(path.read_text(encoding=TEXT_ENCODING).rstrip() for path in part_files)
        bundled = bundled.rstrip() + "\n"
        if minify_css:
            bundled = minify_css_conservative(bundled)

        (self.output_dir / OUTPUT_STYLESHEET).write_text(bundled, encoding=TEXT_ENCODING)
        print(f"   OK Bundled {OUTPUT_STYLESHEET} ({len(part_files)} parts)")

        for css_file in sorted(css_src.glob("*.css")):
            if css_file.name == OUTPUT_STYLESHEET:
                continue
            shutil.copy2(css_file, self.output_dir / css_file.name)
            print(f"   OK Copied {css_file.name}")

    def copy_js(self) -> None:
        js_src = self.static_dir / "js"
        if not js_src.exists():
            return

        for js_file in sorted(js_src.glob("*.js")):
            shutil.copy2(js_file, self.output_dir / js_file.name)
            print(f"   OK Copied {js_file.name}")

    def copy_images(self) -> None:
        img_src = self.static_dir / "images"
        img_dest = self.output_dir / "images"

        if not img_src.exists():
            return

        if img_dest.exists():
            shutil.rmtree(img_dest)
        shutil.copytree(img_src, img_dest)
        print("   OK Copied images/ directory")

    def copy_seo_files(self) -> None:
        for filename in SEO_FILES:
            src = self.static_dir / filename
            if src.exists():
                shutil.copy2(src, self.output_dir / filename)
                print(f"   OK Copied {filename}")

    def copy_static_files(self, *, minify_css: bool = False) -> None:
        print("\nCopying static assets...")

        if not self.static_dir.exists():
            print(f"   WARNING Static directory not found: {self.static_dir}")
            return

        self.bundle_css(minify_css=minify_css)
        self.copy_js()
        self.copy_images()
        self.copy_seo_files()

    def clean_output(self) -> None:
        if self.output_dir.exists():
            print(f"\nCleaning {self.output_dir}...")
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build(self, *, clean: bool = True, minify_css: bool = False) -> None:
        started_at = time.perf_counter()

        if clean:
            self.clean_output()

        data = self.load_all_data()

        print("\nBuilding pages...")
        for page in page_sources():
            self.build_page(page, data)

        self.copy_static_files(minify_css=minify_css)

        elapsed = time.perf_counter() - started_at
        print("\n" + "=" * 50)
        print(f"OK Build complete in {elapsed:.2f}s")
        print(f"Output: {self.output_dir}")
        print("=" * 50)

    def validate(self) -> bool:
        print("\nValidating output...")

        html_files = sorted(self.output_dir.glob("*.html"))
        if not html_files:
            print("   ERROR No HTML files generated")
            return False

        print(f"   OK Generated {len(html_files)} HTML files")

        for filename in CRITICAL_OUTPUT_FILES:
            if not (self.output_dir / filename).exists():
                print(f"   ERROR Missing critical file: {filename}")
                return False
        print("   OK All critical files present")

        from validator import SiteValidator

        print("\n" + "=" * 60)
        print("QUALITY VALIDATION")
        print("=" * 60)

        validator = SiteValidator(self.output_dir)
        results = validator.validate_all()
        print(validator.generate_report(results))
        validator.save_report(VALIDATION_REPORT_PATH, results)

        total_errors = sum(len(result.errors) for result in results)
        if total_errors > 0:
            print(f"\nValidation failed with {total_errors} errors")
            return False

        print("\nOK Validation passed")
        return True


def run_content_contracts() -> bool:
    from tools.check_content_contracts import main as check_content_contracts

    return check_content_contracts() == 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the Legacy Defenders website")
    parser.add_argument("--no-clean", action="store_true", help="Do not clean output directory")
    parser.add_argument("--validate", action="store_true", help="Run source and output validation")
    parser.add_argument("--minify-css", action="store_true", help="Conservatively minify bundled CSS output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        if args.validate and not run_content_contracts():
            sys.exit(1)

        builder = SiteBuilder()
        builder.build(clean=not args.no_clean, minify_css=args.minify_css)

        if args.validate and not builder.validate():
            sys.exit(1)

        print("\nSuccess. Your site is ready.")
    except KeyboardInterrupt:
        print("\n\nBuild cancelled by user")
        sys.exit(1)
    except Exception as exc:
        print(f"\nBuild failed: {exc}")
        raise


if __name__ == "__main__":
    main()
