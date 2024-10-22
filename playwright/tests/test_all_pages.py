"""
Tests that are applied to every page on the website.
"""

import re

from playwright.sync_api import Page, expect


def test_for_placeholder_text(all_pages: list[Page]) -> None:
    """
    Check for any placeholder words like EDIT in all pages.
    """
    PLACEHOLDERS = ["EDIT", "TODO", "XXXXXX", "DD/MM/YYYY"]

    for page in all_pages:
        for placeholder in PLACEHOLDERS:
            locator = page.get_by_text(placeholder)
            expect(
                locator, f"Found what looks like a placeholder: '{placeholder}' on this page: {page.url}"
            ).to_have_count(0)


def test_for_meta_description_tag(all_pages: list[Page]) -> None:
    """
    Validate each page has a HTML <meta> Tag with a description.
    The regex simply checks for one or more word present in description.
    """
    regex_pattern = re.compile(r"\w+")
    for page in all_pages:
        meta_description = page.locator("meta[name='description']")
        expect(
            meta_description, f"The Page {page.url} is missing a meta description tag: {page.url}"
        ).to_have_attribute(name="content", value=regex_pattern)
