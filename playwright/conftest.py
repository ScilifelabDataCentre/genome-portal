import pytest

from playwright.sync_api import Page


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
