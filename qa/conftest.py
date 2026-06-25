"""
Pytest Configuration & Shared Fixtures
=======================================

PURPOSE
-------
Defines fixtures and configuration shared across all
tests in the qa/ module. Independent of React/Node.js.

KEY FIXTURES
------------
- base_url            session-scoped, from CONFIG.base_url
- page                function-scoped Playwright Page
- mobile_page         function-scoped, 390x844 viewport
- hydrated_page       page with React fully loaded
- portfolio           pre-navigated PortfolioPage POM
- mobile_portfolio    pre-navigated POM at mobile size

Session-scoped (created once, shared across all tests):
  - _http_server: serves the Vite dist/ build on localhost:8080
  - _browser: headless Chromium instance via Playwright

Auto-use fixtures:
  - capture_screenshot: saves a PNG after every test for debugging

STEP LOGGING
------------
The step() context manager prints test progress to stdout.
Use with -s flag in pytest to see live step output:
    pytest -v -s

Example:
    with step("Open the portfolio page"):
        portfolio.navigate()
"""

import contextlib
import http.server
import re
import sys
import threading
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright, Page, BrowserContext

sys.path.insert(0, str(Path(__file__).parent))

from config import CONFIG

DIST_DIR = str(Path(__file__).resolve().parent.parent / "dist")
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"


def _detect_base_path() -> str:
    """Read dist/index.html to find the Vite base path used at build time."""
    index = Path(DIST_DIR) / "index.html"
    if not index.exists():
        return "/"
    html = index.read_text()
    match = re.search(r'src="(/[^"]*?)/assets/', html)
    return match.group(1) + "/" if match else "/"


_BASE_PATH = _detect_base_path()
_BASE_URL = f"http://localhost:{CONFIG.server_port}{_BASE_PATH}"


class _SilentHandler(http.server.SimpleHTTPRequestHandler):
    """Serves dist/ under whatever base path Vite was built with."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST_DIR, **kwargs)

    def translate_path(self, path: str) -> str:
        if _BASE_PATH != "/" and path.startswith(_BASE_PATH):
            path = "/" + path[len(_BASE_PATH):]
        elif _BASE_PATH != "/" and path == _BASE_PATH.rstrip("/"):
            path = "/"
        return super().translate_path(path)

    def log_message(self, format, *args):
        pass


# ── Session-scoped infrastructure ──

@pytest.fixture(scope="session")
def base_url() -> str:
    """Base URL for the local test server."""
    return _BASE_URL


@pytest.fixture(scope="session")
def _http_server():
    """Session-scoped HTTP server serving the Vite dist/ build."""
    server = http.server.HTTPServer(("", CONFIG.server_port), _SilentHandler)
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


# ── Function-scoped contexts and pages ──

@pytest.fixture()
def context(_http_server, _browser) -> BrowserContext:
    """Function-scoped desktop browser context — fresh state per test."""
    ctx = _browser.new_context(
        viewport={"width": CONFIG.desktop_width, "height": CONFIG.desktop_height},
    )
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
    ctx = _browser.new_context(
        viewport={"width": CONFIG.mobile_width, "height": CONFIG.mobile_height},
    )
    yield ctx
    ctx.close()


@pytest.fixture()
def mobile_page(mobile_context: BrowserContext) -> Page:
    """Function-scoped page at mobile viewport."""
    pg = mobile_context.new_page()
    yield pg
    pg.close()


# ── Hydration helpers ──

def _wait_for_hydration(pg: Page, url: str) -> None:
    """Navigate and wait for React to mount into #root."""
    pg.goto(url, wait_until="domcontentloaded")
    pg.locator("#root").wait_for(state="attached", timeout=CONFIG.timeout_hydration)
    pg.wait_for_function(
        "document.querySelector('#root').children.length > 0",
        timeout=CONFIG.timeout_hydration,
    )


@pytest.fixture()
def hydrated_page(page: Page, base_url: str) -> Page:
    """Desktop page navigated to base URL with React hydration confirmed."""
    _wait_for_hydration(page, base_url)
    return page


@pytest.fixture()
def hydrated_mobile_page(mobile_page: Page, base_url: str) -> Page:
    """Mobile page navigated to base URL with React hydration confirmed."""
    _wait_for_hydration(mobile_page, base_url)
    return mobile_page


# ── Auto-screenshot after each test ──

@pytest.fixture(autouse=True)
def auto_screenshot(request, page: Page):
    """Capture screenshot after each test, with safety checks."""
    yield

    try:
        if page.is_closed():
            return

        url = page.url
        if not url or url == "about:blank":
            return

        has_content = page.evaluate("""
            () => {
                if (!document.body) return false
                if (document.body.children.length === 0) return false
                if (document.body.getBoundingClientRect().height < 100) return false
                return true
            }
        """)
        if not has_content:
            return

        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = re.sub(r"[^\w\-_]", "_", request.node.name)

        SCREENSHOTS_DIR.mkdir(exist_ok=True)
        page.screenshot(
            path=str(SCREENSHOTS_DIR / f"{safe_name}_{ts}.png"),
            full_page=False,
            animations="disabled",
        )
    except Exception as e:
        print(f"\n[auto_screenshot] Skipped due to: {e}")


# ── Step logging ──

@contextlib.contextmanager
def step(description: str):
    """Log a test step for structured debugging output."""
    print(f"\n    STEP: {description}")
    yield
    print(f"    ✓ done")
