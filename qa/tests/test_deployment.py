"""Deployment verification tests — run only in CI against the live GitHub Pages URL.

Skipped locally when GITHUB_PAGES_URL is not set.
"""

import sys
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import CONFIG
from constants import PAGE_TITLE, DEPLOYMENT
from errors import Messages as Msg

pytestmark = pytest.mark.skipif(
    not CONFIG.github_pages_url,
    reason="Deployment tests only run in CI with GITHUB_PAGES_URL set",
)

_PAGES_URL = CONFIG.github_pages_url


@pytest.fixture()
def deploy_page(page: Page) -> Page:
    """Page fixture pre-navigated to GitHub Pages URL."""
    return page


class TestDeployment:

    @pytest.mark.deployment
    def test_assets_load_on_github_pages(self, deploy_page: Page):
        """Verify production site loads with no 404 asset errors."""
        failed_requests: list[str] = []
        deploy_page.on(
            "response",
            lambda r: failed_requests.append(r.url) if r.status == 404 else None,
        )

        deploy_page.goto(
            _PAGES_URL,
            wait_until="networkidle",
            timeout=CONFIG.timeout_navigation,
        )

        asset_404s = [
            url for url in failed_requests
            if any(ext in url for ext in DEPLOYMENT.CHECKED_ASSET_EXTENSIONS)
            and not any(exc in url for exc in DEPLOYMENT.EXCLUDED_404_PATHS)
        ]
        assert not asset_404s, Msg.ASSET_404.format(urls=asset_404s)

        expect(deploy_page.get_by_role("navigation")).to_be_visible(
            timeout=CONFIG.timeout_hydration,
        )
        expect(deploy_page.get_by_role("heading", level=1)).to_be_visible(
            timeout=CONFIG.timeout_hydration,
        )

    @pytest.mark.deployment
    def test_base_path_is_correct(self, deploy_page: Page):
        deploy_page.goto(_PAGES_URL, wait_until="networkidle")

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
        assert bad_paths == [], Msg.DEPLOY_WRONG_BASE_PATH.format(paths=bad_paths)

    @pytest.mark.deployment
    def test_no_console_errors_on_production(self, deploy_page: Page):
        js_errors: list[str] = []
        deploy_page.on("pageerror", lambda err: js_errors.append(str(err)))

        deploy_page.goto(_PAGES_URL, wait_until="networkidle")

        assert js_errors == [], Msg.DEPLOY_JS_ERRORS.format(errors=js_errors)
