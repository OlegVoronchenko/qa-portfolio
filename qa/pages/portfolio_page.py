"""
Page Object Model — Portfolio Page
====================================

PURPOSE
-------
Encapsulates all Playwright locators and actions for the QA
portfolio single-page application. Tests interact with the
page exclusively through this class, never using raw selectors.

WHY POM
-------
Centralizing locators here means that when the React component
markup changes (e.g., a CSS class rename or DOM restructure),
only this file needs updating — not every test that touches
that element. This is critical for maintaining 20+ tests.

LOCATOR STRATEGY
----------------
All locators prefer ARIA roles (get_by_role, get_by_text) over
CSS selectors. This aligns with Playwright best practices and
makes tests resilient to styling changes while also verifying
accessibility semantics.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page, Locator, TimeoutError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from constants import SECTIONS
from config import CONFIG

SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent / "screenshots"


class PortfolioPage:
    """Page Object Model for the portfolio site.

    PURPOSE
    -------
    Encapsulates all element locators and navigation actions
    for the portfolio page. Tests interact with this class
    instead of using raw Playwright selectors directly.

    WHY USE PAGE OBJECT MODEL
    -------------------------
    If a CSS class or DOM structure changes, only this file
    needs updating — all tests continue to work unchanged.
    This is the standard pattern for maintainable UI tests.

    LOCATOR STRATEGY
    ----------------
    Locators are defined as properties that return Playwright
    Locator objects. They use the recommended priority order:
    1. get_by_role()    — for interactive and landmark elements
    2. get_by_text()    — for visible text content
    3. get_by_label()   — for form fields
    4. CSS id (#xxx)    — only for section landmarks

    NO ASSERTIONS IN POM
    --------------------
    This class only locates and acts. All assertions live
    in the test files for clear separation of concerns.

    USAGE
    -----
        portfolio = PortfolioPage(page, base_url)
        portfolio.navigate()
        link = portfolio.nav_link("About")
        assert link.is_visible()
    """

    def __init__(self, page: Page, base_url: str) -> None:
        self._page = page
        self._base_url = base_url

    # ── Actions ──

    def navigate(self) -> None:
        """Load the portfolio and wait for React to hydrate."""
        self._page.goto(self._base_url, wait_until="domcontentloaded")
        self._page.wait_for_function(
            "document.querySelector('#root').children.length > 0",
            timeout=CONFIG.timeout_hydration,
        )

    def take_screenshot(
        self,
        name: str,
        full_page: bool = False,
    ) -> str:
        """Capture screenshot with CI diagnostics."""
        SCREENSHOTS_DIR.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = SCREENSHOTS_DIR / f"{name}_{ts}.png"

        if os.getenv("CI"):
            diag = self._page.evaluate("""() => ({
                url: location.href,
                title: document.title,
                viewport: {
                    w: window.innerWidth,
                    h: window.innerHeight
                },
                root_children: document.querySelector('#root')?.children?.length ?? 0,
                root_html_length: document.querySelector('#root')?.innerHTML?.length ?? 0,
                h1_count: document.querySelectorAll('h1').length,
                h1_text: document.querySelector('h1')?.innerText?.slice(0, 50) ?? '',
                h1_visible: (() => {
                    const h1 = document.querySelector('h1')
                    if (!h1) return false
                    const rect = h1.getBoundingClientRect()
                    const style = getComputedStyle(h1)
                    return rect.width > 0 && rect.height > 0
                        && style.display !== 'none'
                        && style.visibility !== 'hidden'
                        && parseFloat(style.opacity) > 0
                })(),
                body_bg: getComputedStyle(document.body).backgroundColor,
                scroll_y: window.scrollY,
                ready_state: document.readyState,
            })""")
            print(f"\n[CI DIAG] Before screenshot for '{name}':")
            for key, val in diag.items():
                print(f"  {key}: {val}")

        self._page.screenshot(
            path=str(path),
            full_page=full_page,
            animations="disabled",
        )

        if os.getenv("CI"):
            size_kb = path.stat().st_size / 1024
            print(f"[CI DIAG] Screenshot saved: {path.name} ({size_kb:.1f} KB)")
            if size_kb < 10:
                print(
                    f"[CI DIAG] WARNING: Screenshot suspiciously small "
                    f"({size_kb:.1f} KB) — likely blank!"
                )

        self._verify_screenshot_not_blank(path)
        return str(path)

    def _verify_screenshot_not_blank(self, path: Path) -> None:
        """Fail if screenshot is >95% white — page didn't render."""
        try:
            from PIL import Image
        except ImportError:
            return

        pixels = Image.open(path).convert("RGB").getdata()
        total = len(pixels)
        if total == 0:
            return
        white_count = sum(
            1 for r, g, b in pixels
            if r > 240 and g > 240 and b > 240
        )
        white_ratio = white_count / total
        assert white_ratio < 0.95, (
            f"Screenshot is {white_ratio:.1%} white pixels — "
            f"page did not render. Path: {path}"
        )

    def wait_for_content_ready(self, timeout: int = None) -> None:
        """Wait until real page content is visible, not just DOM loaded."""
        if timeout is None:
            timeout = 30000 if os.getenv("CI") else 15000
        self._page.wait_for_load_state("networkidle", timeout=timeout)
        self.hero_heading.wait_for(state="visible", timeout=timeout)
        h1_text = self.hero_heading.inner_text(timeout=5000)
        if not h1_text.strip():
            raise TimeoutError(
                "Hero heading is visible but has empty text"
            )

    # ── Section locators ──

    @property
    def hero_section(self) -> Locator:
        return self._page.locator(SECTIONS.HERO)

    @property
    def hero_heading(self) -> Locator:
        return self._page.get_by_role("heading", level=1)

    @property
    def navigation(self) -> Locator:
        return self._page.get_by_role("navigation")

    @property
    def skills_section(self) -> Locator:
        return self._page.locator(SECTIONS.SKILLS)

    @property
    def projects_section(self) -> Locator:
        return self._page.locator(SECTIONS.PROJECTS)

    @property
    def contact_section(self) -> Locator:
        return self._page.locator(SECTIONS.CONTACT)

    @property
    def test_results_section(self) -> Locator:
        return self._page.locator(SECTIONS.TEST_RESULTS)

    # ── Element locators ──

    def nav_link(self, name: str) -> Locator:
        return self.navigation.get_by_role("link", name=name)

    @property
    def project_cards(self) -> Locator:
        return self.projects_section.get_by_role("article")

    @property
    def contact_links(self) -> Locator:
        return self.contact_section.get_by_role("link")

    @property
    def all_images(self) -> Locator:
        return self._page.locator("img")

    @property
    def all_headings(self) -> Locator:
        return self._page.locator("h1, h2, h3, h4, h5, h6")

    def skill_text(self, name: str) -> Locator:
        return self.skills_section.get_by_text(name, exact=True)

    # ── Queries ──

    def get_title(self) -> str:
        return self._page.title()

    def get_hero_heading_text(self) -> str:
        return self.hero_heading.inner_text()

    def count_project_cards(self) -> int:
        return self.project_cards.count()

    def count_contact_links(self) -> int:
        return self.contact_links.count()

    def get_scroll_width(self) -> int:
        return self._page.evaluate("document.documentElement.scrollWidth")

    def get_viewport_width(self) -> int:
        return self._page.viewport_size["width"]

    def get_load_time_ms(self) -> float:
        return self._page.evaluate(
            "performance.timing.loadEventEnd - performance.timing.navigationStart"
        )
