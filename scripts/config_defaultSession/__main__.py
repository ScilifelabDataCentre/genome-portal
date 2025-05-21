"""
Package to create a defaultSession config.json for a species based on a config.yml file.

Assumes that the dockermake has been run once to download the files.

(The intention is that add_new_species has been run once first, but as long as there is a config.yml, this package will work)

"""

import argparse
from pathlib import Path

import yaml
from add_tracks_to_view import DefaultSession, get_GWAS_tracks, get_optional_tracks, get_protein_coding_gene_file_name
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
        # TODO it seems that the error catcher here is also triggered if an incorrect .config.yml is entered
        # it seems to happen if the -o flag is not set
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

    default_session = DefaultSession(
        species_name=species_name_variants["species_name"],
        species_abbreviation=species_name_variants["species_abbreviation"],
        species_slug=species_name_variants["species_slug"],
    )

    for assembly_counter, config in enumerate(configs):
        if not config:
            raise ValueError(
                f"Document {assembly_counter+1} in the config.yml is empty. Each document must contain data. Exiting."
            )
        default_session.add_view(
            assembly_counter=assembly_counter,
            config=config,
            default_scaffold=None,  # TODO add module to calcualte this from the fasta file
            sequence_length=None,  # TODO add module to calcualte this from the fasta file
        )

        protein_coding_gene_file_name = get_protein_coding_gene_file_name(
            assembly_counter=assembly_counter,
            config=config,
        )

        default_session.add_protein_coding_genes(
            assembly_counter=assembly_counter,
            protein_coding_gene_file_name=protein_coding_gene_file_name,
        )

        default_session = get_optional_tracks(
            default_session=default_session,
            config=config,
            assembly_counter=assembly_counter,
        )  # TODO this adds LinearBasicDisaply tracks. improve the logic to that
        # tracks that should not be set as LinearBasicDisaply are skipped over and handled
        # by another downstream function.

        default_session = get_GWAS_tracks(
            default_session=default_session,
            config=config,
            assembly_counter=assembly_counter,
        )  # clean up the logic for trackID and make it more DRY

        # TODO consider if it would be better to loop tracks once in get_optional_tracks
        # and send them out to subfunctions that handle the different types of tracks?

        # TODO if protein_coding_gene_file_name is None and assembly_counter !=0,
        # there has to be at least one other track for that assembly!

        # TODO handle GWAS tracks that have `defaultSession: true` in the config.yml

    data = default_session.make_defaultSession_dict()
    save_json(data, output_json_path, config_yml_path)
