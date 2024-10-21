"""
Tests for the contribute page and it's two subpages.
"""

import re

from utils import validate_date_format

from playwright.sync_api import Page, expect

SUBPAGES = (
    "Recommendations for file formats",
    "Recommendations of how to make data files publicly available",
)


def test_has_title(contribute_page: Page) -> None:
    """Test that the contact page has the correct title."""
    expect(contribute_page).to_have_title(re.compile("Contribute"))


def test_has_last_updated(contribute_page: Page) -> None:
    """Test that the contribute page has the last updated date."""
    locator = contribute_page.get_by_text("Page last updated: ")
    expect(locator).to_be_visible()
    date = locator.inner_text().split(":")[1].strip()

    validate_date_format(date=date, date_format="%d %B %Y")


def test_subpages_linked(contribute_page: Page) -> None:
    """Test that the subpages of the contribute page are linked correctly."""
    for subpage in SUBPAGES:
        contribute_page.get_by_role("link", name=subpage).click()
        expect(contribute_page).to_have_title(re.compile(subpage))
        contribute_page.go_back()


def test_table_of_contents_in_subpages(contribute_page: Page) -> None:
    """Test that the table of contents is present in the subpages."""
    for subpage in SUBPAGES:
        contribute_page.get_by_role("link", name=subpage).click()
        expect(contribute_page.locator("#TableOfContents")).to_be_visible()
        contribute_page.go_back()
