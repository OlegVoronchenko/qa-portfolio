#!/usr/bin/env python3
"""
SEO & Discoverability Validator
================================

PURPOSE
-------
CI quality gate that inspects the PRODUCTION BUILD OUTPUT (dist/),
not the source files, and fails loudly if any required SEO signal
is missing, duplicated, or inconsistent with the approved
professional positioning (title, meta description, canonical URL,
Open Graph, Twitter Card, JSON-LD Person schema, sitemap.xml,
robots.txt).

WHY STATIC, NOT BROWSER-BASED
-------------------------------
All of this lives in <head> of the pre-rendered HTML shell and in
two plain text/XML files — none of it requires executing JavaScript
or launching a browser. A static parse is faster, more deterministic,
and catches build-time regressions (e.g. Vite base-path rewriting
breaking an absolute URL) that a live Playwright check wouldn't add
value over. Navigation/CV-link behavior is already covered by the
existing Playwright suite (qa/tests/test_portfolio.py) and is
intentionally NOT duplicated here.

ASSET BASE PATH vs PUBLIC CANONICAL URL
-----------------------------------------
These are two different things and must not be confused:
  - The asset base path (Vite's `base`, set via VITE_BASE_PATH) only
    affects how script/link src/href attributes are rewritten in the
    built HTML — it varies between a local-root build ("/") and the
    GitHub Pages production build ("/qa-portfolio/").
  - The public canonical URL (canonical link, og:url, og:image,
    twitter:image, sitemap <loc>, JSON-LD url) is always the real,
    absolute production URL, hardcoded in index.html — it never
    changes with the asset base path, in either mode.
This script validates the canonical URL set unconditionally in both
modes, and validates the asset base path against what --mode expects.

MODES
-----
--mode production (default): asserts the detected asset base path is
    exactly "/qa-portfolio/" — the real GitHub Pages path. Use this
    for the build CI actually ships (VITE_BASE_PATH=/qa-portfolio/).
--mode local: asserts the detected asset base path is internally
    consistent (every script/link reference uses the same prefix —
    catches a genuinely broken build) without requiring it to match
    the production path. Use this for a plain `npm run build` /
    `npm run dev` build (VITE_BASE_PATH unset, defaults to "/").

The mode is an explicit flag, never inferred from whatever
VITE_BASE_PATH happens to be left set in the current shell — the
actual base path used is independently detected from the built
dist/index.html itself (the same technique qa/conftest.py already
uses to find the local test server's base path).

USAGE
-----
    python3 scripts/validate_seo.py                    # --mode production (default)
    python3 scripts/validate_seo.py --mode local
    python3 scripts/validate_seo.py --mode production

Run AFTER `npm run build` — exits 1 with no dist/ build.
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
EXPECTED_PRODUCTION_BASE_PATH = "/qa-portfolio/"

PRODUCTION_URL = "https://olegvoronchenko.github.io/qa-portfolio/"
PRODUCTION_ORIGIN = "https://olegvoronchenko.github.io"
EXPECTED_LINKEDIN = "https://www.linkedin.com/in/oleg-voronchenko"
EXPECTED_GITHUB = "https://github.com/OlegVoronchenko"

EXPECTED_TITLE = "Oleg Voronchenko | Lead Test Automation Engineer & Senior SDET"
EXPECTED_DESCRIPTION = (
    "Lead Test Automation Engineer and Senior SDET with 15+ years of "
    "experience in automation architecture, engineering leadership, "
    "Java, Python, C#/.NET, healthcare, medical devices, and "
    "AI-assisted engineering."
)


class HeadParser(HTMLParser):
    """Collects <title>, <meta>, <link>, and inline <script> content.

    Deliberately not a full HTML validator — just enough structure
    to assert on duplicates and attribute values without a new
    third-party HTML/XML dependency.
    """

    def __init__(self):
        super().__init__()
        self.titles: list[str] = []
        self.metas: list[dict] = []
        self.links: list[dict] = []
        self.script_srcs: list[str] = []
        self.ld_json_scripts: list[str] = []
        self._in_title = False
        self._in_ld_json = False
        self._buffer = ""

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == "title":
            self._in_title = True
            self._buffer = ""
        elif tag == "meta":
            self.metas.append(attr_dict)
        elif tag == "link":
            self.links.append(attr_dict)
        elif tag == "script":
            if attr_dict.get("src"):
                self.script_srcs.append(attr_dict["src"])
            if attr_dict.get("type") == "application/ld+json":
                self._in_ld_json = True
                self._buffer = ""

    def handle_endtag(self, tag):
        if tag == "title" and self._in_title:
            self.titles.append(self._buffer.strip())
            self._in_title = False
        elif tag == "script" and self._in_ld_json:
            self.ld_json_scripts.append(self._buffer.strip())
            self._in_ld_json = False

    def handle_data(self, data):
        if self._in_title or self._in_ld_json:
            self._buffer += data


def detect_base_path(script_srcs: list[str]) -> str | None:
    """Detect the Vite asset base path from a built HTML's script src,
    e.g. "/qa-portfolio/assets/index-abc123.js" -> "/qa-portfolio/".
    Mirrors qa/conftest.py's _detect_base_path(), which uses the same
    technique to find the local test server's base path. Returns "/"
    for a root build, or None if no recognizable asset script is found.
    """
    for src in script_srcs:
        match = re.search(r'^(/[^"]*?)/assets/', src)
        if match:
            return match.group(1) + "/"
    for src in script_srcs:
        if src.startswith("/"):
            return "/"
    return None


def all_asset_references(script_srcs: list[str], links: list[dict]) -> list[str]:
    """All src/href values that Vite rewrites for the configured base
    path (JS bundle, stylesheet, favicon) — excludes canonical/OG/
    Twitter links and absolute https:// URLs, which are never
    base-path-relative."""
    refs = list(script_srcs)
    for link in links:
        href = link.get("href", "")
        if href.startswith("/") and not href.startswith("//"):
            refs.append(href)
    return refs


def fail(violations: list[str]) -> None:
    print(f"\n{'=' * 60}")
    print("SEO Validation — FAILED")
    print(f"{'=' * 60}\n")
    for v in violations:
        print(f"  ✗ {v}")
    print(f"\n{'=' * 60}\n")
    sys.exit(1)


def meta_by_name(metas, key, value):
    return [m for m in metas if m.get(key) == value]


def main():
    parser_args = argparse.ArgumentParser(description=__doc__)
    parser_args.add_argument(
        "--mode",
        choices=["local", "production"],
        default="production",
        help="'production' (default) requires the real GitHub Pages asset "
             "base path; 'local' only requires internal consistency.",
    )
    args = parser_args.parse_args()

    violations = []

    index_path = DIST_DIR / "index.html"
    if not index_path.exists():
        print(f"ERROR: {index_path} not found. Run `npm run build` first.")
        sys.exit(1)

    html = index_path.read_text(encoding="utf-8")
    parser = HeadParser()
    parser.feed(html)

    # ── Title ──
    if len(parser.titles) != 1:
        violations.append(f"Expected exactly 1 <title>, found {len(parser.titles)}")
    elif parser.titles[0] != EXPECTED_TITLE:
        violations.append(
            f"<title> mismatch.\n      expected: {EXPECTED_TITLE!r}\n      actual:   {parser.titles[0]!r}"
        )

    # ── Meta description ──
    descriptions = meta_by_name(parser.metas, "name", "description")
    if len(descriptions) != 1:
        violations.append(f"Expected exactly 1 meta description, found {len(descriptions)}")
    elif descriptions[0].get("content", "").strip() != EXPECTED_DESCRIPTION:
        violations.append("meta[name=description] content does not match the approved description")

    # ── Canonical ──
    canonicals = [l for l in parser.links if l.get("rel") == "canonical"]
    if len(canonicals) != 1:
        violations.append(f"Expected exactly 1 canonical <link>, found {len(canonicals)}")
    elif canonicals[0].get("href") != PRODUCTION_URL:
        violations.append(f"canonical href should be {PRODUCTION_URL!r}, got {canonicals[0].get('href')!r}")

    # ── Open Graph (each property must appear exactly once) ──
    required_og = {
        "og:type": "website",
        "og:title": EXPECTED_TITLE,
        "og:description": EXPECTED_DESCRIPTION,
        "og:url": PRODUCTION_URL,
        "og:image": PRODUCTION_URL + "og-image.png",
    }
    for prop, expected_value in required_og.items():
        matches = meta_by_name(parser.metas, "property", prop)
        if len(matches) != 1:
            violations.append(f"Expected exactly 1 meta[property={prop}], found {len(matches)}")
        elif matches[0].get("content", "").strip() != expected_value:
            violations.append(
                f"meta[property={prop}] mismatch.\n      expected: {expected_value!r}\n      actual:   {matches[0].get('content')!r}"
            )

    for prop in ("og:image:alt", "og:image:width", "og:image:height", "og:site_name"):
        matches = meta_by_name(parser.metas, "property", prop)
        if len(matches) != 1 or not matches[0].get("content", "").strip():
            violations.append(f"Expected exactly 1 non-empty meta[property={prop}], found {len(matches)}")

    # ── Twitter Card ──
    required_twitter = {
        "twitter:card": "summary_large_image",
        "twitter:title": EXPECTED_TITLE,
        "twitter:description": EXPECTED_DESCRIPTION,
        "twitter:image": PRODUCTION_URL + "og-image.png",
    }
    for name, expected_value in required_twitter.items():
        matches = meta_by_name(parser.metas, "name", name)
        if len(matches) != 1:
            violations.append(f"Expected exactly 1 meta[name={name}], found {len(matches)}")
        elif matches[0].get("content", "").strip() != expected_value:
            violations.append(
                f"meta[name={name}] mismatch.\n      expected: {expected_value!r}\n      actual:   {matches[0].get('content')!r}"
            )

    # ── JSON-LD Person ──
    if len(parser.ld_json_scripts) != 1:
        violations.append(
            f"Expected exactly 1 application/ld+json script, found {len(parser.ld_json_scripts)}"
        )
    else:
        try:
            data = json.loads(parser.ld_json_scripts[0])
        except json.JSONDecodeError as e:
            violations.append(f"JSON-LD is not valid JSON: {e}")
            data = None

        if data is not None:
            if data.get("@context") != "https://schema.org":
                violations.append("JSON-LD @context must be 'https://schema.org'")
            if data.get("@type") != "Person":
                violations.append("JSON-LD @type must be 'Person'")
            if data.get("name") != "Oleg Voronchenko":
                violations.append("JSON-LD name must be 'Oleg Voronchenko'")
            if data.get("url") != PRODUCTION_URL:
                violations.append(f"JSON-LD url must be {PRODUCTION_URL!r}")
            if not data.get("jobTitle"):
                violations.append("JSON-LD jobTitle is missing")
            if not data.get("description"):
                violations.append("JSON-LD description is missing")

            same_as = data.get("sameAs", [])
            if EXPECTED_LINKEDIN not in same_as:
                violations.append(f"JSON-LD sameAs must include {EXPECTED_LINKEDIN!r}")
            if EXPECTED_GITHUB not in same_as:
                violations.append(f"JSON-LD sameAs must include {EXPECTED_GITHUB!r}")
            for url in same_as:
                if not url.startswith("https://"):
                    violations.append(f"JSON-LD sameAs entry is not an absolute https URL: {url!r}")

            if not isinstance(data.get("knowsAbout"), list) or not data["knowsAbout"]:
                violations.append("JSON-LD knowsAbout must be a non-empty list")

    # ── No conflicting duplicate professional links in <head> ──
    all_hrefs_and_content = [l.get("href", "") for l in parser.links] + [
        m.get("content", "") for m in parser.metas
    ]
    bad_github_refs = [
        v for v in all_hrefs_and_content
        if "github.com" in v and v != EXPECTED_GITHUB and "og-image" not in v
    ]
    if bad_github_refs:
        violations.append(f"Found GitHub reference(s) that don't match {EXPECTED_GITHUB!r}: {bad_github_refs}")

    # ── Asset base path (NOT the public canonical URL — see module
    #    docstring) — detected from the build itself, not from
    #    whatever VITE_BASE_PATH happens to be set in the shell ──
    asset_refs = all_asset_references(parser.script_srcs, parser.links)
    detected_base = detect_base_path(parser.script_srcs)

    if detected_base is None:
        violations.append("Could not detect an asset base path from any <script src> in dist/index.html")
    elif args.mode == "production":
        if detected_base != EXPECTED_PRODUCTION_BASE_PATH:
            violations.append(
                f"Production build must use asset base path {EXPECTED_PRODUCTION_BASE_PATH!r}, "
                f"detected {detected_base!r}. Build with VITE_BASE_PATH={EXPECTED_PRODUCTION_BASE_PATH}."
            )
        mismatched = [r for r in asset_refs if not r.startswith(detected_base)]
        if mismatched:
            violations.append(f"Asset reference(s) not using the production base path: {mismatched}")
    else:  # local
        mismatched = [r for r in asset_refs if not r.startswith(detected_base)]
        if mismatched:
            violations.append(
                f"Inconsistent asset base path in local build — detected {detected_base!r} "
                f"but found reference(s) not using it: {mismatched}"
            )

    # ── noscript fallback present ──
    if "<noscript>" not in html:
        violations.append("Expected a <noscript> fallback block for non-JS crawlers")

    # ── sitemap.xml ──
    sitemap_path = DIST_DIR / "sitemap.xml"
    if not sitemap_path.exists():
        violations.append("dist/sitemap.xml not found")
    else:
        try:
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            root = ET.fromstring(sitemap_path.read_text(encoding="utf-8"))
            locs = [el.text.strip() for el in root.findall("sm:url/sm:loc", ns) if el.text]
            if locs != [PRODUCTION_URL]:
                violations.append(
                    f"sitemap.xml should contain exactly one <loc>{PRODUCTION_URL}</loc>, found {locs}"
                )
            for loc in locs:
                if "#" in loc:
                    violations.append(f"sitemap.xml must not list fragment identifiers as pages: {loc}")
                if loc.lower().endswith(".pdf"):
                    violations.append(f"sitemap.xml must not list CV PDFs as pages: {loc}")
            if root.findall("sm:url/sm:lastmod", ns):
                violations.append("sitemap.xml should omit <lastmod> rather than risk a misleading date")
        except ET.ParseError as e:
            violations.append(f"sitemap.xml is not valid XML: {e}")

    # ── robots.txt ──
    robots_path = DIST_DIR / "robots.txt"
    if not robots_path.exists():
        violations.append("dist/robots.txt not found")
    else:
        robots = robots_path.read_text(encoding="utf-8")
        if not re.search(r"(?im)^Sitemap:\s*" + re.escape(PRODUCTION_URL) + "sitemap.xml", robots):
            violations.append("robots.txt must reference the absolute sitemap URL")
        if re.search(r"(?im)^Disallow:\s*/\s*$", robots):
            violations.append("robots.txt disallows the entire site — indexing would be blocked")

    # ── og-image.png exists and is the right shape ──
    og_image_path = DIST_DIR / "og-image.png"
    if not og_image_path.exists():
        violations.append("dist/og-image.png not found")
    else:
        try:
            from PIL import Image
            with Image.open(og_image_path) as img:
                if img.size != (1200, 630):
                    violations.append(f"og-image.png should be 1200x630, got {img.size}")
        except ImportError:
            pass  # Pillow not required for this script to be useful elsewhere

    if violations:
        fail(violations)

    print(f"\n{'=' * 60}")
    print(f"SEO Validation — PASSED (--mode {args.mode})")
    print(f"{'=' * 60}")
    print(f"  ✓ Title, description, canonical, Open Graph, Twitter Card")
    print(f"  ✓ JSON-LD Person schema valid")
    print(f"  ✓ sitemap.xml / robots.txt present and consistent")
    print(f"  ✓ og-image.png present at 1200x630")
    print(f"  ✓ Asset base path: {detected_base!r}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
