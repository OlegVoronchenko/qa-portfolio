"""Parse a CV file (PDF or DOCX) into structured profile JSON using regex patterns.

Works 100% locally — no external API or AI service required.
"""

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "src" / "data" / "profile.json"
BACKUP_PATH = PROJECT_ROOT / "cv" / "parsed_profile.json"
DEFAULT_PATH = PROJECT_ROOT / "src" / "data" / "profile.default.json"

KNOWN_SKILLS = {
    "automation": [
        "Python", "Playwright", "Cypress", "Selenium", "pytest", "unittest",
        "Robot Framework", "WebdriverIO", "Appium", "TestNG", "JUnit",
    ],
    "api_testing": [
        "Postman", "REST", "GraphQL", "httpx", "requests", "Insomnia",
        "REST Assured", "SoapUI", "curl", "Swagger", "OpenAPI",
    ],
    "cicd": [
        "GitHub Actions", "Jenkins", "GitLab CI", "Docker", "CircleCI",
        "Azure DevOps", "TeamCity", "Kubernetes", "Terraform", "Ansible",
    ],
    "reporting": [
        "Allure", "pytest-html", "TestRail", "Jira", "Zephyr", "TestLink",
        "Xray", "ReportPortal", "Grafana",
    ],
}

EMAIL_RE = re.compile(r"[\w\.\+\-]+@[\w\.\-]+\.\w+")
LINKEDIN_RE = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/([\w\-]+)")
GITHUB_RE = re.compile(r"(?:https?://)?(?:www\.)?github\.com/([\w\-]+)")
TELEGRAM_RE = re.compile(r"(?:https?://)?t\.me/([\w]+)|@([\w]{5,})")
PHONE_RE = re.compile(r"[\+]?[\d\s\-\(\)]{10,}")
PERIOD_RE = re.compile(
    r"(?i)(\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
    r"\s+\d{4}|\d{4})\s*[-–—]+\s*"
    r"(\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
    r"\s+\d{4}|\d{4}|present|current|now)"
)
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
CERT_RE = re.compile(r"(?i)(ISTQB|CTFL|CTAL|AWS|Google|Microsoft|Azure|Scrum|CSPO|PSM|PMP|SAFe)")
DEGREE_RE = re.compile(
    r"(?i)(bachelor|master|phd|doctor|bsc|msc|b\.s\.|m\.s\.|diploma|associate|mba)"
)
INSTITUTION_RE = re.compile(r"(?i)(university|college|school|institute|academy|polytechnic)")

SECTION_PATTERNS = {
    "summary": re.compile(r"(?i)^(summary|objective|profile|about\s*me|overview)\s*$"),
    "experience": re.compile(r"(?i)^(experience|employment|work\s*history|career|professional)\s*"),
    "skills": re.compile(r"(?i)^(skills|technologies|technical|competencies|tools)\s*"),
    "education": re.compile(r"(?i)^(education|academic|qualification|degree)\s*"),
    "certifications": re.compile(r"(?i)^(certif|license|accreditation)\s*"),
    "projects": re.compile(r"(?i)^(project|portfolio|work\s*sample)\s*"),
    "languages": re.compile(r"(?i)^(language|spoken)\s*"),
}


class CVParser:
    def parse(self, file_path):
        path = Path(file_path)
        if not path.exists():
            print(f"ERROR: File not found: {path}")
            sys.exit(1)

        text = self._extract_text(path)
        print(f"Extracted {len(text)} characters from {path.name}")

        sections = self._detect_sections(text)
        profile = self._build_profile(text, sections)
        return profile

    def save(self, profile):
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps(profile, indent=2, ensure_ascii=False) + "\n"
        OUTPUT_PATH.write_text(content)
        print(f"Written profile to {OUTPUT_PATH}")

        BACKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
        BACKUP_PATH.write_text(content)
        print(f"Backup written to {BACKUP_PATH}")

    def _extract_text(self, path):
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return self._extract_pdf(path)
        elif suffix == ".docx":
            return self._extract_docx(path)
        else:
            print(f"ERROR: Unsupported file type: {suffix}")
            sys.exit(1)

    def _extract_pdf(self, path):
        import pdfplumber
        parts = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    parts.append(page_text)
        return "\n\n".join(parts)

    def _extract_docx(self, path):
        import docx
        doc = docx.Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    def _detect_sections(self, text):
        lines = text.split("\n")
        sections = {}
        current_section = "header"
        current_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                current_lines.append(line)
                continue

            matched = False
            for section_name, pattern in SECTION_PATTERNS.items():
                if pattern.match(stripped):
                    if current_lines:
                        sections[current_section] = "\n".join(current_lines)
                    current_section = section_name
                    current_lines = []
                    matched = True
                    break

            if not matched:
                current_lines.append(line)

        if current_lines:
            sections[current_section] = "\n".join(current_lines)

        return sections

    def _build_profile(self, full_text, sections):
        defaults = self._load_defaults()

        personal = self._extract_personal(full_text, sections.get("header", ""))
        summary = self._extract_summary(sections.get("summary", ""))
        experience = self._extract_experience(sections.get("experience", ""))
        skills = self._extract_skills(full_text, sections.get("skills", ""))
        education = self._extract_education(sections.get("education", ""))
        certifications = self._extract_certifications(
            sections.get("certifications", "") or full_text
        )
        languages = self._extract_languages(sections.get("languages", ""))
        projects = self._extract_projects(sections.get("projects", ""))

        profile = {
            "personal": {
                "name": personal.get("name") or defaults.get("personal", {}).get("name", "Your Name"),
                "role": personal.get("role") or defaults.get("personal", {}).get("role", "QA Automation Engineer"),
                "location": personal.get("location") or defaults.get("personal", {}).get("location", ""),
                "email": personal.get("email") or "",
                "linkedin": personal.get("linkedin") or "",
                "github": personal.get("github") or "",
                "telegram": personal.get("telegram") or "",
                "availability": defaults.get("personal", {}).get("availability", "Available for hire"),
            },
            "summary": summary or defaults.get("summary", ""),
            "stats": defaults.get("stats", {
                "years_experience": "5+",
                "tests_written": "500+",
                "pass_rate": "99.2%",
            }),
            "experience": experience or defaults.get("experience", []),
            "skills": {
                "automation": skills.get("automation") or defaults.get("skills", {}).get("automation", []),
                "api_testing": skills.get("api_testing") or defaults.get("skills", {}).get("api_testing", []),
                "cicd": skills.get("cicd") or defaults.get("skills", {}).get("cicd", []),
                "reporting": skills.get("reporting") or defaults.get("skills", {}).get("reporting", []),
                "methodologies": skills.get("methodologies") or defaults.get("skills", {}).get("methodologies", []),
            },
            "tools": defaults.get("tools", []),
            "projects": projects or defaults.get("projects", []),
            "education": education or defaults.get("education", []),
            "certifications": certifications or defaults.get("certifications", []),
            "languages": languages or defaults.get("languages", []),
            "contact": {
                "email": personal.get("email") or defaults.get("contact", {}).get("email", ""),
                "github": personal.get("github") or defaults.get("contact", {}).get("github", ""),
                "linkedin": personal.get("linkedin") or defaults.get("contact", {}).get("linkedin", ""),
                "telegram": personal.get("telegram") or defaults.get("contact", {}).get("telegram", ""),
            },
        }
        return profile

    def _load_defaults(self):
        try:
            return json.loads(DEFAULT_PATH.read_text())
        except Exception:
            return {}

    def _extract_personal(self, full_text, header_text):
        personal = {}

        m = EMAIL_RE.search(full_text)
        if m:
            personal["email"] = m.group()

        m = LINKEDIN_RE.search(full_text)
        if m:
            personal["linkedin"] = f"https://linkedin.com/in/{m.group(1)}"

        m = GITHUB_RE.search(full_text)
        if m:
            personal["github"] = f"https://github.com/{m.group(1)}"

        m = TELEGRAM_RE.search(full_text)
        if m:
            username = m.group(1) or m.group(2)
            if username:
                personal["telegram"] = f"https://t.me/{username}"

        lines = [l.strip() for l in header_text.split("\n") if l.strip()]
        non_contact = []
        for line in lines:
            if EMAIL_RE.search(line) or LINKEDIN_RE.search(line) or GITHUB_RE.search(line):
                continue
            if PHONE_RE.match(line):
                continue
            if line.startswith("http"):
                continue
            non_contact.append(line)

        if non_contact:
            personal["name"] = non_contact[0]
        if len(non_contact) > 1:
            personal["role"] = non_contact[1]

        location_re = re.compile(r"(?i)(?:location|based|city|address)\s*[:|\-]\s*(.+)")
        for line in lines:
            m = location_re.match(line)
            if m:
                personal["location"] = m.group(1).strip()
                break
        if "location" not in personal:
            for line in non_contact[2:]:
                if "," in line and len(line) < 60 and not any(c.isdigit() for c in line[:3]):
                    personal["location"] = line
                    break

        return personal

    def _extract_summary(self, text):
        text = text.strip()
        if not text:
            return ""
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        return " ".join(lines)

    def _extract_experience(self, text):
        if not text.strip():
            return []

        blocks = re.split(r"\n(?=\S.*(?:\d{4}|present|current))", text, flags=re.IGNORECASE)
        experiences = []

        for block in blocks:
            block = block.strip()
            if not block:
                continue

            entry = {"company": "", "role": "", "period": "", "location": "", "description": "", "achievements": []}
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            if not lines:
                continue

            period_match = PERIOD_RE.search(block)
            if period_match:
                entry["period"] = period_match.group().strip()

            achievements = []
            desc_lines = []
            for line in lines:
                if PERIOD_RE.search(line):
                    cleaned = PERIOD_RE.sub("", line).strip(" |–—-,")
                    if cleaned:
                        if not entry["company"]:
                            parts = [p.strip() for p in re.split(r"[|–—]", cleaned) if p.strip()]
                            if parts:
                                entry["company"] = parts[0]
                            if len(parts) > 1:
                                entry["role"] = parts[1]
                    continue
                if re.match(r"^[-•▪●∙\*]\s+", line):
                    achievements.append(re.sub(r"^[-•▪●∙\*]\s+", "", line))
                elif not entry["company"] and line == line.upper() and len(line) > 3:
                    entry["company"] = line.title()
                elif not entry["role"] and any(
                    kw in line.lower() for kw in ["engineer", "developer", "analyst", "tester", "qa", "manager", "lead"]
                ):
                    entry["role"] = line
                else:
                    desc_lines.append(line)

            entry["achievements"] = achievements
            entry["description"] = " ".join(desc_lines)

            if entry["company"] or entry["role"] or entry["period"]:
                experiences.append(entry)

        return experiences

    def _extract_skills(self, full_text, skills_text):
        text = f"{skills_text}\n{full_text}"
        found = {"automation": [], "api_testing": [], "cicd": [], "reporting": [], "methodologies": []}

        for category, known in KNOWN_SKILLS.items():
            for skill in known:
                if re.search(re.escape(skill), text, re.IGNORECASE):
                    if skill not in found[category]:
                        found[category].append(skill)

        return found

    def _extract_education(self, text):
        if not text.strip():
            return []

        entries = []
        blocks = re.split(r"\n(?=\S)", text)

        for block in blocks:
            block = block.strip()
            if not block or len(block) < 10:
                continue

            entry = {"institution": "", "degree": "", "period": "", "location": ""}
            lines = [l.strip() for l in block.split("\n") if l.strip()]

            for line in lines:
                if INSTITUTION_RE.search(line) and not entry["institution"]:
                    entry["institution"] = line.strip(" |–—-,:")
                elif DEGREE_RE.search(line) and not entry["degree"]:
                    entry["degree"] = re.sub(r"(?i)^degree\s*[:|\-]\s*", "", line).strip()

                period_m = PERIOD_RE.search(line)
                if period_m and not entry["period"]:
                    entry["period"] = period_m.group().strip()

            if not entry["institution"] and lines:
                entry["institution"] = lines[0]

            if entry["institution"] or entry["degree"]:
                entries.append(entry)

        return entries

    def _extract_certifications(self, text):
        if not text.strip():
            return []

        certs = []
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        for line in lines:
            m = CERT_RE.search(line)
            if m:
                cert = {"name": "", "issuer": "", "year": ""}
                cleaned = re.sub(r"^[-•▪●∙\*]\s+", "", line).strip()
                parts = re.split(r"\s*[-–—,|]\s*", cleaned)
                cert["name"] = parts[0].strip()
                if len(parts) > 1:
                    cert["issuer"] = parts[1].strip()
                year_m = YEAR_RE.search(line)
                if year_m:
                    cert["year"] = year_m.group()
                certs.append(cert)

        return certs

    def _extract_languages(self, text):
        if not text.strip():
            return []

        langs = []
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        level_re = re.compile(
            r"(?i)(native|fluent|professional|intermediate|basic|advanced|"
            r"b1|b2|c1|c2|a1|a2|beginner|conversational|upper.?intermediate)"
        )

        for line in lines:
            cleaned = re.sub(r"^[-•▪●∙\*]\s+", "", line).strip()
            level_m = level_re.search(cleaned)
            if level_m:
                lang_name = cleaned[:level_m.start()].strip(" -–—:,|")
                if lang_name and len(lang_name) < 30:
                    langs.append({"language": lang_name, "level": level_m.group().strip()})
            elif "—" in cleaned or "–" in cleaned or " - " in cleaned:
                parts = re.split(r"\s*[-–—]\s*", cleaned, maxsplit=1)
                if len(parts) == 2 and len(parts[0]) < 30:
                    langs.append({"language": parts[0].strip(), "level": parts[1].strip()})

        return langs

    def _extract_projects(self, text):
        if not text.strip():
            return []

        projects = []
        blocks = re.split(r"\n(?=\S)", text)

        for block in blocks:
            block = block.strip()
            if not block or len(block) < 10:
                continue

            lines = [l.strip() for l in block.split("\n") if l.strip()]
            if not lines:
                continue

            project = {
                "name": lines[0].strip(" |–—-,:"),
                "type": "Live Demo",
                "description": "",
                "stack": [],
                "metrics": [],
            }

            desc_lines = []
            for line in lines[1:]:
                if re.match(r"^[-•▪●∙\*]\s+", line):
                    desc_lines.append(re.sub(r"^[-•▪●∙\*]\s+", "", line))
                elif re.search(r"(?i)stack|tech|tools", line):
                    techs = re.split(r"[,;]\s*", re.sub(r"(?i)^.*?:\s*", "", line))
                    project["stack"] = [t.strip() for t in techs if t.strip()]
                else:
                    desc_lines.append(line)

            project["description"] = " ".join(desc_lines)
            if "api" in project["name"].lower() or "api" in project["description"].lower():
                project["type"] = "API Testing"
            elif "e2e" in project["name"].lower() or "end" in project["name"].lower():
                project["type"] = "E2E Testing"

            projects.append(project)

        return projects


if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not file_path:
        print("Usage: python parse_cv.py <path_to_cv>")
        sys.exit(1)
    parser = CVParser()
    profile = parser.parse(file_path)
    parser.save(profile)
