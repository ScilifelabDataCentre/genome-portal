from add_tracks_to_view import (
    initiate_defaultSession,
)


def test_initiate_defaultSession(example_names: dict[str, str]) -> None:
    assembly_counter = 0
    data = initiate_defaultSession(
        species_name_variants=example_names,
        assembly_counter=assembly_counter,
    )
    assert data["defaultSession"]["id"].startswith(example_names["species_abbreviation"])
    assert data["defaultSession"]["name"] == example_names["species_name"]
    assert (
        data["defaultSession"]["widgets"]["hierarchicalTrackSelector"]["view"]
        == f"{example_names["species_abbreviation"]}_default_session_view_{assembly_counter}"
    )
