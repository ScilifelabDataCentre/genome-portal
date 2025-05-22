"""
Package to create a defaultSession config.json for a species based on a config.yml file.

Assumes that the dockermake has been run once to download the files.

(The intention is that add_new_species has been run once first, but as long as there is a config.yml, this package will work)

Handles multi-assembly config.yml (YAML document) files by assembly_counter


config.yml keys that are recognised by this script:
assembly.defaultScaffold: str   (name of the scaffold to display in the defaultSession when the JBrowse instance is initialized)
assembly.bpPerPx: int = 50      (this is the "zoom level" in the JBrowse view. Longer scaffolds tend to need a larger value)
track.defaultSession: Bool      (ignored by protein-coding gene tracks since they are mandatory)
track.trackType: str            (one of ["linear", "arc", "gwas"])
track.scoreColumn: str:         (name of the score column in the track file)

old keys that are deprecated and should not be used:
track.GWAS
track.scoreColumnGWAS

#expanding the code
to add a new display type to the code, define a new key value for trackType and add the corresponding logic to get_track_display_type()
if a track needs a plugin, the logic can be added to check_if_plugin_needed

"""

import argparse
from pathlib import Path

import yaml
from add_tracks_to_view import (
    DefaultSession,
    process_tracks,
)
from utils import check_config_json_exists, get_fasta_header_and_scaffold_length, get_species_abbreviation, save_json


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
        metavar="[Species' config.yml]",
        help="Input; the path to config.yml for the species.",
    )

    parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        help="""If the defaultSession config.json for the species already exist, should it be overwritten?
            If flag NOT provided, no overwrite performed.""",
    )

    parser.add_argument(
        "-s",
        "--skip-reading-fasta",
        action="store_true",
        help="""Skips analysing the FASTA file to get the default scaffold and sequence length.
            This is useful if the FASTA file is not available.""",
        required=False,
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

        if args.skip_reading_fasta:
            default_scaffold = None
            scaffold_length = None
        else:
            default_scaffold, scaffold_length = get_fasta_header_and_scaffold_length(
                config=config, species_slug=default_session.species_slug
            )

        default_session.add_view(
            assembly_counter=assembly_counter,
            config=config,
            default_scaffold=default_scaffold,
            scaffold_length=scaffold_length,
            bpPerPx=config["assembly"].get("bpPerPx", 50),
        )

        default_session = process_tracks(
            default_session=default_session,
            config=config,
            assembly_counter=assembly_counter,
        )

        # TODO consider the track_color key in the config.yml

        # TODO if protein_coding_gene_file_name is None and assembly_counter !=0,
        # there has to be at least one other track for that assembly!

        # TODO order of the tracks in the config.yml is not preserved in the final config.json made by the makefile.
        # see if that could be fixed in the makefile? The other option is to use categories in the defaultSession
        # config.json like we have done for linum in the past

    data = default_session.make_defaultSession_dict()
    save_json(data, output_json_path, config_yml_path)
