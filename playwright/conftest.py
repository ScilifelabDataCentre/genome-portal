"""
Fixtures for Playwright tests.
"""

import pytest
from pytest import FixtureRequest

from playwright.sync_api import Page


@pytest.fixture
def page_obj(page: Page, request: FixtureRequest, base_url: str) -> Page:
    """
    A fixture that converts a path (str) to a Playwright Page object from that path.
    Used when want to test multiple pages with the same test function at once.

    Works by:
    - Taking the path from request.param and constructs the full URL using base_url.
    - Navigates the Playwright Page object to the URL.
    - Returns the Page object for use in tests.

    This function is used with @pytest.mark.parametrize:
    - Each test uses "indirect=True" to pass the path to this fixture instead of directly to the test function.
    """
    url = f"{base_url}/{request.param}"
    page.goto(url)
    return page


def generate_single_page(page: Page, url: str) -> Page:
    """
    Generate a single page object.
    Helper function to generate unique pages like about, contact, etc.
    """
    page.goto(url)
    return page


@pytest.fixture
def home_page(page: Page, base_url: str) -> Page:
    return generate_single_page(page=page, url=f"{base_url}/")


@pytest.fixture
def about_page(page: Page, base_url: str) -> Page:
    return generate_single_page(page=page, url=f"{base_url}/about/")


@pytest.fixture
def about_page_swedish(page: Page, base_url: str) -> Page:
    return generate_single_page(page=page, url=f"{base_url}/about/sv/")


@pytest.fixture
def cite_us_page(page: Page, base_url: str) -> Page:
    return generate_single_page(page=page, url=f"{base_url}/citation/")


@pytest.fixture
def contact_page(page: Page, base_url: str) -> Page:
    return generate_single_page(page=page, url=f"{base_url}/contact/")


@pytest.fixture
def contribute_page(page: Page, base_url: str) -> Page:
    return generate_single_page(page=page, url=f"{base_url}/contribute/")


@pytest.fixture
def glossary_page(page: Page, base_url: str) -> Page:
    return generate_single_page(page=page, url=f"{base_url}/glossary/")


@pytest.fixture
def privacy_page(page: Page, base_url: str) -> Page:
    return generate_single_page(page=page, url=f"{base_url}/privacy/")


@pytest.fixture
def supported_formats_page(page: Page, base_url: str) -> Page:
    return generate_single_page(page=page, url=f"{base_url}/contribute/supported_file_formats/")
