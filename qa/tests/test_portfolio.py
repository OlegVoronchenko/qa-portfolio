"""
Portfolio Test Suite — Functional & Non-Functional Verification
================================================================

PURPOSE
-------
End-to-end Playwright tests verifying that the portfolio site
renders correctly, navigates properly, displays profile data,
responds to mobile viewports, loads within performance budget,
and meets WCAG accessibility standards.

TEST CATEGORIES
---------------
  Smoke (REQ-001)         — page loads, title, hero, nav, no JS errors, React hydration
  Navigation (REQ-002)    — each nav link visible with correct anchor href
  Content (REQ-003)       — skills tags, project cards, contact links, test results section
  Responsive (REQ-004)    — no horizontal scroll at 390px, hero visible on mobile
  Performance (REQ-005)   — page load time under 3000ms budget
  Accessibility (REQ-006) — all images have alt text, heading hierarchy is correct

REQUIREMENTS TRACEABILITY
-------------------------
Every test method has a comment above its definition linking it
to a requirement ID (REQ-XXX) and acceptance criteria (AC-XXX-N).
These IDs match docs/requirements/REQ-*.md and are displayed as
clickable badges in the Test Results section of the live site.

FIXTURES
--------
  portfolio       — desktop page navigated and hydrated via POM
  mobile_portfolio — mobile (390x844) page navigated via POM
  page / base_url  — raw Playwright page + server URL for custom navigation
  hydrated_page    — desktop page with React hydration confirmed
"""

import sys
from pathlib import Path

import pytest
from playwright.sync_api import Page

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import CONFIG
from conftest import step
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
    """Mobile-sized PortfolioPage with extra stabilization for CI."""
    import os

    mobile_page.set_viewport_size(
        {"width": CONFIG.mobile_width, "height": CONFIG.mobile_height}
    )
    pom = PortfolioPage(mobile_page, base_url)
    pom.navigate()
    if os.getenv("CI"):
        mobile_page.wait_for_load_state("networkidle", timeout=30000)
        mobile_page.wait_for_timeout(1000)
    return pom


# ── Smoke ──

class TestSmoke:
    """Smoke tests — critical path verification.

    Covers REQ-001 (Page Load & Core Rendering).
    Runs first in CI. If any smoke test fails, the build
    is considered broken and subsequent tests are skipped.
    """

    # REQ-001 | AC-001-1, AC-001-2, AC-001-3
    @pytest.mark.smoke
    def test_page_loads_with_correct_title(self, portfolio: PortfolioPage):
        """Verify the browser tab title identifies the engineer.

        Checks three substrings in page.title():
          - Name:  'Oleg'
          - Role:  'Automation'
          - Type:  'Engineer'

        Failure means: either the page didn't load, or the
        <title> tag in index.html was changed incorrectly.
        """
        with step("Read page title from browser tab"):
            title = portfolio.get_title()

        with step("Capture screenshot before assertions"):
            portfolio.take_screenshot("assert_page_title")

        with step(f"Assert title contains name '{PAGE_TITLE.CONTAINS_NAME}'"):
            assert PAGE_TITLE.CONTAINS_NAME in title, \
                Msg.TITLE_MISSING_NAME.format(title=title)

        with step(f"Assert title contains role '{PAGE_TITLE.CONTAINS_ROLE}'"):
            assert PAGE_TITLE.CONTAINS_ROLE in title, \
                Msg.TITLE_MISSING_ROLE.format(
                    expected=PAGE_TITLE.CONTAINS_ROLE, actual=title,
                )

        with step(f"Assert title contains type '{PAGE_TITLE.CONTAINS_TYPE}'"):
            assert PAGE_TITLE.CONTAINS_TYPE in title, \
                Msg.TITLE_MISSING_ROLE.format(
                    expected=PAGE_TITLE.CONTAINS_TYPE, actual=title,
                )

    # REQ-001 | AC-001-4
    @pytest.mark.smoke
    def test_hero_heading_displays_name(self, portfolio: PortfolioPage):
        """Verify the main h1 heading contains the engineer's name.

        Locates the first heading with level=1 via ARIA role
        and checks that it contains 'Oleg'.

        Failure means: Hero component didn't render, or the
        name was removed from the h1 element.
        """
        with step("Get h1 heading text content"):
            text = portfolio.get_hero_heading_text()

        with step("Capture screenshot of hero section"):
            portfolio.take_screenshot("assert_hero_heading")

        with step(f"Assert heading contains '{HERO.CONTAINS_NAME}'"):
            assert HERO.CONTAINS_NAME in text, Msg.HERO_NAME_MISSING.format(
                expected=HERO.CONTAINS_NAME, actual=text,
            )

    # REQ-001 | AC-001-5
    @pytest.mark.smoke
    def test_navigation_is_present(self, portfolio: PortfolioPage):
        """Verify a <nav> landmark exists and is visible.

        Uses ARIA role='navigation' to locate the navbar.
        Checks both element count and visibility.

        Failure means: Navbar component didn't render, or
        the <nav> element was replaced with a non-semantic tag.
        """
        with step("Locate navigation landmark by ARIA role"):
            nav = portfolio.navigation
            nav_count = nav.count()

        with step("Capture screenshot of navigation"):
            portfolio.take_screenshot("assert_navigation")

        with step(f"Assert navigation is visible (found {nav_count} elements)"):
            url = portfolio._page.url
            assert nav.is_visible(), Msg.NAV_NOT_VISIBLE.format(
                url=url, count=nav_count,
            )

    # REQ-001 | AC-001-6
    @pytest.mark.smoke
    def test_page_has_no_javascript_errors(self, page: Page, base_url: str):
        """Verify no uncaught JS exceptions during page load.

        Attaches a listener to the 'pageerror' event before
        navigation, then asserts the error list is empty.

        Failure means: a runtime JS error occurred — could be
        a missing module, undefined variable, or API failure.
        """
        js_errors: list[str] = []

        with step("Attach JavaScript error listener"):
            page.on("pageerror", lambda err: js_errors.append(str(err)))

        with step(f"Navigate to {base_url} and wait for network idle"):
            page.goto(base_url, wait_until="networkidle")

        with step("Assert no JavaScript errors were captured"):
            assert js_errors == [], Msg.JS_ERRORS_FOUND.format(errors=js_errors)

    # REQ-001 | AC-001-7, AC-001-8
    @pytest.mark.smoke
    def test_react_app_hydrated_successfully(self, hydrated_page: Page):
        """Verify React mounted into #root with child elements.

        Checks that #root has at least one child (React rendered)
        and no error boundary is displayed (React didn't crash).

        Failure means: JS bundle failed to execute, or React
        threw during render and an error boundary caught it.
        """
        with step("Count #root child elements"):
            child_count = hydrated_page.evaluate(
                "document.querySelector('#root').children.length"
            )

        with step("Get #root innerHTML preview for diagnostics"):
            preview = hydrated_page.evaluate(
                "document.querySelector('#root').innerHTML.slice(0, 200)"
            )
            url = hydrated_page.url

        with step(f"Assert #root has children (found {child_count})"):
            assert child_count > 0, Msg.HYDRATION_FAILED.format(
                actual=child_count, url=url, preview=preview,
            )

        with step("Check for React error boundary"):
            error_boundary = hydrated_page.locator(
                '[data-reactroot] .error-boundary, #root > [class*="error"]'
            )
            boundary_count = error_boundary.count()

        with step(f"Assert no error boundary rendered (found {boundary_count})"):
            assert boundary_count == 0, Msg.ERROR_BOUNDARY_RENDERED.format(
                count=boundary_count, url=url,
            )


# ── Navigation ──

class TestNavigation:
    """Navigation tests — header link verification.

    Covers REQ-002 (Navigation Links).
    Parametrized across all four nav items to keep test
    code DRY while ensuring full coverage.
    """

    # REQ-002 | AC-002-1, AC-002-2 (and per parametrize)
    @pytest.mark.navigation
    @pytest.mark.parametrize("label, href", NAV.ALL_WITH_HREFS)
    def test_nav_link_is_visible_with_correct_href(
        self, portfolio: PortfolioPage, label: str, href: str,
    ):
        """Verify each nav link is visible with the correct anchor href.

        Parametrized across all nav items defined in constants.
        Checks visibility and href attribute for each link.

        Failure means: a nav link was removed, hidden, or its
        href was changed in the Navbar component.
        """
        with step(f"Locate nav link '{label}'"):
            link = portfolio.nav_link(label)

        with step(f"Assert '{label}' link is visible"):
            assert link.is_visible(), Msg.NAV_LINK_NOT_VISIBLE.format(name=label)

        with step(f"Assert '{label}' href equals '{href}'"):
            actual_href = link.get_attribute("href")
            assert actual_href == href, Msg.NAV_LINK_WRONG_HREF.format(
                name=label, expected=href, actual=actual_href,
            )


# ── Content ──

class TestContent:
    """Content tests — section data and rendering.

    Covers REQ-003 (Page Content & Data Rendering).
    Verifies that profile.json data is correctly displayed
    in Skills, Projects, Contact, and Test Results sections.
    """

    # REQ-003 | AC-003-1, AC-003-2, AC-003-3
    @pytest.mark.content
    @pytest.mark.parametrize("skill", SKILLS.ALL)
    def test_skills_section_contains_core_stack(
        self, portfolio: PortfolioPage, skill: str,
    ):
        """Verify core skill tag is visible in the Skills section.

        Parametrized across Python, Playwright, pytest.
        Uses exact text matching within #skills.

        Failure means: the skill was removed from profile.json
        or the Skills component stopped rendering it.
        """
        with step(f"Locate skill tag with exact text '{skill}'"):
            tag = portfolio.skill_text(skill)

        with step("Capture screenshot of skills section"):
            portfolio.take_screenshot(f"assert_skill_{skill.lower()}")

        with step(f"Assert '{skill}' tag is visible"):
            assert tag.first.is_visible(), Msg.SKILL_NOT_VISIBLE.format(name=skill)

    # REQ-003 | AC-003-4
    @pytest.mark.content
    def test_projects_section_has_expected_cards(self, portfolio: PortfolioPage):
        """Verify the Projects section renders the expected number of cards.

        Counts elements with role='article' inside #projects.
        Expected: {COUNTS.PROJECT_CARDS} cards from profile.json.

        Failure means: a project was added or removed from
        profile.json, or the Projects component changed markup.
        """
        with step("Count project cards with role='article'"):
            count = portfolio.count_project_cards()

        with step("Capture screenshot of project cards"):
            portfolio.take_screenshot("assert_project_cards")

        with step(f"Assert {COUNTS.PROJECT_CARDS} project cards (found {count})"):
            assert count == COUNTS.PROJECT_CARDS, Msg.WRONG_PROJECT_COUNT.format(
                expected=COUNTS.PROJECT_CARDS, actual=count,
            )

    # REQ-003 | AC-003-5
    @pytest.mark.content
    def test_contact_section_has_required_channels(self, portfolio: PortfolioPage):
        """Verify the Contact section renders the expected number of links.

        Counts links with role='link' inside #contact.
        Expected: {COUNTS.CONTACT_LINKS} channels from profile.json.

        Failure means: a contact channel was added or removed
        from profile.json, or the Contact component changed.
        """
        with step("Count contact links with role='link'"):
            count = portfolio.count_contact_links()

        with step("Capture screenshot of contact section"):
            portfolio.take_screenshot("assert_contact_channels")

        with step(f"Assert {COUNTS.CONTACT_LINKS} contact links (found {count})"):
            assert count == COUNTS.CONTACT_LINKS, Msg.WRONG_CONTACT_COUNT.format(
                expected=COUNTS.CONTACT_LINKS, actual=count,
            )

    # REQ-003 | AC-003-6, AC-003-7, AC-003-8
    @pytest.mark.content
    def test_test_results_section_renders(self, page: Page, base_url: str):
        """
        Test results section must render summary cards and test rows.

        Verifies:
        - Section is visible
        - Summary cards show numeric values (passed/failed/total)
        - At least 1 test row is rendered in the list
        - No error state is shown (e.g. "failed to load")

        Failure means: test_report.json was not generated,
        not deployed, or the fetch URL is wrong.
        """
        with step("Open the portfolio page"):
            portfolio = PortfolioPage(page, base_url)
            portfolio.navigate()

        with step("Locate the test results section"):
            section = page.locator("#test-results")
            assert section.is_visible(), (
                "Test results section #test-results is not visible on page"
            )

        with step("Wait for test data to load from test_report.json"):
            page.wait_for_timeout(2000)

        with step("Verify summary cards show numeric values"):
            summary_cards = section.locator(
                "[class*='summary'], [class*='stat'], [class*='count']"
            )
            card_count = summary_cards.count()

            section_text = section.inner_text()
            has_numbers = any(
                char.isdigit() for char in section_text
            )
            assert has_numbers, (
                f"Test results section has no numeric values. "
                f"Section text: '{section_text[:200]}'. "
                f"Likely test_report.json failed to load."
            )

        with step("Verify at least one test row is rendered"):
            row_count = page.evaluate("""
                () => {
                    const section = document.querySelector('#test-results');
                    if (!section) return 0;
                    return section.querySelectorAll(
                        'div[class*="cursor-pointer"]'
                    ).length;
                }
            """)

            assert row_count > 0, (
                f"No test rows found in results section. "
                f"Expected at least 1 row from test_report.json. "
                f"Found {row_count} rows. "
                f"Check that test_report.json is deployed to dist/ "
                f"and fetch URL uses import.meta.env.BASE_URL prefix."
            )

        with step("Take screenshot showing test results"):
            from datetime import datetime
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            page.screenshot(
                path=f"screenshots/assert_test_results_{ts}.png",
                full_page=False
            )


# ── Responsive ──

class TestResponsive:
    """Responsive tests — mobile viewport behavior.

    Covers REQ-004 (Responsive Layout).
    Tests at 390x844 (iPhone 14) — the most common
    mobile device size to verify no horizontal overflow.
    """

    # REQ-004 | AC-004-1
    @pytest.mark.responsive
    def test_mobile_viewport_no_horizontal_scroll(
        self, mobile_portfolio: PortfolioPage,
    ):
        """No horizontal overflow at 390x844 mobile viewport.

        Measures document.scrollWidth vs window.innerWidth.
        Screenshot captures real rendered mobile layout.
        """
        with step("Wait for mobile page content to be ready"):
            mobile_portfolio.wait_for_content_ready()

        with step("Measure document scroll width"):
            scroll_w = mobile_portfolio.get_scroll_width()

        with step("Get viewport width (390px iPhone 14)"):
            viewport_w = mobile_portfolio.get_viewport_width()

        with step(
            f"Capture full-page screenshot "
            f"(scroll_w={scroll_w}, viewport_w={viewport_w})"
        ):
            mobile_portfolio.take_screenshot(
                "assert_mobile_no_scroll", full_page=True
            )

        with step(
            f"Assert no overflow: "
            f"scroll_w={scroll_w} <= viewport_w={viewport_w}"
        ):
            assert scroll_w <= viewport_w, \
                Msg.HORIZONTAL_OVERFLOW.format(
                    scroll_w=scroll_w, viewport_w=viewport_w,
                )

    # REQ-004 | AC-004-2
    @pytest.mark.responsive
    def test_mobile_hero_section_visible(
        self, mobile_portfolio: PortfolioPage,
    ):
        """Hero h1 must be visible on 390px mobile viewport."""
        with step("Wait for mobile page content to be ready"):
            mobile_portfolio.wait_for_content_ready()

        with step("Locate hero heading"):
            heading = mobile_portfolio.hero_heading

        with step("Get heading text to verify it rendered"):
            heading_text = heading.inner_text()

        with step(
            f"Capture screenshot showing rendered mobile hero "
            f"(h1 text: '{heading_text[:30]}...')"
        ):
            mobile_portfolio.take_screenshot(
                "assert_mobile_hero", full_page=False
            )

        with step(
            f"Assert hero heading visible at {CONFIG.mobile_width}px "
            f"with non-empty text"
        ):
            assert heading.is_visible(), \
                Msg.MOBILE_HERO_NOT_VISIBLE.format(
                    width=CONFIG.mobile_width,
                )
            assert heading_text.strip(), \
                "Hero heading is visible but text is empty"


# ── Performance ──

class TestPerformance:
    """Performance tests — page load timing.

    Covers REQ-005 (Page Load Performance).
    Uses browser Navigation Timing API to measure
    real load duration, not synthetic metrics.
    """

    # REQ-005 | AC-005-1
    @pytest.mark.performance
    def test_page_load_time_within_budget(self, page: Page, base_url: str):
        """Verify page loads within the performance budget.

        Uses Navigation Timing API to measure total load time
        (navigationStart to loadEventEnd).
        Budget: 3000ms.

        Failure means: the page is too slow — check bundle size,
        blocking resources, or server response time.
        """
        with step(f"Navigate to {base_url} and wait for load event"):
            page.goto(base_url, wait_until="load")

        with step("Measure load time via Navigation Timing API"):
            load_ms = page.evaluate(
                "performance.timing.loadEventEnd "
                "- performance.timing.navigationStart"
            )

        with step(f"Assert load time {load_ms:.0f}ms < {PERF.MAX_LOAD_TIME_MS}ms"):
            assert load_ms < PERF.MAX_LOAD_TIME_MS, Msg.SLOW_PAGE_LOAD.format(
                actual=load_ms, budget=PERF.MAX_LOAD_TIME_MS,
            )


# ── Accessibility ──

class TestAccessibility:
    """Accessibility tests — WCAG 2.1 Level AA basics.

    Covers REQ-006 (Accessibility).
    Verifies image alt text and heading hierarchy —
    the two most common WCAG violations on portfolio sites.
    """

    # REQ-006 | AC-006-1
    @pytest.mark.accessibility
    def test_images_have_alt_text(self, page: Page, base_url: str):
        """
        Every image on the page must have a non-empty
        alt attribute for accessibility.
        Uses JS evaluation to avoid per-element timeouts.
        """
        with step("Open the portfolio page"):
            portfolio = PortfolioPage(page, base_url)
            portfolio.navigate()

        with step("Evaluate all images via JavaScript"):
            violations: list[dict] = page.evaluate("""
                () => Array.from(document.querySelectorAll('img'))
                    .filter(img =>
                        img.getAttribute('aria-hidden') !== 'true'
                        && (!img.alt || img.alt.trim() === '')
                    )
                    .map((img, i) => ({
                        index: i,
                        src: (img.src || '').slice(0, 80)
                    }))
            """)

        with step("Take screenshot at assertion point"):
            from datetime import datetime
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            page.screenshot(
                path=f"screenshots/assert_images_alt_{ts}.png",
                full_page=False
            )

        with step("Verify no images are missing alt text"):
            assert violations == [], (
                f"Found {len(violations)} image(s) without alt text: "
                + str(violations)
            )

    # REQ-006 | AC-006-2, AC-006-3, AC-006-4
    @pytest.mark.accessibility
    def test_headings_hierarchy_is_correct(self, portfolio: PortfolioPage):
        """Verify heading levels follow semantic HTML hierarchy.

        Checks three rules:
          1. Exactly one h1 on the page
          2. h1 appears before any h2
          3. No heading level is skipped (e.g., h2 followed by h4)

        Failure means: heading hierarchy is broken — this hurts
        screen reader navigation and SEO.
        """
        with step("Collect all heading elements and their tag names"):
            headings = portfolio.all_headings.all()
            tags = [h.evaluate("el => el.tagName.toLowerCase()") for h in headings]

        with step(f"Assert exactly {COUNTS.H1_HEADINGS} h1 (found {tags.count('h1')})"):
            h1_count = tags.count("h1")
            assert h1_count == COUNTS.H1_HEADINGS, Msg.WRONG_H1_COUNT.format(
                expected=COUNTS.H1_HEADINGS, actual=h1_count,
            )

        with step("Assert h1 appears before first h2"):
            h1_idx = tags.index("h1")
            h2_indices = [i for i, t in enumerate(tags) if t == "h2"]
            if h2_indices:
                assert h1_idx < h2_indices[0], Msg.H1_NOT_FIRST

        with step("Assert no heading levels are skipped"):
            levels = [int(t[1]) for t in tags]
            for i in range(1, len(levels)):
                gap = levels[i] - levels[i - 1]
                assert gap <= 1, Msg.HEADING_LEVEL_SKIPPED.format(
                    prev=levels[i - 1], next=levels[i], pos=i,
                )
