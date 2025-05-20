"""
Submodule to populate fields in assembly.md and config.yml files
"""

from pathlib import Path

import yaml
from add_content_files import TEMPLATE_DIR
from get_assembly_metadata_from_ENA_NCBI import AssemblyMetadata

YML_FILE_NAME = "config.yml"
TEMPLATE_FILE_PATH = TEMPLATE_DIR / YML_FILE_NAME


def populate_config_yml(assembly_metadata: AssemblyMetadata, user_data_tracks: dict, config_dir_path: Path) -> None:
    """
    1. Read the config.yml template file
    2. Populate the following fields in the config.yml file:
    - organism
    - assembly.name
    - assembly.displayName
    - assembly.accession
    with the corresponding values from the dataclass "assembly_metadata".
    3. Populate the tracks field in the config.yml file with the data tracks values.
    4. Write the updated config.yml file to the config_dir_path.
    """

    # with open(TEMPLATE_FILE_PATH, "r") as config_f:
    #     config_data = dict(yaml.safe_load(config_f))
    config_data = {}
    config_data["organism"] = assembly_metadata.species_name
    config_data["assembly"] = {}
    config_data["assembly"]["name"] = assembly_metadata.assembly_name
    config_data["assembly"]["displayName"] = (
        f"{assembly_metadata.species_name_abbrev} genome assembly {assembly_metadata.assembly_accession}"
    )
    config_data["assembly"]["accession"] = assembly_metadata.assembly_accession
    config_data["tracks"] = []
    for track in user_data_tracks:
        file_name = track.get("fileName")
        download_url = None
        for link in track.get("links", []):
            if "Download" in link:
                download_url = link["Download"]
                break
        if track.get("dataTrackName") == "Genome":
            config_data["assembly"]["url"] = download_url
            config_data["assembly"]["fileName"] = file_name
        else:
            config_data["tracks"].append(
                {"name": track.get("dataTrackName"), "url": download_url, "fileName": file_name}
            )

    config_file_path = config_dir_path / "config.yml"

    with open(config_file_path, "w") as config_w:
        yaml.safe_dump(config_data, config_w, sort_keys=False, default_flow_style=False)
        print(f"File created: {config_file_path.resolve()}")
