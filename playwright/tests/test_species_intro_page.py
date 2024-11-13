"""
Tests for each species introduction page.
"""

import re

import pytest
from utils import INTRO_PAGE_PATHS, validate_date_format

from playwright.sync_api import Page, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

REQUIRED_HEADERS = ["Taxonomy", "External links", "Description", "How to cite", "References", "Changelog"]


@pytest.mark.parametrize("page_obj", INTRO_PAGE_PATHS, indirect=True)
@pytest.mark.parametrize("heading_text", REQUIRED_HEADERS)
def test_required_headers_visible(page_obj: Page, heading_text: str) -> None:
    """
    Test the required headers for the intro page are present.
    """
    locator = page_obj.get_by_role("heading", name=heading_text)
    expect(locator, f"The heading: {heading_text} is not visible on page: {page_obj.url}").to_be_visible()


@pytest.mark.parametrize("page_obj", INTRO_PAGE_PATHS, indirect=True)
def test_for_changelog(page_obj: Page) -> None:
    """
    Check if all species pages have a changelog.
    """
    changelog = page_obj.get_by_role("heading", name="Changelog")
    expect(changelog, f"Changelog not found on page: {page_obj.url}").to_be_visible(timeout=1_000)


@pytest.mark.parametrize("page_obj", INTRO_PAGE_PATHS, indirect=True)
def test_banner_title_correct(page_obj: Page) -> None:
    """
    Check all species pages have the correct banner title.
    """
    banner_title = page_obj.get_by_role("heading", name="Species overview")
    expect(banner_title, f"Species banner not found/correct on page: {page_obj.url}").to_be_visible(timeout=1_000)


@pytest.mark.parametrize("page_obj", INTRO_PAGE_PATHS, indirect=True)
def test_browse_genome_button(page_obj: Page) -> None:
    """
    Test clicking the browse the genome button resolves to the genome browser page.
    """
    with page_obj.expect_popup() as new_tab_info:
        page_obj.get_by_role("button", name="Browse the genome").click()
    new_tab = new_tab_info.value
    heading = new_tab.get_by_role("heading", name="Genome Browser")
    expect(heading, f"Navigation to genome browser for page {page_obj.url} went wrong").to_be_visible()


@pytest.mark.parametrize("page_obj", INTRO_PAGE_PATHS, indirect=True)
def test_has_last_updated(page_obj: Page) -> None:
    """Test that all intro page have a last updated text and that it is correctly formatted."""
    # Check if the last updated date is visible on the page.
    last_updated_text = page_obj.get_by_text("Page last updated: ")
    expect(last_updated_text, f"Last updated not found on page: {page_obj.url}").to_be_visible()

    # validate the date, the try except block is to show which page is failing.
    date = last_updated_text.inner_text().split(":")[1].strip()

    valid_date = True
    try:
        validate_date_format(date=date, date_format="%d/%m/%Y")
    except AssertionError:
        valid_date = False

    assert valid_date, f"Date format incorrect on page: {page_obj.url}"


@pytest.mark.parametrize("page_obj", INTRO_PAGE_PATHS, indirect=True)
def test_sbdi_gbif_links(page_obj: Page) -> None:
    """
    Test the SBDI and GBIF links found in the external links are correct.
    These have a placeholder in the template, so this test should catch if they haven't been filled in.
    """
    sbdi_a_tag = page_obj.get_by_role("button", name="Location Icon Occurrence data in SBDI").locator("..")
    expect(sbdi_a_tag, f"Link to SBDI not found on page: {page_obj.url}").to_have_attribute(
        "href", re.compile(r"https://species.biodiversitydata.se/species/\d+")
    )

    gbif_a_tag = page_obj.get_by_role("button", name="Location Icon Occurrence data in GBIF").locator("..")
    expect(gbif_a_tag, f"Link to GBIF not found on page: {page_obj.url}").to_have_attribute(
        "href", re.compile(r"https://www.gbif.org/species/\d+")
    )


@pytest.mark.parametrize("page_obj", INTRO_PAGE_PATHS, indirect=True)
def test_vulnerability_links(page_obj: Page) -> None:
    """
    Vulnerability links are optional, so these should have been deleted from a species page if not present.

    This tests is to catch if the links are present because they haven't been removed from the template.
    Therefore the check is to spot the presence of the '[EDIT]' text.
    """
    VULNERABILITY_SECTIONS = ["IUCN Category:", "Swedish Red List:"]

    for section in VULNERABILITY_SECTIONS:
        try:
            section_text = page_obj.get_by_text(section).locator("..").text_content(timeout=1_000)
        except PlaywrightTimeoutError:
            section_text = None

        if section_text:
            is_edited = not re.search(r"\[EDIT\]", section_text)
            assert is_edited, f"'[EDIT]' found by {section} text for page: {page_obj.url}"
