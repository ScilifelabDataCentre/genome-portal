import re

from playwright.sync_api import Page, expect


def test_has_title(about_page: Page):
    """Test that the about page has the correct title."""
    expect(about_page).to_have_title(re.compile("About"))


def test_can_navigate_to_swedish_version(about_page: Page):
    """Test that can swap back and forth between swedish and english version of the pages."""
    alert = about_page.get_by_role("alert")
    expect(alert).to_be_visible()
    about_page.get_by_role("link", name="klicka här för att komma dit.").click()
    expect(about_page).to_have_title(re.compile("Information på svenska"))
    # now on swedish version of the page.
    alert = about_page.get_by_role("alert")
    expect(alert).to_be_visible()
    about_page.get_by_role("link", name="click here to go to this page.").click()
    expect(about_page).to_have_title(re.compile("About"))
