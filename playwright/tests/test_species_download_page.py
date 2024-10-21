"""
Tests for each species download page.

The conftest.py has a fixture (all_download_pages) that returns a list of all the download pages for each species.
This way each test can be run on every species including those newly added.
"""

import re
from typing import NamedTuple

import pytest
from utils import validate_date_format

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


def test_required_header_visible(all_download_pages: list[Page]) -> None:
    """
    Test the required header 'Data availability' is present in the download page.
    """
    HEADER_TEXT = "Data availability"
    for download_page in all_download_pages:
        locator = download_page.get_by_role("heading", name=HEADER_TEXT)
        expect(locator, f"The heading: {HEADER_TEXT} is not visible on page: {download_page.url}").to_be_visible()


def test_toggle_switch(all_download_pages: list[Page]) -> None:
    """
    Test the toggle switch correctly swaps between the long and short table views.
    """
    for download_page in all_download_pages:
        toggle_switch = download_page.get_by_role("switch", name="Show reduced table view")
        short_table = download_page.locator("#downloadTableShort_wrapper")
        long_table = download_page.locator("#downloadTableLong_wrapper")

        expect(long_table).to_be_hidden()
        expect(short_table).to_be_visible()

        toggle_switch.click()
        expect(long_table).to_be_visible()
        expect(short_table).to_be_hidden()

        toggle_switch.click()
        expect(long_table).to_be_hidden()
        expect(short_table).to_be_visible()


def test_date_format_in_download_table(all_download_pages: list[Page]) -> None:
    """
    Validates the date format in the download table is correct.
    """
    for download_page in all_download_pages:
        toggle_switch = download_page.get_by_role("switch", name="Show reduced table view")
        toggle_switch.click()

        dates_column = get_date_column_texts(page=download_page)

        for date in dates_column:
            valid_date = True
            try:
                validate_date_format(date=date, date_format="%d %B %Y")
            except AssertionError:
                valid_date = False

            assert valid_date, f"Download table date formatting incorrect on page: {download_page.url}. Format should be e.g.: 15 October 2024"


class LinkInfo(NamedTuple):
    """
    Stores the content/location of an individual download table link (inside the Links column) on the download table.
    Used to test the links in the download table.
    """

    link_type: str
    page: Page
    href: str
    link_locator: Locator


@pytest.fixture(scope="function")
def all_links(all_download_pages: list[Page]):
    """
    Obtain all the links from the download table on all download pages.
    The links are stored as a namedtuple
    """
    all_links = []
    for download_page in all_download_pages:
        links_table_column = get_links_column(page=download_page)
        for single_cell in links_table_column:
            links_in_the_cell = single_cell.locator("a").all()
            for link_locator in links_in_the_cell:
                all_links.append(
                    LinkInfo(
                        link_type=link_locator.inner_text(),
                        page=download_page,
                        href=link_locator.get_attribute("href"),
                        link_locator=link_locator,
                    )
                )
    return all_links


def test_download_links(all_links: NamedTuple) -> None:
    """
    Test to validate the download links on each download page's table.
    Test confirms the link is a direct download link, but does not wait for the download to complete.
    That could take way too long.
    """
    for link_info in all_links:
        if link_info.link_type == "Download":
            download_works = True
            try:
                with link_info.page.expect_download() as _:
                    link_info.link_locator.click()
            except PlaywrightTimeoutError:
                download_works = False

            assert download_works, (
                f"A Download button link on the table on page: {link_info.page.url} does not appear to be a link.\n"
                f"This is the href: {link_info.href}"
            )


def test_article_links(all_links: NamedTuple) -> None:
    """
    Test to validate the artcile links on each download page's table.
    Test is to see if in format of a valid DOI.
    """
    for link_info in all_links:
        if link_info.link_type == "Article":
            valid_doi = re.match(r"^https://doi\.org/", link_info.href)
            assert valid_doi, (
                f"An Article button link on the table on page: {link_info.page.url} does not appear to be a valid DOI.\n"
                f"This is the href: {link_info.href}"
            )


def test_website_links(all_links: NamedTuple) -> None:
    """
    Test to validate the website links on each download page's table.
    Confirm the Website is a valid URL - hard to test more specifically than this.
    """
    for link_info in all_links:
        if link_info.link_type == "Website":
            valid_url = re.match(r"^https?://", link_info.href)
            assert valid_url, (
                f"An Website button link on the table on page: {link_info.page.url} does not appear to be a valid website.\n"
                f"This is the href: {link_info.href}"
            )
