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
        "description": "Browser tab title must identify the engineer by name and role",
        "mark": "smoke",
        "steps": [
            "Open the portfolio page in browser",
            "Read the browser tab title",
            "Verify title contains 'Oleg'",
            "Verify title contains 'Automation'",
            "Verify title contains 'Engineer'",
        ],
    },
    "test_hero_heading_displays_name": {
        "description": "Main heading on hero section must show the engineer name",
        "mark": "smoke",
        "steps": [
            "Open the portfolio page",
            "Find the main heading (h1) on the page",
            "Read the heading text",
            "Verify heading text contains 'Oleg'",
        ],
    },
    "test_navigation_is_present": {
        "description": "Navigation bar must be visible when the page loads",
        "mark": "smoke",
        "steps": [
            "Open the portfolio page",
            "Look for the navigation bar on screen",
            "Verify at least one navigation element is found",
            "Confirm the navigation bar is visible",
        ],
    },
    "test_page_has_no_javascript_errors": {
        "description": "No JavaScript errors should appear in the browser console",
        "mark": "smoke",
        "steps": [
            "Set up a listener to catch any JS errors",
            "Open the portfolio page",
            "Wait for the page to fully load",
            "Check the collected error list",
            "Verify no JavaScript errors were thrown",
        ],
    },
    "test_react_app_hydrated_successfully": {
        "description": "React application must render visible content on screen",
        "mark": "smoke",
        "steps": [
            "Open the portfolio page",
            "Check the React root container (#root)",
            "Count the child elements inside the root",
            "Verify the root has more than 0 rendered children",
            "Confirm no React error boundary was triggered",
        ],
    },
    "test_nav_link_is_visible_with_correct_href[About-#about]": {
        "description": "About link in navbar must point to #about section",
        "mark": "navigation",
        "steps": [
            "Open the portfolio page",
            "Look for 'About' link inside the navigation bar",
            "Verify the 'About' link is visible on screen",
            "Check the link destination attribute",
            "Verify href equals '#about'",
        ],
    },
    "test_nav_link_is_visible_with_correct_href[Skills-#skills]": {
        "description": "Skills link in navbar must point to #skills section",
        "mark": "navigation",
        "steps": [
            "Open the portfolio page",
            "Look for 'Skills' link inside the navigation bar",
            "Verify the 'Skills' link is visible on screen",
            "Check the link destination attribute",
            "Verify href equals '#skills'",
        ],
    },
    "test_nav_link_is_visible_with_correct_href[Projects-#projects]": {
        "description": "Projects link in navbar must point to #projects section",
        "mark": "navigation",
        "steps": [
            "Open the portfolio page",
            "Look for 'Projects' link inside the navigation bar",
            "Verify the 'Projects' link is visible on screen",
            "Check the link destination attribute",
            "Verify href equals '#projects'",
        ],
    },
    "test_nav_link_is_visible_with_correct_href[Contact-#contact]": {
        "description": "Contact link in navbar must point to #contact section",
        "mark": "navigation",
        "steps": [
            "Open the portfolio page",
            "Look for 'Contact' link inside the navigation bar",
            "Verify the 'Contact' link is visible on screen",
            "Check the link destination attribute",
            "Verify href equals '#contact'",
        ],
    },
    "test_skills_section_contains_core_stack[Python]": {
        "description": "Python must appear as a skill tag in the Skills section",
        "mark": "content",
        "steps": [
            "Open the portfolio page",
            "Scroll to the Skills section",
            "Look for a tag with text 'Python'",
            "Verify the 'Python' skill tag is visible",
        ],
    },
    "test_skills_section_contains_core_stack[Playwright]": {
        "description": "Playwright must appear as a skill tag in the Skills section",
        "mark": "content",
        "steps": [
            "Open the portfolio page",
            "Scroll to the Skills section",
            "Look for a tag with text 'Playwright'",
            "Verify the 'Playwright' skill tag is visible",
        ],
    },
    "test_skills_section_contains_core_stack[pytest]": {
        "description": "pytest must appear as a skill tag in the Skills section",
        "mark": "content",
        "steps": [
            "Open the portfolio page",
            "Scroll to the Skills section",
            "Look for a tag with text 'pytest'",
            "Verify the 'pytest' skill tag is visible",
        ],
    },
    "test_projects_section_has_expected_cards": {
        "description": "Projects section must display exactly 3 project cards",
        "mark": "content",
        "steps": [
            "Open the portfolio page",
            "Scroll to the Projects section",
            "Count the number of project cards displayed",
            "Verify the count equals 3",
        ],
    },
    "test_contact_section_has_required_channels": {
        "description": "Contact section must show exactly 3 contact channels",
        "mark": "content",
        "steps": [
            "Open the portfolio page",
            "Scroll to the Contact section",
            "Count the number of contact links displayed",
            "Verify the count equals 3",
        ],
    },
    "test_test_results_section_renders": {
        "description": "Test results section must be visible with content",
        "mark": "content",
        "steps": [
            "Open the portfolio page",
            "Scroll to the Test Results section",
            "Confirm the section is visible on screen",
            "Look for headings inside the section",
            "Verify at least one heading exists",
        ],
    },
    "test_mobile_viewport_no_horizontal_scroll": {
        "description": "No horizontal scrollbar at 390px mobile width",
        "mark": "responsive",
        "steps": [
            "Resize browser to 390x844 (iPhone 14)",
            "Open the portfolio page",
            "Measure the total page content width",
            "Compare content width against 390px viewport",
            "Verify no horizontal overflow exists",
        ],
    },
    "test_mobile_hero_section_visible": {
        "description": "Hero heading must be visible at 390px mobile width",
        "mark": "responsive",
        "steps": [
            "Resize browser to 390x844",
            "Open the portfolio page",
            "Find the main heading (h1)",
            "Verify the heading is visible at 390px width",
        ],
    },
    "test_page_load_time_within_budget": {
        "description": "Page must finish loading in under 3000ms",
        "mark": "performance",
        "steps": [
            "Open the portfolio page",
            "Wait for the load event to complete",
            "Measure total load time in milliseconds",
            "Verify load time is under 3000ms",
        ],
    },
    "test_images_have_alt_text": {
        "description": "Every image must have descriptive alt text",
        "mark": "accessibility",
        "steps": [
            "Open the portfolio page",
            "Find all images on the page",
            "Check each image for an alt attribute",
            "Collect any images with missing or empty alt",
            "Verify no images are missing alt text",
        ],
    },
    "test_headings_hierarchy_is_correct": {
        "description": "Heading levels must follow correct order without gaps",
        "mark": "accessibility",
        "steps": [
            "Open the portfolio page",
            "Find all heading elements (h1 through h6)",
            "Verify exactly 1 h1 heading exists",
            "Confirm h1 appears before any h2",
            "Check no heading levels are skipped (e.g. h2 to h4)",
        ],
    },
    "test_assets_load_on_github_pages": {
        "description": "All CSS and JS files must load on production site",
        "mark": "deployment",
        "steps": [
            "Set up a listener to track failed network requests",
            "Open the production site on GitHub Pages",
            "Wait for all resources to finish loading",
            "Check for any 404 errors on JS or CSS files",
            "Verify the navigation bar is visible",
            "Verify the main heading is visible",
        ],
    },
    "test_base_path_is_correct": {
        "description": "Asset paths must include the /qa-portfolio/ prefix",
        "mark": "deployment",
        "steps": [
            "Open the production site on GitHub Pages",
            "Wait for all resources to finish loading",
            "Inspect all script and stylesheet paths",
            "Check for paths missing the /qa-portfolio/ prefix",
            "Verify all asset paths are correctly prefixed",
        ],
    },
    "test_no_console_errors_on_production": {
        "description": "No JavaScript errors on the production site",
        "mark": "deployment",
        "steps": [
            "Set up a listener to catch JS errors",
            "Open the production site on GitHub Pages",
            "Wait for the page to fully load",
            "Check the collected error list",
            "Verify no JavaScript errors occurred",
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
