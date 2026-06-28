# GitHub Pages Deployment Guide

This repository is set up to deploy the generated static site to GitHub Pages.

## Repository

- GitHub repo: `git@github.com:kaw393939/legacy.git`
- Branch: `main`
- Build output: `docs/`
- Custom domain: `www.legacydefenders.com`
- CNAME source: `static/CNAME`
- Generated CNAME: `docs/CNAME`

## Recommended GitHub Pages Setting

Use GitHub Actions as the Pages source:

1. Open the repository on GitHub.
2. Go to `Settings` -> `Pages`.
3. Under `Build and deployment`, set `Source` to `GitHub Actions`.
4. Push to `main`.

The workflow at `.github/workflows/deploy.yml` will:

1. Install Python dependencies from `requirements.txt`.
2. Run `python build.py --validate`.
3. Upload the generated `docs/` folder as a Pages artifact.
4. Deploy it to GitHub Pages.

## Local Build

```bash
python build.py --validate
```

The generated site is written to `docs/`.

## Custom Domain DNS

For `www.legacydefenders.com`, create a CNAME record:

```text
Type: CNAME
Name: www
Value: kaw393939.github.io
```

If the apex domain `legacydefenders.com` should also resolve to GitHub Pages, add these A records:

```text
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

GitHub may take time to provision HTTPS after the first successful deployment.

## Deployment Commands

```bash
python build.py --validate
git add -A
git commit -m "Deploy Legacy Defenders site"
git push origin main
```
