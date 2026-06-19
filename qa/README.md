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

| Situation | Data Source |
|-----------|-------------|
| CV file in cv/ folder | Parsed from CV via AI |
| No CV file | profile.default.json |
| Local development | profile.default.json |

To update your portfolio:
1. Put your CV in `cv/` folder (PDF or DOCX)
2. Push to main
3. CI automatically parses CV and rebuilds site

## Screenshots

Screenshots are automatically captured after every test run and saved to `qa/screenshots/`. In CI, they are uploaded as build artifacts with 30-day retention.
