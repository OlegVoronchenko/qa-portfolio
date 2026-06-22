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


TC_ID_MAP = {
    "test_page_loads_with_correct_title": "TC-001-1",
    "test_hero_heading_displays_name": "TC-001-2",
    "test_navigation_is_present": "TC-001-3",
    "test_page_has_no_javascript_errors": "TC-001-4",
    "test_react_app_hydrated_successfully": "TC-001-5",
    "test_nav_link_is_visible_with_correct_href[About-#about]": "TC-002-1",
    "test_nav_link_is_visible_with_correct_href[Skills-#skills]": "TC-002-2",
    "test_nav_link_is_visible_with_correct_href[Projects-#projects]": "TC-002-3",
    "test_nav_link_is_visible_with_correct_href[Contact-#contact]": "TC-002-4",
    "test_skills_section_contains_core_stack[Python]": "TC-003-1",
    "test_skills_section_contains_core_stack[Playwright]": "TC-003-2",
    "test_skills_section_contains_core_stack[pytest]": "TC-003-3",
    "test_projects_section_has_expected_cards": "TC-003-4",
    "test_contact_section_has_required_channels": "TC-003-5",
    "test_test_results_section_renders": "TC-003-6",
    "test_mobile_viewport_no_horizontal_scroll": "TC-004-1",
    "test_mobile_hero_section_visible": "TC-004-2",
    "test_page_load_time_within_budget": "TC-005-1",
    "test_images_have_alt_text": "TC-006-1",
    "test_headings_hierarchy_is_correct": "TC-006-2",
    "test_assets_load_on_github_pages": "TC-007-1",
    "test_base_path_is_correct": "TC-007-2",
    "test_no_console_errors_on_production": "TC-007-3",
}


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
        "req_id": "REQ-001",
        "ac_ids": ["AC-001-1", "AC-001-2", "AC-001-3"],
        "description": "Browser tab title must identify the engineer by name and role",
        "mark": "smoke",
        "steps": [
            {
                "description": "Open the portfolio page in browser",
                "code": "portfolio = PortfolioPage(page, base_url)\nportfolio.navigate()",
            },
            {
                "description": "Read the browser tab title",
                "code": "title = portfolio.get_title()",
            },
            {
                "description": "Verify title contains 'Oleg'",
                "code": "assert PAGE_TITLE.CONTAINS_NAME in title, \\\n    Msg.TITLE_MISSING_NAME.format(title=title)",
            },
            {
                "description": "Verify title contains 'Automation'",
                "code": "assert PAGE_TITLE.CONTAINS_ROLE in title, \\\n    Msg.TITLE_MISSING_ROLE.format(\n        expected=PAGE_TITLE.CONTAINS_ROLE,\n        actual=title\n    )",
            },
            {
                "description": "Verify title contains 'Engineer'",
                "code": "assert PAGE_TITLE.CONTAINS_TYPE in title, \\\n    Msg.TITLE_MISSING_ROLE.format(\n        expected=PAGE_TITLE.CONTAINS_TYPE,\n        actual=title\n    )",
            },
        ],
    },
    "test_hero_heading_displays_name": {
        "req_id": "REQ-001",
        "ac_ids": ["AC-001-4"],
        "description": "Main heading on hero section must show the engineer name",
        "mark": "smoke",
        "steps": [
            {
                "description": "Open the portfolio page",
                "code": "portfolio = PortfolioPage(page, base_url)\nportfolio.navigate()",
            },
            {
                "description": "Find the main heading (h1) by ARIA role",
                "code": "text = portfolio.get_hero_heading_text()",
            },
            {
                "description": "Read the heading text content",
                "code": "# get_hero_heading_text() calls\n# page.get_by_role('heading', level=1).inner_text()",
            },
            {
                "description": "Verify heading text contains 'Oleg'",
                "code": "assert HERO.CONTAINS_NAME in text, \\\n    Msg.HERO_NAME_MISSING.format(\n        expected=HERO.CONTAINS_NAME,\n        actual=text\n    )",
            },
        ],
    },
    "test_navigation_is_present": {
        "req_id": "REQ-001",
        "ac_ids": ["AC-001-5"],
        "description": "Navigation bar must be visible when the page loads",
        "mark": "smoke",
        "steps": [
            {
                "description": "Open the portfolio page",
                "code": "portfolio = PortfolioPage(page, base_url)\nportfolio.navigate()",
            },
            {
                "description": "Look for the navigation bar by ARIA role",
                "code": "nav = portfolio.navigation\nnav_count = nav.count()",
            },
            {
                "description": "Verify at least one navigation element is found",
                "code": "assert nav_count > 0, \\\n    Msg.NAV_NOT_VISIBLE.format(\n        url=page.url, count=nav_count\n    )",
            },
            {
                "description": "Confirm the navigation bar is visible on screen",
                "code": "assert nav.is_visible(), \\\n    Msg.NAV_NOT_VISIBLE.format(\n        url=page.url, count=nav_count\n    )",
            },
        ],
    },
    "test_page_has_no_javascript_errors": {
        "req_id": "REQ-001",
        "ac_ids": ["AC-001-6"],
        "description": "No JavaScript errors should appear in the browser console",
        "mark": "smoke",
        "steps": [
            {
                "description": "Set up a listener to catch any JS errors before navigation",
                "code": "js_errors: list[str] = []\npage.on('pageerror',\n    lambda err: js_errors.append(str(err)))",
            },
            {
                "description": "Open the portfolio page",
                "code": "page.goto(base_url, wait_until='networkidle')",
            },
            {
                "description": "Wait until no network requests for 500ms (networkidle)",
                "code": "# wait_until='networkidle' in goto() above",
            },
            {
                "description": "Check the collected error list",
                "code": "# js_errors collected via pageerror listener",
            },
            {
                "description": "Verify no JavaScript errors were thrown",
                "code": "assert js_errors == [], \\\n    Msg.JS_ERRORS_FOUND.format(errors=js_errors)",
            },
        ],
    },
    "test_react_app_hydrated_successfully": {
        "req_id": "REQ-001",
        "ac_ids": ["AC-001-7", "AC-001-8"],
        "description": "React application must render visible content on screen",
        "mark": "smoke",
        "steps": [
            {
                "description": "Open the portfolio page",
                "code": "# Uses hydrated_page fixture which calls\n# _wait_for_hydration(page, base_url)",
            },
            {
                "description": "Check the React root container (#root)",
                "code": "child_count = hydrated_page.evaluate(\n    \"document.querySelector('#root').children.length\"\n)",
            },
            {
                "description": "Count child elements inside the root",
                "code": "preview = hydrated_page.evaluate(\n    \"document.querySelector('#root')\"\n    \".innerHTML.slice(0, 200)\"\n)",
            },
            {
                "description": "Verify the root has more than 0 rendered children",
                "code": "assert child_count > 0, \\\n    Msg.HYDRATION_FAILED.format(\n        actual=child_count,\n        url=url, preview=preview\n    )",
            },
            {
                "description": "Confirm no React error boundary was triggered",
                "code": "error_boundary = hydrated_page.locator(\n    '[data-reactroot] .error-boundary, '\n    '#root > [class*=\"error\"]'\n)\nassert error_boundary.count() == 0, \\\n    Msg.ERROR_BOUNDARY_RENDERED.format(\n        count=error_boundary.count(), url=url\n    )",
            },
        ],
    },
    "test_nav_link_is_visible_with_correct_href[About-#about]": {
        "req_id": "REQ-002",
        "ac_ids": ["AC-002-1", "AC-002-2"],
        "description": "About link must be visible in navbar and point to #about",
        "mark": "navigation",
        "steps": [
            {
                "description": "Open the portfolio page",
                "code": "portfolio = PortfolioPage(page, base_url)\nportfolio.navigate()",
            },
            {
                "description": "Find 'About' link inside the navigation bar",
                "code": "link = portfolio.nav_link('About')",
            },
            {
                "description": "Verify the 'About' link is visible on screen",
                "code": "assert link.is_visible(), \\\n    Msg.NAV_LINK_NOT_VISIBLE.format(name='About')",
            },
            {
                "description": "Check the link destination attribute",
                "code": "actual_href = link.get_attribute('href')",
            },
            {
                "description": "Verify href equals '#about'",
                "code": "assert actual_href == '#about', \\\n    Msg.NAV_LINK_WRONG_HREF.format(\n        name='About',\n        expected='#about',\n        actual=actual_href\n    )",
            },
        ],
    },
    "test_nav_link_is_visible_with_correct_href[Skills-#skills]": {
        "req_id": "REQ-002",
        "ac_ids": ["AC-002-3", "AC-002-4"],
        "description": "Skills link must be visible in navbar and point to #skills",
        "mark": "navigation",
        "steps": [
            {
                "description": "Open the portfolio page",
                "code": "portfolio = PortfolioPage(page, base_url)\nportfolio.navigate()",
            },
            {
                "description": "Find 'Skills' link inside the navigation bar",
                "code": "link = portfolio.nav_link('Skills')",
            },
            {
                "description": "Verify the 'Skills' link is visible on screen",
                "code": "assert link.is_visible(), \\\n    Msg.NAV_LINK_NOT_VISIBLE.format(name='Skills')",
            },
            {
                "description": "Check the link destination attribute",
                "code": "actual_href = link.get_attribute('href')",
            },
            {
                "description": "Verify href equals '#skills'",
                "code": "assert actual_href == '#skills', \\\n    Msg.NAV_LINK_WRONG_HREF.format(\n        name='Skills',\n        expected='#skills',\n        actual=actual_href\n    )",
            },
        ],
    },
    "test_nav_link_is_visible_with_correct_href[Projects-#projects]": {
        "req_id": "REQ-002",
        "ac_ids": ["AC-002-5", "AC-002-6"],
        "description": "Projects link must be visible in navbar and point to #projects",
        "mark": "navigation",
        "steps": [
            {
                "description": "Open the portfolio page",
                "code": "portfolio = PortfolioPage(page, base_url)\nportfolio.navigate()",
            },
            {
                "description": "Find 'Projects' link inside the navigation bar",
                "code": "link = portfolio.nav_link('Projects')",
            },
            {
                "description": "Verify the 'Projects' link is visible on screen",
                "code": "assert link.is_visible(), \\\n    Msg.NAV_LINK_NOT_VISIBLE.format(name='Projects')",
            },
            {
                "description": "Check the link destination attribute",
                "code": "actual_href = link.get_attribute('href')",
            },
            {
                "description": "Verify href equals '#projects'",
                "code": "assert actual_href == '#projects', \\\n    Msg.NAV_LINK_WRONG_HREF.format(\n        name='Projects',\n        expected='#projects',\n        actual=actual_href\n    )",
            },
        ],
    },
    "test_nav_link_is_visible_with_correct_href[Contact-#contact]": {
        "req_id": "REQ-002",
        "ac_ids": ["AC-002-7", "AC-002-8"],
        "description": "Contact link must be visible in navbar and point to #contact",
        "mark": "navigation",
        "steps": [
            {
                "description": "Open the portfolio page",
                "code": "portfolio = PortfolioPage(page, base_url)\nportfolio.navigate()",
            },
            {
                "description": "Find 'Contact' link inside the navigation bar",
                "code": "link = portfolio.nav_link('Contact')",
            },
            {
                "description": "Verify the 'Contact' link is visible on screen",
                "code": "assert link.is_visible(), \\\n    Msg.NAV_LINK_NOT_VISIBLE.format(name='Contact')",
            },
            {
                "description": "Check the link destination attribute",
                "code": "actual_href = link.get_attribute('href')",
            },
            {
                "description": "Verify href equals '#contact'",
                "code": "assert actual_href == '#contact', \\\n    Msg.NAV_LINK_WRONG_HREF.format(\n        name='Contact',\n        expected='#contact',\n        actual=actual_href\n    )",
            },
        ],
    },
    "test_skills_section_contains_core_stack[Python]": {
        "req_id": "REQ-003",
        "ac_ids": ["AC-003-1"],
        "description": "Python must appear as a visible skill tag in Skills section",
        "mark": "content",
        "steps": [
            {
                "description": "Open the portfolio page",
                "code": "portfolio = PortfolioPage(page, base_url)\nportfolio.navigate()",
            },
            {
                "description": "Scroll to the Skills section",
                "code": "# portfolio fixture navigates to base_url",
            },
            {
                "description": "Look for a tag with text 'Python' in skills section",
                "code": "tag = portfolio.skill_text('Python')",
            },
            {
                "description": "Verify the 'Python' skill tag is visible",
                "code": "assert tag.first.is_visible(), \\\n    Msg.SKILL_NOT_VISIBLE.format(name='Python')",
            },
        ],
    },
    "test_skills_section_contains_core_stack[Playwright]": {
        "req_id": "REQ-003",
        "ac_ids": ["AC-003-2"],
        "description": "Playwright must appear as a visible skill tag in Skills section",
        "mark": "content",
        "steps": [
            {
                "description": "Open the portfolio page",
                "code": "portfolio = PortfolioPage(page, base_url)\nportfolio.navigate()",
            },
            {
                "description": "Scroll to the Skills section",
                "code": "# portfolio fixture navigates to base_url",
            },
            {
                "description": "Look for a tag with text 'Playwright' in skills section",
                "code": "tag = portfolio.skill_text('Playwright')",
            },
            {
                "description": "Verify the 'Playwright' skill tag is visible",
                "code": "assert tag.first.is_visible(), \\\n    Msg.SKILL_NOT_VISIBLE.format(name='Playwright')",
            },
        ],
    },
    "test_skills_section_contains_core_stack[pytest]": {
        "req_id": "REQ-003",
        "ac_ids": ["AC-003-3"],
        "description": "pytest must appear as a visible skill tag in Skills section",
        "mark": "content",
        "steps": [
            {
                "description": "Open the portfolio page",
                "code": "portfolio = PortfolioPage(page, base_url)\nportfolio.navigate()",
            },
            {
                "description": "Scroll to the Skills section",
                "code": "# portfolio fixture navigates to base_url",
            },
            {
                "description": "Look for a tag with text 'pytest' in skills section",
                "code": "tag = portfolio.skill_text('pytest')",
            },
            {
                "description": "Verify the 'pytest' skill tag is visible",
                "code": "assert tag.first.is_visible(), \\\n    Msg.SKILL_NOT_VISIBLE.format(name='pytest')",
            },
        ],
    },
    "test_projects_section_has_expected_cards": {
        "req_id": "REQ-003",
        "ac_ids": ["AC-003-4"],
        "description": "Projects section must display exactly 3 project cards",
        "mark": "content",
        "steps": [
            {
                "description": "Open the portfolio page",
                "code": "portfolio = PortfolioPage(page, base_url)\nportfolio.navigate()",
            },
            {
                "description": "Scroll to the Projects section",
                "code": "# portfolio fixture navigates to base_url",
            },
            {
                "description": "Count all project cards displayed",
                "code": "count = portfolio.count_project_cards()",
            },
            {
                "description": "Verify the total count equals 3",
                "code": "assert count == COUNTS.PROJECT_CARDS, \\\n    Msg.WRONG_PROJECT_COUNT.format(\n        expected=COUNTS.PROJECT_CARDS,\n        actual=count\n    )",
            },
        ],
    },
    "test_contact_section_has_required_channels": {
        "req_id": "REQ-003",
        "ac_ids": ["AC-003-5"],
        "description": "Contact section must display all required contact channels",
        "mark": "content",
        "steps": [
            {
                "description": "Open the portfolio page",
                "code": "portfolio = PortfolioPage(page, base_url)\nportfolio.navigate()",
            },
            {
                "description": "Scroll to the Contact section",
                "code": "# portfolio fixture navigates to base_url",
            },
            {
                "description": "Count all contact channel links",
                "code": "count = portfolio.count_contact_links()",
            },
            {
                "description": "Verify the total count equals 3",
                "code": "assert count == COUNTS.CONTACT_LINKS, \\\n    Msg.WRONG_CONTACT_COUNT.format(\n        expected=COUNTS.CONTACT_LINKS,\n        actual=count\n    )",
            },
        ],
    },
    "test_test_results_section_renders": {
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
                "description": "Locate the Test Results section (#test-results)",
                "code": "section = page.locator('#test-results')",
            },
            {
                "description": "Verify the section is visible on screen",
                "code": "assert section.is_visible(), \\\n    'Test results section #test-results '\n    'is not visible on page'",
            },
            {
                "description": "Wait 2000ms for fetch(test_report.json) to complete",
                "code": "page.wait_for_timeout(2000)",
            },
            {
                "description": "Check that numeric values appear in summary cards",
                "code": "section_text = section.inner_text()\nhas_numbers = any(\n    char.isdigit() for char in section_text\n)\nassert has_numbers, \\\n    f'No numeric values in section. '\n    f'Text: {section_text[:200]}'",
            },
            {
                "description": "Verify at least 1 test row is rendered in the list",
                "code": "row_count = page.evaluate(\"\"\"\n    () => {\n        const section = document.querySelector(\n            '#test-results'\n        );\n        return section\n            ? section.querySelectorAll(\n                'div[class*=\"cursor-pointer\"]'\n            ).length\n            : 0;\n    }\n\"\"\")\nassert row_count > 0",
            },
        ],
    },
    "test_mobile_viewport_no_horizontal_scroll": {
        "req_id": "REQ-004",
        "ac_ids": ["AC-004-1"],
        "description": "No horizontal scrollbar at 390px mobile width",
        "mark": "responsive",
        "steps": [
            {
                "description": "Resize browser to 390x844 (iPhone 14)",
                "code": "# mobile_portfolio uses mobile_page fixture\n# viewport: {width: 390, height: 844}",
            },
            {
                "description": "Open the portfolio page",
                "code": "mobile_portfolio = PortfolioPage(\n    mobile_page, base_url\n)\nmobile_portfolio.navigate()",
            },
            {
                "description": "Measure the total page content width",
                "code": "scroll_w = mobile_portfolio.get_scroll_width()",
            },
            {
                "description": "Compare content width against 390px viewport",
                "code": "viewport_w = mobile_portfolio.get_viewport_width()",
            },
            {
                "description": "Verify no horizontal overflow exists",
                "code": "assert scroll_w <= viewport_w, \\\n    Msg.HORIZONTAL_OVERFLOW.format(\n        scroll_w=scroll_w,\n        viewport_w=viewport_w\n    )",
            },
        ],
    },
    "test_mobile_hero_section_visible": {
        "req_id": "REQ-004",
        "ac_ids": ["AC-004-2"],
        "description": "Hero heading must be visible at 390px mobile width",
        "mark": "responsive",
        "steps": [
            {
                "description": "Resize browser to 390x844",
                "code": "# mobile_portfolio uses mobile_page fixture\n# viewport: {width: 390, height: 844}",
            },
            {
                "description": "Open the portfolio page",
                "code": "mobile_portfolio = PortfolioPage(\n    mobile_page, base_url\n)\nmobile_portfolio.navigate()",
            },
            {
                "description": "Find the main heading (h1)",
                "code": "heading = mobile_portfolio.hero_heading",
            },
            {
                "description": "Verify the heading is visible at 390px width",
                "code": "assert heading.is_visible(), \\\n    Msg.MOBILE_HERO_NOT_VISIBLE.format(\n        width=CONFIG.mobile_width\n    )",
            },
        ],
    },
    "test_page_load_time_within_budget": {
        "req_id": "REQ-005",
        "ac_ids": ["AC-005-1"],
        "description": "Page must finish loading in under 3000ms",
        "mark": "performance",
        "steps": [
            {
                "description": "Open the portfolio page",
                "code": "page.goto(base_url, wait_until='load')",
            },
            {
                "description": "Wait for load event — all images and scripts ready",
                "code": "# wait_until='load' in goto() above",
            },
            {
                "description": "Measure total load time in milliseconds",
                "code": "load_ms = page.evaluate(\n    'performance.timing.loadEventEnd '\n    '- performance.timing.navigationStart'\n)",
            },
            {
                "description": "Verify load time is under 3000ms",
                "code": "assert load_ms < PERF.MAX_LOAD_TIME_MS, \\\n    Msg.SLOW_PAGE_LOAD.format(\n        actual=load_ms,\n        budget=PERF.MAX_LOAD_TIME_MS\n    )",
            },
        ],
    },
    "test_images_have_alt_text": {
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
                "description": "Find all non-decorative images and check alt via JS",
                "code": "violations = page.evaluate(\"\"\"\n    () => Array.from(\n        document.querySelectorAll('img')\n    )\n    .filter(img =>\n        img.getAttribute('aria-hidden') !== 'true'\n        && (!img.alt || img.alt.trim() === '')\n    )\n    .map((img, i) => ({\n        index: i,\n        src: (img.src || '').slice(0, 80)\n    }))\n\"\"\")",
            },
            {
                "description": "Collect any images with missing or empty alt",
                "code": "# violations list built by JS evaluation above",
            },
            {
                "description": "Verify no images are missing alt text",
                "code": "assert violations == [], \\\n    f'Found {len(violations)} image(s) '\n    f'without alt text: {violations}'",
            },
        ],
    },
    "test_headings_hierarchy_is_correct": {
        "req_id": "REQ-006",
        "ac_ids": ["AC-006-2", "AC-006-3", "AC-006-4"],
        "description": "Heading levels must follow correct order without gaps",
        "mark": "accessibility",
        "steps": [
            {
                "description": "Open the portfolio page",
                "code": "portfolio = PortfolioPage(page, base_url)\nportfolio.navigate()",
            },
            {
                "description": "Find all heading elements (h1 through h6)",
                "code": "headings = portfolio.all_headings.all()\ntags = [\n    h.evaluate('el => el.tagName.toLowerCase()')\n    for h in headings\n]",
            },
            {
                "description": "Verify exactly 1 h1 heading exists",
                "code": "h1_count = tags.count('h1')\nassert h1_count == COUNTS.H1_HEADINGS, \\\n    Msg.WRONG_H1_COUNT.format(\n        expected=COUNTS.H1_HEADINGS,\n        actual=h1_count\n    )",
            },
            {
                "description": "Confirm h1 appears before any h2",
                "code": "h1_idx = tags.index('h1')\nh2_indices = [\n    i for i, t in enumerate(tags) if t == 'h2'\n]\nif h2_indices:\n    assert h1_idx < h2_indices[0], \\\n        Msg.H1_NOT_FIRST",
            },
            {
                "description": "Check no heading levels are skipped (e.g. h2 to h4)",
                "code": "levels = [int(t[1]) for t in tags]\nfor i in range(1, len(levels)):\n    gap = levels[i] - levels[i - 1]\n    assert gap <= 1, \\\n        Msg.HEADING_LEVEL_SKIPPED.format(\n            prev=levels[i-1],\n            next=levels[i], pos=i\n        )",
            },
        ],
    },
    "test_assets_load_on_github_pages": {
        "req_id": "REQ-007",
        "ac_ids": ["AC-007-1", "AC-007-2", "AC-007-3"],
        "description": "All CSS and JS files must load on production site",
        "mark": "deployment",
        "steps": [
            {
                "description": "Set up a listener to track failed network requests",
                "code": "failed_requests: list[str] = []\ndeploy_page.on('response',\n    lambda r: failed_requests.append(r.url)\n    if r.status == 404 else None\n)",
            },
            {
                "description": "Open the production site on GitHub Pages",
                "code": "deploy_page.goto(\n    _PAGES_URL,\n    wait_until='networkidle',\n    timeout=CONFIG.timeout_navigation\n)",
            },
            {
                "description": "Wait until network is idle — no requests for 500ms",
                "code": "# wait_until='networkidle' in goto() above",
            },
            {
                "description": "Check for any 404 errors on JS or CSS files",
                "code": "asset_404s = [\n    url for url in failed_requests\n    if any(\n        ext in url\n        for ext in DEPLOYMENT.CHECKED_EXTENSIONS\n    )\n    and not any(\n        exc in url\n        for exc in DEPLOYMENT.EXCLUDED_404_PATHS\n    )\n]\nassert not asset_404s, \\\n    Msg.ASSET_404.format(urls=asset_404s)",
            },
            {
                "description": "Verify the navigation bar is visible",
                "code": "nav = deploy_page.get_by_role('navigation')\nassert nav.count() > 0\nassert nav.is_visible()",
            },
            {
                "description": "Verify the main heading is visible",
                "code": "h1 = deploy_page.get_by_role(\n    'heading', level=1\n)\nassert h1.count() == 1\nassert h1.inner_text().strip()",
            },
        ],
    },
    "test_base_path_is_correct": {
        "req_id": "REQ-007",
        "ac_ids": ["AC-007-4"],
        "description": "Asset paths must include the /qa-portfolio/ prefix",
        "mark": "deployment",
        "steps": [
            {
                "description": "Open the production site on GitHub Pages",
                "code": "deploy_page.goto(\n    _PAGES_URL,\n    wait_until='networkidle'\n)",
            },
            {
                "description": "Wait until network is idle — all scripts and styles loaded",
                "code": "# wait_until='networkidle' in goto() above",
            },
            {
                "description": "Inspect all script and stylesheet paths",
                "code": "bad_paths = deploy_page.evaluate(\"\"\"() => {\n    const bad = [];\n    document.querySelectorAll(\n        'script[src], link[href]'\n    ).forEach(el => {\n        const val = el.getAttribute('src')\n            || el.getAttribute('href');\n        if (val && val.startsWith('/assets/'))\n            bad.push(val);\n    });\n    return bad;\n}\"\"\")",
            },
            {
                "description": "Check for paths missing the /qa-portfolio/ prefix",
                "code": "# bad_paths contains any paths starting\n# with '/assets/' instead of\n# '/qa-portfolio/assets/'",
            },
            {
                "description": "Verify all asset paths are correctly prefixed",
                "code": "assert bad_paths == [], \\\n    Msg.DEPLOY_WRONG_BASE_PATH.format(\n        paths=bad_paths\n    )",
            },
        ],
    },
    "test_no_console_errors_on_production": {
        "req_id": "REQ-007",
        "ac_ids": ["AC-007-5"],
        "description": "No JavaScript errors on the production site",
        "mark": "deployment",
        "steps": [
            {
                "description": "Set up a listener to catch JS errors",
                "code": "js_errors: list[str] = []\ndeploy_page.on('pageerror',\n    lambda err: js_errors.append(str(err)))",
            },
            {
                "description": "Open the production site on GitHub Pages",
                "code": "deploy_page.goto(\n    _PAGES_URL,\n    wait_until='networkidle'\n)",
            },
            {
                "description": "Wait until network is idle — all async resources settled",
                "code": "# wait_until='networkidle' in goto() above",
            },
            {
                "description": "Check the collected error list",
                "code": "# js_errors collected via pageerror listener",
            },
            {
                "description": "Verify no JavaScript errors occurred",
                "code": "assert js_errors == [], \\\n    Msg.DEPLOY_JS_ERRORS.format(\n        errors=js_errors\n    )",
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


def _resize_screenshot(src_path, max_width=320):
    """Resize a PNG to max_width using sips (macOS) or convert (Linux). Returns bytes."""
    import shutil
    import tempfile
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp.close()
    tmp_path = tmp.name
    try:
        shutil.copy2(str(src_path), tmp_path)
        if shutil.which("sips"):
            subprocess.run(
                ["sips", "--resampleWidth", str(max_width), tmp_path],
                capture_output=True,
            )
        elif shutil.which("convert"):
            subprocess.run(
                ["convert", str(src_path), "-resize", f"{max_width}x", tmp_path],
                capture_output=True,
            )
        else:
            return src_path.read_bytes()
        return Path(tmp_path).read_bytes()
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def find_screenshot_for_test(test_name):
    """Find the most recent screenshot for a test and return as base64 data URI."""
    if not SCREENSHOTS_DIR.exists():
        return None

    safe_name = re.sub(r"[^\w-]", "_", test_name)
    matches = list(SCREENSHOTS_DIR.glob(f"{safe_name}_*.png"))

    short = re.sub(r"[^\w-]", "_", test_name.replace("test_", ""))
    matches += list(SCREENSHOTS_DIR.glob(f"assert_*{short}*.png"))

    if not matches:
        return None

    latest = max(matches, key=lambda p: p.stat().st_mtime)
    try:
        img_data = _resize_screenshot(latest)
        b64 = base64.b64encode(img_data).decode("utf-8")
        return f"data:image/png;base64,{b64}"
    except Exception:
        return None


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
        steps = build_steps(mapped["steps"], test_passed)

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
            "locator_strategy": detect_locator_strategy(mapped["steps"]),
            "coverage": get_coverage_tags(name),
            "tc_id": TC_ID_MAP.get(name, "TC-???"),
            "req_id": mapped.get("req_id"),
            "ac_ids": mapped.get("ac_ids", []),
            "screenshot": find_screenshot_for_test(name),
            "error": error_msg,
        })

    report = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "summary": {
            "passed": sum(1 for t in tests if t["status"] == "pass"),
            "failed": sum(1 for t in tests if t["status"] != "pass"),
            "total": len(tests),
            "duration_ms": total_duration_ms,
        },
        "tests": tests,
    }
    return report


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    print("Running tests...")
    run_tests()

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
