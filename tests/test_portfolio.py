import sys
from pathlib import Path

import pytest
from playwright.sync_api import Page

sys.path.insert(0, str(Path(__file__).parent))
from pages.portfolio_page import PortfolioPage


# ─────────────────────────────────────────────
# Fixtures local to this module
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
# Smoke tests — critical path
# ─────────────────────────────────────────────

class TestSmoke:

    @pytest.mark.smoke
    def test_page_loads_with_correct_title(self, portfolio: PortfolioPage):
        # Act
        title = portfolio.get_title()

        # Assert
        assert "QA" in title, f"Title should contain 'QA', got: '{title}'"
        assert "Engineer" in title, f"Title should contain 'Engineer', got: '{title}'"

    @pytest.mark.smoke
    def test_hero_heading_displays_name(self, portfolio: PortfolioPage):
        # Act
        text = portfolio.get_hero_heading_text()

        # Assert
        assert "Oleg" in text, f"Hero heading should contain 'Oleg', got: '{text}'"

    @pytest.mark.smoke
    def test_navigation_is_present(self, portfolio: PortfolioPage):
        # Assert
        assert portfolio.navigation.is_visible(), "Primary navigation should be visible"

    @pytest.mark.smoke
    def test_page_has_no_javascript_errors(self, page: Page, base_url: str):
        # Arrange — collect uncaught JS exceptions (not network 404s)
        js_errors = []
        page.on("pageerror", lambda err: js_errors.append(str(err)))

        # Act
        page.goto(base_url, wait_until="networkidle")

        # Assert
        assert js_errors == [], f"Uncaught JS errors: {js_errors}"

    @pytest.mark.smoke
    def test_react_app_hydrated_successfully(self, hydrated_page: Page):
        # Assert
        child_count = hydrated_page.evaluate(
            "document.querySelector('#root').children.length"
        )
        assert child_count > 0, "React root should have rendered child elements"

        error_boundary = hydrated_page.locator('[data-reactroot] .error-boundary, #root > [class*="error"]')
        assert error_boundary.count() == 0, "No React error boundary should be rendered"


# ─────────────────────────────────────────────
# Navigation tests
# ─────────────────────────────────────────────

class TestNavigation:

    @pytest.mark.navigation
    @pytest.mark.parametrize("label, href", [
        ("About", "#about"),
        ("Skills", "#skills"),
        ("Projects", "#projects"),
        ("Contact", "#contact"),
    ])
    def test_nav_link_is_visible_with_correct_href(
        self, portfolio: PortfolioPage, label: str, href: str
    ):
        # Act
        link = portfolio.nav_link(label)

        # Assert
        assert link.is_visible(), f"Nav link '{label}' should be visible"
        actual_href = link.get_attribute("href")
        assert actual_href == href, (
            f"Nav link '{label}' href should be '{href}', got: '{actual_href}'"
        )


# ─────────────────────────────────────────────
# Content tests
# ─────────────────────────────────────────────

class TestContent:

    @pytest.mark.content
    @pytest.mark.parametrize("skill", ["Python", "Playwright", "Pytest"])
    def test_skills_section_contains_core_stack(
        self, portfolio: PortfolioPage, skill: str
    ):
        # Act
        tag = portfolio.skill_text(skill)

        # Assert
        assert tag.first.is_visible(), (
            f"Skill '{skill}' should be visible in the skills section"
        )

    @pytest.mark.content
    def test_projects_section_has_three_cards(self, portfolio: PortfolioPage):
        # Act
        count = portfolio.count_project_cards()

        # Assert
        assert count == 3, f"Expected 3 project cards, got: {count}"

    @pytest.mark.content
    def test_contact_section_has_required_channels(self, portfolio: PortfolioPage):
        # Act
        count = portfolio.count_contact_links()

        # Assert
        assert count == 4, f"Expected 4 contact channels, got: {count}"

    @pytest.mark.content
    def test_test_results_section_renders(self, portfolio: PortfolioPage):
        # Assert
        section = portfolio.test_results_section
        assert section.is_visible(), "Test results section should be visible"

        headings = section.get_by_role("heading")
        assert headings.count() > 0, (
            "Test results section should have at least one heading"
        )


# ─────────────────────────────────────────────
# Responsive tests
# ─────────────────────────────────────────────

class TestResponsive:

    @pytest.mark.responsive
    def test_mobile_viewport_no_horizontal_scroll(
        self, mobile_portfolio: PortfolioPage
    ):
        # Act
        scroll_w = mobile_portfolio.get_scroll_width()
        viewport_w = mobile_portfolio.get_viewport_width()

        # Assert
        assert scroll_w <= viewport_w, (
            f"Horizontal overflow on mobile: scrollWidth={scroll_w}, "
            f"viewportWidth={viewport_w}"
        )

    @pytest.mark.responsive
    def test_mobile_hero_section_visible(self, mobile_portfolio: PortfolioPage):
        # Assert
        assert mobile_portfolio.hero_heading.is_visible(), (
            "Hero heading should be visible at 390px mobile viewport"
        )


# ─────────────────────────────────────────────
# Performance tests
# ─────────────────────────────────────────────

class TestPerformance:

    @pytest.mark.performance
    def test_page_load_time_under_3_seconds(self, page: Page, base_url: str):
        # Act
        page.goto(base_url, wait_until="load")
        load_ms = page.evaluate(
            "performance.timing.loadEventEnd - performance.timing.navigationStart"
        )

        # Assert
        assert load_ms < 3000, (
            f"Page loaded in {load_ms:.0f}ms, expected under 3000ms"
        )


# ─────────────────────────────────────────────
# Accessibility tests
# ─────────────────────────────────────────────

class TestAccessibility:

    @pytest.mark.accessibility
    def test_images_have_alt_text(self, portfolio: PortfolioPage):
        # Act
        images = portfolio.all_images.all()
        violations = []
        for img in images:
            alt = img.get_attribute("alt") or ""
            if not alt.strip():
                src = img.get_attribute("src") or "unknown"
                violations.append(src)

        # Assert
        assert violations == [], (
            f"Images missing alt text: {violations}"
        )

    @pytest.mark.accessibility
    def test_headings_hierarchy_is_correct(self, portfolio: PortfolioPage):
        # Act
        headings = portfolio.all_headings.all()
        tags = [h.evaluate("el => el.tagName.toLowerCase()") for h in headings]

        # Assert — exactly one h1
        h1_count = tags.count("h1")
        assert h1_count == 1, f"Expected exactly 1 h1, found: {h1_count}"

        # Assert — h1 comes before any h2
        h1_idx = tags.index("h1")
        h2_indices = [i for i, t in enumerate(tags) if t == "h2"]
        if h2_indices:
            assert h1_idx < h2_indices[0], (
                "h1 should appear before the first h2 in document order"
            )

        # Assert — no heading levels are skipped
        levels = [int(t[1]) for t in tags]
        for i in range(1, len(levels)):
            gap = levels[i] - levels[i - 1]
            assert gap <= 1, (
                f"Heading level skipped: h{levels[i-1]} followed by h{levels[i]} "
                f"at position {i}"
            )
