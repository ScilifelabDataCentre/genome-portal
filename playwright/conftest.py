"""
Essentially holds the fixtures for each page on the website.

Note that of use of context.new_page() is required when you combine multiple page objects in a single test.
For example when generating the all_pages() fixture, we need to create a new page object for each page.
Otherwise it would return a list of the same page object (i.e., the last page included) over and over again.
With context.new_page(), we get a list of all the unique pages that we want to test.
"""

import pytest

from playwright.sync_api import BrowserContext, Page
from tests.utils import get_list_of_species


@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:1313"


def generate_single_page(context: BrowserContext, url: str) -> Page:
    """
    Generate a single page object.
    Helper function to generate unique pages like about, contact, etc.
    """
    page = context.new_page()
    page.goto(url)
    return page


def generate_species_pages(context: BrowserContext, base_url: str, path_suffix: str) -> list[Page]:
    """
    Generate a list of species pages for a given path suffix.
    Helper function to generate intro, assembly, and download pages.
    """
    pages = []
    for species in get_list_of_species():
        page = context.new_page()
        page.goto(f"{base_url}/{species}/{path_suffix}")
        pages.append(page)
    return pages


@pytest.fixture
def home_page(context: BrowserContext, base_url: str) -> Page:
    return generate_single_page(context=context, url=base_url)


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


@pytest.fixture
def all_intro_pages(context: BrowserContext, base_url: str) -> list[Page]:
    """Return a list of all species intro pages."""
    return generate_species_pages(context, base_url, "")


@pytest.fixture
def all_assembly_pages(context: BrowserContext, base_url: str) -> list[Page]:
    """Return a list of all species assembly pages."""
    return generate_species_pages(context, base_url, "assembly")


@pytest.fixture
def all_download_pages(context: BrowserContext, base_url: str) -> list[Page]:
    """Return a list of all species download pages."""
    return generate_species_pages(context, base_url, "download")


@pytest.fixture
def all_pages(
    home_page: Page,
    about_page: Page,
    about_page_swedish: Page,
    glossary_page: Page,
    contact_page: Page,
    contribute_page: Page,
    privacy_page: Page,
    all_intro_pages: list[Page],
    all_assembly_pages: list[Page],
    all_download_pages: list[Page],
) -> list[Page]:
    """Return a list of all pages on the website."""
    return (
        [home_page, about_page, about_page_swedish, glossary_page, contact_page, contribute_page, privacy_page]
        + all_intro_pages
        + all_assembly_pages
        + all_download_pages
    )
