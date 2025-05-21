"""
Package to create a defaultSession config.json for a species based on a config.yml file.

Assumes that the dockermake has been run once to download the files.

(The intention is that add_new_species has been run once first, but as long as there is a config.yml, this package will work)

"""

import argparse
from pathlib import Path

import yaml
from add_tracks_to_view import (
    initiate_defaultSession,
    initiate_views_and_populate_mandatory_tracks,
    populate_values_from_optional_tracks,
)
from utils import check_config_json_exists, get_species_abbreviation, save_json


def run_argparse() -> argparse.Namespace:
    """
    Run argparse and return the user arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        "-y",
        "--yaml",
        required=True,
        type=Path,
        metavar=".yml",
        help="""
        Input; the path to config.yml for the species.
        """,
    )

    parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        help="""If the defaultSession config.json for the species already exist, should it be overwritten?
            If flag NOT provided, no overwrite performed.""",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = run_argparse()
    config_yml_path = args.yaml
    output_json_path = config_yml_path.with_suffix(".json")

    if not args.overwrite:
        check_config_json_exists(output_json_path=output_json_path)

    with open(config_yml_path, "r") as file:
        configs = list(yaml.safe_load_all(file))

    if not configs or not configs[0]:
        raise ValueError("The first document in the config.yml is empty. Exiting.")

    first_config = configs[0]
    if "organism" not in first_config or not first_config["organism"]:
        raise KeyError(
            "The primary assembly (assembly number 1 in config.yml) is required to have a non-empty 'organism' key. Exiting."
        )

    species_name_variants = {
        "species_name": first_config["organism"],
        "species_slug": first_config["organism"].replace(" ", "_").lower(),
        "species_abbreviation": get_species_abbreviation(first_config["organism"]),
    }

    for assembly_counter, config in enumerate(configs):
        if not config:
            raise ValueError(
                f"Document {assembly_counter+1} in the config.yml is empty. Each document must contain data. Exiting."
            )
        data = initiate_defaultSession(
            species_name_variants=species_name_variants,
            assembly_counter=assembly_counter,
        )
        data = initiate_views_and_populate_mandatory_tracks(
            data=data,
            species_name_variants=species_name_variants,
            config=config,
            assembly_counter=assembly_counter,
        )
        data = populate_values_from_optional_tracks(
            config=config,
            data=data,
            species_abbreviation=species_name_variants["species_abbreviation"],
            assembly_counter=assembly_counter,
        )

    save_json(data, output_json_path, config_yml_path)
