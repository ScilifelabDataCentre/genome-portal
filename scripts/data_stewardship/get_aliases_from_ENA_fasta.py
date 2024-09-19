"""
This script generates an JBrowse2-compatible refNameAliases file from genome assembly fasta files downloaded from ENA.
The alias file will allow for displaying annotation tracks from NCBI GenBank on an ENA formatted assembly without having
to modify the data files themselves. Additionally, for cases where the original contig name is preserved in the ENA fasta
header, it will also allow for displaying tracks that calls on contig name fasta headers.

Example of a ENA formatted fasta header from a genome assembly:
>ENA|CAVLGL010000001|CAVLGL010000001.1 Parnassius mnemosyne genome assembly, contig: scaffold_1

NCBI GenBank formatted version of the same assembly:
>CAVLGL010000001.1 Parnassius mnemosyne genome assembly, contig: scaffold_1, whole genome shotgun sequence

Example of the original contig header from the same assembly:
>scaffold_1

### Input:
The path to a fasta file downloaded from ENA. The option --fasta is required.
The script supports gzipped, bgzipped, and non-compressed ENA fasta files.

### Output:
A tab-separated file with the following columns:
ENA header, NCBI header, Contig name

If not specified, the outfile will be saved to a subdirectory named 'alias_files_temp_storage/' within the same directory as the script, and will have the
file name of the fasta file appended with the extension: .alias

### Examples:
python get_aliases_from_ENA_fasta.py --fasta filename.fa

"""

import argparse
import gzip
import os
import re


def parse_arguments():
    """
    Run argparse to set up and capture the arguments of the script.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--fasta",
        required=True,
        type=str,
        metavar=".fa",
        help="""
        Input; the path to the ENA formatted genome assembly fasta file. The script does not support compressed files (e.g.: .fa.gz)
        """,
    )
    parser.add_argument(
        "--out",
        required=False,
        type=str,
        metavar=".tsv",
        help="""
        Output [optional]; the path to save the generated alias file. If not specified, the outfile will be saved to 'alias_files_temp_storage/'
        in the current directory and will be given the file name of the fasta file appended with the suffix: .alias
        """,
    )
    return parser.parse_args()


def open_fasta_file(fasta_path: str):
    """
    Subfunction for make_alias_file that opens the fasta file given by the --fasta input argument, after checking if it is gzipped or not.
    It passes the opened file onto the next subfunction, in which the alias dictionary is generated.
    """
    try:
        with gzip.open(fasta_path, "rt") as file:
            alias_dict = process_fasta_headers(file)
            print(f"The file {fasta_path} is gzipped. Creating refNameAlias file...")
    except gzip.BadGzipFile:
        with open(fasta_path, "r") as file:
            alias_dict = process_fasta_headers(file)
            print(f"The file {fasta_path} is not gzipped. Creating refNameAlias file...")
    return alias_dict


def process_fasta_headers(file: str) -> dict[str, dict[str, str]]:
    """
    Subfunction for open_fasta_file. Processes the fasta headers and extracts the ENA
    and NCBI headers, and, if present, the contig header. It raises an error if the fasta headers
    are not formatted in the ENA style. Returns a nested dictionary back to open_fasta_file.
    """
    alias_dict = {}
    for line in file:
        if line.startswith(">"):
            # Find fasta headers in the multi-fasta
            if line.startswith(">ENA|"):
                ENA_fasta_header = re.split(">| ", line.rstrip())[1]
                NCBI_fasta_header = re.split("\\|| ", line.rstrip())[2]
                if re.search("contig: ", line):
                    contig_name_fasta_header = re.split("contig: ", line.rstrip())[1]
                else:
                    contig_name_fasta_header = ""
                alias_dict[ENA_fasta_header] = {NCBI_fasta_header: contig_name_fasta_header}
            else:
                raise ValueError("The fasta headers are not formatted in the ENA style.")
    return alias_dict


def make_alias_file(fasta_path: str, alias_output_path: str) -> dict[str, dict[str, str]]:
    """
    Subfunction for main. Calls process_fasta_headers to generate the alias dictionary, and writes the dictionary to a file.
    If the --out argument was specified, the file will be saved to the specified path. If not, it will be saved to the
    alias_files_temp_storage subdirectory and be named after the inputted fasta file and suffixed with .alias.
    """
    alias_dict = open_fasta_file(fasta_path)
    with open(alias_output_path, "w") as file:
        file.write("#ENA_header\tNCBI_header\toriginal_header\n")
        for outer_key, outer_value in alias_dict.items():
            for inner_key, inner_value in outer_value.items():
                aliases = "".join(f"{outer_key}\t{inner_key}\t{inner_value}\n")
                file.write(aliases)
    print("Wrote alias file to:", alias_output_path)


def main():
    """
    Main function that calls the subfunctions to generate the alias file.
    """
    args = parse_arguments()
    fasta_path = args.fasta
    alias_output_path = args.out

    if not alias_output_path:
        fasta_filename = os.path.basename(fasta_path)
        while any(fasta_filename.endswith(ext) for ext in [".gz", ".bgz"]):
            fasta_filename, _ = os.path.splitext(fasta_filename)
        alias_output_path = "alias_files_temp_storage/" + fasta_filename + ".alias"

    try:
        make_alias_file(fasta_path, alias_output_path)
    except ValueError as e:
        print("""
              ERROR: This does not seem to be an ENA formatted fasta file.
              Please make sure that the file is not compressed and that the headers start with: ">ENA|".
              """)
        raise e


if __name__ == "__main__":
    main()
