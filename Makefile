# Convenience commands for the Legacy Defenders static site.

.PHONY: help install build serve dev validate check lighthouse clean status new-page

PYTHON ?= python
PORT ?= 8000

help:
	@echo "Legacy Defenders development commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       Install Python dependencies"
	@echo ""
	@echo "Build and preview:"
	@echo "  make build         Build docs/ with minified CSS and validation"
	@echo "  make serve         Serve docs/ at http://localhost:8000"
	@echo "  make dev           Build, validate, and serve"
	@echo ""
	@echo "Quality:"
	@echo "  make validate      Validate content contracts and generated output"
	@echo "  make check         Run the full local quality gate"
	@echo "  make lighthouse    Run Lighthouse against the local server"
	@echo ""
	@echo "Content:"
	@echo "  make new-page      Show the page generator help"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean         Remove generated docs/"
	@echo "  make status        Show project status"

install:
	$(PYTHON) -m pip install -r requirements.txt

build:
	$(PYTHON) build.py --minify-css --validate

serve:
	$(PYTHON) -m http.server $(PORT) --directory docs

dev: build serve

validate:
	$(PYTHON) tools/check_content_contracts.py
	$(PYTHON) build.py --minify-css --validate
	node tools/check_site_integrity.mjs
	node --check static/js/main.js

check:
	$(PYTHON) site.py check

lighthouse:
	node tools/run_lighthouse_budget.mjs http://localhost:$(PORT)/index.html --min 90

clean:
	$(PYTHON) site.py clean

status:
	$(PYTHON) site.py status

new-page:
	$(PYTHON) tools/new_page.py --help
