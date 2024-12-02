"""
This script takes a populated config.yml file for a species in the Swedish Reference Genome Portal and generates a
minimal JBrowse 2 defaultSession from it. The resulting output file can be copied to the config.json file in the species
directory, from where it will be parsed by the makefile and used to generate the final config.json that will be used by
the JBrowse 2 instance.

To get the most out of this script, the config.yml for the species should be populated with at least the assembly and
protein-coding genes tracks, and `makefile build` should preferrably have been run once so that the files have been
downloaded to ./data/[SPECIES_NAME].

The script supports config.yml tracks that are have explicit file names in the urls, and tracks that use the key `fileName`
for download of files where the file names is hidden in the url (e.g. Figshare).

### Input:
The path to a config.yml file configured for the Swedish Reference Genome Portal. The option --yaml is required.

### Output:
A json file with a minimal JBrowse 2 defaultSession for the Swedish Reference Genome Portal. Unless specified otherwise,
the output will be saved to ./scripts/data_stewardship/temp/test_default_session.json in the Genome Portal git directory.
The file or its content can then be copied to config.json in .config/[SPECIES_NAMES].

### Dependencies:
pyyaml                          -   Used for parsing the yaml file.
                                    Can be for instance be installed with pip: pip install pyyaml

### Usage:
(Assuming that the following two steps have already been completed:
1. Populate the config.yml file for the species.
2. Run `makefile build` to download the assembly and protein-coding genes files.)

python ./scripts/data_stewardship/configure_default_session.py --yaml ./config/linum_tenue/config.yml

python ./scripts/data_stewardship/configure_default_session.py --yaml ./config/littorina_saxatilis/config.yml \
    --out ./path/to/output_file.json

--yaml is a mandatory flag that points to the config.yml file for the species.
--out is an optional flag that allows the user to specify the path to save the generated JSON file. If not specified,
        the outfile will be saved to ./scripts/data_stewardship/temp/[SPECIES_NAME]_default_session.json.

### This script was developed and tested with:
Python 3.12.3
pyyaml 6.0.2

"""

import argparse
import gzip
import json
import os
import subprocess

import yaml


def parse_arguments():
    """
    Run argparse to set up and capture the arguments of the script.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--yaml",
        required=True,
        type=str,
        metavar=".yml",
        help="""
        Input; the path to config.yml for the species.
        """,
    )
    parser.add_argument(
        "--out",
        required=False,
        type=str,
        metavar=".json",
        help="""
        Output [optional]; the path to save the generated JSON file. If not specified, the outfile will be saved to
        ./scripts/data_stewardship/temp/[SPECIES_NAME]_default_session.json.
        """,
    )
    return parser.parse_args()


def get_git_repo_root():
    try:
        git_root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).strip().decode("utf-8")
        return git_root
    except subprocess.CalledProcessError:
        raise RuntimeError(
            """It seems like you are not currently not in a git repository.
            Please run this script from within the Genome Portal git repository."""
        ) from None


def get_species_abbreviation(organism):
    words = organism.split()
    if len(words) >= 2:
        return (words[0][0] + words[1][:3]).lower()
    # Fallback if the organism name is not formatted with white space delimiter:
    return (organism[:4]).lower()


def get_fasta_header_and_sequence_length(file_path, default_scaffold=None):
    def parse_fasta_file(file, default_scaffold):
        first_fasta_header = None
        sequence_length = 0
        parser_is_in_sequence = False
        header_found = False

        for line in file:
            if line.startswith(">"):
                current_header = line[1:].strip().split()[0]
                if default_scaffold:
                    if current_header == default_scaffold:
                        header_found = True
                        parser_is_in_sequence = True
                    elif parser_is_in_sequence:
                        break
                else:
                    if parser_is_in_sequence:
                        break
                    first_fasta_header = current_header
                    parser_is_in_sequence = True
            elif parser_is_in_sequence:
                sequence_length += len(line.strip())

        return first_fasta_header, sequence_length, header_found

    if file_path.endswith(".gz"):
        with gzip.open(file_path, "rt") as file:
            first_fasta_header, sequence_length, header_found = parse_fasta_file(file, default_scaffold)
    else:
        with open(file_path, "r") as file:
            first_fasta_header, sequence_length, header_found = parse_fasta_file(file, default_scaffold)

    if default_scaffold and not header_found:
        raise ValueError(
            f"No FASTA header named '{default_scaffold}' was found in the file. Please check the defaultScaffold value in the config.yml."
        )

    return (default_scaffold if default_scaffold else first_fasta_header), sequence_length


def get_protein_coding_genes_file_name(config):
    for track in config["tracks"]:
        if track["name"].lower() in ["protein coding genes", "protein-coding genes"]:
            if "fileName" in track:
                if track["fileName"].endswith((".gz", ".zip")):
                    return track["fileName"].rsplit(".", 1)[0]
                else:
                    return track["fileName"]
            elif "url" in track:
                file_name = os.path.basename(track["url"])
                if file_name.endswith((".gz", ".zip")):
                    return file_name.rsplit(".", 1)[0]
                else:
                    return file_name
    raise ValueError("No track with name 'Protein coding genes' found. Exiting.")


def populate_mandatory_values(config, git_root, species_name, species_abbreviation, species_name_underscored):
    assembly_file_name = os.path.basename(config["assembly"]["url"])
    protein_coding_gene_file_name = get_protein_coding_genes_file_name(config)

    assembly_file_path = os.path.join(
        git_root, "data", species_name_underscored, assembly_file_name.replace(".fasta", ".fna")
    )
    if os.path.exists(assembly_file_path):
        # The "get" method returns None if the key is not found
        default_scaffold = config["assembly"].get("defaultScaffold")
        default_scaffold, sequence_length = get_fasta_header_and_sequence_length(assembly_file_path, default_scaffold)
    else:
        print(
            f"Assembly file {assembly_file_path} does not exist in ./data/{species_name_underscored}/. If the assembly url has been configured, it can be downloaded by running the makefile."
        )

    data = {}
    data["defaultSession"] = {
        "id": f"{species_abbreviation}_default_session",
        "name": species_name,
        "widgets": {
            "hierarchicalTrackSelector": {
                "id": "hierarchicalTrackSelector",
                "type": "HierarchicalTrackSelectorWidget",
                "view": f"{species_abbreviation}_default_session_view",
                "faceted": {"showSparse": False, "showFilters": True, "showOptions": False, "panelWidth": 400},
            }
        },
        "activeWidgets": {"hierarchicalTrackSelector": "hierarchicalTrackSelector"},
        "views": [
            {
                "id": f"{species_abbreviation}_default_session_view",
                "minimized": False,
                "type": "LinearGenomeView",
                "trackLabels": "offset",
                "offsetPx": 0,
                "bpPerPx": 50,
                "displayedRegions": [
                    {
                        "refName": default_scaffold if default_scaffold else "[SCAFFOLD_HEADER]",
                        "start": 0,
                        "end": sequence_length if sequence_length else 100000,
                        "reversed": False,
                        "assemblyName": config["assembly"]["name"],
                    }
                ],
                "tracks": [
                    {
                        "id": f"{species_abbreviation}_default_protein_coding_genes",
                        "type": "FeatureTrack",
                        "configuration": protein_coding_gene_file_name,
                        "minimized": False,
                        "displays": [
                            {
                                "id": f"{species_abbreviation}_default_protein_coding_genes_display",
                                "type": "LinearBasicDisplay",
                                "heightPreConfig": 150,
                                "configuration": f"{protein_coding_gene_file_name}-LinearBasicDisplay",
                            }
                        ],
                    }
                ],
            }
        ],
    }
    return data


def populate_values_from_optional_tracks(config, data, species_abbreviation):
    plugin_added = False
    assembly_name = config.get("assembly", {}).get("name", "")

    for track in config["tracks"]:
        if "defaultSession" in track and track["defaultSession"]:
            # Ensure protein-coding genes are not added to the default session again if the user has happened to set it with defaultSession: true in the config.yml
            if track["name"].lower() in ["protein coding genes", "protein-coding genes"]:
                continue
            data = add_defaultSession_true_tracks(track, data, species_abbreviation)

        if "GWAS" in track and track["GWAS"]:
            if not plugin_added:
                plugin_call = {
                    "name": "GWAS",
                    "url": "https://unpkg.com/jbrowse-plugin-gwas/dist/jbrowse-plugin-gwas.umd.production.min.js",
                }
                if "plugins" not in data:
                    data["plugins"] = []
                data["plugins"].append(plugin_call)
                plugin_added = True
            data = add_gwas_true_tracks(track, data, species_abbreviation, assembly_name)

    return data


def add_defaultSession_true_tracks(track, data, species_abbreviation):
    track_outer_id = (
        f"{species_abbreviation}_default_{track['name'].replace(' ', '_').replace('\'', '').replace(',', '')}"
    )
    track_file_name = f"{track['fileName'].rstrip('.gz').rstrip('.zip').rstrip('.bgz')}"
    track_type = "LinearBasicDisplay"
    track_config = track_file_name
    display_config = f"{track_file_name}-LinearBasicDisplay"

    # For the case when a track true for both defaultSession and GWAS:
    if "GWAS" in track and track["GWAS"]:
        track_type = "LinearManhattanDisplay"
        # this next line needs can be improved: it serves to to reproduce the same output as the old handcrafted config.json for L. tenue.
        # (the line is based on the track_outer_id form the GWAS function below)
        track_config = (
            f"{species_abbreviation}_init_{track['name'].replace(' ', '_').replace('\'', '').replace(',', '')}"
        )
        display_config = f"{track_config}_display"

    new_track = {
        "id": track_outer_id,
        "type": "FeatureTrack",
        "configuration": track_config,
        "minimized": False,
        "displays": [
            {
                "id": f"{track_outer_id}_display",
                "type": track_type,
                "heightPreConfig": 150,
                "configuration": display_config,
            }
        ],
    }
    data["defaultSession"]["views"][0]["tracks"].append(new_track)

    return data


def add_gwas_true_tracks(track, data, species_abbreviation, assembly_name):
    if "scoreColumnGWAS" not in track:
        raise ValueError(
            f"Track '{track['name']}' is configured to be treated as a GWAS track but is missing 'scoreColumnGWAS' in the config.yml. Please update this and re-run the script."
        )
    adapter_scoreColumn = track["scoreColumnGWAS"]

    track_outer_id = f"{species_abbreviation}_init_{track['name'].replace(' ', '_').replace('\'', '').replace(',', '')}"

    def get_base_extension(file_name):
        base_name = os.path.splitext(file_name)[0] if file_name.endswith((".gz", ".zip")) else file_name
        return os.path.splitext(base_name)[1].lstrip(".")

    base_extension = get_base_extension(track["fileName"])

    # Eventually we need to support more file types here as we encounter them.
    # There is also a discussion to be had if the makefile should handle GWAS files instead of this script
    if base_extension == "bed":
        adapter_type = "BedTabixAdapter"
        bed_gz_location = track["fileName"]
        if bed_gz_location.endswith((".gz", ".zip")):
            bed_gz_location = bed_gz_location.replace(".gz", ".bgz").replace(".zip", ".bgz")
        index_location = f"{bed_gz_location}.tbi"

    # category is hardcoded for now, but could be added to the config.yml in the future
    # An added benefit of having the category is that it ensures that the tracks come below the protein-codon genes in the track selector
    new_GWAS_track = {
        "type": "FeatureTrack",
        "trackId": track_outer_id,
        "name": track["name"],
        "assemblyNames": [assembly_name],
        "category": ["GWAS"],
        "adapter": {
            "type": adapter_type,
            "scoreColumn": adapter_scoreColumn,
            "bedGzLocation": {"uri": bed_gz_location},
            "index": {"location": {"uri": index_location}},
        },
        "displays": [{"displayId": f"{track_outer_id}_display", "type": "LinearManhattanDisplay"}],
    }

    if "tracks" not in data:
        data["tracks"] = []
    data["tracks"].append(new_GWAS_track)

    return data


def save_json(data, output_json_path, config_path):
    with open(output_json_path, "w") as file:
        json.dump(data, file, indent=2)
        print(f"\nSaved the populated defaultSession JSON to: {output_json_path}.")
        print(f"To test the file, copy it to: {config_path.replace('.yml', '.json')} and run the makefile (make all).")
        print(
            "\nNote! The settings for which scaffold to display as default were set based on the first scaffold in the FASTA."
        )
        print("bgPerPx often needs manual adjustment based on the length of the scaffold and gene annotation density.")
        print("If the first scaffold is not the one you want to display by default, this need to be adjusted manually.")


def main():
    args = parse_arguments()
    config_path = args.yaml
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    if "tracks" not in config:
        raise ValueError(
            "The configuration file does not contain 'tracks'. Thus there are no tracks to set for the defaultSession. Exiting."
        )
    species_name = config["organism"]
    species_abbreviation = get_species_abbreviation(species_name)
    species_name_underscored = species_name.replace(" ", "_").lower()
    git_root = get_git_repo_root()
    output_json_path = args.out
    if not output_json_path:
        output_json_path = os.path.join(
            git_root, f"scripts/data_stewardship/temp/{species_name_underscored}_default_session.json"
        )

    populated_data = populate_mandatory_values(
        config, git_root, species_name, species_abbreviation, species_name_underscored
    )
    populated_data = populate_values_from_optional_tracks(config, populated_data, species_abbreviation)
    save_json(populated_data, output_json_path, config_path)


if __name__ == "__main__":
    main()
