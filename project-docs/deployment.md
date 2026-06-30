# Deployment

## First Site Deployment

Legacy Defenders is the first active site profile deployed from this framework.

GitHub Pages URL:

[https://kaw393939.github.io/legacy/](https://kaw393939.github.io/legacy/)

Repository remote:

```bash
git@github.com:kaw393939/legacy.git
```

## GitHub Pages Model

The generated first-site output lives in `docs/`. GitHub Actions rebuilds and validates the site before publishing the Pages artifact.

## Workflows

Deployment workflow:

```text
.github/workflows/deploy.yml
```

Triggered by:

- Push to `main`.
- Manual `workflow_dispatch`.

The deployment workflow:

1. Checks out the repository.
2. Installs Python 3.12.
3. Installs `requirements.txt`.
4. Runs `python site.py check --lighthouse`.
5. Uploads `docs/` as the Pages artifact.
6. Deploys with `actions/deploy-pages`.

Preview workflow:

```text
.github/workflows/preview.yml
```

Pull requests run the same quality gate and upload `validation-report.json` plus the generated `docs/` artifact for review.

## Publish Flow

```powershell
git status --short --branch
.\.venv\Scripts\python.exe site.py check --lighthouse
git add -A
git commit -m "Update site"
git push origin main
```

After pushing, check the GitHub Actions run and confirm the Pages deployment completed.

## Important Notes

- GitHub Actions rebuilds output, so source files must be valid even if committed `docs/` looks correct.
- `docs/` should generally be committed with the matching source changes so the repository remains browseable and Pages-compatible.
- Do not commit secrets.
- The static build does not require runtime server infrastructure.
