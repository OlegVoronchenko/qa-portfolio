#!/usr/bin/env python3
"""
Test Standards Checker
======================

PURPOSE
-------
CI quality gate that enforces test code conventions:
- Every test function has a docstring
- Every test function has a @pytest.mark decorator
- No hardcoded URLs in test code (must use CONFIG.base_url)

WHY THIS EXISTS
---------------
Tests are themselves a deliverable in this portfolio.
Inconsistent or undocumented tests undermine the entire
point of demonstrating QA discipline.

ENFORCEMENT RULES
-----------------
For every function starting with 'test_':
1. Must have a docstring as the first statement
2. Must have at least one @pytest.mark.{category} decorator
3. Must not contain 'localhost:8080' or 'localhost:5173'

EXIT CODE
---------
0 — all tests meet standards
1 — at least one violation (CI blocks deploy)
"""

import ast
import sys
from pathlib import Path

QA_DIR = Path(__file__).parent.parent / 'qa'
TESTS_DIR = QA_DIR / 'tests'

REQUIRED_MARKS = {'smoke', 'navigation', 'content',
                  'responsive', 'performance',
                  'accessibility', 'deployment'}


class TestStandardsChecker(ast.NodeVisitor):
    """AST visitor that collects convention violations from test files.

    Walks the syntax tree of each test file, inspecting every
    test_* function for required docstrings, pytest marks, and
    absence of hardcoded URLs.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.violations = []
        self.current_class = None

    def visit_ClassDef(self, node):
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node):
        if not node.name.startswith('test_'):
            self.generic_visit(node)
            return

        location = f"{self.filepath}:{node.lineno} ({node.name})"

        if not (node.body and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, (ast.Constant, ast.Str))):
            self.violations.append(
                f"MISSING DOCSTRING: {location}"
            )

        marks = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Attribute):
                if (hasattr(decorator, 'attr') and
                        decorator.attr in REQUIRED_MARKS):
                    marks.append(decorator.attr)

        if not marks:
            self.violations.append(
                f"MISSING MARK: {location} "
                f"— add @pytest.mark.smoke/content/etc"
            )

        source = ast.unparse(node) if hasattr(ast, 'unparse') else ''
        hardcoded_urls = [
            'localhost:8080',
            'localhost:5173',
        ]
        for url in hardcoded_urls:
            if url in source:
                self.violations.append(
                    f"HARDCODED URL '{url}': {location} "
                    f"— use CONFIG.base_url instead"
                )

        self.generic_visit(node)


def check_file(path: Path) -> list:
    try:
        tree = ast.parse(path.read_text())
        checker = TestStandardsChecker(str(path))
        checker.visit(tree)
        return checker.violations
    except SyntaxError as e:
        return [f"SYNTAX ERROR in {path}: {e}"]


def main():
    all_violations = []
    checked = 0

    for path in TESTS_DIR.rglob('test_*.py'):
        violations = check_file(path)
        all_violations.extend(violations)
        checked += 1

    print(f"\n{'='*60}")
    print(f"Test Standards Check — scanned {checked} test files")
    print(f"{'='*60}")

    if not all_violations:
        print("✓ All tests meet required standards!")
        sys.exit(0)

    print(f"\n✗ Found {len(all_violations)} violation(s):\n")
    for v in all_violations:
        print(f"  {v}")

    print(f"\n{'='*60}")
    print("Fix all violations before merging.")
    print(f"{'='*60}\n")
    sys.exit(1)


if __name__ == '__main__':
    main()
