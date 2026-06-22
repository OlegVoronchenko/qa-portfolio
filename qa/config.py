"""
Test Configuration
==================

PURPOSE
-------
Single source of truth for all test configuration values.
Environment variables override defaults — making the test
suite portable between local development and CI.

WHY THIS EXISTS
---------------
Hardcoded URLs, timeouts, and viewport sizes scattered
across test files create maintenance nightmares. This
file centralizes everything into a frozen dataclass.

USAGE
-----
    from config import CONFIG
    page.goto(CONFIG.base_url)
    page.set_viewport_size({'width': CONFIG.mobile_width, ...})

ENVIRONMENT VARIABLES
---------------------
- BASE_URL              local dev/CI URL (default: http://localhost:8080)
- GITHUB_PAGES_URL      production URL (deployment tests only)
- TIMEOUT_NAVIGATION    page goto timeout in ms (default: 30000)
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class TestConfig:
    """Immutable test configuration resolved from environment variables.

    All timeouts are in milliseconds. Viewport sizes match real
    devices: desktop is a standard 720p monitor, mobile is iPhone 14.
    """

    base_url: str
    github_pages_url: str
    timeout_default: int
    timeout_navigation: int
    timeout_hydration: int
    desktop_width: int
    desktop_height: int
    mobile_width: int
    mobile_height: int
    server_port: int


def get_config() -> TestConfig:
    """Build config from environment, falling back to sensible defaults."""
    return TestConfig(
        base_url=os.getenv("BASE_URL", "http://localhost:8080"),
        github_pages_url=os.getenv("GITHUB_PAGES_URL", ""),
        timeout_default=10_000,
        timeout_navigation=30_000,
        timeout_hydration=15_000,
        desktop_width=1280,
        desktop_height=720,
        mobile_width=390,
        mobile_height=844,
        server_port=8080,
    )


CONFIG = get_config()
