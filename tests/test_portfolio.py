"""Portfolio test suite — smoke, navigation, content, responsive, performance, a11y."""

import sys
from pathlib import Path

import pytest
from playwright.sync_api import Page

sys.path.insert(0, str(Path(__file__).parent))

from config import CONFIG
from constants import PAGE_TITLE, HERO, NAV, SKILLS, COUNTS, PERF
from errors import Messages as Msg
from pages.portfolio_page import PortfolioPage


# ── Module fixtures ──

@pytest.fixture()
def portfolio(page: Page, base_url: str) -> PortfolioPage:
    """Navigated PortfolioPage ready for assertions."""
    pom = PortfolioPage(page, base_url)
    pom.navigate()
    return pom


@pytest.fixture()
def mobile_portfolio(mobile_page: Page, base_url: str) -> PortfolioPage:
    """Navigated PortfolioPage at mobile viewport."""
    pom = PortfolioPage(mobile_page, base_url)
    pom.navigate()
    return pom


# ── Smoke ──

class TestSmoke:

    @pytest.mark.smoke
    def test_page_loads_with_correct_title(self, portfolio: PortfolioPage):
        title = portfolio.get_title()

        assert PAGE_TITLE.CONTAINS_ROLE in title, Msg.TITLE_MISSING_ROLE.format(
            expected=PAGE_TITLE.CONTAINS_ROLE, actual=title,
        )
        assert PAGE_TITLE.CONTAINS_TYPE in title, Msg.TITLE_MISSING_ROLE.format(
            expected=PAGE_TITLE.CONTAINS_TYPE, actual=title,
        )

    @pytest.mark.smoke
    def test_hero_heading_displays_name(self, portfolio: PortfolioPage):
        text = portfolio.get_hero_heading_text()

        assert HERO.CONTAINS_NAME in text, Msg.HERO_NAME_MISSING.format(
            expected=HERO.CONTAINS_NAME, actual=text,
        )

    @pytest.mark.smoke
    def test_navigation_is_present(self, portfolio: PortfolioPage):
        assert portfolio.navigation.is_visible(), Msg.NAV_NOT_VISIBLE

    @pytest.mark.smoke
    def test_page_has_no_javascript_errors(self, page: Page, base_url: str):
        js_errors: list[str] = []
        page.on("pageerror", lambda err: js_errors.append(str(err)))

        page.goto(base_url, wait_until="networkidle")

        assert js_errors == [], Msg.JS_ERRORS_FOUND.format(errors=js_errors)

    @pytest.mark.smoke
    def test_react_app_hydrated_successfully(self, hydrated_page: Page):
        child_count = hydrated_page.evaluate(
            "document.querySelector('#root').children.length"
        )
        assert child_count > 0, Msg.HYDRATION_FAILED

        error_boundary = hydrated_page.locator(
            '[data-reactroot] .error-boundary, #root > [class*="error"]'
        )
        assert error_boundary.count() == 0, Msg.ERROR_BOUNDARY_RENDERED


# ── Navigation ──

class TestNavigation:

    @pytest.mark.navigation
    @pytest.mark.parametrize("label, href", NAV.ALL_WITH_HREFS)
    def test_nav_link_is_visible_with_correct_href(
        self, portfolio: PortfolioPage, label: str, href: str,
    ):
        link = portfolio.nav_link(label)

        assert link.is_visible(), Msg.NAV_LINK_NOT_VISIBLE.format(name=label)
        actual_href = link.get_attribute("href")
        assert actual_href == href, Msg.NAV_LINK_WRONG_HREF.format(
            name=label, expected=href, actual=actual_href,
        )


# ── Content ──

class TestContent:

    @pytest.mark.content
    @pytest.mark.parametrize("skill", SKILLS.ALL)
    def test_skills_section_contains_core_stack(
        self, portfolio: PortfolioPage, skill: str,
    ):
        tag = portfolio.skill_text(skill)

        assert tag.first.is_visible(), Msg.SKILL_NOT_VISIBLE.format(name=skill)

    @pytest.mark.content
    def test_projects_section_has_expected_cards(self, portfolio: PortfolioPage):
        count = portfolio.count_project_cards()

        assert count == COUNTS.PROJECT_CARDS, Msg.WRONG_PROJECT_COUNT.format(
            expected=COUNTS.PROJECT_CARDS, actual=count,
        )

    @pytest.mark.content
    def test_contact_section_has_required_channels(self, portfolio: PortfolioPage):
        count = portfolio.count_contact_links()

        assert count == COUNTS.CONTACT_LINKS, Msg.WRONG_CONTACT_COUNT.format(
            expected=COUNTS.CONTACT_LINKS, actual=count,
        )

    @pytest.mark.content
    def test_test_results_section_renders(self, portfolio: PortfolioPage):
        section = portfolio.test_results_section

        assert section.is_visible(), Msg.TEST_RESULTS_NOT_VISIBLE

        headings = section.get_by_role("heading")
        assert headings.count() > 0, Msg.TEST_RESULTS_NO_HEADINGS


# ── Responsive ──

class TestResponsive:

    @pytest.mark.responsive
    def test_mobile_viewport_no_horizontal_scroll(
        self, mobile_portfolio: PortfolioPage,
    ):
        scroll_w = mobile_portfolio.get_scroll_width()
        viewport_w = mobile_portfolio.get_viewport_width()

        assert scroll_w <= viewport_w, Msg.HORIZONTAL_OVERFLOW.format(
            scroll_w=scroll_w, viewport_w=viewport_w,
        )

    @pytest.mark.responsive
    def test_mobile_hero_section_visible(self, mobile_portfolio: PortfolioPage):
        assert mobile_portfolio.hero_heading.is_visible(), (
            Msg.MOBILE_HERO_NOT_VISIBLE.format(width=CONFIG.mobile_width)
        )


# ── Performance ──

class TestPerformance:

    @pytest.mark.performance
    def test_page_load_time_within_budget(self, page: Page, base_url: str):
        page.goto(base_url, wait_until="load")
        load_ms = page.evaluate(
            "performance.timing.loadEventEnd - performance.timing.navigationStart"
        )

        assert load_ms < PERF.MAX_LOAD_TIME_MS, Msg.SLOW_PAGE_LOAD.format(
            actual=load_ms, budget=PERF.MAX_LOAD_TIME_MS,
        )


# ── Accessibility ──

class TestAccessibility:

    @pytest.mark.accessibility
    def test_images_have_alt_text(self, portfolio: PortfolioPage):
        images = portfolio.all_images.all()
        violations = [
            img.get_attribute("src") or "unknown"
            for img in images
            if not (img.get_attribute("alt") or "").strip()
        ]

        assert violations == [], Msg.IMAGES_MISSING_ALT.format(sources=violations)

    @pytest.mark.accessibility
    def test_headings_hierarchy_is_correct(self, portfolio: PortfolioPage):
        headings = portfolio.all_headings.all()
        tags = [h.evaluate("el => el.tagName.toLowerCase()") for h in headings]

        h1_count = tags.count("h1")
        assert h1_count == COUNTS.H1_HEADINGS, Msg.WRONG_H1_COUNT.format(
            expected=COUNTS.H1_HEADINGS, actual=h1_count,
        )

        h1_idx = tags.index("h1")
        h2_indices = [i for i, t in enumerate(tags) if t == "h2"]
        if h2_indices:
            assert h1_idx < h2_indices[0], Msg.H1_NOT_FIRST

        levels = [int(t[1]) for t in tags]
        for i in range(1, len(levels)):
            gap = levels[i] - levels[i - 1]
            assert gap <= 1, Msg.HEADING_LEVEL_SKIPPED.format(
                prev=levels[i - 1], next=levels[i], pos=i,
            )
