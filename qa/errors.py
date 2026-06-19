"""Assertion error message templates — consistent, descriptive failure output."""


class Messages:
    # Smoke
    TITLE_MISSING_NAME = "Page title should contain engineer name, got: '{title}'"
    TITLE_MISSING_ROLE = "Page title should contain '{expected}', got: '{actual}'"
    HERO_NAME_MISSING = "Hero heading should contain '{expected}', got: '{actual}'"
    NAV_NOT_VISIBLE = "Primary navigation should be visible on page load"
    JS_ERRORS_FOUND = "Uncaught JavaScript errors on page: {errors}"
    HYDRATION_FAILED = "React root should have rendered child elements"
    ERROR_BOUNDARY_RENDERED = "No React error boundary should be rendered"

    # Navigation
    NAV_LINK_NOT_VISIBLE = "Nav link '{name}' should be visible in navbar"
    NAV_LINK_WRONG_HREF = "Nav link '{name}' href should be '{expected}', got: '{actual}'"

    # Content
    SKILL_NOT_VISIBLE = "Skill '{name}' should be visible in the skills section"
    WRONG_PROJECT_COUNT = "Expected {expected} project cards, got: {actual}"
    WRONG_CONTACT_COUNT = "Expected {expected} contact channels, got: {actual}"
    TEST_RESULTS_NOT_VISIBLE = "Test results section should be visible"
    TEST_RESULTS_NO_HEADINGS = "Test results section should have at least one heading"

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
    DEPLOY_NAV_NOT_VISIBLE = "Navigation not visible — React may have failed to render"
    DEPLOY_H1_NOT_VISIBLE = "h1 heading not visible — React may have failed to render"
    DEPLOY_404_PAGE = "Page displays 404 text — deployment may have failed"
    DEPLOY_WRONG_BASE_PATH = (
        "Assets using wrong base path '/assets/' instead of repo-prefixed path: {paths}"
    )
    DEPLOY_JS_ERRORS = "JavaScript errors on production: {errors}"
