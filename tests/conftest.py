import http.server
import threading
import pytest
from playwright.sync_api import sync_playwright

SITE_DIR = str(__import__("pathlib").Path(__file__).resolve().parent.parent / "dist")
PORT = 8080


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SITE_DIR, **kwargs)

    def log_message(self, format, *args):
        pass


@pytest.fixture(scope="session")
def _http_server():
    server = http.server.HTTPServer(("", PORT), _QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()


@pytest.fixture(scope="session")
def _browser():
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=True)
    yield browser
    browser.close()
    pw.stop()


@pytest.fixture()
def page(_http_server, _browser):
    ctx = _browser.new_context(viewport={"width": 1280, "height": 720})
    pg = ctx.new_page()
    yield pg
    pg.close()
    ctx.close()


@pytest.fixture()
def mobile_page(_http_server, _browser):
    ctx = _browser.new_context(viewport={"width": 390, "height": 844})
    pg = ctx.new_page()
    yield pg
    pg.close()
    ctx.close()
