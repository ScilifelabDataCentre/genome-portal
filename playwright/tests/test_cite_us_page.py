"""
Test the cite us page.
"""

import re

from playwright.sync_api import Page, expect


def test_has_toc(cite_us_page: Page):
    """
    Test that the cite us page has a table of contents.
    """
    expect(cite_us_page.locator("#TableOfContents")).to_be_visible()


def test_has_title(cite_us_page: Page):
    """Test that the cite us page has the correct title."""
    expect(cite_us_page).to_have_title(re.compile("How to cite the Genome Portal and the data"))
