"""
Tests for the home page and navbar.
"""

import re

from playwright.sync_api import Locator, Page, expect


def get_search_bar(page: Page) -> Locator:
    """Helper function to return the search bar."""
    return page.locator("#Search")


def get_no_results_alert(page: Page) -> Locator:
    """Helper function to return the no results alert."""
    return page.get_by_text("No results found with your search term")


def get_species_cards(page: Page) -> Locator:
    """Helper function to return the species cards."""
    return page.locator("div.card")


def get_species_card_order(page: Page) -> list[str]:
    """Helper function to return the order of the species cards."""
    species_cards = get_species_cards(page)
    return species_cards.locator("#science-name").all_inner_texts()


def test_has_title(home_page: Page):
    """Test that the home page has the correct title."""
    expect(home_page).to_have_title(re.compile("Swedish Reference Genome Portal"))


def test_navbar_links(home_page: Page):
    """Test navbar links redirect to the correct page."""
    links = {"Home": "Home", "About": "About", "Glossary": "Glossary", "Contact": "Contact"}

    for name, title in links.items():
        home_page.locator("#navbarSupportedContent").get_by_role("link", name=name).click()
        expect(home_page).to_have_title(re.compile(title))


def test_no_results_alert_responsive(home_page: Page):
    """
    Test updating text in search bar shows/hides the no results alert.
    """
    no_results_alert = get_no_results_alert(home_page)
    search_bar = get_search_bar(home_page)

    search_bar.fill("dnskfdslfdf")
    expect(no_results_alert).to_be_visible()

    search_bar.fill("")
    expect(no_results_alert).not_to_be_visible()

    search_bar.fill("sdsdsdsdsd")
    expect(no_results_alert).to_be_visible()

    search_bar.fill("Littorina saxatilis")  # species that exists.
    expect(no_results_alert).not_to_be_visible()


def test_search_cards_responsive(home_page: Page):
    """
    Test the species cards are responsive to the search.
    As in the appear and disappear based on the search term used.
    """
    search_bar = get_search_bar(home_page)
    species_cards = get_species_cards(home_page)

    total_numb_cards = species_cards.count()

    search_bar.fill("sdsdsdsdsd")
    assert species_cards.count() == 0

    search_bar.fill("Littorina saxatilis")  # species that exists.
    assert species_cards.count() == 1

    search_bar.fill("Linum")  # gives at least 2 results.
    assert species_cards.count() >= 2

    search_bar.fill("")
    assert species_cards.count() == total_numb_cards


def test_search_dropdown_ordering(home_page: Page):
    """
    Test clicking the different search ordering dropdown options alters the card ordering.
    Default ordering is last updated.

    Loops through the different ordering options and checks the order of the cards is as expected.
    """
    initial_cards_order = get_species_card_order(home_page)
    alphabetically_ordered = sorted(initial_cards_order)
    rev_alphabetically_ordered = sorted(initial_cards_order, reverse=True)

    home_page.locator("button").filter(has_text="Last updated").click()
    home_page.get_by_role("button", name="Name (A to Z)").click()
    new_cards_order = get_species_card_order(home_page)
    assert new_cards_order == alphabetically_ordered

    home_page.locator("button").filter(has_text="Name (A to Z)").click()
    home_page.get_by_role("button", name="Name (Z to A)").click()
    new_cards_order = get_species_card_order(home_page)
    assert new_cards_order == rev_alphabetically_ordered

    home_page.locator("button").filter(has_text="Name (Z to A)").click()
    home_page.get_by_role("button", name="Last updated").click()
    new_cards_order = get_species_card_order(home_page)
    assert new_cards_order == initial_cards_order


def test_search_and_dropdown_work_together(home_page: Page):
    """
    Test after searching for something, changing the ordering via the dropdown still works.

    Uses above test as identical to above but with the search bar filled.
    """
    search_bar = get_search_bar(home_page)

    search_bar.fill("Linum")  # gives at least 2 results.
    test_search_dropdown_ordering(home_page)

    search_bar.fill("")  # gives all results
    test_search_dropdown_ordering(home_page)
