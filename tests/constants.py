"""Expected values and test data — separated from test logic."""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class PageTitle:
    CONTAINS_ROLE: str = "QA"
    CONTAINS_TYPE: str = "Engineer"


@dataclass(frozen=True)
class HeroContent:
    CONTAINS_NAME: str = "Oleg"


@dataclass(frozen=True)
class Sections:
    HERO: str = "#hero"
    ABOUT: str = "#about"
    SKILLS: str = "#skills"
    PROJECTS: str = "#projects"
    TEST_RESULTS: str = "#test-results"
    CONTACT: str = "#contact"


@dataclass(frozen=True)
class NavLinks:
    ABOUT: str = "About"
    SKILLS: str = "Skills"
    PROJECTS: str = "Projects"
    CONTACT: str = "Contact"
    ALL_WITH_HREFS: Tuple[tuple, ...] = (
        ("About", "#about"),
        ("Skills", "#skills"),
        ("Projects", "#projects"),
        ("Contact", "#contact"),
    )


@dataclass(frozen=True)
class CoreSkills:
    ALL: Tuple[str, ...] = ("Python", "Playwright", "Pytest")


@dataclass(frozen=True)
class ExpectedCounts:
    PROJECT_CARDS: int = 3
    CONTACT_LINKS: int = 4
    H1_HEADINGS: int = 1


@dataclass(frozen=True)
class PerformanceBudget:
    MAX_LOAD_TIME_MS: int = 3_000


PAGE_TITLE = PageTitle()
HERO = HeroContent()
SECTIONS = Sections()
NAV = NavLinks()
SKILLS = CoreSkills()
COUNTS = ExpectedCounts()
PERF = PerformanceBudget()
