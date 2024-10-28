"""
Tests for each species assembly page.
"""

import pytest
from utils import all_assembly_page_paths

from playwright.sync_api import Page, expect

REQUIRED_HEADERS = ["Description", "Annotation Statistics", "Assembly Statistics"]

ALL_ASSEMBLY_PAGE_PATHS = all_assembly_page_paths()


@pytest.mark.parametrize("heading_text", REQUIRED_HEADERS)
@pytest.mark.parametrize("page_obj", ALL_ASSEMBLY_PAGE_PATHS, indirect=True)
def test_required_headers_visible(page_obj: Page, heading_text: str) -> None:
    """
    Test the required headers for the assembly page are present.
    """
    locator = page_obj.get_by_role("heading", name=heading_text)
    expect(locator, f"The heading: {heading_text} is not visible on page: {page_obj.url}").to_be_visible()
