"""
Test copy to clipboard functionality.
"""

import pytest

from playwright.sync_api import Page, expect

CLIPBOARD_PAGES = (
    "citation",
    "contribute/supported_file_formats",
)


@pytest.mark.parametrize("page_obj", CLIPBOARD_PAGES, indirect=True)
def test_copy_to_clipboard_animation(page_obj: Page):
    """
    Test that the copy to clipboard button swaps to a checkmark icon after being clicked.
    And then swaps back to the copy icon after a short delay (2 seconds).

    Just tests the first button on the page.
    """
    copy_button = page_obj.get_by_role("button", name="Copy Copy to clipboard icon").first
    copied_button = page_obj.get_by_role("button", name="Copied checkmark icon").first

    expect(copy_button).to_be_visible()
    expect(copied_button).not_to_be_visible()

    copy_button.click()
    page_obj.wait_for_timeout(2000)
    expect(copy_button).to_be_visible()
    expect(copied_button).not_to_be_visible()


@pytest.mark.parametrize("page_obj", CLIPBOARD_PAGES, indirect=True)
def test_copy_to_clipboard_text(page_obj: Page):
    """
    Test that the text copied to clipboard matches the text below for each block.

    Note: To reliably test this, a new page is created for each button. Attempts without gave flaky results.
    For example, some clipboard texts would be duplicated, others would not show up.
    """
    page_obj.context.grant_permissions(["clipboard-read", "clipboard-write"])
    numb_buttons = page_obj.get_by_role("button", name="Copy Copy to clipboard icon").count()

    for idx in range(0, numb_buttons):
        new_page = page_obj.context.new_page()
        new_page.goto(page_obj.url)

        button = new_page.get_by_role("button", name="Copy Copy to clipboard icon").nth(idx)
        button.click()
        clipboard_text = new_page.evaluate("navigator.clipboard.readText()")

        citation_text = new_page.locator("pre").nth(idx).inner_text()

        assert (
            clipboard_text == citation_text
        ), f"Text copied from the clipboard: '{clipboard_text}' \n does not match the text below the clipboard '{citation_text}'"
