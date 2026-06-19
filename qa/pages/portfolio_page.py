"""Page Object Model for the QA portfolio SPA — locators, actions, queries."""

import sys
from pathlib import Path

from playwright.sync_api import Page, Locator

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from constants import SECTIONS
from config import CONFIG

SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent / "screenshots"


class PortfolioPage:
    """Page Object for the QA portfolio single-page application."""

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

    def take_screenshot(self, name: str) -> None:
        """Capture a named screenshot at the current state."""
        SCREENSHOTS_DIR.mkdir(exist_ok=True)
        self._page.screenshot(
            path=str(SCREENSHOTS_DIR / f"{name}.png"),
            full_page=False,
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
