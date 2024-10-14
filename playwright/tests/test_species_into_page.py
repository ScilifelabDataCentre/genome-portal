"""
Tests for each species intro page.
"""

from playwright.sync_api import Page


def test_for_changelog(all_intro_pages: list[Page]):
    """
    Check if all species pages have a changelog.
    """
    for intro_page in all_intro_pages:
        changelog_visible = intro_page.get_by_role("heading", name="Changelog").is_visible()
        assert changelog_visible, f"Changelog not found on page: {intro_page.url}"


def test_banner_title_correct(all_intro_pages: list[Page]):
    """
    Check all species pages have the correct banner title.
    """
    pass


def test_external_links():
    """ """
    pass


def test_page_last_updated():
    """ """
    pass


def test_species_image():
    """ """
    pass


def test_species_map():
    """ """
    pass


def test_browse_genome_button():
    """
    Test clicking browser the genome button resolves to a page.
    """
    pass
