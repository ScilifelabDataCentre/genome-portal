"""
Tests that are applied to every page on the website.
"""

import re

from playwright.sync_api import Page, expect


def test_for_unedited_content(all_pages: list[Page]):
    """
    Check for words in the template files that should have been removed/replaced.
    [EDIT] is present in the templates a lot.
    """
    for page in all_pages:
        locator = page.get_by_text("[EDIT")
        expect(locator, f"Found the word '[EDIT]' on this page: {page.url}").to_have_count(0)


def test_for_todo(all_pages: list[Page]):
    """
    Check for any TODOs in the pages.
    """
    for page in all_pages:
        locator = page.get_by_text("TODO")
        expect(locator, f"Found the word 'TODO' on this page: {page.url}").to_have_count(0)


def test_for_meta_description_tag(all_pages: list[Page]):
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
