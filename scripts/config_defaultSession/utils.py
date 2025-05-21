import gzip
import json
import os
from pathlib import Path


def check_config_json_exists(output_json_path: Path) -> None:
    """
    If overwrite mode not specificed in args, check that the folders are empty.
    Raise error if not.
    """

    if output_json_path:
        raise FileExistsError(
            f"""
            It appears that a defaultSession JSON file already exists at {output_json_path}.",
            If you are sure you want to overwrite these files, add the flag "--overwrite".
            Exiting..."""
        )


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
        if file_path.name.endswith(".gz"):
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


def save_json(data, output_json_path, config_path):
    """
    Subfunction that writes a dictionary (data) as a JSON file at the specified output path.
    """
    try:
        with open(output_json_path, "w") as file:
            json.dump(data, file, indent=2)
            print(f"\nSaved the populated defaultSession JSON to: {output_json_path}.")
            print(f"To test the file, copy it to: {output_json_path} and run the makefile (make all).")
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
