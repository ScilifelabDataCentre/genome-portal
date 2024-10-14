import pytest

from playwright.sync_api import BrowserContext, Page
from tests.utils import get_list_of_species

SPECIES = get_list_of_species()


@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:1313"


@pytest.fixture
def home_page(page: Page, base_url: str) -> Page:
    page.goto(base_url)
    return page


@pytest.fixture
def about_page(page: Page, base_url: str) -> Page:
    page.goto(base_url + "/about/")
    return page


@pytest.fixture
def glossary_page(page: Page, base_url: str) -> Page:
    page.goto(base_url + "/glossary/")
    return page


@pytest.fixture
def contact_page(page: Page, base_url: str) -> Page:
    page.goto(base_url + "/contact/")
    return page


@pytest.fixture
def contribute_page(page: Page, base_url: str) -> Page:
    page.goto(base_url + "/contribute/")
    return page


def generate_pages(context: BrowserContext, base_url: str, path_suffix: str) -> list[Page]:
    """
    Generate a list of species pages for a given path suffix.
    Helper functionto generate intro, assembly, and download pages.
    """
    pages = []
    for species in SPECIES:
        page = context.new_page()
        page.goto(f"{base_url}/{species}{path_suffix}")
        pages.append(page)
    return pages


@pytest.fixture
def all_intro_pages(context: BrowserContext, base_url: str) -> list[Page]:
    """Return a list of all species intro pages."""
    return generate_pages(context, base_url, "")


@pytest.fixture
def all_assembly_pages(context: BrowserContext, base_url: str) -> list[Page]:
    """Return a list of all species assembly pages."""
    return generate_pages(context, base_url, "/assembly")


@pytest.fixture
def all_download_pages(context: BrowserContext, base_url: str) -> list[Page]:
    """Return a list of all species download pages."""
    return generate_pages(context, base_url, "/download")
