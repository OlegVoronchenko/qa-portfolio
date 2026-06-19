"""Centralized test configuration — all environment and infra settings in one place."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class TestConfig:
    """Immutable test configuration resolved from environment variables."""

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
