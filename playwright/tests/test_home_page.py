import re

from playwright.sync_api import Page, expect


def test_has_title(home_page: Page):
    """Test that the home page has the correct title."""
    expect(home_page).to_have_title(re.compile("Swedish Reference Genome Portal"))


def test_navbar_links(home_page: Page):
    """Test navbar links redirect to the correct page."""
    links = {"Home": "Home", "About": "About", "Glossary": "Glossary", "Contact": "Contact"}

    for name, title in links.items():
        home_page.locator("#navbarSupportedContent").get_by_role("link", name=name).click()
        expect(home_page).to_have_title(re.compile(title))
