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
    for t in raw.get("tests", []):
        nodeid = t.get("nodeid", "")
        name = nodeid.split("::")[-1] if "::" in nodeid else nodeid
        outcome = t.get("outcome", "unknown")
        duration = t.get("call", {}).get("duration", 0)
        tests.append({
            "name": name,
            "status": "passed" if outcome == "passed" else "failed",
            "duration": f"{duration:.3f}s",
        })

    report = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "total": len(tests),
        "passed": sum(1 for t in tests if t["status"] == "passed"),
        "failed": sum(1 for t in tests if t["status"] == "failed"),
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
        dest.write_text(json.dumps(report, indent=2))
        print(f"  -> {dest}")

    print(f"\nDone: {report['passed']}/{report['total']} passed")


if __name__ == "__main__":
    main()
