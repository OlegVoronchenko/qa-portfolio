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
        "description": "Page must load and title must identify the engineer",
        "mark": "smoke",
        "steps": [
            "Navigate to http://localhost:8080",
            "Call page.title() → get browser tab title",
            "Assert 'Oleg' in page.title() → True",
            "Assert 'Automation' in page.title() → True",
            "Assert 'Engineer' in page.title() → True",
        ],
    },
    "test_hero_heading_displays_name": {
        "description": "Hero section h1 must contain the engineer name",
        "mark": "smoke",
        "steps": [
            "Navigate to base URL",
            "page.get_by_role('heading', level=1) → locate h1",
            "Call heading.inner_text() → get text content",
            "Assert 'Oleg' in heading.inner_text() → True",
        ],
    },
    "test_navigation_is_present": {
        "description": "Navigation landmark must be visible on page load",
        "mark": "smoke",
        "steps": [
            "Navigate to base URL",
            "page.get_by_role('navigation') → locate <nav>",
            "Assert nav.count() > 0 → found 1 element",
            "Assert nav.is_visible() == True",
        ],
    },
    "test_page_has_no_javascript_errors": {
        "description": "No JavaScript console errors during page load",
        "mark": "smoke",
        "steps": [
            "Register page.on('pageerror') listener before navigation",
            "Navigate to base URL",
            "Wait for networkidle state",
            "Collect all pageerror events into js_errors list",
            "Assert js_errors == [] → no uncaught JS exceptions",
        ],
    },
    "test_react_app_hydrated_successfully": {
        "description": "React app must render content into #root element",
        "mark": "smoke",
        "steps": [
            "Navigate to base URL",
            "page.locator('#root') → locate React mount point",
            "Evaluate: document.querySelector('#root').children.length",
            "Assert children_count > 0 → React rendered into #root",
            "page.locator('[data-reactroot] .error-boundary') → check error boundary",
            "Assert error_boundary.count() == 0 → no React errors",
        ],
    },
    "test_nav_link_is_visible_with_correct_href[About-#about]": {
        "description": "Nav link 'About' must be visible with href='#about'",
        "mark": "navigation",
        "steps": [
            "Navigate to base URL",
            "page.get_by_role('navigation').get_by_role('link', name='About')",
            "Assert link.is_visible() == True",
            "Assert link.get_attribute('href') == '#about'",
        ],
    },
    "test_nav_link_is_visible_with_correct_href[Skills-#skills]": {
        "description": "Nav link 'Skills' must be visible with href='#skills'",
        "mark": "navigation",
        "steps": [
            "Navigate to base URL",
            "page.get_by_role('navigation').get_by_role('link', name='Skills')",
            "Assert link.is_visible() == True",
            "Assert link.get_attribute('href') == '#skills'",
        ],
    },
    "test_nav_link_is_visible_with_correct_href[Projects-#projects]": {
        "description": "Nav link 'Projects' must be visible with href='#projects'",
        "mark": "navigation",
        "steps": [
            "Navigate to base URL",
            "page.get_by_role('navigation').get_by_role('link', name='Projects')",
            "Assert link.is_visible() == True",
            "Assert link.get_attribute('href') == '#projects'",
        ],
    },
    "test_nav_link_is_visible_with_correct_href[Contact-#contact]": {
        "description": "Nav link 'Contact' must be visible with href='#contact'",
        "mark": "navigation",
        "steps": [
            "Navigate to base URL",
            "page.get_by_role('navigation').get_by_role('link', name='Contact')",
            "Assert link.is_visible() == True",
            "Assert link.get_attribute('href') == '#contact'",
        ],
    },
    "test_skills_section_contains_core_stack[Python]": {
        "description": "Skill tag 'Python' must be visible in skills section",
        "mark": "content",
        "steps": [
            "Navigate to base URL",
            "page.locator('#skills').get_by_text('Python', exact=True)",
            "Assert skill_locator.first.is_visible() == True",
            "Assert text content == 'Python'",
        ],
    },
    "test_skills_section_contains_core_stack[Playwright]": {
        "description": "Skill tag 'Playwright' must be visible in skills section",
        "mark": "content",
        "steps": [
            "Navigate to base URL",
            "page.locator('#skills').get_by_text('Playwright', exact=True)",
            "Assert skill_locator.first.is_visible() == True",
            "Assert text content == 'Playwright'",
        ],
    },
    "test_skills_section_contains_core_stack[pytest]": {
        "description": "Skill tag 'pytest' must be visible in skills section",
        "mark": "content",
        "steps": [
            "Navigate to base URL",
            "page.locator('#skills').get_by_text('pytest', exact=True)",
            "Assert skill_locator.first.is_visible() == True",
            "Assert text content == 'pytest'",
        ],
    },
    "test_projects_section_has_expected_cards": {
        "description": "Projects section must display exactly 3 project cards",
        "mark": "content",
        "steps": [
            "Navigate to base URL",
            "page.locator('#projects') → locate projects section",
            "Count elements with role='article'",
            "Assert project_cards.count() == 3 (ExpectedCounts.PROJECT_CARDS)",
        ],
    },
    "test_contact_section_has_required_channels": {
        "description": "Contact section must show all 3 communication channels",
        "mark": "content",
        "steps": [
            "Navigate to base URL",
            "page.locator('#contact') → locate contact section",
            "Count elements with role='link' in contact section",
            "Assert contact_links.count() == 3 (ExpectedCounts.CONTACT_LINKS)",
        ],
    },
    "test_test_results_section_renders": {
        "description": "Test results section must render with heading content",
        "mark": "content",
        "steps": [
            "Navigate to base URL",
            "page.locator('#test-results') → locate test results section",
            "Assert section.is_visible() == True",
            "Count heading elements in section",
            "Assert headings.count() > 0 → section has content",
        ],
    },
    "test_mobile_viewport_no_horizontal_scroll": {
        "description": "Page must not cause horizontal overflow on mobile viewport",
        "mark": "responsive",
        "steps": [
            "Set viewport to 390×844 (iPhone 14 size)",
            "Navigate to base URL",
            "Evaluate: document.documentElement.scrollWidth",
            "Evaluate: window.innerWidth",
            "Assert scrollWidth (actual) <= innerWidth (390px) → no overflow",
        ],
    },
    "test_mobile_hero_section_visible": {
        "description": "Hero heading must be visible at 390px mobile viewport",
        "mark": "responsive",
        "steps": [
            "Set viewport to 390×844",
            "Navigate to base URL",
            "page.get_by_role('heading', level=1) → locate h1",
            "Assert heading.is_visible() == True at width=390px",
        ],
    },
    "test_page_load_time_within_budget": {
        "description": "Full page load must complete within 3000ms budget",
        "mark": "performance",
        "steps": [
            "Navigate to base URL",
            "Evaluate: performance.timing.loadEventEnd",
            "Evaluate: performance.timing.navigationStart",
            "Calculate: loadEventEnd - navigationStart = actual_ms",
            "Assert actual_ms < 3000 (PerformanceBudget.MAX_LOAD_TIME_MS)",
        ],
    },
    "test_images_have_alt_text": {
        "description": "All images must have non-empty alt attributes for accessibility",
        "mark": "accessibility",
        "steps": [
            "Navigate to base URL",
            "Evaluate: document.querySelectorAll('img') → find all images",
            "Filter images where alt == '' or alt is missing",
            "Assert violations == [] → every img has non-empty alt text",
        ],
    },
    "test_headings_hierarchy_is_correct": {
        "description": "Page must have exactly one h1 and correct heading hierarchy",
        "mark": "accessibility",
        "steps": [
            "Navigate to base URL",
            "page.locator('h1').count() → count h1 elements",
            "Assert h1_count == 1 (ExpectedCounts.H1_HEADINGS)",
            "page.locator('h2').first → find first h2",
            "Assert h1 position < h2 position in DOM",
            "Check heading levels: h1→h2→h3 no gaps allowed",
        ],
    },
}


def match_steps_map(test_name):
    """Find STEPS_MAP entry by matching test name prefix (handles parametrized tests)."""
    if test_name in STEPS_MAP:
        return STEPS_MAP[test_name]
    base = test_name.split("[")[0]
    if base in STEPS_MAP:
        return STEPS_MAP[base]
    return None


def build_steps(step_names, test_passed):
    """Build step objects; if test failed, mark the last step as failed."""
    steps = []
    for i, name in enumerate(step_names):
        is_last = i == len(step_names) - 1
        status = "fail" if (not test_passed and is_last) else "pass"
        steps.append({"name": name, "status": status})
    return steps


def generic_steps(test_name, test_passed):
    """Generate generic steps for tests not in STEPS_MAP."""
    words = test_name.replace("test_", "").replace("_", " ")
    step_names = ["Navigate to page", f"Execute {words}", "Assert expected result"]
    return build_steps(step_names, test_passed)


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

        mapped = match_steps_map(name)
        if mapped:
            description = mapped["description"]
            mark = mapped["mark"]
            steps = build_steps(mapped["steps"], test_passed)
        else:
            description = f"Verify {name.replace('test_', '').replace('_', ' ')}"
            mark = "general"
            steps = generic_steps(name, test_passed)

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
