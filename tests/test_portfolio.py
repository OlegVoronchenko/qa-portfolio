import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from pages.portfolio_page import PortfolioPage


class TestPortfolio:
    def test_page_loads_and_title_correct(self, page):
        portfolio = PortfolioPage(page)
        portfolio.navigate()
        assert "Oleg V." in portfolio.get_title()
        assert "QA" in portfolio.get_title()

    def test_hero_section_visible(self, page):
        portfolio = PortfolioPage(page)
        portfolio.navigate()
        assert portfolio.hero.is_visible()

    def test_hero_title_contains_qa(self, page):
        portfolio = PortfolioPage(page)
        portfolio.navigate()
        text = portfolio.hero_title.inner_text()
        assert "Oleg V." in text

    def test_nav_link_about_exists(self, page):
        portfolio = PortfolioPage(page)
        portfolio.navigate()
        assert portfolio.nav_link("about").is_visible()

    def test_nav_link_skills_exists(self, page):
        portfolio = PortfolioPage(page)
        portfolio.navigate()
        assert portfolio.nav_link("skills").is_visible()

    def test_nav_link_projects_exists(self, page):
        portfolio = PortfolioPage(page)
        portfolio.navigate()
        assert portfolio.nav_link("projects").is_visible()

    def test_nav_link_contact_exists(self, page):
        portfolio = PortfolioPage(page)
        portfolio.navigate()
        assert portfolio.nav_link("contact").is_visible()

    def test_skills_section_has_python_tag(self, page):
        portfolio = PortfolioPage(page)
        portfolio.navigate()
        assert portfolio.skill_tag_containing("Python").first.is_visible()

    def test_skills_section_has_playwright_tag(self, page):
        portfolio = PortfolioPage(page)
        portfolio.navigate()
        assert portfolio.skill_tag_containing("Playwright").first.is_visible()

    def test_skills_section_has_pytest_tag(self, page):
        portfolio = PortfolioPage(page)
        portfolio.navigate()
        assert portfolio.skill_tag_containing("Pytest").first.is_visible()

    def test_projects_section_has_three_cards(self, page):
        portfolio = PortfolioPage(page)
        portfolio.navigate()
        assert portfolio.project_cards.count() == 3

    def test_contact_section_has_four_items(self, page):
        portfolio = PortfolioPage(page)
        portfolio.navigate()
        assert portfolio.contact_items.count() == 4

    def test_mobile_no_horizontal_overflow(self, mobile_page):
        portfolio = PortfolioPage(mobile_page)
        portfolio.navigate()
        viewport_width = mobile_page.viewport_size["width"]
        scroll_width = mobile_page.evaluate("document.documentElement.scrollWidth")
        assert scroll_width <= viewport_width

    def test_page_loads_under_3_seconds(self, page):
        portfolio = PortfolioPage(page)
        start = time.time()
        portfolio.navigate()
        elapsed = time.time() - start
        assert elapsed < 3.0, f"Page load took {elapsed:.2f}s"

    def test_no_broken_images(self, page):
        portfolio = PortfolioPage(page)
        portfolio.navigate()
        page.wait_for_load_state("networkidle")
        images = portfolio.images.all()
        for img in images:
            natural_width = img.evaluate("el => el.naturalWidth")
            assert natural_width > 0, f"Broken image: {img.get_attribute('src')}"
