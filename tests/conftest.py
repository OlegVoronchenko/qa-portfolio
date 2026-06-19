import http.server
import threading
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright, Page, BrowserContext

DIST_DIR = str(Path(__file__).resolve().parent.parent / "dist")
PORT = 8080
BASE_URL = f"http://localhost:{PORT}"


class _SilentHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST_DIR, **kwargs)

    def log_message(self, format, *args):
        pass


@pytest.fixture(scope="session")
def base_url() -> str:
    """Base URL for the local test server."""
    return BASE_URL


@pytest.fixture(scope="session")
def _http_server():
    """Session-scoped HTTP server serving the Vite dist/ build."""
    server = http.server.HTTPServer(("", PORT), _SilentHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()


@pytest.fixture(scope="session")
def _browser():
    """Session-scoped Playwright browser instance."""
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=True)
    yield browser
    browser.close()
    pw.stop()


@pytest.fixture()
def context(_http_server, _browser) -> BrowserContext:
    """Function-scoped browser context — fresh state per test."""
    ctx = _browser.new_context(viewport={"width": 1280, "height": 720})
    yield ctx
    ctx.close()


@pytest.fixture()
def page(context: BrowserContext) -> Page:
    """Function-scoped page from the desktop context."""
    pg = context.new_page()
    yield pg
    pg.close()


@pytest.fixture()
def mobile_context(_http_server, _browser) -> BrowserContext:
    """Function-scoped mobile context — iPhone 14 viewport."""
    ctx = _browser.new_context(viewport={"width": 390, "height": 844})
    yield ctx
    ctx.close()


@pytest.fixture()
def mobile_page(mobile_context: BrowserContext) -> Page:
    """Function-scoped page at 390x844 mobile viewport."""
    pg = mobile_context.new_page()
    yield pg
    pg.close()


@pytest.fixture()
def hydrated_page(page: Page, base_url: str) -> Page:
    """Page navigated to base URL with React hydration confirmed."""
    page.goto(base_url, wait_until="domcontentloaded")
    page.locator("#root").wait_for(state="attached")
    page.wait_for_function("document.querySelector('#root').children.length > 0")
    return page


@pytest.fixture()
def hydrated_mobile_page(mobile_page: Page, base_url: str) -> Page:
    """Mobile page navigated to base URL with React hydration confirmed."""
    mobile_page.goto(base_url, wait_until="domcontentloaded")
    mobile_page.locator("#root").wait_for(state="attached")
    mobile_page.wait_for_function("document.querySelector('#root').children.length > 0")
    return mobile_page
