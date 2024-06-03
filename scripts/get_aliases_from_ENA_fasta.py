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

If not specified, the outfile will be saved to the same directory as the fasta file, with the
file name of the fasta file appended with the extension: .alias

### Examples:
python get_aliases_from_ENA_fasta.py --fasta filename.fa

"""

import argparse
import gzip
import re


def parse_the_arguments():
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
        Output [optional]; the path to save the generated alias file. If not specified, the outfile will be saved to the current directory
        with using the file name of the fasta file appended with the suffix: .alias
        """,
    )

    return parser.parse_args()


def make_alias_dictionary(fasta: str) -> dict[str, dict[str, str]]:
    """
    Load the fasta file given by the input argument. First check if it is gzipped or not.
    Then call on the subfunction process_fasta_headers. The subfunction tests if it looks like
    an ENA formatted fasta; if not: exit. If it is ENA formatted: it splits and extracts the substrings
    that contain the GenBank header, and, if present, the contig header. It returns a nested dictionary
    with the ENA header as outer key, NCBI header as inner key, and contig name as inner value. This
    dictionary is then passed back to make_alias_dictionary and returned.
    """

    alias_dict = {}

    try:
        with gzip.open(fasta, "rt") as file:
            alias_dict = process_fasta_headers(file, alias_dict)
            print(f"The file {fasta} is gzipped. Creating refNameAlias file...")
    except gzip.BadGzipFile:
        with open(fasta, "r") as file:
            alias_dict = process_fasta_headers(file, alias_dict)
            print(f"The file {fasta} is not gzipped. Creating refNameAlias file...")

    return alias_dict


def process_fasta_headers(file: str, alias_dict: dict) -> dict[str, dict[str, str]]:
    """
    Subfunction for make_alias_dictionary. Processes the fasta headers and extracts the ENA
    and NCBI headers, and, if present, the contig header. It raises an error if the fasta headers
    are not formatted in the ENA style. Returns a nested dictionary back to make_alias_dictionary.
    """
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
                raise ValueError
    return alias_dict


if __name__ == "__main__":
    args = parse_the_arguments()

    fasta = args.fasta

    if args.out is not None:
        alias_output = args.out
    else:
        alias_output = fasta + ".alias"

    # Read the ENA formated fasta file and generate dictionary with the aliases:
    try:
        alias_dict = make_alias_dictionary(fasta)
    except ValueError as e:
        print("""
              ERROR: This does not seem to be an ENA formatted fasta file.
              Please make sure that the file is not compressed and that the headers start with: ">ENA|".
              """)
        raise e

    # Write the alias dictionary to a tab-separated file:
    with open(alias_output, "w") as file:
        for outer_key, outer_value in alias_dict.items():
            for inner_key, inner_value in outer_value.items():
                aliases = "".join(f"{outer_key}\t{inner_key}\t{inner_value}\n")
                file.write(aliases)

    print("Wrote alias file to:", alias_output)
