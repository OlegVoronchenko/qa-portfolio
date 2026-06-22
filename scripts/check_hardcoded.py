#!/usr/bin/env python3
"""
Hardcoded String Detector
=========================

PURPOSE
-------
CI quality gate that fails the build if personal data
(name, email, stats) is hardcoded in React components
instead of read from profile.json via useProfile() hook.

WHY THIS EXISTS
---------------
Updating the portfolio should require changing ONE file
(the CV) not chasing hardcoded strings across 20+ React
components. This script enforces that discipline.

ENFORCEMENT RULES
-----------------
Forbidden in src/ JSX/TSX files:
- Engineer name, email, LinkedIn, GitHub URLs
- Hardcoded stats ('15+ years', '10K+ tests', '98%')
- Tool names in static <span> elements
- Company names as text

Allowed locations:
- profile.default.json (the actual data source)
- CV_TEMPLATE.md (the template)
- ARCHITECTURE.md (documentation)
- Generated files (parsed_profile.json, test_report.json)

EXIT CODE
---------
0 — no violations found
1 — at least one hardcoded string found (CI blocks deploy)
"""

import re
import sys
from pathlib import Path

FORBIDDEN_PATTERNS = [
    (r'Oleg Voronchenko', 'Name must come from profile.personal.name'),
    (r'GlobalLogic', 'Company must come from profile.experience[].company'),
    (r'oleg\.v\.qa@gmail\.com', 'Email must come from profile.contact.email'),
    (r'linkedin\.com/in/oleg', 'LinkedIn must come from profile.contact.linkedin'),
    (r'github\.com/oleg', 'GitHub must come from profile.contact.github'),

    (r'15\+\s*years', 'Years experience must come from profile.stats'),
    (r'10K\+\s*tests', 'Test count must come from profile.stats'),
    (r'98%\s*suite', 'Suite stability must come from profile.stats'),

    (r'<span[^>]*>Java<\/span>', 'Java must come from profile.skills'),
    (r'<span[^>]*>Selenium<\/span>', 'Selenium must come from profile.skills'),
    (r'<span[^>]*>Appium<\/span>', 'Appium must come from profile.skills'),
    (r'<span[^>]*>Cypress<\/span>', 'Cypress must come from profile.skills'),
]

SKIP_PATTERNS = [
    'profile.default.json',
    'profile.json',
    'CV_TEMPLATE.md',
    'ARCHITECTURE.md',
    'generate_report.py',
    'parse_cv.py',
    'node_modules',
    'dist',
    '.git',
]


def should_skip(path: Path) -> bool:
    path_str = str(path)
    return any(skip in path_str for skip in SKIP_PATTERNS)


def check_file(path: Path) -> list:
    violations = []
    try:
        content = path.read_text(encoding='utf-8')
        for pattern, message in FORBIDDEN_PATTERNS:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                violations.append({
                    'file': str(path),
                    'line': line_num,
                    'pattern': pattern,
                    'found': match.group(),
                    'message': message,
                })
    except Exception as e:
        print(f"Warning: could not read {path}: {e}")
    return violations


def main():
    src_dir = Path(__file__).parent.parent / 'src'

    if not src_dir.exists():
        print(f"ERROR: src/ directory not found at {src_dir}")
        sys.exit(1)

    all_violations = []
    checked_files = 0

    for ext in ['*.jsx', '*.tsx', '*.js', '*.ts']:
        for path in src_dir.rglob(ext):
            if not should_skip(path):
                violations = check_file(path)
                all_violations.extend(violations)
                checked_files += 1

    print(f"\n{'='*60}")
    print(f"Hardcoded String Check — scanned {checked_files} files")
    print(f"{'='*60}")

    if not all_violations:
        print("✓ No hardcoded strings found — all clear!")
        sys.exit(0)

    print(f"\n✗ Found {len(all_violations)} hardcoded string(s):\n")
    for v in all_violations:
        print(f"  FILE:    {v['file']}")
        print(f"  LINE:    {v['line']}")
        print(f"  FOUND:   '{v['found']}'")
        print(f"  REASON:  {v['message']}")
        print()

    print(f"{'='*60}")
    print("Fix: move these values to src/data/profile.default.json")
    print("and read them via useProfile() hook in your component.")
    print(f"{'='*60}\n")
    sys.exit(1)


if __name__ == '__main__':
    main()
