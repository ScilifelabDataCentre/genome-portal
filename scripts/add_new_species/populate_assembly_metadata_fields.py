"""
Submodule to populate fields in assembly.md and config.yml files
"""

from pathlib import Path

import yaml

YML_FILE_NAME = "config.yml"
TEMPLATE_FILE_PATH = Path(__file__).parent.parent / "templates" / YML_FILE_NAME


def populate_config_yml(assembly_metadata_dict: dict, config_dir_path: Path, data_tracks_list_of_dicts: dict) -> None:
    """
    1. Read the config.yml template file
    2. Populate the following fields in the config.yml file:
    - organism
    - assembly.name
    - assembly.displayName
    - assembly.accession
    with the corresponding values from assembly_metadata_dict.
    3. Populate the tracks field in the config.yml file with the data tracks values.
    4. Write the updated config.yml file to the config_dir_path.
    """

    with open(TEMPLATE_FILE_PATH, "r") as config_f:
        config_data = dict(yaml.safe_load(config_f))

    config_data["organism"] = assembly_metadata_dict["species_name"]
    config_data["assembly"]["name"] = assembly_metadata_dict["name"]
    config_data["assembly"]["displayName"] = (
        f"{assembly_metadata_dict['species_name_abbrev']} genome assembly {assembly_metadata_dict['accession']}"
    )
    config_data["assembly"]["accession"] = assembly_metadata_dict["accession"]
    config_data["tracks"] = []
    for track in data_tracks_list_of_dicts:
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


def populate_assembly_md_with_assembly_metadata(assembly_metadata_dict: dict, content_dir_path: Path) -> None:
    """
    Populate the following fields in the species assembly.md file:
    - ASSEMBLY_NAME
    - ASSEMBLY_TYPE
    - ASSEMBLY_LEVEL
    - GENOME_REPRESENTATION
    - ASSEMBLY_ACCESSION
    with the corresponding values from assembly_metadata_dict.
    """
    assembly_md_file_path = content_dir_path / "assembly.md"

    with open(assembly_md_file_path, "r") as assembly_f:
        assembly_markdown = assembly_f.read()
        assembly_markdown = assembly_markdown.replace("ASSEMBLY_NAME", assembly_metadata_dict["name"])
        assembly_markdown = assembly_markdown.replace("ASSEMBLY_TYPE", assembly_metadata_dict["assembly_type"])
        assembly_markdown = assembly_markdown.replace("ASSEMBLY_LEVEL", assembly_metadata_dict["assembly_level"])
        assembly_markdown = assembly_markdown.replace(
            "GENOME_REPRESENTATION", assembly_metadata_dict["genome_representation"]
        )
        assembly_markdown = assembly_markdown.replace("ASSEMBLY_ACCESSION", assembly_metadata_dict["accession"])

    with open(assembly_md_file_path, "w") as assembly_w:
        assembly_w.write(assembly_markdown)
        print(f"File updated with genome assembly metadata from ENA and NCBI: {assembly_md_file_path.resolve()}")


def populate_assembly_metadata_fields(
    config_dir_path: Path, content_dir_path: Path, data_tracks_list_of_dicts: dict, assembly_metadata_dict: dict
) -> None:
    """
    Populate the config.yml and assembly.md files with assembly metadata. Assumes that add_content_files.py
    and add_config_files.py have already been run to create the config.yml and assembly.md files in the
    desired endpoint directories.

    NOTE! fetch_assembly_metadata requires a valid GenBank accession number for the genome assembly
    of the species. See fetch_assembly_metadata docstring for details.
    """

    populate_config_yml(assembly_metadata_dict, config_dir_path, data_tracks_list_of_dicts)

    populate_assembly_md_with_assembly_metadata(assembly_metadata_dict, content_dir_path)
