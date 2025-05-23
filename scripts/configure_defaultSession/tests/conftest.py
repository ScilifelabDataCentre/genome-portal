from pathlib import Path
from typing import Any

import pytest
import yaml
from default_session_builder import DefaultSession
from utils import get_species_abbreviation

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def example_configs() -> list[Any]:
    """
    Paths to example Excel files for testing.
    """
    config_yml_path = FIXTURES_DIR / "config.yml"

    with open(config_yml_path, "r") as file:
        configs = list(yaml.safe_load_all(file))

    return configs


@pytest.fixture
def example_init_default_session() -> DefaultSession:
    species_name = "Tiny herb"
    default_session = DefaultSession(
        species_name=species_name,
        species_abbreviation=get_species_abbreviation(species_name=species_name),
        species_slug=species_name.replace(" ", "_").lower(),
    )
    return default_session


@pytest.fixture
def example_default_session_with_view(example_init_default_session: DefaultSession) -> DefaultSession:
    default_session = example_init_default_session
    default_session.views.append(
        {
            "id": "ther_default_session_view_0",
            "minimized": False,
            "type": "LinearGenomeView",
            "trackLabels": "offset",
            "offsetPx": 0,
            "bpPerPx": 200,
            "displayedRegions": [
                {
                    "refName": "ENA|CAMGYJ010000002|CAMGYJ010000002.1",
                    "start": 0,
                    "end": 72476498,
                    "reversed": False,
                    "assemblyName": "Linum_tenue_thrum_v1",
                }
            ],
            "tracks": [],
        }
    )
    return default_session


@pytest.fixture
def example_track_params() -> dict[str, dict[str, Any]]:
    track_params = {
        "protein_coding_genes_gff_track": {
            "track_view_id": "ther_default_Protein-coding_genes",
            "track_top_id": "ltenue_v1_genes.gff",
            "track_file_name": "ltenue_v1_genes.gff",
            "track_name": "Protein-coding genes",
            "display_type": "LinearBasicDisplay",
            "track_config": "ltenue_v1_genes.gff",
            "display_config": "ltenue_v1_genes.gff-LinearBasicDisplay",
            "score_column": None,
            "is_quantiative_track": False,
            "assemblyNames": "Linum_tenue_thrum_v1",
        },
        "bed_gwas_track": {
            "track_view_id": "ther_default_Tajimas_D_population_06",
            "track_top_id": "Lten_pop06_TD.bed",
            "track_file_name": "Lten_pop06_TD.bed",
            "track_name": "Tajima's D, population 06",
            "display_type_key": "gwas",
            "display_type": "LinearManhattanDisplay",
            "track_config": "Lten_pop06_TD.bed",
            "display_config": "Lten_pop06_TD.bed-LinearManhattanDisplay",
            "score_column": "TajimaD",
            "is_quantiative_track": False,
            "assemblyNames": "Linum_tenue_thrum_v1",
        },
        "bedGraph_like_track": {
            "track_view_id": "ther_default_Test_of_bedGraph_track",
            "track_top_id": "Lten_pop08_TD_for_wiggle.bed",
            "track_file_name": "Lten_pop08_TD_for_wiggle.bed",
            "track_name": "Test of bedGraph track",
            "display_type_key": "wiggle",
            "display_type": "LinearWiggleDisplay",
            "track_config": "Lten_pop08_TD_for_wiggle.bed",
            "display_config": "Lten_pop08_TD_for_wiggle.bed-LinearWiggleDisplay",
            "is_quantiative_track": True,
            "assemblyNames": "Linum_tenue_thrum_v1",
        },
    }
    return track_params
