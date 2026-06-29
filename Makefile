# Convenience commands for the Legacy Defenders static site.

.PHONY: help install build serve dev validate check lighthouse clean status new-page

PYTHON ?= python

help:
	@echo "Legacy Defenders development commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       Install Python dependencies"
	@echo ""
	@echo "Build and preview:"
	@echo "  make build         Build the generated site"
	@echo "  make serve         Serve the generated site at http://localhost:8000"
	@echo "  make dev           Build, validate, and serve"
	@echo ""
	@echo "Quality:"
	@echo "  make validate      Validate content contracts and generated output"
	@echo "  make check         Run the full local quality gate"
	@echo "  make lighthouse    Run the full quality gate with Lighthouse"
	@echo ""
	@echo "Content:"
	@echo "  make new-page      Show the page generator help"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean         Remove generated output"
	@echo "  make status        Show project status"

install:
	$(PYTHON) -m pip install -r requirements.txt

build:
	$(PYTHON) site.py build

serve:
	$(PYTHON) site.py serve

dev:
	$(PYTHON) site.py dev

validate:
	$(PYTHON) site.py validate

check:
	$(PYTHON) site.py check

lighthouse:
	$(PYTHON) site.py check --lighthouse

clean:
	$(PYTHON) site.py clean

status:
	$(PYTHON) site.py status

new-page:
	$(PYTHON) site.py new-page
