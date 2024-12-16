"""
Tests for each species download page.
"""

import re

import pytest
from utils import DOWNLOAD_PAGE_PATHS, validate_date_format

from playwright.sync_api import Locator, Page, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


def get_links_column(page: Page) -> list[str]:
    """
    Helper function to get the links column cells from the download table.
    Column is titled "Links"
    """
    short_table = page.locator("#downloadTableShort_wrapper")
    return short_table.locator("td:nth-child(3)").all()


def get_date_column_texts(page: Page) -> list[str]:
    """
    Helper function to get the date column cells from the download table.
    Column is titled "First date on Portal"
    """
    short_table = page.locator("#downloadTableLong_wrapper")
    return short_table.locator("td:nth-child(8)").all_inner_texts()


@pytest.mark.parametrize("page_obj", DOWNLOAD_PAGE_PATHS, indirect=True)
def test_required_header_visible(page_obj: Page) -> None:
    """
    Test the required header 'Data availability' is present in the download page.
    """
    HEADER_TEXT = "Data availability"
    locator = page_obj.get_by_role("heading", name=HEADER_TEXT)
    expect(locator, f"The heading: {HEADER_TEXT} is not visible on page: {page_obj.url}").to_be_visible()


@pytest.mark.parametrize("page_obj", DOWNLOAD_PAGE_PATHS, indirect=True)
def test_toggle_switch(page_obj: Page) -> None:
    """
    Test the toggle switch correctly swaps between the long and short table views.
    """
    toggle_switch = page_obj.get_by_role("switch", name="Show reduced table view")
    short_table = page_obj.locator("#downloadTableShort_wrapper")
    long_table = page_obj.locator("#downloadTableLong_wrapper")

    expect(long_table).to_be_hidden()
    expect(short_table).to_be_visible()

    toggle_switch.click()
    expect(long_table).to_be_visible()
    expect(short_table).to_be_hidden()

    toggle_switch.click()
    expect(long_table).to_be_hidden()
    expect(short_table).to_be_visible()


@pytest.mark.parametrize("page_obj", DOWNLOAD_PAGE_PATHS, indirect=True)
def test_date_format_in_download_table(page_obj: Page) -> None:
    """
    Validates the date format in the download table is correct.
    """
    toggle_switch = page_obj.get_by_role("switch", name="Show reduced table view")
    toggle_switch.click()

    dates_column = get_date_column_texts(page=page_obj)

    for date in dates_column:
        valid_date = True
        try:
            validate_date_format(date=date, date_format="%d %B %Y")
        except AssertionError:
            valid_date = False

        assert (
            valid_date
        ), f"Download table date formatting incorrect on page: {page_obj.url}. Format should be e.g.: 15 October 2024"


@pytest.mark.parametrize("page_obj", DOWNLOAD_PAGE_PATHS, indirect=True)
def test_table_links(page_obj: Page):
    """
    For each species download table, there is a "Links" column. Each cell in this column can contain up to 3 links.
    Links are of type: "Download", "Article", "Website".
    This test validates each link in the table as precisely as possible.
    """
    links_table_column = get_links_column(page=page_obj)
    for single_cell in links_table_column:
        links_in_the_cell = single_cell.locator("a").all()
        for link_locator in links_in_the_cell:
            link_type = link_locator.inner_text()
            link_href = link_locator.get_attribute("href")

            if link_type == "Download":
                validate_download_link(page=page_obj, link_locator=link_locator, link_href=link_href)
            elif link_type == "Article":
                validate_article_link(page=page_obj, link_href=link_href)
            elif link_type == "Website":
                validate_website_link(page=page_obj, link_href=link_href)
            else:
                raise ValueError("Unknown link type: {link_type} for url {link_info.page.url}")


def validate_download_link(page: Page, link_locator: Locator, link_href: str) -> None:
    """
    Validate a download link on each download page's table.
    Checks the link is a direct download link, but does not wait for the download to complete.
    That could take way too long.
    """
    KNOWN_FAILING_LINKS = "https://figshare.scilifelab.se/ndownloader/files/50074047"

    download_works = True
    try:
        with page.expect_download() as _:
            link_locator.click()
    except PlaywrightTimeoutError:
        if link_href not in KNOWN_FAILING_LINKS:
            download_works = False

    assert download_works, (
        f"A Download button link on the table on page: {page.url} does not appear to be a link.\n"
        f"This is the href: {link_href}"
    )


def validate_article_link(page: Page, link_href: str) -> None:
    """
    Validate a article link on each download tables page's table.
    Checks to see if in format of a valid DOI.
    """
    valid_doi = re.match(r"^https://doi\.org/", link_href)
    assert valid_doi, (
        f"An Article button link on the table on page: {page.url} does not appear to be a valid DOI.\n"
        f"This is the href: {link_href}"
    )


def validate_website_link(page: Page, link_href: str) -> None:
    """
    Validate a website link on each download tables page's table.
    Confirm the Website is a valid URL - hard to test more specifically than this.
    """
    valid_url = re.match(r"^https?://", link_href)
    assert valid_url, (
        f"An Website button link on the table on page: {page.url} does not appear to be a valid website.\n"
        f"This is the href: {link_href}"
    )
