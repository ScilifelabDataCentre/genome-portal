"""
This scripts takes a populated config.yml file for a species in the Swedish Reference Genome Portal and generates a
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
A json file with a minimal JBrowse 2 defaultSession for the Swedish Reference Genome Portal. The output will be saved to
./scripts/data_stewardship/temp/test_default_session.json in the Genome Portal git repository. The file or its content can
then be copied to config.json in .config/[SPECIES_NAMES].

### Dependencies:
pyyaml                          -   Used for parsing the yaml file.
                                    Can be for instance be installed with pip: pip install pyyaml
minimal_default_session.json    -   A template default_session.json file with placeholders for the values that will be
                                    fetched from the config.yml. The template is located in ./scripts/templates .

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


def get_git_root():
    try:
        git_root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).strip().decode("utf-8")
        return git_root
    except subprocess.CalledProcessError:
        raise RuntimeError(
            """It seems like you are not currently not in a git repository.
            Please run this script from within the Genome Portal git repository."""
        ) from None


def load_yaml_config(config_path):
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def load_json_template(json_path):
    with open(json_path, "r") as file:
        return json.load(file)


def get_species_abbreviation(organism):
    words = organism.split()
    if len(words) >= 2:
        return (words[0][0] + words[1][:3]).lower()
    # Fallback if the organism name is not formatted with white space delimiter:
    return (organism[:4]).lower()


def strip_extension(file_name):
    if file_name.endswith(".gz"):
        return file_name.replace(".gz", "")
    elif file_name.endswith(".zip"):
        return file_name.replace(".zip", "")
    return file_name


def get_first_fasta_header_and_sequence_length(file_path):
    first_sequence_length = 0
    parser_is_in_sequence = False

    if file_path.endswith(".gz"):
        with gzip.open(file_path, "rt") as file:
            for line in file:
                if line.startswith(">"):
                    if parser_is_in_sequence:
                        break
                    first_fasta_header = line[1:].strip().split()[0]
                    parser_is_in_sequence = True
                elif parser_is_in_sequence:
                    first_sequence_length += len(line.strip())
    else:
        with open(file_path, "r") as file:
            for line in file:
                if line.startswith(">"):
                    if parser_is_in_sequence:
                        break
                    first_fasta_header = line[1:].strip().split()[0]
                    parser_is_in_sequence = True
                elif parser_is_in_sequence:
                    first_sequence_length += len(line.strip())

    return first_fasta_header, first_sequence_length


def get_protein_coding_genes_file_name(config):
    for track in config["tracks"]:
        if track["name"].lower() in ["protein coding genes", "protein-coding genes"]:
            protein_coding_genes_found = True
            if "fileName" in track:
                protein_coding_gene_file_name = strip_extension(track["fileName"])
                return protein_coding_gene_file_name
            elif "url" in track:
                protein_coding_gene_file_name = strip_extension(os.path.basename(track["url"]))
                return protein_coding_gene_file_name

    if not protein_coding_genes_found:
        raise ValueError("No track with name 'Protein coding genes' found. Exiting.")


def populate_placeholder_values(data, config, git_root, species_name, species_abbreviation, species_name_underscored):
    assembly_name = config["assembly"]["name"]
    assembly_file_name = os.path.basename(config["assembly"]["url"])
    protein_coding_gene_file_name = get_protein_coding_genes_file_name(config)

    # Check if the assembly URL filename exists in ./data/[SPECIES_NAME]/ after being downloaded by the makefile
    assembly_file_path = os.path.join(
        git_root, "data", species_name_underscored, assembly_file_name.replace(".fasta", ".fna")
    )
    if os.path.exists(assembly_file_path):
        first_fasta_header, first_sequence_length = get_first_fasta_header_and_sequence_length(assembly_file_path)
    else:
        first_fasta_header = None
        print(
            f"Assembly file {assembly_file_path} does not exist in ./data/{species_name_underscored}/. If the assembly url has been configured, it can be downloaded by running the makefile."
        )

    # Populate the JSON template with the values that were fetched from or via the config file
    data["defaultSession"]["id"] = data["defaultSession"]["id"].replace("[SPECIES_ABBREVIATION]", species_abbreviation)
    data["defaultSession"]["name"] = species_name
    data["defaultSession"]["widgets"]["hierarchicalTrackSelector"]["view"] = data["defaultSession"]["widgets"][
        "hierarchicalTrackSelector"
    ]["view"].replace("[SPECIES_ABBREVIATION]", species_abbreviation)
    data["defaultSession"]["views"][0]["id"] = data["defaultSession"]["views"][0]["id"].replace(
        "[SPECIES_ABBREVIATION]", species_abbreviation
    )
    if first_fasta_header:
        data["defaultSession"]["views"][0]["displayedRegions"][0]["refName"] = first_fasta_header
    else:
        print(
            "Warning: The first fasta header in the assembly file could not be found. The 'refName' field in the JSON template will not be populated by the script. Please update the output file manually."
        )
    if first_sequence_length:
        data["defaultSession"]["views"][0]["displayedRegions"][0]["end"] = first_sequence_length
    else:
        print(
            "Warning: The length of the first sequence in the in the assembly file could not be found. The 'end' and 'bpPerPx' fields in the JSON template will not be populated by the script. Please update the output file manually."
        )
    data["defaultSession"]["views"][0]["displayedRegions"][0]["assemblyName"] = assembly_name
    data["defaultSession"]["views"][0]["tracks"][0]["id"] = data["defaultSession"]["views"][0]["tracks"][0][
        "id"
    ].replace("[SPECIES_ABBREVIATION]", species_abbreviation)
    data["defaultSession"]["views"][0]["tracks"][0]["configuration"] = protein_coding_gene_file_name
    data["defaultSession"]["views"][0]["tracks"][0]["displays"][0]["id"] = data["defaultSession"]["views"][0]["tracks"][
        0
    ]["displays"][0]["id"].replace("[SPECIES_ABBREVIATION]", species_abbreviation)
    data["defaultSession"]["views"][0]["tracks"][0]["displays"][0]["configuration"] = data["defaultSession"]["views"][
        0
    ]["tracks"][0]["displays"][0]["configuration"].replace("[TRACK_FILE_NAME]", protein_coding_gene_file_name)

    return data


def add_defaultSession_true_tracks(config, data, species_abbreviation):
    for track in config["tracks"]:
        if "defaultSession" in track and track["defaultSession"]:
            print(track)
            print(track["defaultSession"])
            # Ensure protein-coding genes are not added to the default session again if the user has set its with efaultSession: true in the config.yml
            if track["name"].lower() in ["protein coding genes", "protein-coding genes"]:
                continue

            track_outer_id = f"{species_abbreviation}_default_{track['name'].replace(' ', '_').lower()}"
            track_file_name = f"{track['fileName'].rstrip('.gz').rstrip('.zip').rstrip('.bgz')}"
            new_track = {
                "id": track_outer_id,
                "type": "FeatureTrack",
                "configuration": track_file_name,
                "minimized": False,
                "displays": [
                    {
                        "id": f"{track_outer_id}_display",
                        "type": "LinearBasicDisplay",
                        "heightPreConfig": 150,
                        "configuration": f"{track_file_name}-LinearBasicDisplay",
                    }
                ],
            }
            data["defaultSession"]["views"][0]["tracks"].append(new_track)

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
    git_root = get_git_root()
    json_path = os.path.join(git_root, "scripts/templates/minimal_default_session.json")

    config = load_yaml_config(config_path)
    if "tracks" not in config:
        raise ValueError("The configuration file does not contain 'tracks'. Exiting.")
    data = load_json_template(json_path)

    species_name = config["organism"]
    species_abbreviation = get_species_abbreviation(species_name)
    species_name_underscored = species_name.replace(" ", "_").lower()

    populated_data = populate_placeholder_values(
        data, config, git_root, species_name, species_abbreviation, species_name_underscored
    )
    populated_data = add_defaultSession_true_tracks(config, populated_data, species_abbreviation)
    output_json_path = args.out
    if not output_json_path:
        output_json_path = os.path.join(
            git_root, f"scripts/data_stewardship/temp/{species_name_underscored}_default_session.json"
        )

    save_json(populated_data, output_json_path, config_path)


if __name__ == "__main__":
    main()
