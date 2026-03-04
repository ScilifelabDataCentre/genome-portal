import json
from pathlib import Path

import pytest
from utils import SPECIES_LIST

HUGO_ASSETS_DIR = Path(__file__).parent.parent.parent / "hugo/assets"


@pytest.mark.parametrize("species", SPECIES_LIST)
def test_data_tracks_links_are_https(species):
    """
    Check if all links in every species' data_tracks.json file start with "https://".
    """
    data_tracks_path = HUGO_ASSETS_DIR / species / "data_tracks.json"

    if not data_tracks_path.exists():
        raise FileNotFoundError(
            f"data_tracks.json file not found for species: {species}. \n"
            "There may be a name mismatch in species name between the 'hugo/assets' and 'hugo/content/species' folders"
        )

    with open(data_tracks_path, "r") as f:
        data_tracks = json.load(f)

    for track in data_tracks:
        links = track.get("links", [])
        for link_dict in links:
            for url in link_dict.values():
                assert url.startswith("https://"), (
                    f"URL {url} in {species} data_tracks.json does not start with https:// \n"
                    "A web browser will not be able to open this link in the species' downloads page.\n"
                    "Tip: if the link starts with 'ftp://ftp' change it to: 'https://ftp'"
                )
