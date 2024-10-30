"""
Tests that are applied to every page on the website.
"""

import re

import pytest
from utils import all_page_paths

from playwright.sync_api import Page, expect

ALL_PAGE_PATHS = all_page_paths()


@pytest.mark.parametrize("page_obj", ALL_PAGE_PATHS, indirect=True)
def test_for_placeholder_text(page_obj: Page) -> None:
    """
    Check for any placeholder words like EDIT in all pages.

    By using indirect=True, we can pass the list of paths to the fixture (instead of the directly to test function).
    The fixture converts them to page objects and passes them to the test function.
    """
    PLACEHOLDERS = ["EDIT", "TODO", "XXXXXX", "DD/MM/YYYY"]
    for placeholder in PLACEHOLDERS:
        locator = page_obj.get_by_text(placeholder)
        expect(
            locator, f"Found what looks like a placeholder: '{placeholder}' on this page: {page_obj.url}"
        ).to_have_count(0)


@pytest.mark.parametrize("page_obj", ALL_PAGE_PATHS, indirect=True)
def test_for_meta_description_tag(page_obj: list[Page]) -> None:
    """
    Validate each page has a HTML <meta> Tag with a description.
    The regex simply checks for one or more word present in description.
    """
    regex_pattern = re.compile(r"\w+")
    meta_description = page_obj.locator("meta[name='description']")
    expect(
        meta_description, f"The Page {page_obj.url} is missing a meta description tag: {page_obj.url}"
    ).to_have_attribute(name="content", value=regex_pattern)
