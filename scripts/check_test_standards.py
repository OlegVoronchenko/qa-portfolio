#!/usr/bin/env python3
"""
Test standards checker for qa/ module.
Verifies tests follow project conventions.
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
