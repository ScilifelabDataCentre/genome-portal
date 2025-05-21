import pytest


@pytest.fixture
def example_names() -> dict[str, str]:
    species_name_variants = {
        "species_name": "Aspergillus nidulans",
        "species_slug": "aspergillus_nidulans",
        "species_abbreviation": "anid",
    }
    return species_name_variants
