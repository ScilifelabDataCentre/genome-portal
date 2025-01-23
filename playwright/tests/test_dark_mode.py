"""
Tests the ability to switch between light and dark mode.
Both by recognizing the prefered color scheme on page load and by toggling the theme.
"""

import re

import pytest
from utils import hex_to_rgb

from playwright.sync_api import Locator, Page, expect


@pytest.fixture
def html_locator(home_page: Page) -> Locator:
    return home_page.locator("html")


def test_correct_color_scheme_on_load(home_page: Page, html_locator: Locator) -> None:
    """
    Test the page has the correct color scheme on page load.
    (Need to clear localStorage to avoid the saved color scheme being used - expected behavior)
    """
    expect(html_locator).to_have_attribute("data-bs-theme", "light")

    home_page.emulate_media(color_scheme="dark")
    home_page.evaluate("localStorage.clear()")
    home_page.reload()
    expect(html_locator).to_have_attribute("data-bs-theme", "dark")

    home_page.emulate_media(color_scheme="light")
    home_page.evaluate("localStorage.clear()")
    home_page.reload()
    expect(html_locator).to_have_attribute("data-bs-theme", "light")


def test_can_swap_color_scheme(home_page: Page, html_locator: Locator) -> None:
    """
    Test that the page can be switched between light and dark mode
    """
    expect(html_locator).to_have_attribute("data-bs-theme", "light")

    home_page.get_by_role("button", name="Toggle theme").click()
    home_page.get_by_role("button", name=re.compile("Dark")).click()

    expect(html_locator).to_have_attribute("data-bs-theme", "dark")

    home_page.get_by_role("button", name="Toggle theme").click()
    home_page.get_by_role("button", name=re.compile("Light")).click()

    expect(html_locator).to_have_attribute("data-bs-theme", "light")


def test_text_and_bg_color_change(home_page: Page) -> None:
    """
    Test that the font text and bg color changes when the color scheme changes.
    Playwright needs colors in RGB format hence the converter.
    """
    body_locator = home_page.locator("body")
    light_theme_bg_color = hex_to_rgb("#ffffff")
    light_theme_color = hex_to_rgb("#212529")
    dark_theme_bg_color = hex_to_rgb("#212121")
    dark_theme_color = hex_to_rgb("#dee2e6")

    # initial light theme
    expect(body_locator).to_have_css("background-color", light_theme_bg_color)
    expect(body_locator).to_have_css("color", light_theme_color)

    # dark theme
    home_page.get_by_role("button", name="Toggle theme").click()
    home_page.get_by_role("button", name=re.compile("Dark")).click()

    expect(body_locator).to_have_css("background-color", dark_theme_bg_color)
    expect(body_locator).to_have_css("color", dark_theme_color)

    # switch back to light theme
    home_page.get_by_role("button", name="Toggle theme").click()
    home_page.get_by_role("button", name=re.compile("Light")).click()

    expect(body_locator).to_have_css("background-color", light_theme_bg_color)
    expect(body_locator).to_have_css("color", light_theme_color)
