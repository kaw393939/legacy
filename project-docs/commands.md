# Commands

Run commands from the repository root.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Site CLI

Build generated output:

```powershell
.\.venv\Scripts\python.exe site.py build
```

Serve `docs/` locally:

```powershell
.\.venv\Scripts\python.exe site.py serve
```

Run checks, then serve:

```powershell
.\.venv\Scripts\python.exe site.py dev
```

Run source, generated output, frontend, and JS checks:

```powershell
.\.venv\Scripts\python.exe site.py validate
```

Run the full quality gate:

```powershell
.\.venv\Scripts\python.exe site.py check
```

Run the full quality gate with Lighthouse:

```powershell
.\.venv\Scripts\python.exe site.py check --lighthouse
```

Run Lighthouse against a specific URL:

```powershell
.\.venv\Scripts\python.exe site.py lighthouse http://localhost:8000/index.html
```

Capture desktop and mobile QA screenshots:

```powershell
.\.venv\Scripts\python.exe site.py visual-qa
```

Remove generated output and validation report:

```powershell
.\.venv\Scripts\python.exe site.py clean
```

Show project status:

```powershell
.\.venv\Scripts\python.exe site.py status
```

Optimize images from originals:

```powershell
.\.venv\Scripts\python.exe site.py optimize-images
```

## Page Scaffolding

Create a standard content page:

```powershell
.\.venv\Scripts\python.exe site.py new-page --kind page --slug example-guide --title "Example Guide" --description "Short meta description under 160 characters."
```

Create a situation guide:

```powershell
.\.venv\Scripts\python.exe site.py new-page --kind situation --slug new-situation --title "New Situation Help" --description "Describe the situation and the first useful next step."
```

## Direct Tools

Generated-site integrity check:

```powershell
.\.venv\Scripts\python.exe -m tools.check_site_integrity
```

Lighthouse budget runner:

```powershell
node tools/run_lighthouse_budget.mjs --url http://localhost:8000/index.html --min 90
```

JavaScript syntax check:

```powershell
node --check static\js\main.js
```
