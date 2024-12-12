"""
Tests for the home page and the navbar.
"""

import re
import time

import pytest
from utils import validate_date_format

from playwright.sync_api import Locator, Page, expect


def pagination_exists(page: Page) -> bool:
    """
    Check if there is pagination on the home page.
    Controls what tests need to be run.
    """
    return page.locator(".pagination").count() > 0


def get_page_button_link(page: Page, button_name: str | int) -> Locator:
    """Return the locator for the page button."""
    return page.locator(f'.pagination .page-link[data-page="{button_name}"]')


def get_numb_pages(page: Page) -> int:
    return page.locator(".pagination .page-item").count() - 2  # -2 for prev and next btns.


def get_species_cards(page: Page) -> Locator:
    """Helper function to return the species cards."""
    return page.locator("div.card")


def get_species_card_order(page: Page) -> list[str]:
    """Helper function to return the the species cards titles (science names) in order."""
    species_cards = get_species_cards(page)
    return species_cards.locator("#science-name").all_inner_texts()


@pytest.fixture
def search_bar(home_page: Page) -> Locator:
    """Helper function to return the search bar."""
    return home_page.locator("#Search")


@pytest.fixture
def no_results_alert(home_page: Page) -> Locator:
    """Fixture for the no results alert that goes from hidden to displayed if no results from the search."""
    return home_page.get_by_text("No results found with your search term")


@pytest.fixture
def pagination_btns(home_page: Page) -> dict[str, Locator]:
    """Fixture that returns a dictionary of pagination buttons."""
    buttons = {
        "prev": get_page_button_link(home_page, "prev"),
        "next": get_page_button_link(home_page, "next"),
    }
    for i in range(1, get_numb_pages(home_page) + 1):
        buttons[str(i)] = get_page_button_link(home_page, str(i))
    return buttons


def test_has_title(home_page: Page) -> None:
    """Test that the home page has the correct title."""
    expect(home_page).to_have_title(re.compile("Swedish Reference Genome Portal"))


def test_navbar_links(home_page: Page) -> None:
    """Test navbar links redirect to the correct page."""
    NAVBAR_LINKS = {
        "Home": "Home",
        "Contribute": "Contribute",
        "User guide": "User guide",
        "Glossary": "Glossary",
        "About": "About",
        "Contact": "Contact",
        "FAQ": "Frequently Asked Questions",
        "Cite us": "How to cite the Genome Portal and the data",
    }

    for name, title in NAVBAR_LINKS.items():
        home_page.locator("#navbarSupportedContent").get_by_role("link", name=name).click()
        expect(home_page).to_have_title(re.compile(title))


def test_last_updated_format(home_page: Page) -> None:
    """
    Test that the last updated date on each species card has the correct format.
    **Note** changing the date format used would impact the home page species search function.
    """
    species_cards = get_species_cards(home_page)
    last_updated_texts = species_cards.get_by_text("Last updated:").all_inner_texts()
    for text in last_updated_texts:
        date = text.split(":")[1].strip()
        validate_date_format(date=date, date_format="%d/%m/%Y")


def test_no_results_alert_responsive(home_page: Page, no_results_alert: Locator, search_bar: Locator) -> None:
    """
    Test updating text in search bar shows/hides the no results alert.
    """
    search_bar.fill("dnskfdslfdf")
    expect(no_results_alert).to_be_visible()

    search_bar.fill("")
    expect(no_results_alert).not_to_be_visible()

    search_bar.fill("sdsdsdsdsd")
    expect(no_results_alert).to_be_visible()

    search_bar.fill("Littorina saxatilis")  # species that exists.
    expect(no_results_alert).not_to_be_visible()


def test_pagination_page_number_nav(home_page: Page, pagination_btns: dict[str, Locator]) -> None:
    """
    Test changing the page of the species results works as expected.
    Just navigates to each page using the page numbers.
    """
    if not pagination_exists(home_page):
        return

    expect(pagination_btns["1"].locator("..")).to_have_class(re.compile("active"))
    expect(pagination_btns["prev"].locator("..")).to_have_class(re.compile("disabled"))

    numb_pages = get_numb_pages(home_page)
    for page_numb in range(2, numb_pages + 1):
        pagination_btns[f"{str(page_numb)}"].click()

        expect(pagination_btns[f"{str(page_numb)}"].locator("..")).to_have_class(re.compile("active"))

        if page_numb == numb_pages:
            expect(pagination_btns["next"].locator("..")).to_have_class(re.compile("disabled"))


def test_pagination_nav_buttons(home_page: Page, pagination_btns: dict[str, Locator]) -> None:
    """
    Test using "Next" and "Previous" buttons to navigate through the results pages.
    """
    if not pagination_exists(home_page):
        return

    first_page_link = pagination_btns["1"]
    numb_of_pages = get_numb_pages(home_page)
    last_page_link = pagination_btns[str(numb_of_pages)]

    expect(pagination_btns["prev"].locator("..")).to_have_class(re.compile("disabled"))

    for _ in range(1, numb_of_pages):
        pagination_btns["next"].click()
    expect(pagination_btns["next"].locator("..")).to_have_class(re.compile("disabled"))
    expect(last_page_link.locator("..")).to_have_class(re.compile("active"))

    for _ in range(1, numb_of_pages):
        pagination_btns["prev"].click()
    expect(pagination_btns["prev"].locator("..")).to_have_class(re.compile("disabled"))
    expect(first_page_link.locator("..")).to_have_class(re.compile("active"))


def count_visible_cards(species_cards: list[Locator]) -> int:
    """Helper function to count the number of visible species cards."""
    visible_cards = 0
    for card in species_cards:
        if card.is_visible():
            visible_cards += 1
    return visible_cards


def test_search_box_responsive(home_page: Page, search_bar: Locator) -> None:
    """
    Test the search box is responsive, results appear and disappear based on the search term used.
    Search bar is debounced, hence time.sleep usage.
    """
    species_cards = home_page.locator(".scilife-species-card").all()
    total_numb_cards = len(species_cards)

    search_bar.fill("sdsdsdsdsdghjjj")
    time.sleep(0.3)
    assert count_visible_cards(species_cards) == 0

    search_bar.fill("Littorina saxatilis")  # species that exists.
    time.sleep(0.3)
    assert count_visible_cards(species_cards) == 1

    search_bar.fill("Linum")  # gives at least 2 results.
    time.sleep(0.3)
    assert count_visible_cards(species_cards) >= 2

    search_bar.fill("")
    time.sleep(0.3)
    assert count_visible_cards(species_cards) == total_numb_cards


def test_search_dropdown_ordering(home_page: Page) -> None:
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


def test_search_and_dropdown_work_together(home_page: Page, search_bar: Locator) -> None:
    """
    Test after searching for something, changing the ordering of the search via the dropdown still works.

    Uses the "test_search_dropdown_ordering" function as identical to above but now with the search bar filled.
    """
    search_bar.fill("Linum")  # gives at least 2 results.
    test_search_dropdown_ordering(home_page)

    search_bar.fill("")  # gives all results
    test_search_dropdown_ordering(home_page)
