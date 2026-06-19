# QA Automation Engineer — Portfolio

React + Vite + Tailwind portfolio website with a comprehensive Playwright test suite demonstrating QA automation best practices.

## Quick Start

```bash
# Install Node dependencies and build
npm install
npm run build

# Install Python test dependencies
pip3 install -r requirements.txt
playwright install chromium

# Run all tests
pytest tests/ -v

# Generate test report (JSON)
python scripts/generate_report.py
```

Or use the all-in-one script:

```bash
bash scripts/serve_and_test.sh
```

## Project Structure

```
qa-portfolio/
├── src/
│   ├── components/             # React components (8 sections)
│   ├── App.jsx                 # Root component
│   ├── main.jsx                # Entry point
│   └── index.css               # Tailwind + custom styles
├── tests/
│   ├── pages/
│   │   └── portfolio_page.py   # Page Object Model (role-based locators)
│   ├── conftest.py             # Fixtures (HTTP server, browser, mobile)
│   ├── test_portfolio.py       # 15 tests (smoke, content, a11y, perf)
│   └── test_deployment.py      # 3 deployment verification tests (CI only)
├── scripts/
│   ├── generate_report.py      # pytest → JSON report generator
│   └── serve_and_test.sh       # One-command runner
├── .github/workflows/
│   └── test-and-deploy.yml     # CI/CD pipeline
├── vite.config.js              # Vite config (env-driven base path)
├── tailwind.config.js
├── package.json
├── pytest.ini                  # Pytest config with custom marks
├── requirements.txt
└── README.md
```

## Test Strategy

The test suite has two layers:

### Local tests (`tests/test_portfolio.py`)
Run against a built `dist/` folder served on `localhost:8080`. These verify the app works correctly regardless of deployment target.

| Category | Tests | What they verify |
|----------|-------|-----------------|
| **Smoke** (5) | Title, hero heading, navigation, JS errors, React hydration | Critical path — app loads and renders |
| **Navigation** (4) | About, Skills, Projects, Contact links | Nav links visible with correct hrefs |
| **Content** (6) | Skills (Python/Playwright/Pytest), 3 project cards, 4 contacts, test results | Section content completeness |
| **Responsive** (2) | No horizontal scroll, hero visible at 390px | Mobile viewport correctness |
| **Performance** (1) | Page load < 3 seconds | Load time via Performance API |
| **Accessibility** (2) | All images have alt text, heading hierarchy correct | Semantic HTML quality |

### Deployment tests (`tests/test_deployment.py`)
Run only in CI after deploying to GitHub Pages. Skipped locally when `GITHUB_PAGES_URL` is not set.

| Test | What it verifies |
|------|-----------------|
| `test_assets_load_on_github_pages` | No 404s on assets, React renders, correct title |
| `test_base_path_is_correct` | Asset paths use `/repo-name/assets/`, not `/assets/` |
| `test_no_console_errors_on_production` | No uncaught JS errors in production |

This two-layer approach ensures both **local correctness** and **production deployment validity**.

## Deploy to GitHub Pages

1. Push this repo to GitHub
2. Go to **Settings → Pages → Source** and select `gh-pages` branch
3. The GitHub Actions workflow automatically:
   - Builds the React app with the correct base path
   - Runs all 20 local tests
   - Generates the test report
   - Deploys `dist/` to GitHub Pages
   - Runs 3 deployment verification tests against the live URL

Your portfolio will be live at `https://<username>.github.io/<repo-name>/`.

## Tech Stack

- **Site**: React 18, Vite 5, Tailwind CSS 3, Lucide React
- **Tests**: Python, Playwright, pytest (Page Object Model)
- **CI/CD**: GitHub Actions
- **Reporting**: pytest-json-report → custom JSON
