"""
Tests for each species assembly page.

The conftest.py has a fixture (all_assembly_pages) that returns a list of all the assembly pages for each species.
This way each test can be run on every species including those newly added.
"""

import pytest  # noqa

from utils import validate_date_format  # noqa

from playwright.sync_api import Page, expect, Locator  # noqa
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError  # noqa

REQUIRED_HEADERS = ["Description", "Annotation Statistics", "Assembly Statistics"]


@pytest.mark.parametrize("heading_text", REQUIRED_HEADERS)
def test_required_headers_visible(all_assembly_pages: list[Page], heading_text: str):
    """
    Test the required headers for the assembly page are present.
    """
    for assembly_page in all_assembly_pages:
        locator = assembly_page.get_by_role("heading", name=heading_text)
        expect(locator, f"The heading: {heading_text} is not visible on page: {assembly_page.url}").to_be_visible()
