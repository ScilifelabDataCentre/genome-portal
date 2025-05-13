import argparse
import gzip
from pathlib import Path


def parse_arguments():
    """
    Subfunction that runs argparse to set up and capture the arguments of the script.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--gff",
        required=True,
        type=str,
        metavar=".gff",
        help="""
        Input; the path to the .gff or .gff.gz file that is to be reformatted.
        """,
    )
    return parser.parse_args()


def make_gff_dicts(file: Path) -> dict:
    mRNA_attributes_nested_dict = {}
    for line in file:
        if line.startswith("#"):
            continue
        columns = line.strip().split("\t")
        if len(columns) < 9:
            continue
        col9 = columns[8]
        attributes_pair_list = col9.strip().split(";")
        attributes_flat_dict = dict(pair.split("=", 1) for pair in attributes_pair_list)

        if columns[2] == "mRNA" and "Parent" in attributes_flat_dict:
            mRNA_attributes_nested_dict[attributes_flat_dict["Parent"]] = attributes_flat_dict

    return mRNA_attributes_nested_dict


def rename_gff_name_field(file, mRNA_attributes_nested_dict: dict, output_file_path: Path) -> None:
    with open(output_file_path, "w") as output_file:
        for line in file:
            if line.startswith("#"):
                output_file.write(line)
                continue
            columns = line.strip().split("\t")
            if len(columns) < 9:
                output_file.write(line)
                continue
            col9 = columns[8]

            attr_pairs = [pair.split("=", 1) for pair in col9.split(";")]
            attributes = {key: value for key, value in attr_pairs}

            locus_tag = attributes.get("ID")
            if locus_tag in mRNA_attributes_nested_dict and "standard_name" in mRNA_attributes_nested_dict[locus_tag]:
                attributes["Name"] = mRNA_attributes_nested_dict[locus_tag]["standard_name"]

            columns[8] = ";".join(f"{k}={v}" for k, v in attributes.items())
            new_line = "\t".join(columns)
            output_file.write(new_line + "\n")


def main():
    args = parse_arguments()
    file_path = args.gff
    output_file_path = Path(file_path).with_suffix(".renamed.gff")
    if file_path.endswith(".gz"):
        with gzip.open(file_path, "rt") as file:
            mRNA_attributes_nested_dict = make_gff_dicts(file)
            file.seek(0)
            rename_gff_name_field(file, mRNA_attributes_nested_dict, output_file_path)
    else:
        with open(file_path, "r") as file:
            mRNA_attributes_nested_dict = make_gff_dicts(file)
            file.seek(0)
            rename_gff_name_field(file, mRNA_attributes_nested_dict, output_file_path)


if __name__ == "__main__":
    main()
