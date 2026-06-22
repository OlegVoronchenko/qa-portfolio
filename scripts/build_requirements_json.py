#!/usr/bin/env python3
"""
Parse docs/requirements/REQ-*.md files into a single
requirements.json bundle for the React app.
"""

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "requirements"
OUTPUT_FILE = PROJECT_ROOT / "src" / "data" / "requirements.json"


def parse_requirement_file(path: Path) -> dict:
    """Extract REQ metadata and AC details from a markdown file."""
    content = path.read_text(encoding='utf-8')

    req_id = path.stem.split('-')[0] + '-' + path.stem.split('-')[1]
    req_id = req_id.upper()

    title_match = re.search(r'^#\s+(REQ-\d+)\s*—\s*(.+)$',
                            content, re.MULTILINE)

    req_section = re.search(
        r'## Requirement\s*\n\n(.+?)\n\n---',
        content, re.DOTALL
    )
    requirement_text = (
        req_section.group(1).strip().replace('\n', ' ')
        if req_section else ''
    )

    ac_entries = {}
    ac_pattern = re.compile(
        r'### (AC-\d+-\d+)\s*—\s*(.+?)\n(.+?)(?=\n###|\n---|\Z)',
        re.DOTALL
    )

    for match in ac_pattern.finditer(content):
        ac_id = match.group(1)
        ac_title = match.group(2).strip()
        ac_body = match.group(3).strip()

        ac_body = re.sub(r'```[\s\S]*?```', '', ac_body)
        ac_body = re.sub(r'^Rationale:\s*', 'Rationale: ',
                         ac_body, flags=re.MULTILINE)
        ac_body = ac_body.replace('\n\n', ' | ').replace('\n', ' ')
        ac_body = re.sub(r'\s+', ' ', ac_body).strip()

        ac_entries[ac_id] = {
            "id": ac_id,
            "title": ac_title,
            "description": ac_body[:500]
        }

    return {
        "id": req_id,
        "title": title_match.group(2).strip() if title_match else '',
        "requirement": requirement_text[:500],
        "acceptance_criteria": ac_entries
    }


def main():
    if not DOCS_DIR.exists():
        print(f"ERROR: {DOCS_DIR} not found")
        return

    requirements = {}

    for md_file in sorted(DOCS_DIR.glob("REQ-*.md")):
        req_data = parse_requirement_file(md_file)
        requirements[req_data['id']] = req_data
        print(f"  Parsed {md_file.name}: "
              f"{len(req_data['acceptance_criteria'])} AC entries")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(requirements, indent=2, ensure_ascii=False)
    )

    print(f"\n  Written {OUTPUT_FILE}")
    print(f"  Total requirements: {len(requirements)}")


if __name__ == '__main__':
    main()
