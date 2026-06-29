#!/usr/bin/env python3
"""Legacy Defenders static site generator."""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

import markdown
import yaml
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape


def _minify_css_conservative(css: str) -> str:
    """Remove comments and excess whitespace without changing CSS semantics."""

    css = css.replace("\r\n", "\n").replace("\r", "\n")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,>+~])\s*", r"\1", css)
    css = css.replace(";}", "}")
    return css.strip() + "\n"


def _enhance_responsive_tables(html: str) -> str:
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
            cells = row.find_all(["td", "th"], recursive=False)
            for index, cell in enumerate(cells):
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
    """Build Markdown/YAML/Jinja source files into the docs/ static site."""

    def __init__(self, config_path: str = "content/config.yaml") -> None:
        self.project_root = Path(__file__).resolve().parent
        self.config = self.load_yaml(config_path)

        self.content_dir = self.project_root / "content"
        self.template_dir = self.project_root / self.config["build"]["template_dir"]
        self.static_dir = self.project_root / self.config["build"]["static_dir"]
        self.output_dir = self.project_root / self.config["build"]["output_dir"]
        self.asset_version = self.compute_asset_version()

        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        print("Legacy Defenders - Site Builder")
        print("=" * 50)

    def load_yaml(self, path: str) -> dict:
        try:
            return yaml.safe_load((self.project_root / path).read_text(encoding="utf-8")) or {}
        except Exception as exc:
            print(f"ERROR loading {path}: {exc}")
            sys.exit(1)

    def compute_asset_version(self) -> str:
        """Create a stable cache-busting token from source CSS and JS."""

        digest = hashlib.sha256()
        asset_roots = [self.static_dir / "css", self.static_dir / "js"]

        for asset_root in asset_roots:
            if not asset_root.exists():
                continue
            for path in sorted(asset_root.rglob("*")):
                if path.is_file() and path.suffix in {".css", ".js"}:
                    relative = path.relative_to(self.project_root).as_posix()
                    digest.update(relative.encode("utf-8"))
                    digest.update(b"\0")
                    digest.update(path.read_bytes())
                    digest.update(b"\0")

        return digest.hexdigest()[:12]

    def load_all_data(self) -> dict:
        data_dir = self.content_dir / "data"
        data: dict = {}

        print("\nLoading content data...")

        for yaml_file in sorted(data_dir.glob("*.yaml")):
            key = yaml_file.stem
            key_normalized = key.replace("-", "_")
            content = self.load_yaml(f"content/data/{yaml_file.name}")

            if isinstance(content, dict):
                if key in content:
                    data[key_normalized] = content[key]
                elif key_normalized in content:
                    data[key_normalized] = content[key_normalized]
                else:
                    data[key_normalized] = content
            else:
                data[key_normalized] = content

            print(f"   OK Loaded {key_normalized}")

        return data

    def parse_page(self, page_path: Path) -> tuple[dict, str]:
        raw = page_path.read_text(encoding="utf-8")

        if raw.startswith("---"):
            parts = raw.split("---", 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1]) or {}
                markdown_content = parts[2].strip()
            else:
                frontmatter = {}
                markdown_content = raw
        else:
            frontmatter = {}
            markdown_content = raw

        md = markdown.Markdown(extensions=["meta", "extra", "codehilite", "toc"])
        html_content = md.convert(markdown_content)
        return frontmatter, _enhance_responsive_tables(html_content)

    def build_page(self, page_file: str, data: dict) -> None:
        page_path = self.content_dir / "pages" / page_file

        if not page_path.exists():
            print(f"   WARNING Page not found: {page_file}")
            return

        print(f"   Building {page_file}...")

        frontmatter, content = self.parse_page(page_path)
        output_file = "index.html" if page_file == "home.md" else f"{page_path.stem}.html"

        layout = frontmatter.get("layout", "page")
        template = self.jinja_env.get_template(f"{layout}.html")

        context = {
            "site": self.config["site"],
            "features": self.config.get("features", {}),
            "page": frontmatter,
            "content": content,
            "build_time": datetime.now().isoformat(),
            "asset_version": self.asset_version,
            "current_year": datetime.now().year,
            "section": frontmatter,
            **data,
        }

        html = template.render(**context)
        (self.output_dir / output_file).write_text(html, encoding="utf-8")
        print(f"      OK Generated {output_file}")

    def copy_static_files(self, minify_css: bool = False) -> None:
        print("\nCopying static assets...")

        if not self.static_dir.exists():
            print(f"   WARNING Static directory not found: {self.static_dir}")
            return

        css_src = self.static_dir / "css"
        if css_src.exists():
            parts_dir = css_src / "parts"
            part_files = sorted(parts_dir.glob("*.css")) if parts_dir.exists() else []

            if part_files:
                bundled = "\n".join(p.read_text(encoding="utf-8").rstrip() for p in part_files)
                bundled = bundled.rstrip() + "\n"
                if minify_css:
                    bundled = _minify_css_conservative(bundled)
                (self.output_dir / "styles.css").write_text(bundled, encoding="utf-8")
                print(f"   OK Bundled styles.css ({len(part_files)} parts)")

                for css_file in sorted(css_src.glob("*.css")):
                    if css_file.name == "styles.css":
                        continue
                    shutil.copy2(css_file, self.output_dir / css_file.name)
                    print(f"   OK Copied {css_file.name}")
            else:
                for css_file in sorted(css_src.glob("*.css")):
                    shutil.copy2(css_file, self.output_dir / css_file.name)
                    print(f"   OK Copied {css_file.name}")

        js_src = self.static_dir / "js"
        if js_src.exists():
            for js_file in sorted(js_src.glob("*.js")):
                shutil.copy2(js_file, self.output_dir / js_file.name)
                print(f"   OK Copied {js_file.name}")

        img_src = self.static_dir / "images"
        img_dest = self.output_dir / "images"
        if img_src.exists():
            if img_dest.exists():
                shutil.rmtree(img_dest)
            shutil.copytree(img_src, img_dest)
            print("   OK Copied images/ directory")

        for seo_file in ["robots.txt", "sitemap.xml", "CNAME", ".nojekyll"]:
            src = self.static_dir / seo_file
            if src.exists():
                shutil.copy2(src, self.output_dir / seo_file)
                print(f"   OK Copied {seo_file}")

    def clean_output(self) -> None:
        if self.output_dir.exists():
            print(f"\nCleaning {self.output_dir}...")
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build(self, clean: bool = True, minify_css: bool = False) -> None:
        start_time = datetime.now()

        if clean:
            self.clean_output()

        data = self.load_all_data()

        print("\nBuilding pages...")
        pages_dir = self.content_dir / "pages"

        for page_file in sorted(pages_dir.glob("*.md")):
            self.build_page(page_file.name, data)

        self.copy_static_files(minify_css=minify_css)

        elapsed = (datetime.now() - start_time).total_seconds()

        print("\n" + "=" * 50)
        print(f"OK Build complete in {elapsed:.2f}s")
        print(f"Output: {self.output_dir}")
        print("=" * 50)

    def validate(self) -> bool:
        print("\nValidating output...")

        html_files = list(self.output_dir.glob("*.html"))
        if not html_files:
            print("   ERROR No HTML files generated")
            return False

        print(f"   OK Generated {len(html_files)} HTML files")

        for filename in ["index.html", "styles.css"]:
            if not (self.output_dir / filename).exists():
                print(f"   ERROR Missing critical file: {filename}")
                return False
        print("   OK All critical files present")

        try:
            from validator import SiteValidator

            print("\n" + "=" * 60)
            print("QUALITY VALIDATION")
            print("=" * 60)

            validator = SiteValidator(self.output_dir)
            results = validator.validate_all()

            report = validator.generate_report()
            print(report)

            report_path = self.project_root / "validation-report.json"
            validator.save_report(report_path)

            total_errors = sum(len(result.errors) for result in results)
            if total_errors > 0:
                print(f"\nValidation failed with {total_errors} errors")
                return False

            print("\nOK Validation passed")
            return True
        except Exception as exc:
            print(f"WARNING Validation error (skipping quality checks): {exc}")
            return True


def run_content_contracts() -> bool:
    from tools.check_content_contracts import main as check_content_contracts

    return check_content_contracts() == 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Legacy Defenders website")
    parser.add_argument("--no-clean", action="store_true", help="Do not clean output directory")
    parser.add_argument("--validate", action="store_true", help="Run source and output validation")
    parser.add_argument("--minify-css", action="store_true", help="Conservatively minify bundled CSS output")
    args = parser.parse_args()

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
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
