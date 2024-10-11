import pytest

from playwright.sync_api import Page


@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:1313"


@pytest.fixture
def home_page(page: Page, base_url: str) -> Page:
    page.goto(base_url)
    return page
