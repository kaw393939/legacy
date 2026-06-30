#!/usr/bin/env python3
"""Convenience CLI for the static site framework."""

from __future__ import annotations

import argparse
import logging
import socket
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from typing import Sequence

from tools.site_framework import (
    ROOT,
    VALIDATION_REPORT,
    VALIDATION_REPORT_PATH,
    configured_output_dir,
    load_yaml,
)


PYTHON_SYNTAX_FILES = ("build.py", "site.py", "validator.py")
JAVASCRIPT_TOOL_FILES = ("tools/run_lighthouse_budget.mjs", "tools/run_visual_qa.mjs")
VISUAL_QA_TOOL = "tools/run_visual_qa.mjs"


class SiteManager:
    """Small command runner around the real build and QA scripts."""

    def __init__(self, config_file: str = "site.config.yaml") -> None:
        self.root = ROOT
        self.config = self.load_config(config_file)
        self.output_dir = configured_output_dir()
        self._setup_logging()

    def load_config(self, config_file: str) -> dict:
        path = self.root / config_file
        if not path.exists():
            return {
                "project": {"name": "Static Site"},
                "performance": {"minify_css": True, "lighthouse_min_score": 90},
            }
        return load_yaml(path)

    def _setup_logging(self) -> None:
        level_name = self.config.get("logging", {}).get("level", "INFO")
        level = getattr(logging, str(level_name).upper(), logging.INFO)
        logging.basicConfig(level=level, format="%(levelname)s: %(message)s", stream=sys.stdout)
        self.logger = logging.getLogger("static-site")

    def _run(self, command: Sequence[str], *, label: str) -> None:
        self.logger.info(label)
        subprocess.run(list(command), cwd=self.root, check=True)

    def _python_source_files(self) -> list[str]:
        tool_files = sorted((self.root / "tools").glob("*.py"))
        paths = [self.root / filename for filename in PYTHON_SYNTAX_FILES]
        return [str(path.relative_to(self.root)) for path in [*paths, *tool_files]]

    def _javascript_source_files(self) -> list[str]:
        runtime_files = sorted((self.root / "static" / "js").rglob("*.js"))
        tool_files = [self.root / filename for filename in JAVASCRIPT_TOOL_FILES]
        return [str(path.relative_to(self.root)) for path in [*runtime_files, *tool_files]]

    def _free_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])

    def _wait_for_url(self, url: str, *, timeout_seconds: float = 20.0) -> None:
        deadline = time.monotonic() + timeout_seconds
        last_error: Exception | None = None

        while time.monotonic() < deadline:
            try:
                with urllib.request.urlopen(url, timeout=2) as response:
                    if 200 <= response.status < 400:
                        return
            except (OSError, urllib.error.URLError) as exc:
                last_error = exc

            time.sleep(0.5)

        detail = f": {last_error}" if last_error else ""
        raise RuntimeError(f"Timed out waiting for local server at {url}{detail}")

    def _run_lighthouse_server(self) -> None:
        port = self._free_port()
        url = f"http://127.0.0.1:{port}/index.html"
        self.logger.info("Starting temporary Lighthouse server at %s", url)

        server = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "http.server",
                str(port),
                "--bind",
                "127.0.0.1",
                "--directory",
                str(self.output_dir),
            ],
            cwd=self.root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        try:
            self._wait_for_url(url)
            self.lighthouse(url)
        finally:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)

    def _run_temporary_server(self, callback) -> None:
        port = self._free_port()
        base_url = f"http://127.0.0.1:{port}/"
        self.logger.info("Starting temporary server at %s", base_url)

        server = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "http.server",
                str(port),
                "--bind",
                "127.0.0.1",
                "--directory",
                str(self.output_dir),
            ],
            cwd=self.root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        try:
            self._wait_for_url(f"{base_url}index.html")
            callback(base_url)
        finally:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)

    def build(self, *, validate: bool = False) -> None:
        command = [sys.executable, "build.py"]
        if self.config.get("performance", {}).get("minify_css", True):
            command.append("--minify-css")
        if validate:
            command.append("--validate")
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

    def check_python_syntax(self) -> None:
        self._run(
            [sys.executable, "-m", "py_compile", *self._python_source_files()],
            label="Checking Python syntax",
        )

    def check_javascript_syntax(self) -> None:
        for script in self._javascript_source_files():
            self._run(["node", "--check", script], label=f"Checking JavaScript syntax: {script}")

    def optimize_images(self) -> None:
        self._run([sys.executable, "-m", "tools.optimize_images"], label="Optimizing source images")

    def validate(self) -> None:
        self.check_python_syntax()
        self.optimize_images()
        self._run([sys.executable, "-m", "tools.check_content_contracts"], label="Checking source content contracts")
        self._run([sys.executable, "-m", "tools.check_site_contracts"], label="Checking site profile contracts")
        self._run([sys.executable, "-m", "tools.check_frontend_architecture"], label="Checking frontend architecture")
        self._run([sys.executable, "-m", "tools.check_framework_boundaries"], label="Checking framework boundaries")
        self.build()
        self._run(
            [sys.executable, "-m", "tools.check_site_integrity", "--report", VALIDATION_REPORT],
            label="Checking generated site integrity",
        )
        self.check_javascript_syntax()

    def lighthouse(self, url: str = "http://localhost:8000/index.html") -> None:
        min_score = str(self.config.get("performance", {}).get("lighthouse_min_score", 90))
        self._run(
            ["node", "tools/run_lighthouse_budget.mjs", "--url", url, "--min", min_score],
            label=f"Checking Lighthouse budgets for {url}",
        )

    def visual_qa(self) -> None:
        self.build()

        def capture(base_url: str) -> None:
            self._run(
                ["node", VISUAL_QA_TOOL, "--base-url", base_url],
                label=f"Capturing visual QA screenshots for {base_url}",
            )

        self._run_temporary_server(capture)

    def check(self, *, include_lighthouse: bool = False) -> None:
        self.validate()
        self._run(["git", "diff", "--check"], label="Checking git diff whitespace")
        if include_lighthouse:
            self._run_lighthouse_server()

    def clean(self) -> None:
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
            self.logger.info("Removed %s", self.output_dir)
        if VALIDATION_REPORT_PATH.exists():
            VALIDATION_REPORT_PATH.unlink()
            self.logger.info("Removed %s", VALIDATION_REPORT_PATH)

    def status(self) -> None:
        project = self.config.get("project", {})
        print(f"{project.get('name', 'Static Site')} v{project.get('version', 'unknown')}")
        print(f"Root: {self.root}")
        print(f"Output: {self.output_dir}")
        print(f"Output exists: {self.output_dir.exists()}")
        if self.output_dir.exists():
            html_count = len(list(self.output_dir.glob("*.html")))
            print(f"Generated HTML pages: {html_count}")
        subprocess.run(["git", "status", "--short", "--branch"], cwd=self.root, check=False)

    def new_page(self, args: Sequence[str]) -> None:
        forwarded_args = list(args) or ["--help"]
        self._run([sys.executable, "-m", "tools.new_page", *forwarded_args], label="Creating page scaffold")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage the static site framework")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("build", help="Build the generated site")
    subparsers.add_parser("serve", help="Serve the generated site locally")
    subparsers.add_parser("dev", help="Run checks and serve the generated site")
    subparsers.add_parser("validate", help="Run source, output, and JS checks")

    check_parser = subparsers.add_parser("check", help="Run the full local quality gate")
    check_parser.add_argument("--lighthouse", action="store_true", help="Also run Lighthouse against localhost")

    lighthouse_parser = subparsers.add_parser("lighthouse", help="Run Lighthouse budget checks")
    lighthouse_parser.add_argument("url", nargs="?", default="http://localhost:8000/index.html")

    subparsers.add_parser("visual-qa", help="Capture desktop and mobile QA screenshots")
    subparsers.add_parser("clean", help="Remove generated output")
    subparsers.add_parser("status", help="Show project status")
    subparsers.add_parser("optimize-images", help="Optimize static image originals into publishable assets")

    new_page_parser = subparsers.add_parser("new-page", help="Create a page or situation scaffold")
    new_page_parser.add_argument("--kind", choices=["page", "situation"], default="page")
    new_page_parser.add_argument("--profile")
    new_page_parser.add_argument("--slug")
    new_page_parser.add_argument("--title", required=True)
    new_page_parser.add_argument("--description", required=True)
    new_page_parser.add_argument("--force", action="store_true")

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
        elif args.command == "visual-qa":
            manager.visual_qa()
        elif args.command == "clean":
            manager.clean()
        elif args.command == "status":
            manager.status()
        elif args.command == "optimize-images":
            manager.optimize_images()
        elif args.command == "new-page":
            forwarded_args = ["--kind", args.kind, "--title", args.title, "--description", args.description]
            if args.profile:
                forwarded_args.extend(["--profile", args.profile])
            if args.slug:
                forwarded_args.extend(["--slug", args.slug])
            if args.force:
                forwarded_args.append("--force")
            manager.new_page(forwarded_args)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode) from exc
    except RuntimeError as exc:
        raise SystemExit(f"ERROR: {exc}") from exc


if __name__ == "__main__":
    main()
