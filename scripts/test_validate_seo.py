#!/usr/bin/env python3
"""
Unit tests for scripts/validate_seo.py's base-path detection logic.

Covers the local-root vs production-base distinction added to fix a
real bug: the validator used to assume the production base path
unconditionally and would reject a perfectly valid local-root build.
These tests exercise the pure detection functions directly with
synthetic input, so they don't require an actual `npm run build`.

Run: python3 scripts/test_validate_seo.py
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_seo import detect_base_path, all_asset_references  # noqa: E402


class DetectBasePathTests(unittest.TestCase):
    def test_root_build(self):
        self.assertEqual(detect_base_path(["/assets/index-abc123.js"]), "/")

    def test_production_build(self):
        self.assertEqual(
            detect_base_path(["/qa-portfolio/assets/index-abc123.js"]),
            "/qa-portfolio/",
        )

    def test_no_script_src(self):
        self.assertIsNone(detect_base_path([]))

    def test_relative_script_src_not_detected_as_root(self):
        # A script without a leading "/" isn't a recognizable Vite
        # asset reference — must not be misread as a root build.
        self.assertIsNone(detect_base_path(["main.jsx"]))


class AllAssetReferencesTests(unittest.TestCase):
    def test_includes_script_and_root_relative_links(self):
        refs = all_asset_references(
            script_srcs=["/qa-portfolio/assets/index-abc.js"],
            links=[
                {"rel": "icon", "href": "/qa-portfolio/favicon.svg"},
                {"rel": "canonical", "href": "https://olegvoronchenko.github.io/qa-portfolio/"},
            ],
        )
        self.assertIn("/qa-portfolio/assets/index-abc.js", refs)
        self.assertIn("/qa-portfolio/favicon.svg", refs)

    def test_excludes_absolute_https_links(self):
        # Canonical/OG/Twitter links are never base-path-relative and
        # must never be treated as asset references.
        refs = all_asset_references(
            script_srcs=[],
            links=[
                {"rel": "canonical", "href": "https://olegvoronchenko.github.io/qa-portfolio/"},
            ],
        )
        self.assertEqual(refs, [])

    def test_detects_mismatched_reference_for_local_mode_consistency_check(self):
        # Simulates a broken build where one asset got the wrong prefix.
        refs = all_asset_references(
            script_srcs=["/qa-portfolio/assets/index-abc.js"],
            links=[{"rel": "icon", "href": "/favicon.svg"}],  # missing prefix
        )
        base = detect_base_path(["/qa-portfolio/assets/index-abc.js"])
        mismatched = [r for r in refs if not r.startswith(base)]
        self.assertEqual(mismatched, ["/favicon.svg"])


if __name__ == "__main__":
    unittest.main()
