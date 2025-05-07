"""
This script takes a populated config.yml file for a species in the Swedish Reference Genome Portal and generates a
minimal JBrowse 2 defaultSession from it. The resulting output file can be copied to the config.json file in the species
directory, from where it will be parsed by the makefile and used to generate the final config.json that will be used by
the JBrowse 2 instance.

The config.yml for the species should be populated with at least one assembly and its protein-coding genes tracks,
and `./scripts/dockermake` should have been run once so that the files have been downloaded to ./data/[SPECIES_NAME].
For the tracks, both explicit file names in the URLs, and tracks that use the key `fileName` for download of files where
the file names is hidden in the url (e.g. Figshare) are supported.

The script supports multi-assembly configurations, where the `---` YAML document notation is used after each assembly
to indicate that the next assembly and its associated tracks should be configured in its own JBrowse view in the session.

Furthermore, the script also supports the configuration of GWAS tracks: it adds them to the defaultSession, handles calling of the GWAS
plugin, and the setup of the GWAS tracks in the tracks section of the JSON object.

### Input:
The path to a config.yml file configured for the Swedish Reference Genome Portal. The option --yaml is required.

### Output:
A JSON file with a minimal JBrowse 2 defaultSession for the Swedish Reference Genome Portal. Unless specified otherwise,
the output will be saved to ./scripts/data_stewardship/temp/test_default_session.json in the Genome Portal git directory.
The file or its content can then be copied to config.json in .config/[SPECIES_NAMES].

### Dependencies:
pyyaml                          -   Used for parsing the yaml file.
                                    Can be for instance be installed with pip: `pip install pyyaml`

### Usage:
(Assuming that the following two steps have already been completed:
1. Populate the config.yml file for the species.
2. Run `./scripts/dockermake` to download the assembly and protein-coding genes files.)

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
    Subfunction that runs argparse to set up and capture the arguments of the script.
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
    """
    Subfunction that checks if the script is run from within a git repository and, if so, returns the root directory of the repository.
    The path to the root directory is used to locate in other subfunctions to locate the assembly files and to set a default directory for
    saving the output JSON file.
    """
    try:
        git_root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).strip().decode("utf-8")
        return git_root
    except subprocess.CalledProcessError:
        raise RuntimeError(
            """It seems like you are not currently not in a git repository.
            Please run this script from within the Genome Portal git repository."""
        ) from None


def get_species_abbreviation(organism):
    """
    Subfunction that takes the scientific (binomial) species name and returns an abbreviation that will be used as a track id suffix.
    Example: "Linum tenue" -> "lten". In order for this to work, the organism name need to be a non-empty string; this is checked in the main() function.
    """
    words = organism.split()
    if len(words) >= 2:
        return (words[0][0] + words[1][:3]).lower()
    # Fallback if the organism name is not formatted with white space delimiter:
    return (organism[:4]).lower()


def get_fasta_header_and_sequence_length(file_path, default_scaffold=None):
    """
    Subfunction that reads an assembly FASTA file and returns the header of the first scaffold and its sequence length.
    Alternatively, if the user has defined a default scaffold in the config.yml with the defaultScaffold key,
    the function will return the header of that scaffold instead of the first scaffold. The header and length are used to
    populate the defaultSession JSON object to control which scaffold is display upon loading a new session and its zoom level.
    """

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

    try:
        if file_path.endswith(".gz"):
            with gzip.open(file_path, "rt") as file:
                first_fasta_header, sequence_length, header_found = parse_fasta_file(file, default_scaffold)
        else:
            with open(file_path, "r") as file:
                first_fasta_header, sequence_length, header_found = parse_fasta_file(file, default_scaffold)
    except IOError as e:
        raise IOError(f"Error: Failed to open the assembly file from the given path at {file_path}. Error: {e}") from e

    if default_scaffold and not header_found:
        raise ValueError(
            f"Error: No FASTA header named '{default_scaffold}' was found in the file. Please check the defaultScaffold value in the config.yml."
        )

    return (default_scaffold if default_scaffold else first_fasta_header), sequence_length


def get_track_file_name(track):
    """
    Subfunction that extracts the base file name from a config.yml dictionary. The base file name is used as a
    non-arbirtary value in the JBrowse config.json, and it cannot contain file extensions such as .gz, .zip,
    or .bgz. Filenames can either be fetched from explict URLs or from the fileName key.

    This function is intended to be run within a loop as per the following:
    for track in config["tracks"]:
        filename = get_track_file_name(track)
    """
    if "fileName" in track:
        file_name = track["fileName"]
    elif "url" in track:
        file_name = os.path.basename(track["url"])
    else:
        raise ValueError(
            "Error: Was not able to obtain the track filenames from the URLs or the fileName keys. Exiting."
        )
    return file_name.rsplit(".", 1)[0] if file_name.endswith((".gz", ".bgz", ".zip")) else file_name


def populate_defaultSession_object(data, species_info, assembly_counter):
    """
    Subfunction that populates the outer parts of the defaultSession JSON object with the species name and abbreviation.
    Also adds disableAnalytics to the dictionary to prevent Google Analytics from being loaded when running JBrowse.
    """
    data["defaultSession"] = {
        "id": f"{species_info["species_abbreviation"]}_default_session",
        "name": species_info["species_name"],
        "widgets": {
            "hierarchicalTrackSelector": {
                "id": "hierarchicalTrackSelector",
                "type": "HierarchicalTrackSelectorWidget",
                "view": f"{species_info["species_abbreviation"]}_default_session_view_{assembly_counter}",
                "faceted": {"showSparse": False, "showFilters": True, "showOptions": False, "panelWidth": 400},
            }
        },
        "activeWidgets": {"hierarchicalTrackSelector": "hierarchicalTrackSelector"},
    }
    data["configuration"] = {"disableAnalytics": True}
    return data


def initiate_views_and_populate_mandatory_tracks(data, species_info, config, git_root, config_dir, assembly_counter):
    """
    Subfunction that adds a JBrowse view to the defaultSession JSON object. The funcion is iterated upon by main()
    so that a new view is added for each assembly in the config.yml. It then checks if the primary assembly has a
    protein-coding genes track, and if not, raises an error. For the secondary assemblies, there is no requirement to
    have a protein-coding genes track, but at least one track is required. (The populate_values_from_optional_tracks()
    is later called by main() to also ensure that the secondary assemblies have at least one track set to defaultSession: true.)
    """

    # Check if there is a protein-coding genes track configured for the current assembly
    protein_coding_gene_file_name = None
    for track in config.get("tracks", []):
        if "name" in track and track["name"].lower() in ["protein coding genes", "protein-coding genes"]:
            protein_coding_gene_file_name = get_track_file_name(track)
            break

    if not protein_coding_gene_file_name:
        # Primary assemblies are required to have a protein-coding genes track; it is optional for secondary assemblies.
        if assembly_counter == 0:
            raise ValueError(
                f"Error: The primary assembly (assembly number {assembly_counter+1}) is required to have a track named 'Protein coding genes'. Exiting."
            )
        # Secondary assemblies do not need to have a track name "Protein coding genes", but need to have at least one track.
        elif not ("tracks" in config and isinstance(config["tracks"], list) and len(config["tracks"]) > 0):
            raise ValueError(
                f"Error: There seem to be no tracks configured for assembly number {assembly_counter+1} in the config.yml. "
                "In order to configure a defaultSession, there need to be at least one track. Exiting."
            )

    species_abbreviation = species_info["species_abbreviation"]
    species_name_underscored = species_info["species_name_underscored"]
    assembly_file_name = os.path.basename(config["assembly"]["url"])
    assembly_file_path = os.path.join(
        git_root, config_dir.replace("config", "data"), assembly_file_name.replace(".fasta", ".fna")
    )

    if os.path.exists(assembly_file_path):
        # The "get" method returns None if the key is not found
        default_scaffold = config["assembly"].get("defaultScaffold")
        default_scaffold, sequence_length = get_fasta_header_and_sequence_length(assembly_file_path, default_scaffold)
    else:
        print(
            f"Assembly file {assembly_file_path} does not exist in ./data/{species_name_underscored}/. If the assembly url has been configured, it can be downloaded by running the makefile."
        )
    views = [
        {
            "id": f"{species_abbreviation}_default_session_view_{assembly_counter}",
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
            "tracks": [],
        }
    ]

    if "views" in data["defaultSession"]:
        data["defaultSession"]["views"].extend(views)
    else:
        data["defaultSession"]["views"] = views

    if protein_coding_gene_file_name:
        protein_coding_genes_track = [
            {
                "id": f"{species_abbreviation}_default_protein_coding_genes_view_{assembly_counter}",
                "type": "FeatureTrack",
                "configuration": protein_coding_gene_file_name,
                "minimized": False,
                "displays": [
                    {
                        "id": f"{species_abbreviation}_default_protein_coding_genes_view_{assembly_counter}_display",
                        "type": "LinearBasicDisplay",
                        "heightPreConfig": 150,
                        "configuration": f"{protein_coding_gene_file_name}-LinearBasicDisplay",
                    }
                ],
            }
        ]
        data["defaultSession"]["views"][assembly_counter]["tracks"].extend(protein_coding_genes_track)

    return data


def populate_values_from_optional_tracks(config, data, species_abbreviation, assembly_counter):
    """
    Subfunction that handles the defaultSession JSON object with tracks that have the defaultSession flag set to true. It does this by
    calling on a nested subfunction named add_defaultSession_true_tracks().

    It also supports tracks that are set to be treated as GWAS tracks. At the time this script was written, the Genome Portal
    makefile did not support adding GWAS tracks to config.json via the JBrowse CLI tools. Thus, such tracks are handled by the nested
    subfunction add_gwas_true_tracks()
    """

    def add_defaultSession_true_tracks(track, data, species_abbreviation, assembly_counter, gwas_track_id):
        track_outer_id = (
            f"{species_abbreviation}_default_{track['name'].replace(' ', '_').replace('\'', '').replace(',', '')}"
        )
        track_file_name = get_track_file_name(track)
        track_type = "LinearBasicDisplay"
        track_config = track_file_name
        display_config = f"{track_file_name}-LinearBasicDisplay"

        # For the case when a track is true for both the defaultSession and GWAS keys:
        if "GWAS" in track and track["GWAS"]:
            track_type = "LinearManhattanDisplay"
            track_config = gwas_track_id
            display_config = f"{gwas_track_id}_display"

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
        data["defaultSession"]["views"][assembly_counter]["tracks"].append(new_track)

        return data

    def add_gwas_true_tracks(track, data, species_abbreviation, assembly_name, gwas_track_id):
        # This sub-subfunction handles adding of GWAS tracks to config.json (not to the defaultSession object),
        # since the makefile currently does not support the extra configuration needed for GWAS tracks.
        if "scoreColumnGWAS" not in track:
            raise ValueError(
                f"Error: Track '{track['name']}' is configured to be treated as a GWAS track but is missing 'scoreColumnGWAS' in the config.yml. "
                "Please update this and re-run the script."
            )
        adapter_scoreColumn = track["scoreColumnGWAS"]

        def get_base_extension(file_name):
            base_name = os.path.splitext(file_name)[0] if file_name.endswith((".gz", ".zip")) else file_name
            return os.path.splitext(base_name)[1].lstrip(".")

        base_extension = get_base_extension(track["fileName"])

        # Currently, this only support BED(-like) GWAS tracks. Eventually we need to support more file types here as we encounter them.
        if base_extension == "bed":
            adapter_type = "BedTabixAdapter"
            bed_gz_location = track["fileName"]
            if bed_gz_location.endswith((".gz", ".zip")):
                bed_gz_location = bed_gz_location.replace(".gz", ".bgz").replace(".zip", ".bgz")
            index_location = f"{bed_gz_location}.tbi"

        # The category value is hardcoded for now, but could be added to the config.yml in the future
        # The benefit of having definied a category is that it ensures that the GWAS tracks become sorted
        # below the protein-codon genes in the track selector.
        new_GWAS_track = {
            "type": "FeatureTrack",
            "trackId": gwas_track_id,
            "name": track["name"],
            "assemblyNames": [assembly_name],
            "category": ["GWAS"],
            "adapter": {
                "type": adapter_type,
                "scoreColumn": adapter_scoreColumn,
                "bedGzLocation": {"uri": bed_gz_location},
                "index": {"location": {"uri": index_location}},
            },
            "displays": [{"displayId": f"{gwas_track_id}_display", "type": "LinearManhattanDisplay"}],
        }

        if "tracks" not in data:
            data["tracks"] = []
        data["tracks"].append(new_GWAS_track)

        return data

    plugin_added = False
    assembly_name = config.get("assembly", {}).get("name", "")

    has_at_least_one_default_session_flag = any(
        "defaultSession" in track and track["defaultSession"] for track in config.get("tracks", [])
    )

    has_protein_coding_genes_track_in_dict = any(
        (track_id := track.get("id")) and "protein_coding_genes" in track_id
        for track in data["defaultSession"]["views"][assembly_counter]["tracks"]
    )

    if has_at_least_one_default_session_flag or has_protein_coding_genes_track_in_dict:
        for track in config["tracks"]:
            gwas_track_id = None
            # First, check if there are any GWAS tracks that need to be handled. They are currently not
            # configured by the makefile, but instead are added to config.json by the if statement below.
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
                gwas_track_id = (
                    f"{species_abbreviation}_gwas_{track['name'].replace(' ', '_').replace('\'', '').replace(',', '')}"
                )
                data = add_gwas_true_tracks(track, data, species_abbreviation, assembly_name, gwas_track_id)
            # Secondly, check if there are any tracks that are set to defaultSession: true. If so, add them to the defaultSession JSON object.
            if "defaultSession" in track and track["defaultSession"]:
                # Ensure protein-coding genes are not added to the default session again if the user has happened to set it with defaultSession: true in the config.yml
                if track["name"].lower() in ["protein coding genes", "protein-coding genes"]:
                    continue
                data = add_defaultSession_true_tracks(
                    track, data, species_abbreviation, assembly_counter, gwas_track_id
                )
    else:
        if not has_protein_coding_genes_track_in_dict:
            raise ValueError(
                f"Error: There seem to be no tracks set with the defaultSession: true flag for assembly number {assembly_counter+1} in the config.yml. "
                "In order to configure a defaultSession, there need to be at least one track set to defaultSession: true "
                "(protein-coding genes tracks are treated as defaultSession: true by default). Exiting."
            )

    return data


def save_json(data, output_json_path, config_path):
    """
    Subfunction that writes a dictionary (data) as a JSON file at the specified output path.
    """
    try:
        with open(output_json_path, "w") as file:
            json.dump(data, file, indent=2)
            print(f"\nSaved the populated defaultSession JSON to: {output_json_path}.")
            print(
                f"To test the file, copy it to: {config_path.replace('.yml', '.json')} and run the makefile (make all)."
            )
            print(
                "\nNote! The settings for which scaffold to display as default were set based on the first scaffold in the FASTA."
            )
            print(
                "bgPerPx often needs manual adjustment based on the length of the scaffold and gene annotation density."
            )
            print(
                "If the first scaffold is not the one you want to display by default, this need to be adjusted manually."
            )
    except IOError as e:
        print(f"Error: Failed to save JSON file. Error: {e}")


def main():
    """
    Main function. Reads config.yml, extracts commonly used variables, and then calls on subfunctions to populate the
    defaultSession object accordingly and to eventually save the resulting JSON file.
    """
    args = parse_arguments()
    config_path = args.yaml
    config_dir = os.path.dirname(config_path)
    try:
        with open(config_path, "r") as file:
            configs = list(yaml.safe_load_all(file))
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"Error: {e}")
        return

    git_root = get_git_repo_root()

    for assembly_counter, config in enumerate(configs):
        if not config:
            raise ValueError(
                f"Error: Document {assembly_counter+1} in the config.yml is empty. Each document must contain data. Exiting."
            )
        if assembly_counter == 0:
            if "organism" not in config or not config["organism"]:
                raise ValueError(
                    f"Error: The primary assembly (assembly number {assembly_counter+1} in config.yml) is required to have a non-empty 'organism' key. Exiting."
                )
            species_info = {
                "species_name": config["organism"],
                "species_abbreviation": get_species_abbreviation(config["organism"]),
                "species_name_underscored": config["organism"].replace(" ", "_").lower(),
            }
            output_json_path = args.out
            if not output_json_path:
                output_json_path = os.path.join(
                    git_root,
                    f"scripts/data_stewardship/temp/{species_info['species_name_underscored']}_default_session.json",
                )
            populated_data = {}
            populated_data = populate_defaultSession_object(populated_data, species_info, assembly_counter)

        populated_data = initiate_views_and_populate_mandatory_tracks(
            populated_data, species_info, config, git_root, config_dir, assembly_counter
        )
        populated_data = populate_values_from_optional_tracks(
            config, populated_data, species_info["species_abbreviation"], assembly_counter
        )

    save_json(populated_data, output_json_path, config_path)


if __name__ == "__main__":
    main()
