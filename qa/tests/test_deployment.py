"""Deployment verification tests — run only in CI against the live GitHub Pages URL.

Skipped locally when GITHUB_PAGES_URL is not set.
"""

import sys
from pathlib import Path

import pytest
from playwright.sync_api import Page

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import CONFIG
from conftest import step
from constants import DEPLOYMENT
from errors import Messages as Msg

pytestmark = pytest.mark.skipif(
    not CONFIG.github_pages_url,
    reason="Deployment tests only run in CI with GITHUB_PAGES_URL set",
)

_PAGES_URL = CONFIG.github_pages_url


@pytest.fixture()
def deploy_page(page: Page) -> Page:
    """Page fixture for deployment tests."""
    return page


class TestDeployment:

    # REQ-007 | AC-007-1, AC-007-2, AC-007-3
    @pytest.mark.deployment
    def test_assets_load_on_github_pages(self, deploy_page: Page):
        """Verify production site loads with no 404 asset errors.

        Monitors network responses during page load and collects
        any 404s for asset file types (.js, .css, .png, etc.).
        Also verifies navigation and h1 are visible after load.

        Failure means: assets have wrong base path, deployment
        is missing files, or React failed to hydrate.
        """
        failed_requests: list[str] = []

        with step("Attach network response monitor for 404s"):
            deploy_page.on(
                "response",
                lambda r: failed_requests.append(r.url)
                if r.status == 404
                else None,
            )

        with step(f"Navigate to {_PAGES_URL} and wait for network idle"):
            deploy_page.goto(
                _PAGES_URL,
                wait_until="networkidle",
                timeout=CONFIG.timeout_navigation,
            )

        with step("Filter asset 404s from captured responses"):
            asset_404s = [
                url
                for url in failed_requests
                if any(ext in url for ext in DEPLOYMENT.CHECKED_ASSET_EXTENSIONS)
                and not any(
                    exc in url for exc in DEPLOYMENT.EXCLUDED_404_PATHS
                )
            ]

        with step(f"Assert no asset 404s (found {len(asset_404s)})"):
            assert not asset_404s, Msg.ASSET_404.format(urls=asset_404s)

        with step("Verify navigation landmark exists and is visible"):
            nav = deploy_page.get_by_role("navigation")
            nav_count = nav.count()
            assert nav_count > 0, Msg.DEPLOY_NAV_NOT_FOUND.format(
                url=_PAGES_URL, count=nav_count,
            )
            assert nav.is_visible(), Msg.DEPLOY_NAV_HIDDEN.format(
                count=nav_count, url=_PAGES_URL,
            )

        with step("Verify h1 heading exists with content"):
            h1 = deploy_page.get_by_role("heading", level=1)
            h1_count = h1.count()
            assert h1_count == 1, Msg.DEPLOY_H1_WRONG_COUNT.format(
                actual=h1_count, url=_PAGES_URL,
            )
            h1_text = h1.inner_text()
            assert h1_text.strip(), Msg.DEPLOY_H1_EMPTY.format(url=_PAGES_URL)

    # REQ-007 | AC-007-4
    @pytest.mark.deployment
    def test_base_path_is_correct(self, deploy_page: Page):
        """Verify assets use the correct repo-prefixed base path.

        Scans <script src> and <link href> for paths starting
        with '/assets/' which would be wrong on GitHub Pages
        (should be '/<repo-name>/assets/').

        Failure means: VITE_BASE_PATH was not set during build.
        """
        with step(f"Navigate to {_PAGES_URL}"):
            deploy_page.goto(_PAGES_URL, wait_until="networkidle")

        with step("Scan script and link elements for wrong base path"):
            bad_paths = deploy_page.evaluate("""() => {
                const bad = [];
                document.querySelectorAll('script[src], link[href]').forEach(el => {
                    const val = el.getAttribute('src') || el.getAttribute('href');
                    if (val && val.startsWith('/assets/')) {
                        bad.push(val);
                    }
                });
                return bad;
            }""")

        with step(f"Assert no '/assets/' paths (found {len(bad_paths)})"):
            assert bad_paths == [], Msg.DEPLOY_WRONG_BASE_PATH.format(
                paths=bad_paths,
            )

    # REQ-007 | AC-007-5
    @pytest.mark.deployment
    def test_no_console_errors_on_production(self, deploy_page: Page):
        """Verify no JavaScript errors on the production site.

        Attaches a pageerror listener before navigation and
        collects all uncaught exceptions.

        Failure means: production JS is crashing — could be
        missing environment variables, wrong API URLs, or
        browser compatibility issues.
        """
        js_errors: list[str] = []

        with step("Attach JavaScript error listener"):
            deploy_page.on("pageerror", lambda err: js_errors.append(str(err)))

        with step(f"Navigate to {_PAGES_URL} and wait for network idle"):
            deploy_page.goto(_PAGES_URL, wait_until="networkidle")

        with step(f"Assert no JS errors (found {len(js_errors)})"):
            assert js_errors == [], Msg.DEPLOY_JS_ERRORS.format(errors=js_errors)
