"""
Tests for the privacy page.
"""

import re

from playwright.sync_api import Page, expect


def test_has_title(privacy_page: Page):
    """Test that the cite us page has the correct title."""
    expect(privacy_page).to_have_title(re.compile("Privacy policy"))


def test_opt_out_link(privacy_page: Page):
    """Test that the Matomo opt-out link swaps between the correct states when clicked on."""
    opt_out_frame = privacy_page.locator("#matoOpOut").content_frame
    opt_out_button = opt_out_frame.get_by_text("You are not opted out.")
    opt_in_button = opt_out_frame.get_by_text("You are currently opted out.")

    expect(opt_out_button).to_be_visible()
    expect(opt_in_button).not_to_be_visible()

    opt_out_button.click()

    expect(opt_out_button).not_to_be_visible()
    expect(opt_in_button).to_be_visible()

    opt_in_button.click()

    expect(opt_out_button).to_be_visible()
    expect(opt_in_button).not_to_be_visible()
