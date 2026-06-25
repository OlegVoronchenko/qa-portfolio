#!/usr/bin/env python3
"""
Test Report Generator
=====================

PURPOSE
-------
Reads pytest JSON output and produces test_report.json
that the React app fetches to display live test results
on the portfolio site.

WHY THIS EXISTS
---------------
pytest's native JSON output is too low-level for UI display.
This script enriches each test with:
- Test Case ID (TC-XXX-N)
- Requirement and AC IDs (REQ-XXX, AC-XXX-N)
- Human-readable descriptions and step-by-step explanations
- Code snippets showing what each step does
- Coverage tags (UI, Accessibility, Performance, etc.)
- Locator strategy used (get_by_role, get_by_text, etc.)
- Screenshot embedded as base64

HOW IT WORKS
------------
1. Runs pytest from qa/ directory with --json-report plugin
2. Reads the raw JSON report from qa/reports/raw.json
3. Maps each test to its STEPS_MAP entry for human-readable
   step descriptions, code snippets, and metadata
4. Detects locator strategies (role, text, CSS, JS evaluate)
5. Attaches coverage tags, requirement IDs, and test case IDs
6. Resizes and base64-encodes screenshots for inline display
7. Writes final report to qa/reports/ and dist/ directories

OUTPUT SCHEMA
-------------
{
  "timestamp": "2024-01-15 14:30 UTC",
  "summary": { "passed": 20, "failed": 0, "total": 20, ... },
  "tests": [
    {
      "name": "test_page_loads_with_correct_title",
      "status": "pass",
      "duration_ms": 1234,
      "mark": "smoke",
      "description": "Browser tab title must identify...",
      "steps": [...],
      "locator_strategy": "get_by_role",
      "coverage": ["UI", "SEO", "Page Load"],
      "tc_id": "TC-001-1",
      "req_id": "REQ-001",
      "ac_ids": ["AC-001-1", "AC-001-2", "AC-001-3"],
      "screenshot": "data:image/png;base64,...",
      "error": null
    }
  ]
}

OUTPUT LOCATIONS
----------------
- dist/test_report.json     → deployed to GitHub Pages
- qa/reports/test_report.json → kept as CI artifact
"""

import base64
import json
import os
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
QA_DIR = PROJECT_ROOT / "qa"
REPORTS_DIR = QA_DIR / "reports"
SCREENSHOTS_DIR = QA_DIR / "screenshots"
DIST_DIR = PROJECT_ROOT / "dist"


COVERAGE_MAP = {
    "test_page_loads_with_correct_title": ["UI", "SEO", "Page Load"],
    "test_hero_heading_displays_name": ["UI", "Content", "Typography"],
    "test_navigation_is_present": ["UI", "Navigation", "Accessibility"],
    "test_page_has_no_javascript_errors": ["JavaScript", "Console", "Runtime"],
    "test_react_app_hydrated_successfully": ["React", "Hydration", "SPA"],
    "test_nav_link_is_visible_with_correct_href": ["Navigation", "Links", "Anchors"],
    "test_skills_section_contains_core_stack": ["UI", "Content", "Data Binding"],
    "test_projects_section_has_expected_cards": ["UI", "Content", "Count"],
    "test_contact_section_has_required_channels": ["UI", "Content", "Contact"],
    "test_test_results_section_renders": ["UI", "API", "Data Fetch"],
    "test_mobile_viewport_no_horizontal_scroll": ["Mobile", "Responsive", "Layout"],
    "test_mobile_hero_section_visible": ["Mobile", "Responsive", "Visibility"],
    "test_page_load_time_within_budget": ["Performance", "Timing", "Budget"],
    "test_images_have_alt_text": ["Accessibility", "WCAG", "Images"],
    "test_headings_hierarchy_is_correct": ["Accessibility", "WCAG", "Semantics"],
    "test_assets_load_on_github_pages": ["Deployment", "Network", "Assets"],
    "test_base_path_is_correct": ["Deployment", "Routing", "Base Path"],
    "test_no_console_errors_on_production": ["Deployment", "JavaScript", "Production"],
}

STEPS_MAP = {
    "test_page_loads_with_correct_title": {
        "tc_id": "TC-001-1",
        "req_id": "REQ-001",
        "ac_ids": ["AC-001-1", "AC-001-2", "AC-001-3"],
        "description": "Browser tab title must identify the engineer by name and role",
        "mark": "smoke",
        "steps": [
            {
                "description": "Read page title from browser tab",
                "code": "title = portfolio.get_title()",
            },
            {
                "description": "Capture screenshot before assertions",
                "code": "portfolio.take_screenshot('assert_page_title')",
            },
            {
                "description": "Assert title contains name 'Oleg'",
                "code": "assert PAGE_TITLE.CONTAINS_NAME in title, \\\n    Msg.TITLE_MISSING_NAME.format(title=title)",
            },
            {
                "description": "Assert title contains role 'Automation'",
                "code": "assert PAGE_TITLE.CONTAINS_ROLE in title, \\\n    Msg.TITLE_MISSING_ROLE.format(\n        expected=PAGE_TITLE.CONTAINS_ROLE, actual=title,\n    )",
            },
            {
                "description": "Assert title contains type 'Engineer'",
                "code": "assert PAGE_TITLE.CONTAINS_TYPE in title, \\\n    Msg.TITLE_MISSING_ROLE.format(\n        expected=PAGE_TITLE.CONTAINS_TYPE, actual=title,\n    )",
            },
        ],
    },
    "test_hero_heading_displays_name": {
        "tc_id": "TC-001-2",
        "req_id": "REQ-001",
        "ac_ids": ["AC-001-4"],
        "description": "Main heading on hero section must show the engineer name",
        "mark": "smoke",
        "steps": [
            {
                "description": "Get h1 heading text content",
                "code": "text = portfolio.get_hero_heading_text()",
            },
            {
                "description": "Capture screenshot of hero section",
                "code": "portfolio.take_screenshot('assert_hero_heading')",
            },
            {
                "description": "Assert heading contains 'Oleg'",
                "code": "assert HERO.CONTAINS_NAME in text, Msg.HERO_NAME_MISSING.format(\n    expected=HERO.CONTAINS_NAME, actual=text,\n)",
            },
        ],
    },
    "test_navigation_is_present": {
        "tc_id": "TC-001-3",
        "req_id": "REQ-001",
        "ac_ids": ["AC-001-5"],
        "description": "Navigation bar must be visible when the page loads",
        "mark": "smoke",
        "steps": [
            {
                "description": "Locate navigation landmark by ARIA role",
                "code": "nav = portfolio.navigation\nnav_count = nav.count()",
            },
            {
                "description": "Capture screenshot of navigation",
                "code": "portfolio.take_screenshot('assert_navigation')",
            },
            {
                "description": "Assert navigation is visible",
                "code": "url = portfolio._page.url\nassert nav.is_visible(), Msg.NAV_NOT_VISIBLE.format(\n    url=url, count=nav_count,\n)",
            },
        ],
    },
    "test_page_has_no_javascript_errors": {
        "tc_id": "TC-001-4",
        "req_id": "REQ-001",
        "ac_ids": ["AC-001-6"],
        "description": "No JavaScript errors should appear in the browser console",
        "mark": "smoke",
        "steps": [
            {
                "description": "Attach JavaScript error listener",
                "code": "page.on(\"pageerror\", lambda err: js_errors.append(str(err)))",
            },
            {
                "description": "Navigate to base URL and wait for network idle",
                "code": "page.goto(base_url, wait_until=\"networkidle\")",
            },
            {
                "description": "Assert no JavaScript errors were captured",
                "code": "assert js_errors == [], Msg.JS_ERRORS_FOUND.format(errors=js_errors)",
            },
        ],
    },
    "test_react_app_hydrated_successfully": {
        "tc_id": "TC-001-5",
        "req_id": "REQ-001",
        "ac_ids": ["AC-001-7", "AC-001-8"],
        "description": "React application must render visible content on screen",
        "mark": "smoke",
        "steps": [
            {
                "description": "Count #root child elements",
                "code": "child_count = hydrated_page.evaluate(\n    \"document.querySelector('#root').children.length\"\n)",
            },
            {
                "description": "Get #root innerHTML preview for diagnostics",
                "code": "preview = hydrated_page.evaluate(\n    \"document.querySelector('#root').innerHTML.slice(0, 200)\"\n)\nurl = hydrated_page.url",
            },
            {
                "description": "Assert #root has children",
                "code": "assert child_count > 0, Msg.HYDRATION_FAILED.format(\n    actual=child_count, url=url, preview=preview,\n)",
            },
            {
                "description": "Check for React error boundary",
                "code": "error_boundary = hydrated_page.locator(\n    '[data-reactroot] .error-boundary, #root > [class*=\"error\"]'\n)\nboundary_count = error_boundary.count()",
            },
            {
                "description": "Assert no error boundary rendered",
                "code": "assert boundary_count == 0, Msg.ERROR_BOUNDARY_RENDERED.format(\n    count=boundary_count, url=url,\n)",
            },
        ],
    },
    "test_nav_link_is_visible_with_correct_href[About-#about]": {
        "tc_id": "TC-002-1",
        "req_id": "REQ-002",
        "ac_ids": ["AC-002-1", "AC-002-2"],
        "description": "About link must be visible in navbar and point to #about",
        "mark": "navigation",
        "steps": [
            {
                "description": "Locate nav link 'About'",
                "code": "link = portfolio.nav_link(label)",
            },
            {
                "description": "Assert 'About' link is visible",
                "code": "assert link.is_visible(), Msg.NAV_LINK_NOT_VISIBLE.format(name=label)",
            },
            {
                "description": "Assert 'About' href equals '#about'",
                "code": "actual_href = link.get_attribute(\"href\")\nassert actual_href == href, Msg.NAV_LINK_WRONG_HREF.format(\n    name=label, expected=href, actual=actual_href,\n)",
            },
        ],
    },
    "test_nav_link_is_visible_with_correct_href[Skills-#skills]": {
        "tc_id": "TC-002-2",
        "req_id": "REQ-002",
        "ac_ids": ["AC-002-3", "AC-002-4"],
        "description": "Skills link must be visible in navbar and point to #skills",
        "mark": "navigation",
        "steps": [
            {
                "description": "Locate nav link 'Skills'",
                "code": "link = portfolio.nav_link(label)",
            },
            {
                "description": "Assert 'Skills' link is visible",
                "code": "assert link.is_visible(), Msg.NAV_LINK_NOT_VISIBLE.format(name=label)",
            },
            {
                "description": "Assert 'Skills' href equals '#skills'",
                "code": "actual_href = link.get_attribute(\"href\")\nassert actual_href == href, Msg.NAV_LINK_WRONG_HREF.format(\n    name=label, expected=href, actual=actual_href,\n)",
            },
        ],
    },
    "test_nav_link_is_visible_with_correct_href[Projects-#projects]": {
        "tc_id": "TC-002-3",
        "req_id": "REQ-002",
        "ac_ids": ["AC-002-5", "AC-002-6"],
        "description": "Projects link must be visible in navbar and point to #projects",
        "mark": "navigation",
        "steps": [
            {
                "description": "Locate nav link 'Projects'",
                "code": "link = portfolio.nav_link(label)",
            },
            {
                "description": "Assert 'Projects' link is visible",
                "code": "assert link.is_visible(), Msg.NAV_LINK_NOT_VISIBLE.format(name=label)",
            },
            {
                "description": "Assert 'Projects' href equals '#projects'",
                "code": "actual_href = link.get_attribute(\"href\")\nassert actual_href == href, Msg.NAV_LINK_WRONG_HREF.format(\n    name=label, expected=href, actual=actual_href,\n)",
            },
        ],
    },
    "test_nav_link_is_visible_with_correct_href[Contact-#contact]": {
        "tc_id": "TC-002-4",
        "req_id": "REQ-002",
        "ac_ids": ["AC-002-7", "AC-002-8"],
        "description": "Contact link must be visible in navbar and point to #contact",
        "mark": "navigation",
        "steps": [
            {
                "description": "Locate nav link 'Contact'",
                "code": "link = portfolio.nav_link(label)",
            },
            {
                "description": "Assert 'Contact' link is visible",
                "code": "assert link.is_visible(), Msg.NAV_LINK_NOT_VISIBLE.format(name=label)",
            },
            {
                "description": "Assert 'Contact' href equals '#contact'",
                "code": "actual_href = link.get_attribute(\"href\")\nassert actual_href == href, Msg.NAV_LINK_WRONG_HREF.format(\n    name=label, expected=href, actual=actual_href,\n)",
            },
        ],
    },
    "test_skills_section_contains_core_stack[Python]": {
        "tc_id": "TC-003-1",
        "req_id": "REQ-003",
        "ac_ids": ["AC-003-1"],
        "description": "Python must appear as a visible skill tag in Skills section",
        "mark": "content",
        "steps": [
            {
                "description": "Locate skill tag with exact text 'Python'",
                "code": "tag = portfolio.skill_text(skill)",
            },
            {
                "description": "Capture screenshot of skills section",
                "code": "portfolio.take_screenshot(f\"assert_skill_{skill.lower()}\")",
            },
            {
                "description": "Assert 'Python' tag is visible",
                "code": "assert tag.first.is_visible(), Msg.SKILL_NOT_VISIBLE.format(name=skill)",
            },
        ],
    },
    "test_skills_section_contains_core_stack[Playwright]": {
        "tc_id": "TC-003-2",
        "req_id": "REQ-003",
        "ac_ids": ["AC-003-2"],
        "description": "Playwright must appear as a visible skill tag in Skills section",
        "mark": "content",
        "steps": [
            {
                "description": "Locate skill tag with exact text 'Playwright'",
                "code": "tag = portfolio.skill_text(skill)",
            },
            {
                "description": "Capture screenshot of skills section",
                "code": "portfolio.take_screenshot(f\"assert_skill_{skill.lower()}\")",
            },
            {
                "description": "Assert 'Playwright' tag is visible",
                "code": "assert tag.first.is_visible(), Msg.SKILL_NOT_VISIBLE.format(name=skill)",
            },
        ],
    },
    "test_skills_section_contains_core_stack[pytest]": {
        "tc_id": "TC-003-3",
        "req_id": "REQ-003",
        "ac_ids": ["AC-003-3"],
        "description": "pytest must appear as a visible skill tag in Skills section",
        "mark": "content",
        "steps": [
            {
                "description": "Locate skill tag with exact text 'pytest'",
                "code": "tag = portfolio.skill_text(skill)",
            },
            {
                "description": "Capture screenshot of skills section",
                "code": "portfolio.take_screenshot(f\"assert_skill_{skill.lower()}\")",
            },
            {
                "description": "Assert 'pytest' tag is visible",
                "code": "assert tag.first.is_visible(), Msg.SKILL_NOT_VISIBLE.format(name=skill)",
            },
        ],
    },
    "test_projects_section_has_expected_cards": {
        "tc_id": "TC-003-4",
        "req_id": "REQ-003",
        "ac_ids": ["AC-003-4"],
        "description": "Projects section must display exactly 3 project cards",
        "mark": "content",
        "steps": [
            {
                "description": "Count project cards with role='article'",
                "code": "count = portfolio.count_project_cards()",
            },
            {
                "description": "Capture screenshot of project cards",
                "code": "portfolio.take_screenshot('assert_project_cards')",
            },
            {
                "description": "Assert project card count matches expected",
                "code": "assert count == COUNTS.PROJECT_CARDS, Msg.WRONG_PROJECT_COUNT.format(\n    expected=COUNTS.PROJECT_CARDS, actual=count,\n)",
            },
        ],
    },
    "test_contact_section_has_required_channels": {
        "tc_id": "TC-003-5",
        "req_id": "REQ-003",
        "ac_ids": ["AC-003-5"],
        "description": "Contact section must display all required contact channels",
        "mark": "content",
        "steps": [
            {
                "description": "Count contact links with role='link'",
                "code": "count = portfolio.count_contact_links()",
            },
            {
                "description": "Capture screenshot of contact section",
                "code": "portfolio.take_screenshot('assert_contact_channels')",
            },
            {
                "description": "Assert contact link count matches expected",
                "code": "assert count == COUNTS.CONTACT_LINKS, Msg.WRONG_CONTACT_COUNT.format(\n    expected=COUNTS.CONTACT_LINKS, actual=count,\n)",
            },
        ],
    },
    "test_test_results_section_renders": {
        "tc_id": "TC-003-6",
        "req_id": "REQ-003",
        "ac_ids": ["AC-003-6", "AC-003-7", "AC-003-8"],
        "description": "Test results section must show loaded data from test_report.json",
        "mark": "content",
        "steps": [
            {
                "description": "Open the portfolio page",
                "code": "portfolio = PortfolioPage(page, base_url)\nportfolio.navigate()",
            },
            {
                "description": "Locate the test results section",
                "code": "section = page.locator(\"#test-results\")\nassert section.is_visible(), (\n    \"Test results section #test-results is not visible on page\"\n)",
            },
            {
                "description": "Wait for test data to load from test_report.json",
                "code": "page.wait_for_timeout(2000)",
            },
            {
                "description": "Verify summary cards show numeric values",
                "code": "summary_cards = section.locator(\n    \"[class*='summary'], [class*='stat'], [class*='count']\"\n)\ncard_count = summary_cards.count()\nsection_text = section.inner_text()\nhas_numbers = any(\n    char.isdigit() for char in section_text\n)\nassert has_numbers, (\n    f\"Test results section has no numeric values. \"\n    f\"Section text: '{section_text[:200]}'. \"\n    f\"Likely test_report.json failed to load.\"\n)",
            },
            {
                "description": "Verify at least one test row is rendered",
                "code": "row_count = page.evaluate(\"\"\"\n    () => {\n        const section = document.querySelector('#test-results');\n        if (!section) return 0;\n        return section.querySelectorAll(\n            'div[class*=\"cursor-pointer\"]'\n        ).length;\n    }\n\"\"\")\nassert row_count > 0, (\n    f\"No test rows found in results section. \"\n    f\"Expected at least 1 row from test_report.json. \"\n    f\"Found {row_count} rows. \"\n    f\"Check that test_report.json is deployed to dist/ \"\n    f\"and fetch URL uses import.meta.env.BASE_URL prefix.\"\n)",
            },
            {
                "description": "Take screenshot showing test results",
                "code": "from datetime import datetime\nts = datetime.now().strftime(\"%Y%m%d_%H%M%S\")\npage.screenshot(\n    path=f\"screenshots/assert_test_results_{ts}.png\",\n    full_page=False\n)",
            },
        ],
    },
    "test_mobile_viewport_no_horizontal_scroll": {
        "tc_id": "TC-004-1",
        "req_id": "REQ-004",
        "ac_ids": ["AC-004-1"],
        "description": "No horizontal overflow at 390x844 mobile viewport",
        "mark": "responsive",
        "environment_override": {"viewport": "390x844 (iPhone 14)"},
        "steps": [
            {
                "description": "Wait for mobile page content to be ready",
                "code": "mobile_portfolio.wait_for_content_ready()",
            },
            {
                "description": "Measure document scroll width",
                "code": "scroll_w = mobile_portfolio.get_scroll_width()",
            },
            {
                "description": "Get viewport width (390px iPhone 14)",
                "code": "viewport_w = mobile_portfolio.get_viewport_width()",
            },
            {
                "description": "Capture high-quality mobile screenshot",
                "code": "mobile_portfolio.take_mobile_screenshot(\n    \"no_horizontal_scroll\", full_page=True\n)",
            },
            {
                "description": "Assert scroll_w <= viewport_w (no overflow)",
                "code": "assert scroll_w <= viewport_w, \\\n    Msg.HORIZONTAL_OVERFLOW.format(\n        scroll_w=scroll_w, viewport_w=viewport_w,\n    )",
            },
        ],
    },
    "test_mobile_hero_section_visible": {
        "tc_id": "TC-004-2",
        "req_id": "REQ-004",
        "ac_ids": ["AC-004-2"],
        "description": "Hero h1 must be visible on 390px mobile viewport",
        "mark": "responsive",
        "environment_override": {"viewport": "390x844 (iPhone 14)"},
        "steps": [
            {
                "description": "Wait for mobile page content to be ready",
                "code": "mobile_portfolio.wait_for_content_ready()",
            },
            {
                "description": "Capture high-quality mobile hero screenshot",
                "code": "mobile_portfolio.take_mobile_screenshot(\n    \"hero_visible\", full_page=False\n)",
            },
            {
                "description": "Assert hero heading visible at mobile width",
                "code": "assert mobile_portfolio.hero_heading.is_visible(), \\\n    Msg.MOBILE_HERO_NOT_VISIBLE.format(\n        width=CONFIG.mobile_width,\n    )",
            },
        ],
    },
    "test_page_load_time_within_budget": {
        "tc_id": "TC-005-1",
        "req_id": "REQ-005",
        "ac_ids": ["AC-005-1"],
        "description": "Page must finish loading in under 3000ms",
        "mark": "performance",
        "steps": [
            {
                "description": "Navigate to base URL and wait for load event",
                "code": "page.goto(base_url, wait_until=\"load\")",
            },
            {
                "description": "Measure load time via Navigation Timing API",
                "code": "load_ms = page.evaluate(\n    \"performance.timing.loadEventEnd \"\n    \"- performance.timing.navigationStart\"\n)",
            },
            {
                "description": "Assert load time is under budget",
                "code": "assert load_ms < PERF.MAX_LOAD_TIME_MS, Msg.SLOW_PAGE_LOAD.format(\n    actual=load_ms, budget=PERF.MAX_LOAD_TIME_MS,\n)",
            },
        ],
    },
    "test_images_have_alt_text": {
        "tc_id": "TC-006-1",
        "req_id": "REQ-006",
        "ac_ids": ["AC-006-1"],
        "description": "Every image must have descriptive alt text",
        "mark": "accessibility",
        "steps": [
            {
                "description": "Open the portfolio page",
                "code": "portfolio = PortfolioPage(page, base_url)\nportfolio.navigate()",
            },
            {
                "description": "Evaluate all images via JavaScript",
                "code": "violations: list[dict] = page.evaluate(\"\"\"\n    () => Array.from(document.querySelectorAll('img'))\n        .filter(img =>\n            img.getAttribute('aria-hidden') !== 'true'\n            && (!img.alt || img.alt.trim() === '')\n        )\n        .map((img, i) => ({\n            index: i,\n            src: (img.src || '').slice(0, 80)\n        }))\n\"\"\")",
            },
            {
                "description": "Take screenshot at assertion point",
                "code": "from datetime import datetime\nts = datetime.now().strftime(\"%Y%m%d_%H%M%S\")\npage.screenshot(\n    path=f\"screenshots/assert_images_alt_{ts}.png\",\n    full_page=False\n)",
            },
            {
                "description": "Verify no images are missing alt text",
                "code": "assert violations == [], (\n    f\"Found {len(violations)} image(s) without alt text: \"\n    + str(violations)\n)",
            },
        ],
    },
    "test_headings_hierarchy_is_correct": {
        "tc_id": "TC-006-2",
        "req_id": "REQ-006",
        "ac_ids": ["AC-006-2", "AC-006-3", "AC-006-4"],
        "description": "Heading levels must follow correct order without gaps",
        "mark": "accessibility",
        "steps": [
            {
                "description": "Collect all heading elements and their tag names",
                "code": "headings = portfolio.all_headings.all()\ntags = [h.evaluate(\"el => el.tagName.toLowerCase()\") for h in headings]",
            },
            {
                "description": "Assert exactly 1 h1 heading exists",
                "code": "h1_count = tags.count(\"h1\")\nassert h1_count == COUNTS.H1_HEADINGS, Msg.WRONG_H1_COUNT.format(\n    expected=COUNTS.H1_HEADINGS, actual=h1_count,\n)",
            },
            {
                "description": "Assert h1 appears before first h2",
                "code": "h1_idx = tags.index(\"h1\")\nh2_indices = [i for i, t in enumerate(tags) if t == \"h2\"]\nif h2_indices:\n    assert h1_idx < h2_indices[0], Msg.H1_NOT_FIRST",
            },
            {
                "description": "Assert no heading levels are skipped",
                "code": "levels = [int(t[1]) for t in tags]\nfor i in range(1, len(levels)):\n    gap = levels[i] - levels[i - 1]\n    assert gap <= 1, Msg.HEADING_LEVEL_SKIPPED.format(\n        prev=levels[i - 1], next=levels[i], pos=i,\n    )",
            },
        ],
    },
    "test_assets_load_on_github_pages": {
        "tc_id": "TC-007-1",
        "req_id": "REQ-007",
        "ac_ids": ["AC-007-1", "AC-007-2", "AC-007-3"],
        "description": "All CSS and JS files must load on production site",
        "mark": "deployment",
        "steps": [
            {
                "description": "Attach network response monitor for 404s",
                "code": "deploy_page.on(\n    \"response\",\n    lambda r: failed_requests.append(r.url)\n    if r.status == 404\n    else None,\n)",
            },
            {
                "description": "Navigate to production URL and wait for network idle",
                "code": "deploy_page.goto(\n    _PAGES_URL,\n    wait_until=\"networkidle\",\n    timeout=CONFIG.timeout_navigation,\n)",
            },
            {
                "description": "Filter asset 404s from captured responses",
                "code": "asset_404s = [\n    url\n    for url in failed_requests\n    if any(ext in url for ext in DEPLOYMENT.CHECKED_ASSET_EXTENSIONS)\n    and not any(\n        exc in url for exc in DEPLOYMENT.EXCLUDED_404_PATHS\n    )\n]",
            },
            {
                "description": "Assert no asset 404s",
                "code": "assert not asset_404s, Msg.ASSET_404.format(urls=asset_404s)",
            },
            {
                "description": "Verify navigation landmark exists and is visible",
                "code": "nav = deploy_page.get_by_role(\"navigation\")\nnav_count = nav.count()\nassert nav_count > 0, Msg.DEPLOY_NAV_NOT_FOUND.format(\n    url=_PAGES_URL, count=nav_count,\n)\nassert nav.is_visible(), Msg.DEPLOY_NAV_HIDDEN.format(\n    count=nav_count, url=_PAGES_URL,\n)",
            },
            {
                "description": "Verify h1 heading exists with content",
                "code": "h1 = deploy_page.get_by_role(\"heading\", level=1)\nh1_count = h1.count()\nassert h1_count == 1, Msg.DEPLOY_H1_WRONG_COUNT.format(\n    actual=h1_count, url=_PAGES_URL,\n)\nh1_text = h1.inner_text()\nassert h1_text.strip(), Msg.DEPLOY_H1_EMPTY.format(url=_PAGES_URL)",
            },
        ],
    },
    "test_base_path_is_correct": {
        "tc_id": "TC-007-2",
        "req_id": "REQ-007",
        "ac_ids": ["AC-007-4"],
        "description": "Asset paths must include the /qa-portfolio/ prefix",
        "mark": "deployment",
        "steps": [
            {
                "description": "Navigate to production URL",
                "code": "deploy_page.goto(_PAGES_URL, wait_until=\"networkidle\")",
            },
            {
                "description": "Scan script and link elements for wrong base path",
                "code": "bad_paths = deploy_page.evaluate(\"\"\"() => {\n    const bad = [];\n    document.querySelectorAll('script[src], link[href]').forEach(el => {\n        const val = el.getAttribute('src') || el.getAttribute('href');\n        if (val && val.startsWith('/assets/')) {\n            bad.push(val);\n        }\n    });\n    return bad;\n}\"\"\")",
            },
            {
                "description": "Assert no '/assets/' paths found",
                "code": "assert bad_paths == [], Msg.DEPLOY_WRONG_BASE_PATH.format(\n    paths=bad_paths,\n)",
            },
        ],
    },
    "test_no_console_errors_on_production": {
        "tc_id": "TC-007-3",
        "req_id": "REQ-007",
        "ac_ids": ["AC-007-5"],
        "description": "No JavaScript errors on the production site",
        "mark": "deployment",
        "steps": [
            {
                "description": "Attach JavaScript error listener",
                "code": "deploy_page.on(\"pageerror\", lambda err: js_errors.append(str(err)))",
            },
            {
                "description": "Navigate to production URL and wait for network idle",
                "code": "deploy_page.goto(_PAGES_URL, wait_until=\"networkidle\")",
            },
            {
                "description": "Assert no JS errors",
                "code": "assert js_errors == [], Msg.DEPLOY_JS_ERRORS.format(errors=js_errors)",
            },
        ],
    },
}


def get_steps_for_test(test_name):
    """Look up test metadata from STEPS_MAP. Falls back to generic only if not found."""
    if test_name in STEPS_MAP:
        return STEPS_MAP[test_name]
    return {
        "description": f"Verify {test_name.replace('test_', '').replace('_', ' ')}",
        "mark": "unknown",
        "steps": [
            {"description": f"Execute {test_name}", "code": ""},
            {"description": "Assert expected result", "code": ""},
        ],
    }


def filter_phantom_steps(steps: list[dict]) -> list[dict]:
    """Remove steps whose code is only a comment."""
    filtered = []
    for step in steps:
        code = step.get('code', '').strip()
        if not code:
            continue
        lines = [l.strip() for l in code.split('\n') if l.strip()]
        if all(l.startswith('#') for l in lines):
            continue
        filtered.append(step)
    return filtered


def build_steps(step_defs, test_passed):
    """Build step objects; if test failed, mark the last step as failed."""
    steps = []
    for i, step in enumerate(step_defs):
        is_last = i == len(step_defs) - 1
        status = "fail" if (not test_passed and is_last) else "pass"
        steps.append({
            "name": step["description"],
            "code": step.get("code", ""),
            "status": status,
        })
    return steps


POM_ROLE_METHODS = (
    "portfolio.nav_link", "portfolio.navigation", "portfolio.hero_heading",
    "portfolio.skill_text", "portfolio.get_hero_heading_text",
    "portfolio.get_title", "portfolio.all_headings",
    "portfolio.count_project_cards", "portfolio.count_contact_links",
    "mobile_portfolio.", "deploy_page.get_by_role",
)


def detect_locator_strategy(steps):
    """Detect the primary locator strategy used in a test's step code."""
    all_code = " ".join(s.get("code", "") for s in steps)
    if "get_by_role" in all_code or any(m in all_code for m in POM_ROLE_METHODS):
        return "get_by_role"
    if "get_by_text" in all_code:
        return "get_by_text"
    if "get_by_label" in all_code:
        return "get_by_label"
    if "get_by_placeholder" in all_code:
        return "get_by_placeholder"
    if "get_by_alt_text" in all_code:
        return "get_by_alt_text"
    if "data-testid" in all_code:
        return "data-testid"
    if "locator(" in all_code or "evaluate(" in all_code:
        return "css-selector"
    return "evaluate"


def get_coverage_tags(test_name):
    """Get coverage tags for a test, matching parametrized tests by prefix."""
    if test_name in COVERAGE_MAP:
        return COVERAGE_MAP[test_name]
    base = test_name.split("[")[0]
    if base in COVERAGE_MAP:
        return COVERAGE_MAP[base]
    return ["UI"]


_MOBILE_SCREENSHOT_MAP = {
    "test_mobile_hero_section_visible": "mobile_hero_visible",
    "test_mobile_viewport_no_horizontal_scroll": "mobile_no_horizontal_scroll",
}


def _encode_screenshot(path: Path) -> str:
    """Encode screenshot as base64, downscaling large images."""
    size_kb = path.stat().st_size / 1024

    if size_kb < 500:
        try:
            from PIL import Image
            from io import BytesIO
            img = Image.open(path)
            if img.width > 800:
                ratio = 800 / img.width
                img = img.resize((800, int(img.height * ratio)), Image.LANCZOS)
            buf = BytesIO()
            img.save(buf, format="PNG", optimize=True)
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            return f"data:image/png;base64,{b64}"
        except ImportError:
            pass
        b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
        return f"data:image/png;base64,{b64}"

    try:
        from PIL import Image
        from io import BytesIO
        img = Image.open(path)
        if img.width > 800:
            ratio = 800 / img.width
            img = img.resize((800, int(img.height * ratio)), Image.LANCZOS)
        buf = BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=80)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{b64}"
    except ImportError:
        b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
        return f"data:image/png;base64,{b64}"


def find_screenshot_for_test(test_name):
    """Find the most recent screenshot for a test and return as base64 data URI."""
    if not SCREENSHOTS_DIR.exists():
        return None

    base_name = test_name.split("[")[0]
    safe_name = re.sub(r"[^\w-]", "_", test_name)
    short = re.sub(r"[^\w-]", "_", base_name.replace("test_", ""))

    patterns = [
        f"assert_{short}*.png",
        f"assert_{'_'.join(short.split('_')[:2])}*.png",
    ]

    if base_name in _MOBILE_SCREENSHOT_MAP:
        patterns.insert(0, f"{_MOBILE_SCREENSHOT_MAP[base_name]}_*.png")

    patterns.append(f"{safe_name}_*.png")

    for pattern in patterns:
        matches = list(SCREENSHOTS_DIR.glob(pattern))
        if matches:
            latest = max(matches, key=lambda p: p.stat().st_mtime)
            try:
                return _encode_screenshot(latest)
            except Exception:
                return None

    return None


def _get_pip_version(package: str) -> str:
    """Get installed version of a pip package."""
    try:
        import importlib.metadata
        return importlib.metadata.version(package)
    except Exception:
        return "unknown"


def _get_chromium_version() -> str:
    """Get Playwright Chromium revision from its install path."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            path = p.chromium.executable_path
            for segment in path.split("/"):
                if segment.startswith("chromium-"):
                    return segment.replace("chromium-", "rev ")
            return "latest"
    except Exception:
        return "latest"


def collect_environment() -> dict:
    """Collect real environment metadata from the current run.

    Values come from platform module, installed packages,
    and CI environment variables — nothing is hardcoded.
    """
    return {
        "os": platform.system(),
        "os_version": platform.release(),
        "os_machine": platform.machine(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),

        "playwright_version": _get_pip_version("playwright"),
        "pytest_version": _get_pip_version("pytest"),
        "pytest_playwright_version": _get_pip_version("pytest-playwright"),

        "browser": "Chromium",
        "browser_version": _get_chromium_version(),

        "ci": "GitHub Actions" if os.getenv("CI") else "Local",
        "runner_os": os.getenv("RUNNER_OS", ""),
        "runner_name": os.getenv("RUNNER_NAME", ""),
        "runner_arch": os.getenv("RUNNER_ARCH", ""),

        "github_sha": (os.getenv("GITHUB_SHA") or "")[:7],
        "github_sha_full": os.getenv("GITHUB_SHA", ""),
        "github_ref": os.getenv("GITHUB_REF_NAME", "local"),
        "github_run_id": os.getenv("GITHUB_RUN_ID", ""),
        "github_run_number": os.getenv("GITHUB_RUN_NUMBER", ""),
        "github_actor": os.getenv("GITHUB_ACTOR", ""),
        "github_commit_url": (
            f"https://github.com/OlegVoronchenko/qa-portfolio"
            f"/commit/{os.getenv('GITHUB_SHA', '')}"
            if os.getenv("GITHUB_SHA") else ""
        ),
        "github_run_url": (
            f"https://github.com/OlegVoronchenko/qa-portfolio"
            f"/actions/runs/{os.getenv('GITHUB_RUN_ID', '')}"
            if os.getenv("GITHUB_RUN_ID") else ""
        ),

        "timestamp": datetime.now(timezone.utc).isoformat(),
        "timestamp_unix": int(datetime.now(timezone.utc).timestamp()),

        "viewport_default": "1280x720",
        "viewport_mobile": "390x844 (iPhone 14)",
        "base_url": os.getenv("BASE_URL", "http://localhost:8080"),
    }


def run_tests():
    """Run pytest from qa/ directory and save raw JSON report."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/", "-v",
            "--json-report", "--json-report-file", str(REPORTS_DIR / "raw.json"),
        ],
        cwd=str(QA_DIR),
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode


def parse_report():
    raw_path = REPORTS_DIR / "raw.json"
    if not raw_path.exists():
        print(f"ERROR: {raw_path} not found — did pytest run?")
        sys.exit(1)

    raw = json.loads(raw_path.read_text())
    tests = []
    total_duration_ms = 0

    for t in raw.get("tests", []):
        nodeid = t.get("nodeid", "")
        name = nodeid.split("::")[-1] if "::" in nodeid else nodeid
        outcome = t.get("outcome", "unknown")
        if outcome == "skipped":
            continue
        duration = t.get("call", {}).get("duration", 0)
        duration_ms = round(duration * 1000)
        total_duration_ms += duration_ms
        test_passed = outcome == "passed"

        mapped = get_steps_for_test(name)
        description = mapped["description"]
        mark = mapped["mark"]
        clean_steps = filter_phantom_steps(mapped["steps"])
        steps = build_steps(clean_steps, test_passed)

        error_msg = None
        if not test_passed:
            crash = t.get("call", {}).get("crash", {})
            error_msg = crash.get("message", "Test failed")

        tests.append({
            "name": name,
            "status": "pass" if test_passed else "fail",
            "duration_ms": duration_ms,
            "mark": mark,
            "description": description,
            "steps": steps,
            "locator_strategy": detect_locator_strategy(clean_steps),
            "coverage": get_coverage_tags(name),
            "tc_id": mapped.get("tc_id", "TC-???"),
            "req_id": mapped.get("req_id"),
            "ac_ids": mapped.get("ac_ids", []),
            "screenshot": find_screenshot_for_test(name),
            "error": error_msg,
            "environment_override": mapped.get("environment_override"),
        })

    report = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "summary": {
            "passed": sum(1 for t in tests if t["status"] == "pass"),
            "failed": sum(1 for t in tests if t["status"] != "pass"),
            "total": len(tests),
            "duration_ms": total_duration_ms,
        },
        "environment": collect_environment(),
        "tests": tests,
    }
    return report


def main():
    """Read pytest JSON output and generate enriched test_report.json.

    Does NOT run pytest — that must happen in a separate step.
    For local development, run pytest first:
        cd qa && python -m pytest tests/ -v --json-report --json-report-file=reports/raw.json
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    raw_path = REPORTS_DIR / "raw.json"
    if not raw_path.exists():
        print(f"ERROR: {raw_path} not found")
        print("Run pytest first with:")
        print("  cd qa && python -m pytest tests/ -v "
              "--json-report --json-report-file=reports/raw.json")
        sys.exit(1)

    print("Generating report...")
    report = parse_report()

    destinations = [REPORTS_DIR / "test_report.json"]
    if DIST_DIR.exists():
        destinations.append(DIST_DIR / "test_report.json")

    for dest in destinations:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(report, indent=2))
        print(f"  -> {dest}")

    print(f"\nDone: {report['summary']['passed']}/{report['summary']['total']} passed")


if __name__ == "__main__":
    main()
