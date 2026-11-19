# QA Module — Independent Test Suite

This module is fully independent. Clone only this folder and run tests without installing React or Node.js.

## Setup

```bash
cd qa/
pip install -r requirements.txt
playwright install chromium
```

## Run against local site

```bash
# First build the site (from project root):
npm run build

# Then run tests:
BASE_URL=http://localhost:8080 pytest tests/ -v
```

## Run against production

```bash
GITHUB_PAGES_URL=https://olegvoronchenko.github.io/qa-portfolio/ pytest tests/ -v
```

## Profile Data Source

`src/data/profile.json` is the single, Git-tracked, canonical source
of professional profile data — used identically by local development,
automated tests, CI, and production builds. There is no separate
fallback/default file; see `scripts/validate_profile.py`.

| Situation | Behavior |
|-----------|----------|
| CV file in `cv/` folder | `scripts/parse_cv.py` (regex-based, local-only — no external API) re-parses it and updates `profile.json` in place |
| No CV file in `cv/` folder | `profile.json` is used exactly as committed |
| Local development | Same `profile.json`, read directly — no copy/fallback step |

To update your portfolio:
1. Put your CV in `cv/` folder (PDF or DOCX)
2. Push to main
3. CI automatically re-parses the CV and updates `profile.json`

## Screenshots

Screenshots are automatically captured after every test run and saved to `qa/screenshots/`. In CI, they are uploaded as build artifacts with 30-day retention.
