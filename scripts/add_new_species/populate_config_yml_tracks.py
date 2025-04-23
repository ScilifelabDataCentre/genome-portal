"""
Submodule to populate tracks in the config.yml based on data imported from the user spreadsheet.
(metadata fields in config.yml are populated by the populate_assembly_metadata_fields submodule).
"""

from pathlib import Path

import yaml


def populate_config_yml_tracks(config_dir_path: Path, data_tracks_list_of_dicts: dict) -> None:
    """
    Populate the config.yml file with data tracks values. Note that the values in the input dict
    can be '[EDIT]' due to the logic in the process_data_tracks_Excel submodule. It is up to the user
    to manually edit the config.yml file to remove these placeholders after running the add_new_species.py script.
    """

    config_file_path = config_dir_path / "config.yml"

    with open(config_file_path, "r") as config_f:
        config_data = yaml.safe_load(config_f)

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

    with open(config_file_path, "w") as config_f:
        yaml.safe_dump(config_data, config_f, sort_keys=False, default_flow_style=False)

    print(f"file updated with data tracks: {config_dir_path}")
