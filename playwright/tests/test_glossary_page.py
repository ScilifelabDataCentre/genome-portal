import pytest

from playwright.sync_api import Locator, Page, expect


@pytest.fixture
def search_input(glossary_page: Page) -> Locator:
    return glossary_page.get_by_label("Search:")


@pytest.fixture
def annotation_cell(glossary_page: Page) -> Locator:
    return glossary_page.get_by_role("cell", name="annotation track")


@pytest.fixture
def assembly_cell(glossary_page: Page) -> Locator:
    return glossary_page.get_by_role("cell", name="assembly")


@pytest.fixture
def no_matching_records_cell(glossary_page: Page) -> Locator:
    return glossary_page.get_by_role("cell", name="No matching records found")


def test_glossary_search(search_input: Locator, annotation_cell: Locator, assembly_cell: Locator):
    """Test a basic search works"""
    search_input.fill("annotation")
    expect(annotation_cell).to_be_visible()
    expect(assembly_cell).not_to_be_visible()


def test_clear_search_then_research(search_input: Locator, annotation_cell: Locator):
    """Test if clearing search and re-running search works"""
    search_input.fill("does not exist blah blah blah")
    expect(annotation_cell).not_to_be_visible()

    search_input.fill("")
    expect(annotation_cell).to_be_visible()

    search_input.fill("annotation")
    expect(annotation_cell).to_be_visible()


def test_non_matching_search(search_input: Locator, no_matching_records_cell: Locator):
    """Test that a search that does not match displays correctly."""
    search_input.fill("does not exist blah blah blah")
    expect(no_matching_records_cell).to_be_visible()
