#!/usr/bin/env python3
"""
Test Metadata Contract Validator
=================================

PURPOSE
-------
CI quality gate that checks the generated test_report.json against
the project's metadata contract: every test must carry a real Test
Case ID, a Requirement ID that resolves in src/data/requirements.json,
Acceptance Criteria IDs that resolve under that requirement, a known
test type (mark), and a non-empty step list.

WHY THIS EXISTS
---------------
scripts/generate_report.py silently falls back to placeholder
metadata (tc_id='TC-???', req_id=None, mark='unknown', steps=[])
whenever a pytest nodeid doesn't match a STEPS_MAP entry. That
happens whenever the nodeid format changes underneath it — e.g. a
pytest-playwright upgrade injecting an extra [browser_name]
parametrize segment into every test, which is exactly what broke
Test ID / Requirement traceability across the whole suite.

This script turns that silent fallback into a hard, specific CI
failure instead of a report that quietly ships broken metadata.

EXIT CODE
---------
0 — every test resolves full, traceable metadata
1 — at least one test is missing Test ID / Requirement traceability
"""

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from generate_report import normalize_test_name  # noqa: E402

REQUIREMENTS_PATH = PROJECT_ROOT / "src" / "data" / "requirements.json"
REPORT_CANDIDATES = [
    PROJECT_ROOT / "dist" / "test_report.json",
    PROJECT_ROOT / "qa" / "reports" / "test_report.json",
]

TC_ID_PATTERN = re.compile(r"^TC-\d{3}-\d+$")
REQ_ID_PATTERN = re.compile(r"^REQ-\d{3}$")


def load_report():
    for path in REPORT_CANDIDATES:
        if path.exists():
            return json.loads(path.read_text()), path
    print(
        "ERROR: no test_report.json found in dist/ or qa/reports/. "
        "Run scripts/generate_report.py first.",
        file=sys.stderr,
    )
    sys.exit(1)


def load_requirements():
    if not REQUIREMENTS_PATH.exists():
        print(
            f"ERROR: {REQUIREMENTS_PATH} not found — run "
            f"scripts/build_requirements_json.py first.",
            file=sys.stderr,
        )
        sys.exit(1)
    return json.loads(REQUIREMENTS_PATH.read_text())


def validate(report: dict, requirements: dict) -> list:
    violations = []
    seen_tc_ids = {}

    for test in report.get("tests", []):
        name = test.get("name", "<unknown>")
        tc_id = test.get("tc_id")
        req_id = test.get("req_id")
        ac_ids = test.get("ac_ids") or []
        mark = test.get("mark")
        steps = test.get("steps") or []

        if not tc_id or tc_id == "TC-???" or not TC_ID_PATTERN.match(tc_id):
            violations.append(
                f"{name}: missing/invalid Test ID (got {tc_id!r}). "
                f"STEPS_MAP has no entry for this nodeid or its "
                f"browser-normalized form ({normalize_test_name(name)!r}); "
                f"add one in scripts/generate_report.py."
            )
        elif tc_id in seen_tc_ids:
            violations.append(
                f"{name}: duplicate Test ID {tc_id!r} "
                f"(already used by {seen_tc_ids[tc_id]!r})"
            )
        else:
            seen_tc_ids[tc_id] = name

        if not req_id:
            violations.append(f"{name}: missing Requirement ID")
        elif not REQ_ID_PATTERN.match(req_id):
            violations.append(f"{name}: malformed Requirement ID {req_id!r}")
        elif req_id not in requirements:
            violations.append(
                f"{name}: Requirement ID {req_id!r} does not exist in "
                f"src/data/requirements.json"
            )
        else:
            known_acs = requirements[req_id].get("acceptance_criteria", {})
            for ac_id in ac_ids:
                if ac_id not in known_acs:
                    violations.append(
                        f"{name}: Acceptance Criterion {ac_id!r} not found "
                        f"under {req_id!r} in requirements.json"
                    )

        if not mark or mark == "unknown":
            violations.append(f"{name}: test type/mark is unknown")

        if not steps:
            violations.append(f"{name}: no test steps recorded")

    return violations


def main():
    report, report_path = load_report()
    requirements = load_requirements()
    violations = validate(report, requirements)

    print(f"\n{'=' * 60}")
    print(f"Test Metadata Contract Check — {report_path}")
    print(f"Checked {len(report.get('tests', []))} test(s)")
    print(f"{'=' * 60}")

    if not violations:
        print("✓ All tests carry complete, traceable metadata!")
        sys.exit(0)

    print(f"\n✗ Found {len(violations)} violation(s):\n")
    for v in violations:
        print(f"  - {v}")
    print(f"\n{'=' * 60}")
    print(
        "Fix STEPS_MAP (scripts/generate_report.py) or "
        "docs/requirements/*.md before merging."
    )
    print(f"{'=' * 60}\n")
    sys.exit(1)


if __name__ == "__main__":
    main()
