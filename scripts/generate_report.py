#!/usr/bin/env python3
"""Generate test_report.json from pytest results for the portfolio site."""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
QA_DIR = PROJECT_ROOT / "qa"
REPORTS_DIR = QA_DIR / "reports"
DIST_DIR = PROJECT_ROOT / "dist"

STEPS_MAP = {
    "test_page_loads_with_correct_title": {
        "description": "Page title must identify engineer by name and role",
        "mark": "smoke",
        "steps": [
            "Navigate to http://localhost:8080",
            "Call page.title() → get browser tab title string",
            "Assert 'Oleg' in page.title()",
            "Assert 'Automation' in page.title()",
            "Assert 'Engineer' in page.title()",
        ],
    },
    "test_hero_heading_displays_name": {
        "description": "Hero h1 must contain the engineer name",
        "mark": "smoke",
        "steps": [
            "Navigate to base URL",
            "page.get_by_role('heading', level=1) → locate h1 element",
            "Call h1.inner_text() → get heading text content",
            "Assert 'Oleg' in h1.inner_text()",
        ],
    },
    "test_navigation_is_present": {
        "description": "Navigation landmark must be visible on page load",
        "mark": "smoke",
        "steps": [
            "Navigate to base URL",
            "page.get_by_role('navigation') → locate <nav> element",
            "Assert nav.count() > 0 → found at least 1 navigation element",
            "Assert nav.is_visible() == True",
        ],
    },
    "test_page_has_no_javascript_errors": {
        "description": "No uncaught JavaScript exceptions on page load",
        "mark": "smoke",
        "steps": [
            "Register page.on('pageerror') listener before navigation",
            "Navigate to base URL",
            "Wait for networkidle state",
            "Collect all pageerror events into js_errors[]",
            "Assert js_errors == [] → no uncaught JS exceptions found",
        ],
    },
    "test_react_app_hydrated_successfully": {
        "description": "React must render content into #root element",
        "mark": "smoke",
        "steps": [
            "Navigate to base URL",
            "page.locator('#root') → locate React mount point",
            "Evaluate document.querySelector('#root').children.length",
            "Assert children_count > 0 → React rendered into #root",
            "page.locator('[data-react-error]').count()",
            "Assert error_boundary_count == 0 → no React errors",
        ],
    },
    "test_nav_link_is_visible_with_correct_href[About-#about]": {
        "description": "About nav link must be visible with href='#about'",
        "mark": "navigation",
        "steps": [
            "Navigate to base URL",
            "page.get_by_role('navigation').get_by_role('link', name='About')",
            "Assert link.is_visible() == True",
            "Assert link.get_attribute('href') == '#about'",
        ],
    },
    "test_nav_link_is_visible_with_correct_href[Skills-#skills]": {
        "description": "Skills nav link must be visible with href='#skills'",
        "mark": "navigation",
        "steps": [
            "Navigate to base URL",
            "page.get_by_role('navigation').get_by_role('link', name='Skills')",
            "Assert link.is_visible() == True",
            "Assert link.get_attribute('href') == '#skills'",
        ],
    },
    "test_nav_link_is_visible_with_correct_href[Projects-#projects]": {
        "description": "Projects nav link must be visible with href='#projects'",
        "mark": "navigation",
        "steps": [
            "Navigate to base URL",
            "page.get_by_role('navigation').get_by_role('link', name='Projects')",
            "Assert link.is_visible() == True",
            "Assert link.get_attribute('href') == '#projects'",
        ],
    },
    "test_nav_link_is_visible_with_correct_href[Contact-#contact]": {
        "description": "Contact nav link must be visible with href='#contact'",
        "mark": "navigation",
        "steps": [
            "Navigate to base URL",
            "page.get_by_role('navigation').get_by_role('link', name='Contact')",
            "Assert link.is_visible() == True",
            "Assert link.get_attribute('href') == '#contact'",
        ],
    },
    "test_skills_section_contains_core_stack[Python]": {
        "description": "Python skill tag must be visible in skills section",
        "mark": "content",
        "steps": [
            "Navigate to base URL",
            "page.locator('#skills') → locate skills section",
            "page.locator('#skills').get_by_text('Python', exact=True)",
            "Assert skill_tag.first.is_visible() == True",
            "Assert skill_tag.first.inner_text() == 'Python'",
        ],
    },
    "test_skills_section_contains_core_stack[Playwright]": {
        "description": "Playwright skill tag must be visible in skills section",
        "mark": "content",
        "steps": [
            "Navigate to base URL",
            "page.locator('#skills') → locate skills section",
            "page.locator('#skills').get_by_text('Playwright', exact=True)",
            "Assert skill_tag.first.is_visible() == True",
            "Assert skill_tag.first.inner_text() == 'Playwright'",
        ],
    },
    "test_skills_section_contains_core_stack[pytest]": {
        "description": "pytest skill tag must be visible in skills section",
        "mark": "content",
        "steps": [
            "Navigate to base URL",
            "page.locator('#skills') → locate skills section",
            "page.locator('#skills').get_by_text('pytest', exact=True)",
            "Assert skill_tag.first.is_visible() == True",
            "Assert skill_tag.first.inner_text() == 'pytest'",
        ],
    },
    "test_projects_section_has_expected_cards": {
        "description": "Projects section must display exactly 3 project cards",
        "mark": "content",
        "steps": [
            "Navigate to base URL",
            "page.locator('#projects') → locate projects section",
            "page.locator('[data-testid=project-card]') → find cards",
            "Assert project_cards.count() == 3",
            "Assert actual_count == ExpectedCounts.PROJECT_CARDS (3)",
        ],
    },
    "test_contact_section_has_required_channels": {
        "description": "Contact section must show all required contact channels",
        "mark": "content",
        "steps": [
            "Navigate to base URL",
            "page.locator('#contact') → locate contact section",
            "page.locator('#contact').get_by_role('link') → find links",
            "Assert contact_links.count() == 3",
            "Assert actual_count == ExpectedCounts.CONTACT_LINKS (3)",
        ],
    },
    "test_test_results_section_renders": {
        "description": "Test results section must render with visible content",
        "mark": "content",
        "steps": [
            "Navigate to base URL",
            "page.locator('#tests') → locate test results section",
            "Assert section.is_visible() == True",
            "page.locator('#tests').get_by_role('heading') → find headings",
            "Assert headings.count() > 0 → section has content",
        ],
    },
    "test_mobile_viewport_no_horizontal_scroll": {
        "description": "No horizontal overflow at 390x844 mobile viewport",
        "mark": "responsive",
        "steps": [
            "Set viewport to width=390 height=844 (iPhone 14)",
            "Navigate to base URL",
            "Evaluate document.documentElement.scrollWidth → actual_width",
            "Evaluate window.innerWidth → viewport_width=390",
            "Assert actual_width <= 390 → no horizontal scroll",
        ],
    },
    "test_mobile_hero_section_visible": {
        "description": "Hero heading must be visible at 390px mobile width",
        "mark": "responsive",
        "steps": [
            "Set viewport to width=390 height=844",
            "Navigate to base URL",
            "page.get_by_role('heading', level=1) → locate h1",
            "Assert h1.is_visible() == True at viewport_width=390",
        ],
    },
    "test_page_load_time_within_budget": {
        "description": "Full page load must complete under 3000ms",
        "mark": "performance",
        "steps": [
            "Navigate to base URL",
            "Evaluate performance.timing.loadEventEnd → end_time",
            "Evaluate performance.timing.navigationStart → start_time",
            "Calculate load_ms = loadEventEnd - navigationStart",
            "Assert load_ms < 3000 (PerformanceBudget.MAX_LOAD_TIME_MS)",
        ],
    },
    "test_images_have_alt_text": {
        "description": "Every img element must have non-empty alt attribute",
        "mark": "accessibility",
        "steps": [
            "Navigate to base URL",
            "Evaluate document.querySelectorAll('img') → all_images",
            "Filter: images where alt == '' or alt attribute missing",
            "Collect violations[] with src of each bad image",
            "Assert violations == [] → all images have alt text",
        ],
    },
    "test_headings_hierarchy_is_correct": {
        "description": "Exactly one h1, no skipped heading levels",
        "mark": "accessibility",
        "steps": [
            "Navigate to base URL",
            "page.locator('h1').count() → count h1 elements",
            "Assert h1_count == 1 (ExpectedCounts.H1_HEADINGS=1)",
            "page.locator('h2').first → get first h2 position",
            "Assert h1 DOM position < h2 DOM position",
            "Loop all headings: Assert level[n+1] - level[n] <= 1",
        ],
    },
    "test_assets_load_on_github_pages": {
        "description": "All JS/CSS assets must load without 404 on production",
        "mark": "deployment",
        "steps": [
            "Register page.on('response') listener for all requests",
            "Navigate to https://olegvoronchenko.github.io/qa-portfolio/",
            "Wait for networkidle → all assets finished loading",
            "Filter responses: status==404 AND url matches .js/.css/.png/.jpg",
            "Exclude: test_report.json, favicon.ico (expected optional files)",
            "Assert asset_404s == [] → no critical assets returned 404",
        ],
    },
    "test_base_path_is_correct": {
        "description": "All asset paths must include /qa-portfolio/ base prefix",
        "mark": "deployment",
        "steps": [
            "Navigate to https://olegvoronchenko.github.io/qa-portfolio/",
            "Wait for networkidle",
            "Evaluate: find all <script src> and <link href> attributes",
            "Filter: paths starting with '/assets/' (missing base prefix)",
            "Assert wrong_paths == [] → all paths start with '/qa-portfolio/assets/'",
        ],
    },
    "test_no_console_errors_on_production": {
        "description": "No JavaScript errors in browser console on production",
        "mark": "deployment",
        "steps": [
            "Register page.on('pageerror') listener before navigation",
            "Navigate to https://olegvoronchenko.github.io/qa-portfolio/",
            "Wait for networkidle state",
            "Collect all pageerror events into js_errors[]",
            "Assert js_errors == [] → no JS exceptions on production URL",
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
            f"Execute {test_name}",
            "Assert expected result",
        ],
    }


def build_steps(step_names, test_passed):
    """Build step objects; if test failed, mark the last step as failed."""
    steps = []
    for i, name in enumerate(step_names):
        is_last = i == len(step_names) - 1
        status = "fail" if (not test_passed and is_last) else "pass"
        steps.append({"name": name, "status": status})
    return steps


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
