"""
Assertion Error Messages
========================

PURPOSE
-------
All assertion failure messages used by tests.
Templated with format placeholders for actual values.

WHY THIS EXISTS
---------------
Generic 'assert True' messages waste debugging time.
Detailed messages with expected vs actual values
let you diagnose failures from CI logs alone — no
need to rerun locally with a debugger.

PATTERN
-------
Every message follows this structure:
    'What was expected, what was found, where, what to check'

Example:
    NAV_LINK_WRONG_HREF: str = (
        "Nav link '{name}' href should be '{expected}', "
        "got '{actual}'. Check Navbar component anchor links."
    )
"""


class Messages:
    """str.format() templates for all assertion error messages.

    Each attribute is a template string with named placeholders.
    Tests call Msg.TEMPLATE_NAME.format(key=value) to produce
    the final error message shown in CI logs.
    """
    # Smoke
    TITLE_MISSING_NAME = "Page title should contain engineer name, got: '{title}'"
    TITLE_MISSING_ROLE = "Page title should contain '{expected}', got: '{actual}'"
    HERO_NAME_MISSING = "Hero heading should contain '{expected}', got: '{actual}'"
    NAV_NOT_VISIBLE = (
        "No navigation landmark found on '{url}'. "
        "Found {count} elements with role='navigation'. "
        "Expected at least 1 visible <nav>."
    )
    JS_ERRORS_FOUND = "Uncaught JavaScript errors on page: {errors}"
    HYDRATION_FAILED = (
        "React #root has {actual} children on '{url}'. "
        "Expected > 0. "
        "This usually means JS failed to load or execute. "
        "Preview: '{preview}'"
    )
    ERROR_BOUNDARY_RENDERED = (
        "React error boundary detected ({count} elements) on '{url}'. "
        "The app crashed during render."
    )

    # Navigation
    NAV_LINK_NOT_VISIBLE = "Nav link '{name}' should be visible in navbar"
    NAV_LINK_WRONG_HREF = (
        "Nav link '{name}' href should be '{expected}', got: '{actual}'"
    )

    # Content
    SKILL_NOT_VISIBLE = "Skill '{name}' should be visible in the skills section"
    WRONG_PROJECT_COUNT = "Expected {expected} project cards, got: {actual}"
    WRONG_CONTACT_COUNT = "Expected {expected} contact channels, got: {actual}"
    TEST_RESULTS_NOT_VISIBLE = (
        "Test results section not visible on '{url}'. "
        "Section exists in DOM: {exists}."
    )
    TEST_RESULTS_NO_HEADINGS = (
        "Test results section has {actual} headings on '{url}'. "
        "Expected at least 1."
    )

    # Responsive
    HORIZONTAL_OVERFLOW = (
        "Horizontal overflow on mobile: "
        "scrollWidth={scroll_w}, viewportWidth={viewport_w}"
    )
    MOBILE_HERO_NOT_VISIBLE = (
        "Hero heading should be visible at {width}px mobile viewport"
    )

    # Performance
    SLOW_PAGE_LOAD = "Page loaded in {actual:.0f}ms, expected under {budget}ms"

    # Accessibility
    IMAGES_MISSING_ALT = "Images missing alt text: {sources}"
    WRONG_H1_COUNT = "Expected exactly {expected} h1, found: {actual}"
    H1_NOT_FIRST = "h1 should appear before the first h2 in document order"
    HEADING_LEVEL_SKIPPED = (
        "Heading level skipped: h{prev} followed by h{next} at position {pos}"
    )

    # Deployment
    ASSET_404 = "Asset requests returned 404 (likely wrong base path): {urls}"
    DEPLOY_TITLE_WRONG = "Page title should contain '{expected}', got: '{actual}'"
    DEPLOY_NAV_NOT_FOUND = (
        "Navigation not found on '{url}'. "
        "Found {count} elements with role='navigation'. "
        "React may not have hydrated."
    )
    DEPLOY_NAV_HIDDEN = (
        "Navigation exists ({count} elements) but is not visible on '{url}'."
    )
    DEPLOY_H1_WRONG_COUNT = (
        "Expected exactly 1 h1 on production, found {actual} on '{url}'."
    )
    DEPLOY_H1_EMPTY = "h1 exists but has no text content on '{url}'."
    DEPLOY_NAV_NOT_VISIBLE = (
        "Navigation not visible on '{url}' — React may have failed to render"
    )
    DEPLOY_H1_NOT_VISIBLE = (
        "h1 heading not visible on '{url}' — React may have failed to render"
    )
    DEPLOY_404_PAGE = "Page displays 404 text — deployment may have failed"
    DEPLOY_WRONG_BASE_PATH = (
        "Assets using wrong base path '/assets/' instead of "
        "repo-prefixed path: {paths}"
    )
    DEPLOY_JS_ERRORS = "JavaScript errors on production: {errors}"
