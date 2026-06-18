# QA Automation Engineer — Portfolio

Personal portfolio website with an integrated Playwright test suite demonstrating QA automation skills.

## Quick Start

```bash
# Install dependencies
pip3 install -r requirements.txt

# Install Playwright browser
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
├── site/
│   ├── index.html          # Portfolio website (single-page)
│   └── test_report.json    # Generated test results
├── tests/
│   ├── pages/
│   │   └── portfolio_page.py   # Page Object Model
│   ├── conftest.py             # Fixtures (HTTP server, browser, mobile)
│   └── test_portfolio.py       # 15 Playwright tests
├── scripts/
│   ├── generate_report.py      # Pytest → JSON report generator
│   └── serve_and_test.sh       # One-command runner
├── reports/                    # Generated reports directory
├── .github/workflows/
│   └── test-and-deploy.yml     # CI/CD pipeline
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Python dependencies
└── README.md
```

## Test Suite

| # | Test | What it verifies |
|---|------|-----------------|
| 1 | `test_page_loads_and_title_correct` | Page loads, title contains name and QA |
| 2 | `test_hero_section_visible` | Hero section renders |
| 3 | `test_hero_title_contains_qa` | Hero heading contains name |
| 4 | `test_nav_link_about_exists` | About nav link present |
| 5 | `test_nav_link_skills_exists` | Skills nav link present |
| 6 | `test_nav_link_projects_exists` | Projects nav link present |
| 7 | `test_nav_link_contact_exists` | Contact nav link present |
| 8 | `test_skills_section_has_python_tag` | Python skill tag visible |
| 9 | `test_skills_section_has_playwright_tag` | Playwright skill tag visible |
| 10 | `test_skills_section_has_pytest_tag` | Pytest skill tag visible |
| 11 | `test_projects_section_has_three_cards` | Exactly 3 project cards |
| 12 | `test_contact_section_has_four_items` | Exactly 4 contact items |
| 13 | `test_mobile_no_horizontal_overflow` | No horizontal scroll on 390×844 |
| 14 | `test_page_loads_under_3_seconds` | Page loads in under 3 seconds |
| 15 | `test_no_broken_images` | All images load successfully |

## Deploy to GitHub Pages

1. Push this repo to GitHub
2. Go to **Settings → Pages → Source** and select `gh-pages` branch
3. The GitHub Actions workflow automatically:
   - Runs all 15 tests
   - Generates the test report
   - Deploys `site/` to GitHub Pages

Your portfolio will be live at `https://<username>.github.io/<repo-name>/`.

## Tech Stack

- **Site**: HTML, CSS, vanilla JavaScript
- **Tests**: Python, Playwright, Pytest
- **CI/CD**: GitHub Actions
- **Reporting**: pytest-json-report → custom JSON
