"""Deployment verification tests — run only in CI against the live GitHub Pages URL.

Skipped locally when GITHUB_PAGES_URL is not set.
"""

import os
import sys
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, str(Path(__file__).parent))

PAGES_URL = os.getenv("GITHUB_PAGES_URL", "")

pytestmark = pytest.mark.skipif(
    not PAGES_URL,
    reason="Deployment tests only run in CI with GITHUB_PAGES_URL set",
)


@pytest.fixture(scope="module")
def browser():
    pw = sync_playwright().start()
    b = pw.chromium.launch(headless=True)
    yield b
    b.close()
    pw.stop()


@pytest.fixture()
def deploy_page(browser) -> Page:
    ctx = browser.new_context(viewport={"width": 1280, "height": 720})
    pg = ctx.new_page()
    yield pg
    pg.close()
    ctx.close()


class TestDeployment:

    @pytest.mark.deployment
    def test_assets_load_on_github_pages(self, deploy_page: Page):
        # Arrange
        failed_requests = []
        deploy_page.on(
            "response",
            lambda resp: failed_requests.append(f"{resp.status} {resp.url}")
            if resp.status >= 400
            else None,
        )

        # Act
        deploy_page.goto(PAGES_URL, wait_until="networkidle")

        # Assert — page title
        title = deploy_page.title()
        assert "QA" in title, f"Page title should contain 'QA', got: '{title}'"

        # Assert — React rendered
        child_count = deploy_page.evaluate(
            "document.querySelector('#root').children.length"
        )
        assert child_count > 0, "React app should have rendered (#root has no children)"

        # Assert — no 404s on critical assets
        critical_failures = [
            r for r in failed_requests if "/assets/" in r
        ]
        assert critical_failures == [], (
            f"Critical asset requests failed: {critical_failures}"
        )

    @pytest.mark.deployment
    def test_base_path_is_correct(self, deploy_page: Page):
        # Act
        deploy_page.goto(PAGES_URL, wait_until="domcontentloaded")

        # Assert — script and link tags use correct base path
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
        assert bad_paths == [], (
            f"Assets using wrong base path '/assets/' instead of "
            f"'/qa-portfolio/assets/': {bad_paths}"
        )

    @pytest.mark.deployment
    def test_no_console_errors_on_production(self, deploy_page: Page):
        # Arrange
        js_errors = []
        deploy_page.on("pageerror", lambda err: js_errors.append(str(err)))

        # Act
        deploy_page.goto(PAGES_URL, wait_until="networkidle")

        # Assert
        assert js_errors == [], f"JS errors on production: {js_errors}"
