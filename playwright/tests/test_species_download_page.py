"""
Tests for each species download page.

The conftest.py has a fixture (all_download_pages) that returns a list of all the download pages for each species.
This way each test can be run on every species including those newly added.
"""

import re  # noqa

import pytest  # noqa
from utils import validate_date_format  # noqa

from playwright.sync_api import Locator, Page, expect  # noqa
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError  # noqa


def test_required_header_visible(all_download_pages: list[Page]):
    """
    Test the required header 'Data availability' is present in the download page.
    """
    HEADER_TEXT = "Data availability"
    for download_page in all_download_pages:
        locator = download_page.get_by_role("heading", name=HEADER_TEXT)
        expect(locator, f"The heading: {HEADER_TEXT} is not visible on page: {download_page.url}").to_be_visible()


def test_toggle_switch(all_download_pages: list[Page]):
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


def test_validate_date_format_in_download_table(all_download_pages: list[Page]):
    """
    Validates the date format in the download table is correct.
    """
    for download_page in all_download_pages:
        toggle_switch = download_page.get_by_role("switch", name="Show reduced table view")
        toggle_switch.click()
        long_table = download_page.locator("#downloadTableLong_wrapper")

        # Get all the date cells for "First date on Portal"
        all_date_texts = long_table.locator("td:nth-child(8)").all_inner_texts()

        for date in all_date_texts:
            valid_date = True
            try:
                validate_date_format(date=date, date_format="%d %B %Y")
            except AssertionError:
                valid_date = False

            assert valid_date, f"Download table date formatting incorrect on page: {download_page.url}. Format should e.g.: 15 October 2024"


def prep_links_column(all_download_pages: list[Page]):
    """
    Test that all links in the download table are valid.

    Each cell in the "Links" column should contain a link with one or more of the following types:
    Download, Website or Article
    Test checks these links have the right atttributes.
    """
    for download_page in all_download_pages:
        short_table = download_page.locator("#downloadTableShort_wrapper")
        links_column_cells = short_table.locator("td:nth-child(3)").all()

        for single_links_cell in links_column_cells:
            links_in_one_cell = single_links_cell.locator("a").all()

            for link in links_in_one_cell:
                link_type = link.inner_text()
                href = link.get_attribute("href")

                if link_type == "Download":
                    # Just want to confirm it is a direct download link, not wait for the download to complete
                    download_works = True
                    try:
                        with download_page.expect_download(timeout=1_000) as _:
                            link.click()
                    except PlaywrightTimeoutError:
                        download_works = False

                    assert download_works, (
                        f"A Download button link on the table on page: {download_page.url} does not appear to be a link:\n"
                        f"This is the link: {href}"
                    )

                # Confirm the Article link is a valid DOI
                elif link_type == "Article":
                    valid_doi = re.match(r"^https://doi\.org/", href)
                    assert valid_doi, (
                        f"An Article button link on the table on page: {download_page.url} does not appear to be a valid DOI:\n"
                        f"This is the link: {href}"
                    )

                # Confirm the Website is a valid URL - hard to test more specifically than this.
                elif link_type == "Website":
                    valid_url = re.match(r"^https?://", href)
                    assert (
                        valid_url
                    ), f"Website with URL: {href}, does not seem to be a valid URL on page: {download_page.url}"

                else:
                    raise ValueError(f"Unknown link type: {link_type}")
