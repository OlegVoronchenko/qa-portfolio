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
            "Read page title from browser tab",
            "Assert title contains engineer name",
            "Assert title contains role keyword",
            "Assert title contains type keyword",
        ],
    },
    "test_hero_heading_displays_name": {
        "description": "Hero section h1 must contain the engineer name",
        "mark": "smoke",
        "steps": [
            "Get h1 heading text content",
            "Assert name present in heading",
        ],
    },
    "test_navigation_is_present": {
        "description": "Navigation landmark must be visible on page load",
        "mark": "smoke",
        "steps": [
            "Locate navigation by ARIA role",
            "Count navigation elements",
            "Assert navigation is visible",
        ],
    },
    "test_page_has_no_javascript_errors": {
        "description": "No JavaScript console errors during page load",
        "mark": "smoke",
        "steps": [
            "Attach JavaScript error listener",
            "Navigate to page and wait for network idle",
            "Assert no errors captured",
        ],
    },
    "test_react_app_hydrated_successfully": {
        "description": "React app must render content into #root element",
        "mark": "smoke",
        "steps": [
            "Count #root child elements",
            "Get innerHTML preview for diagnostics",
            "Assert children count > 0",
            "Check for React error boundary",
            "Assert no error boundary rendered",
        ],
    },
    "test_nav_link_is_visible_with_correct_href": {
        "description": "Each navigation link must be visible with correct anchor href",
        "mark": "navigation",
        "steps": [
            "Locate nav link by name",
            "Assert link is visible",
            "Assert href attribute matches expected anchor",
        ],
    },
    "test_skills_section_contains_core_stack": {
        "description": "Core technology skills must be visible in skills section",
        "mark": "content",
        "steps": [
            "Locate skill tag with exact text match",
            "Assert skill tag is visible",
        ],
    },
    "test_projects_section_has_expected_cards": {
        "description": "Projects section must display exactly 3 project cards",
        "mark": "content",
        "steps": [
            "Count project cards with role='article'",
            "Assert count equals 3",
        ],
    },
    "test_contact_section_has_required_channels": {
        "description": "Contact section must show all 3 communication channels",
        "mark": "content",
        "steps": [
            "Count contact links with role='link'",
            "Assert count equals 3",
        ],
    },
    "test_test_results_section_renders": {
        "description": "Test results section must render with heading content",
        "mark": "content",
        "steps": [
            "Locate test results section by ID",
            "Assert section is visible",
            "Count headings in section",
            "Assert at least 1 heading exists",
        ],
    },
    "test_mobile_viewport_no_horizontal_scroll": {
        "description": "Page must not cause horizontal overflow on mobile viewport",
        "mark": "responsive",
        "steps": [
            "Measure document scroll width",
            "Get viewport width (390px)",
            "Assert no horizontal overflow",
        ],
    },
    "test_mobile_hero_section_visible": {
        "description": "Hero section must be fully visible on mobile viewport",
        "mark": "responsive",
        "steps": [
            "Set viewport to 390x844 mobile size",
            "Locate hero heading",
            "Assert heading is visible at mobile width",
        ],
    },
    "test_page_load_time_within_budget": {
        "description": "Full page load must complete within 3000ms budget",
        "mark": "performance",
        "steps": [
            "Navigate and wait for load event",
            "Measure load time via Navigation Timing API",
            "Assert load time < 3000ms",
        ],
    },
    "test_images_have_alt_text": {
        "description": "All images must have non-empty alt attributes for accessibility",
        "mark": "accessibility",
        "steps": [
            "Find all <img> elements on page",
            "Check alt attribute on each image",
            "Assert no violations found",
        ],
    },
    "test_headings_hierarchy_is_correct": {
        "description": "Page must have exactly one h1 and correct heading hierarchy",
        "mark": "accessibility",
        "steps": [
            "Collect all heading elements",
            "Assert exactly one h1 exists",
            "Assert h1 appears before first h2",
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
