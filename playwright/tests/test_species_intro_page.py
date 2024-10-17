"""
Tests for each species introduction page.

The conftest.py has a fixture (all_intro_pages) that returns a list of all the intro pages for each species.
This way each test can be run on every species including those newly added.
"""

import re

from utils import validate_date_format

from playwright.sync_api import Page, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


def test_for_changelog(all_intro_pages: list[Page]):
    """
    Check if all species pages have a changelog.
    """
    for intro_page in all_intro_pages:
        changelog = intro_page.get_by_role("heading", name="Changelog")
        expect(changelog, f"Changelog not found on page: {intro_page.url}").to_be_visible(timeout=1_000)


def test_banner_title_correct(all_intro_pages: list[Page]):
    """
    Check all species pages have the correct banner title.
    """
    for intro_page in all_intro_pages:
        banner_title = intro_page.get_by_role("heading", name="Species overview")
        expect(banner_title, f"Species banner not found/correct on page: {intro_page.url}").to_be_visible(timeout=1_000)


def test_browse_genome_button(all_intro_pages: list[Page]):
    """
    Test clicking the browse the genome button resolves to the genome browser page.
    """
    for intro_page in all_intro_pages:
        with intro_page.expect_popup() as new_tab_info:
            intro_page.get_by_role("button", name="Browse the genome").click()
        new_tab = new_tab_info.value
        heading = new_tab.get_by_role("heading", name="Genome Browser")
        expect(heading, f"Navigation to genome browser for page {intro_page.url} went wrong").to_be_visible()


def test_has_last_updated(all_intro_pages: list[Page]):
    """Test that all intro page have a last updated text and that it is correctly formatted."""
    for intro_page in all_intro_pages:
        # Check if the last updated date is visible on the page.
        last_updated_text = intro_page.get_by_text("Page last updated: ")
        expect(last_updated_text, f"Last updated not found on page: {intro_page.url}").to_be_visible()

        # validate the date, the try except block is to show which page is failing.
        date = last_updated_text.inner_text().split(":")[1].strip()

        valid_date = True
        try:
            validate_date_format(date=date, date_format="%d/%m/%Y")
        except AssertionError:
            valid_date = False

        assert valid_date, f"Date format incorrect on page: {intro_page.url}"


def test_sbdi_gbif_links(all_intro_pages: list[Page]):
    """
    Test the SBDI and GBIF links found in the external links are correct.
    These have a placeholder in the template, so this test should catch if they haven't been filled in.
    """
    for intro_page in all_intro_pages:
        sbdi_a_tag = intro_page.get_by_role("button", name="Location Icon Occurrence data in SBDI").locator("..")
        expect(sbdi_a_tag, f"Link to SBDI not found on page: {intro_page.url}").to_have_attribute(
            "href", re.compile(r"https://species.biodiversitydata.se/species/\d+")
        )

        gbif_a_tag = intro_page.get_by_role("button", name="Location Icon Occurrence data in GBIF").locator("..")
        expect(gbif_a_tag, f"Link to GBIF not found on page: {intro_page.url}").to_have_attribute(
            "href", re.compile(r"https://www.gbif.org/species/\d+")
        )


def test_vulnerability_links(all_intro_pages: list[Page]):
    """
    Vulnerability links are optional, so these should have been deleted from a species page if not present.

    This tests is to catch if the links are present because they haven't been removed from the template.
    Therefore the check is to spot the presence of the '[EDIT]' text.
    """
    VULNERABILITY_SECTIONS = ["IUCN Category:", "Swedish Red List:"]

    for intro_page in all_intro_pages:
        for section in VULNERABILITY_SECTIONS:
            try:
                section_text = intro_page.get_by_text(section).locator("..").text_content(timeout=1_000)
            except PlaywrightTimeoutError:
                section_text = None

            if section_text:
                is_edited = not re.search(r"\[EDIT\]", section_text)
                assert is_edited, f"'[EDIT]' found by {section} text for page: {intro_page.url}"
