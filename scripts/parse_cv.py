"""Parse a CV file (PDF or DOCX) into structured profile JSON using Claude AI."""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CV_DIR = PROJECT_ROOT / "cv"
OUTPUT_PATH = PROJECT_ROOT / "src" / "data" / "profile.json"
BACKUP_PATH = CV_DIR / "parsed_profile.json"

SCHEMA = {
    "personal": {
        "name": "", "role": "", "location": "", "email": "",
        "linkedin": "", "github": "", "telegram": "", "availability": "",
    },
    "summary": "",
    "stats": {"years_experience": "", "tests_written": "", "pass_rate": ""},
    "experience": [{"company": "", "role": "", "period": "", "location": "", "description": "", "achievements": []}],
    "skills": {"automation": [], "api_testing": [], "cicd": [], "reporting": [], "methodologies": []},
    "tools": [{"category": "", "items": []}],
    "projects": [{"name": "", "type": "", "description": "", "stack": [], "metrics": []}],
    "education": [{"institution": "", "degree": "", "period": "", "location": ""}],
    "certifications": [{"name": "", "issuer": "", "year": ""}],
    "languages": [{"language": "", "level": ""}],
    "contact": {"email": "", "github": "", "linkedin": "", "telegram": ""},
}


def find_cv_file() -> Path | None:
    """Find the best CV file in cv/ directory. Prefers PDF over DOCX."""
    if not CV_DIR.exists():
        return None
    pdfs = list(CV_DIR.glob("*.pdf"))
    if pdfs:
        return pdfs[0]
    docx_files = list(CV_DIR.glob("*.docx"))
    if docx_files:
        return docx_files[0]
    return None


def extract_text_from_pdf(path: Path) -> str:
    import pdfplumber
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n\n".join(text_parts)


def extract_text_from_docx(path: Path) -> str:
    import docx
    doc = docx.Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(path)
    elif suffix == ".docx":
        return extract_text_from_docx(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def parse_with_claude(cv_text: str) -> dict:
    from anthropic import Anthropic

    client = Anthropic()
    prompt = (
        "Parse this CV text and extract information into this exact JSON schema. "
        "Return only valid JSON, no markdown, no explanation.\n\n"
        f"Schema:\n{json.dumps(SCHEMA, indent=2)}\n\n"
        f"CV Text:\n{cv_text}"
    )

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(raw)


def main():
    cv_file = find_cv_file()
    if not cv_file:
        print("No CV file found in cv/ directory")
        sys.exit(1)

    print(f"Parsing CV: {cv_file.name}")
    cv_text = extract_text(cv_file)
    print(f"Extracted {len(cv_text)} characters")

    profile = parse_with_claude(cv_text)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n")
    print(f"Written profile to {OUTPUT_PATH}")

    BACKUP_PATH.write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n")
    print(f"Backup written to {BACKUP_PATH}")


if __name__ == "__main__":
    main()
