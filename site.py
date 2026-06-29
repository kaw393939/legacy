#!/usr/bin/env python3
"""Convenience CLI for the Legacy Defenders static site."""

from __future__ import annotations

import argparse
import logging
import shutil
import subprocess
import sys
from typing import Sequence

from tools.site_framework import ROOT, load_yaml


class SiteManager:
    """Small command runner around the real build and QA scripts."""

    def __init__(self, config_file: str = "site.config.yaml") -> None:
        self.root = ROOT
        self.config = self.load_config(config_file)
        self.output_dir = self.root / self.config.get("build", {}).get("output_dir", "docs")
        self._setup_logging()

    def load_config(self, config_file: str) -> dict:
        path = self.root / config_file
        if not path.exists():
            return {
                "project": {"name": "Legacy Defenders"},
                "build": {"output_dir": "docs"},
                "performance": {"minify_css": True, "lighthouse_min_score": 90},
            }
        return load_yaml(path)

    def _setup_logging(self) -> None:
        level_name = self.config.get("logging", {}).get("level", "INFO")
        level = getattr(logging, str(level_name).upper(), logging.INFO)
        logging.basicConfig(level=level, format="%(levelname)s: %(message)s")
        self.logger = logging.getLogger("legacy-site")

    def _run(self, command: Sequence[str], *, label: str) -> None:
        self.logger.info(label)
        subprocess.run(list(command), cwd=self.root, check=True)

    def build(self) -> None:
        command = [sys.executable, "build.py", "--validate"]
        if self.config.get("performance", {}).get("minify_css", True):
            command.append("--minify-css")
        self._run(command, label="Building generated site")

    def serve(self) -> None:
        port = str(self.config.get("development", {}).get("server", {}).get("port", 8000))
        host = self.config.get("development", {}).get("server", {}).get("host", "localhost")
        self.logger.info("Serving %s at http://%s:%s", self.output_dir, host, port)
        subprocess.run(
            [sys.executable, "-m", "http.server", port, "--directory", str(self.output_dir)],
            cwd=self.root,
            check=False,
        )

    def dev(self) -> None:
        self.check(include_lighthouse=False)
        self.serve()

    def validate(self) -> None:
        self.build()
        self._run([sys.executable, "-m", "tools.check_site_integrity"], label="Checking generated site integrity")
        self._run(["node", "--check", "static/js/main.js"], label="Checking JavaScript syntax")

    def lighthouse(self, url: str = "http://localhost:8000/index.html") -> None:
        min_score = str(self.config.get("performance", {}).get("lighthouse_min_score", 90))
        self._run(
            ["node", "tools/run_lighthouse_budget.mjs", url, "--min", min_score],
            label=f"Checking Lighthouse budgets for {url}",
        )

    def check(self, *, include_lighthouse: bool = False) -> None:
        self.validate()
        self._run(["git", "diff", "--check"], label="Checking git diff whitespace")
        if include_lighthouse:
            self.lighthouse()

    def clean(self) -> None:
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
            self.logger.info("Removed %s", self.output_dir)
        report = self.root / "validation-report.json"
        if report.exists():
            report.unlink()
            self.logger.info("Removed %s", report)

    def status(self) -> None:
        project = self.config.get("project", {})
        print(f"{project.get('name', 'Legacy Defenders')} v{project.get('version', 'unknown')}")
        print(f"Root: {self.root}")
        print(f"Output: {self.output_dir}")
        print(f"Output exists: {self.output_dir.exists()}")
        if self.output_dir.exists():
            html_count = len(list(self.output_dir.glob("*.html")))
            print(f"Generated HTML pages: {html_count}")
        subprocess.run(["git", "status", "--short", "--branch"], cwd=self.root, check=False)

    def new_page(self, args: Sequence[str]) -> None:
        self._run([sys.executable, "-m", "tools.new_page", *args], label="Creating page scaffold")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage the Legacy Defenders static site")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("build", help="Build docs/ with validation")
    subparsers.add_parser("serve", help="Serve docs/ locally")
    subparsers.add_parser("dev", help="Run checks and serve docs/")
    subparsers.add_parser("validate", help="Run source, output, and JS checks")

    check_parser = subparsers.add_parser("check", help="Run the full local quality gate")
    check_parser.add_argument("--lighthouse", action="store_true", help="Also run Lighthouse against localhost")

    lighthouse_parser = subparsers.add_parser("lighthouse", help="Run Lighthouse budget checks")
    lighthouse_parser.add_argument("url", nargs="?", default="http://localhost:8000/index.html")

    subparsers.add_parser("clean", help="Remove generated output")
    subparsers.add_parser("status", help="Show project status")

    new_page_parser = subparsers.add_parser("new-page", help="Create a page or situation scaffold")
    new_page_parser.add_argument("args", nargs=argparse.REMAINDER)

    args = parser.parse_args()
    manager = SiteManager()

    try:
        if args.command == "build":
            manager.build()
        elif args.command == "serve":
            manager.serve()
        elif args.command == "dev":
            manager.dev()
        elif args.command == "validate":
            manager.validate()
        elif args.command == "check":
            manager.check(include_lighthouse=args.lighthouse)
        elif args.command == "lighthouse":
            manager.lighthouse(args.url)
        elif args.command == "clean":
            manager.clean()
        elif args.command == "status":
            manager.status()
        elif args.command == "new-page":
            manager.new_page(args.args)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode) from exc


if __name__ == "__main__":
    main()
