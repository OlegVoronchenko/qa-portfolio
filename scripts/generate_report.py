#!/usr/bin/env python3
"""Run pytest and generate test_report.json for the portfolio site."""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "reports"
DIST_DIR = ROOT / "dist"

STEPS_MAP = {
    "test_page_loads_with_correct_title": {
        "description": "Page must load and title must identify the QA engineer",
        "mark": "smoke",
        "steps": [
            "Navigate to base URL",
            "Wait for page load state",
            "Get page title",
            "Assert title contains name",
            "Assert title contains QA role",
        ],
    },
    "test_hero_heading_displays_name": {
        "description": "Hero section h1 must contain the engineer name",
        "mark": "smoke",
        "steps": [
            "Navigate to page",
            "Locate heading level 1 by role",
            "Get heading inner text",
            "Assert name present in heading",
        ],
    },
    "test_navigation_is_present": {
        "description": "Navigation landmark must be visible on all viewports",
        "mark": "smoke",
        "steps": [
            "Navigate to page",
            "Locate navigation by role",
            "Assert navigation is visible",
        ],
    },
    "test_page_has_no_javascript_errors": {
        "description": "No JavaScript console errors on page load",
        "mark": "smoke",
        "steps": [
            "Set up console error listener",
            "Navigate to page",
            "Wait for networkidle",
            "Filter error-level console messages",
            "Assert no errors found",
        ],
    },
    "test_react_app_hydrated_successfully": {
        "description": "React app must render content into #root element",
        "mark": "smoke",
        "steps": [
            "Navigate to page",
            "Locate #root element",
            "Count child elements",
            "Assert children count > 0",
        ],
    },
    "test_nav_link_is_visible_with_correct_href": {
        "description": "Each navigation link must be visible with correct anchor href",
        "mark": "navigation",
        "steps": [
            "Navigate to page",
            "Locate navigation landmark",
            "Find link by name within navigation",
            "Assert link is visible",
            "Assert href attribute matches expected anchor",
        ],
    },
    "test_skills_section_contains_core_stack": {
        "description": "Core technology skills must be visible in skills section",
        "mark": "content",
        "steps": [
            "Navigate to page",
            "Locate skills section by id",
            "Search for skill text within section",
            "Assert skill tag is visible",
        ],
    },
    "test_projects_section_has_expected_cards": {
        "description": "Projects section must display exactly 3 project cards",
        "mark": "content",
        "steps": [
            "Navigate to page",
            "Locate projects section",
            "Count project card elements",
            "Assert count equals 3",
        ],
    },
    "test_contact_section_has_required_channels": {
        "description": "Contact section must show all 4 communication channels",
        "mark": "content",
        "steps": [
            "Navigate to page",
            "Locate contact section",
            "Count contact item elements",
            "Assert count equals 4",
        ],
    },
    "test_test_results_section_renders": {
        "description": "Test results section must render summary and test rows",
        "mark": "content",
        "steps": [
            "Navigate to page",
            "Locate test results section",
            "Assert summary cards are visible",
            "Wait for test rows to render",
            "Assert at least one test row exists",
        ],
    },
    "test_mobile_viewport_no_horizontal_scroll": {
        "description": "Page must not cause horizontal overflow on mobile viewport",
        "mark": "responsive",
        "steps": [
            "Set viewport to 390x844 mobile size",
            "Navigate to page",
            "Evaluate scrollWidth vs innerWidth",
            "Assert no horizontal overflow",
        ],
    },
    "test_mobile_hero_section_visible": {
        "description": "Hero section must be fully visible on mobile viewport",
        "mark": "responsive",
        "steps": [
            "Set viewport to 390x844 mobile size",
            "Navigate to page",
            "Locate hero heading",
            "Assert heading is visible",
        ],
    },
    "test_page_load_time_within_budget": {
        "description": "Full page load must complete within 3000ms budget",
        "mark": "performance",
        "steps": [
            "Navigate to page",
            "Measure loadEventEnd via Performance API",
            "Measure navigationStart via Performance API",
            "Calculate load duration",
            "Assert duration < 3000ms",
        ],
    },
    "test_images_have_alt_text": {
        "description": "All images must have non-empty alt attributes for accessibility",
        "mark": "accessibility",
        "steps": [
            "Navigate to page",
            "Find all img elements",
            "Check alt attribute on each image",
            "Collect violations",
            "Assert no violations found",
        ],
    },
    "test_headings_hierarchy_is_correct": {
        "description": "Page must have exactly one h1 and correct heading hierarchy",
        "mark": "accessibility",
        "steps": [
            "Navigate to page",
            "Count h1 elements",
            "Assert exactly one h1 exists",
            "Verify h2 elements exist",
            "Assert no heading levels are skipped",
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
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/", "-v",
            "--json-report", "--json-report-file", str(REPORTS_DIR / "raw.json"),
        ],
        cwd=str(ROOT),
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
        print("ERROR: raw.json not found — did pytest run?")
        sys.exit(1)

    raw = json.loads(raw_path.read_text())
    tests = []
    total_duration_ms = 0

    for t in raw.get("tests", []):
        nodeid = t.get("nodeid", "")
        name = nodeid.split("::")[-1] if "::" in nodeid else nodeid
        outcome = t.get("outcome", "unknown")
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
    REPORTS_DIR.mkdir(exist_ok=True)
    print("Running tests...")
    run_tests()

    print("Generating report...")
    report = parse_report()

    for dest in (REPORTS_DIR / "test_report.json", DIST_DIR / "test_report.json"):
        dest.parent.mkdir(exist_ok=True)
        dest.write_text(json.dumps(report, indent=2))
        print(f"  -> {dest}")

    print(f"\nDone: {report['summary']['passed']}/{report['summary']['total']} passed")


if __name__ == "__main__":
    main()
