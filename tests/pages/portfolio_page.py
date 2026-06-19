"""Page Object Model for the QA portfolio SPA — locators, actions, queries."""

from playwright.sync_api import Page, Locator

from constants import SECTIONS
from config import CONFIG


class PortfolioPage:
    """Page Object for the QA portfolio single-page application.

    Locators are exposed as properties (no side-effects).
    Actions perform navigation or interaction.
    Queries return primitive values for test assertions.
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

    # ── Section locators ──

    @property
    def hero_section(self) -> Locator:
        """The full-screen hero section."""
        return self._page.locator(SECTIONS.HERO)

    @property
    def hero_heading(self) -> Locator:
        """The main h1 heading."""
        return self._page.get_by_role("heading", level=1)

    @property
    def navigation(self) -> Locator:
        """The primary nav landmark."""
        return self._page.get_by_role("navigation")

    @property
    def skills_section(self) -> Locator:
        """The skills section."""
        return self._page.locator(SECTIONS.SKILLS)

    @property
    def projects_section(self) -> Locator:
        """The projects section."""
        return self._page.locator(SECTIONS.PROJECTS)

    @property
    def contact_section(self) -> Locator:
        """The contact section."""
        return self._page.locator(SECTIONS.CONTACT)

    @property
    def test_results_section(self) -> Locator:
        """The test results section."""
        return self._page.locator(SECTIONS.TEST_RESULTS)

    # ── Element locators ──

    def nav_link(self, name: str) -> Locator:
        """A specific navigation link by its visible label."""
        return self.navigation.get_by_role("link", name=name)

    @property
    def project_cards(self) -> Locator:
        """All project article cards."""
        return self.projects_section.get_by_role("article")

    @property
    def contact_links(self) -> Locator:
        """All contact channel links."""
        return self.contact_section.get_by_role("link")

    @property
    def all_images(self) -> Locator:
        """Every img element on the page."""
        return self._page.locator("img")

    @property
    def all_headings(self) -> Locator:
        """Every heading element on the page."""
        return self._page.locator("h1, h2, h3, h4, h5, h6")

    def skill_text(self, name: str) -> Locator:
        """A specific skill by its visible text in the skills section."""
        return self.skills_section.get_by_text(name, exact=True)

    # ── Queries ──

    def get_title(self) -> str:
        """Return the document title."""
        return self._page.title()

    def get_hero_heading_text(self) -> str:
        """Return the inner text of the h1 heading."""
        return self.hero_heading.inner_text()

    def count_project_cards(self) -> int:
        """Return the number of project article cards."""
        return self.project_cards.count()

    def count_contact_links(self) -> int:
        """Return the number of contact links."""
        return self.contact_links.count()

    def get_scroll_width(self) -> int:
        """Return document.documentElement.scrollWidth."""
        return self._page.evaluate("document.documentElement.scrollWidth")

    def get_viewport_width(self) -> int:
        """Return the viewport width from page settings."""
        return self._page.viewport_size["width"]

    def get_load_time_ms(self) -> float:
        """Return page load time in milliseconds via Performance API."""
        return self._page.evaluate(
            "performance.timing.loadEventEnd - performance.timing.navigationStart"
        )
