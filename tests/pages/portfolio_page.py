from playwright.sync_api import Page, expect


class PortfolioPage:
    URL = "http://localhost:8080"

    def __init__(self, page: Page):
        self.page = page
        self.hero = page.locator("#hero")
        self.hero_title = page.locator(".hero h1")
        self.navbar = page.locator(".navbar")
        self.nav_links = page.locator(".nav-links")
        self.about_section = page.locator("#about")
        self.skills_section = page.locator("#skills")
        self.projects_section = page.locator("#projects")
        self.contact_section = page.locator("#contact")
        self.project_cards = page.locator(".project-card")
        self.contact_items = page.locator(".contact-item")
        self.skill_tags = page.locator(".skill-tag")
        self.images = page.locator("img")

    def navigate(self):
        self.page.goto(self.URL, wait_until="domcontentloaded")

    def get_title(self) -> str:
        return self.page.title()

    def nav_link(self, section: str):
        return self.nav_links.locator(f'a[href="#{section}"]')

    def skill_tag_containing(self, text: str):
        return self.skills_section.locator(".skill-tag", has_text=text)
