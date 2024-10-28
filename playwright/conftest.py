"""
Fixtures for Playwright tests.
"""

import pytest
from pytest import FixtureRequest

from playwright.sync_api import BrowserContext, Page


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


def generate_single_page(context: BrowserContext, url: str) -> Page:
    """
    Generate a single page object.
    Helper function to generate unique pages like about, contact, etc.
    """
    page = context.new_page()
    page.goto(url)
    return page


@pytest.fixture
def home_page(context: BrowserContext, base_url: str) -> Page:
    return generate_single_page(context=context, url=f"{base_url}/")


@pytest.fixture
def about_page(context: BrowserContext, base_url: str) -> Page:
    return generate_single_page(context=context, url=f"{base_url}/about/")


@pytest.fixture
def about_page_swedish(context: BrowserContext, base_url: str) -> Page:
    return generate_single_page(context=context, url=f"{base_url}/about/sv/")


@pytest.fixture
def glossary_page(context: BrowserContext, base_url: str) -> Page:
    return generate_single_page(context=context, url=f"{base_url}/glossary/")


@pytest.fixture
def contact_page(context: BrowserContext, base_url: str) -> Page:
    return generate_single_page(context=context, url=f"{base_url}/contact/")


@pytest.fixture
def contribute_page(context: BrowserContext, base_url: str) -> Page:
    return generate_single_page(context=context, url=f"{base_url}/contribute/")


@pytest.fixture
def privacy_page(context: BrowserContext, base_url: str) -> Page:
    return generate_single_page(context=context, url=f"{base_url}/privacy/")
