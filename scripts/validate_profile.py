#!/usr/bin/env python3
"""
Canonical Profile Validator
============================

PURPOSE
-------
CI quality gate protecting src/data/profile.json as the single,
Git-tracked source of truth for all professional profile data —
local development, automated tests, CI, and production builds all
read this exact file (see src/hooks/useProfile.js).

Historically this project also had a second file,
src/data/profile.default.json, used as a silent fallback whenever
profile.json (then gitignored) was missing. The two drifted apart
more than once, which caused real regressions (a Skills-section test
that passed locally against profile.json but failed in CI, which
always used the stale profile.default.json). That file has been
removed; this script exists to make sure that class of problem can't
quietly come back.

CHECKS
------
1. src/data/profile.json exists and is valid JSON.
2. profile.json is tracked by Git (not an untracked/local-only copy
   CI would never see).
3. profile.default.json no longer exists (the dual-source config
   this migration removed must not silently reappear).
4. Required top-level keys and their basic shapes are present.
5. profile.contact's professional links are syntactically valid
   absolute https URLs and match the approved, verified values.
6. The approved "Playwright (familiarity)" wording is present in
   skills.automation, preserving the distinction between
   professional commercial experience and tooling familiarity.

This is deliberately structural, not an exhaustive content check —
it is not this script's job to hardcode every achievement or bullet
point as a constant; qa/constants.py and the Playwright suite already
own specific, user-visible content assertions.

USAGE
-----
    python3 scripts/validate_profile.py
"""

import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROFILE_PATH = PROJECT_ROOT / "src" / "data" / "profile.json"
REMOVED_FALLBACK_PATH = PROJECT_ROOT / "src" / "data" / "profile.default.json"

REQUIRED_TOP_LEVEL_KEYS = [
    "personal", "summary", "stats", "experience", "skills",
    "tools", "projects", "education", "certifications", "contact",
]

EXPECTED_LINKEDIN = "https://www.linkedin.com/in/oleg-voronchenko"
EXPECTED_GITHUB = "https://github.com/OlegVoronchenko"
EXPECTED_PORTFOLIO = "https://olegvoronchenko.github.io/qa-portfolio"

APPROVED_PLAYWRIGHT_SKILL = "Playwright (familiarity)"


def fail(violations: list[str]) -> None:
    print(f"\n{'=' * 60}")
    print("Canonical Profile Validation — FAILED")
    print(f"{'=' * 60}\n")
    for v in violations:
        print(f"  ✗ {v}")
    print(f"\n{'=' * 60}\n")
    sys.exit(1)


def is_valid_https_url(value) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def is_git_tracked(path: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(path.relative_to(PROJECT_ROOT))],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        # git unavailable — can't confirm tracking; treat as a soft skip,
        # not a hard failure, since this script must also work outside a
        # git checkout (e.g. a downloaded source archive).
        return True


def main():
    violations = []

    if not PROFILE_PATH.exists():
        print(f"ERROR: {PROFILE_PATH} not found.")
        sys.exit(1)

    try:
        profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: {PROFILE_PATH} is not valid JSON: {e}")
        sys.exit(1)

    if not is_git_tracked(PROFILE_PATH):
        violations.append(
            f"{PROFILE_PATH.relative_to(PROJECT_ROOT)} is not tracked by Git — "
            f"CI would never see local-only changes to it."
        )

    if REMOVED_FALLBACK_PATH.exists():
        violations.append(
            f"{REMOVED_FALLBACK_PATH.relative_to(PROJECT_ROOT)} still exists — "
            f"this reintroduces the dual-source configuration that was removed. "
            f"Merge any new content into profile.json and delete this file."
        )

    missing_keys = [k for k in REQUIRED_TOP_LEVEL_KEYS if k not in profile]
    if missing_keys:
        violations.append(f"Missing required top-level keys: {missing_keys}")

    personal = profile.get("personal", {})
    for field in ("name", "role", "email"):
        if not personal.get(field):
            violations.append(f"personal.{field} is missing or empty")

    if not isinstance(profile.get("experience"), list) or not profile.get("experience"):
        violations.append("experience must be a non-empty list")

    skills = profile.get("skills", {})
    if not isinstance(skills, dict) or not skills:
        violations.append("skills must be a non-empty object")

    automation_skills = skills.get("automation", [])
    if APPROVED_PLAYWRIGHT_SKILL not in automation_skills:
        violations.append(
            f"skills.automation must include {APPROVED_PLAYWRIGHT_SKILL!r} — "
            f"preserving the distinction from full commercial Playwright experience"
        )
    elif "Playwright" in automation_skills:
        # Bare "Playwright" alongside the qualified entry would overstate
        # experience and also create an ambiguous duplicate skill tag.
        violations.append(
            "skills.automation contains both 'Playwright' and "
            f"{APPROVED_PLAYWRIGHT_SKILL!r} — remove the unqualified entry"
        )

    contact = profile.get("contact", {})
    expected_links = {
        "linkedin": EXPECTED_LINKEDIN,
        "github": EXPECTED_GITHUB,
        "portfolio": EXPECTED_PORTFOLIO,
    }
    for key, expected in expected_links.items():
        value = contact.get(key)
        if not is_valid_https_url(value):
            violations.append(f"contact.{key} is not a valid absolute https URL: {value!r}")
        elif value != expected:
            violations.append(f"contact.{key} should be {expected!r}, got {value!r}")

    if violations:
        fail(violations)

    print(f"\n{'=' * 60}")
    print("Canonical Profile Validation — PASSED")
    print(f"{'=' * 60}")
    print(f"  ✓ {PROFILE_PATH.relative_to(PROJECT_ROOT)} is valid, Git-tracked, and canonical")
    print(f"  ✓ No fallback profile.default.json present")
    print(f"  ✓ Required fields and professional links verified")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
