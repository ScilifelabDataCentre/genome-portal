"""
Tests for the contribute page and it's two subpages.
"""

import re

import pytest
from utils import validate_date_format

from playwright.sync_api import Page, expect

# key = subpage name, value = expected title
SUBPAGES = {
    "Supported data file formats": "Supported data file formats",
    "Recommendations on how to make data files publicly available": "Recommendations for making data publicly available",
}


def test_has_title(contribute_page: Page) -> None:
    """Test that the contact page has the correct title."""
    expect(contribute_page).to_have_title(re.compile("Contribute"))


def test_has_last_updated(contribute_page: Page) -> None:
    """Test that the contribute page has the last updated date."""
    locator = contribute_page.get_by_text("Page last updated: ")
    expect(locator).to_be_visible()
    date = locator.inner_text().split(":")[1].strip()

    validate_date_format(date=date, date_format="%d %B %Y")


@pytest.mark.parametrize("subpage_link, subpage_title", SUBPAGES.items())
def test_subpages_linked(contribute_page: Page, subpage_link: str, subpage_title: str) -> None:
    """Test that the subpages of the contribute page are linked correctly."""
    contribute_page.get_by_role("link", name=subpage_link).click()
    expect(contribute_page).to_have_title(re.compile(subpage_title))
    contribute_page.go_back()


@pytest.mark.parametrize("subpage_link", SUBPAGES.keys())
def test_table_of_contents_in_subpages(contribute_page: Page, subpage_link: str) -> None:
    """Test that the table of contents is present in the subpages."""
    contribute_page.get_by_role("link", name=subpage_link).click()
    expect(contribute_page.locator("#TableOfContents")).to_be_visible()
    contribute_page.go_back()
