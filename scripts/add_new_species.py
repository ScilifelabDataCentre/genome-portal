"""
Use this script to create a new species entry for the website.

This script will create new folders in the Hugo content, data and assets directories.
Then template files for these directories will be added which can be filled in.
Places to fill in will be marked with: "[EDIT]"
"""

import argparse
import shutil
from pathlib import Path

import requests
from get_taxonomy import EbiRestException, get_taxonomy

TEMPLATE_DIR = Path(__file__).parent / "templates"

INDEX_FILE = "_index.md"
ASSEMBLY_FILE = "assembly.md"
DOWNLOAD_FILE = "download.md"
CONTENT_FILES = (INDEX_FILE, ASSEMBLY_FILE, DOWNLOAD_FILE)

STATS_FILE = "species_stats.yml"
DATA_FILES = (STATS_FILE,)

LINEAGE_FILE = "lineage.json"
DATA_TRACKS_FILE = "data_tracks.json"


GBIF_ENDPOINT = r"https://api.gbif.org/v1/species/match?name="


def run_argparse() -> argparse.Namespace:
    """
    Run argparse and return the user arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        "--species_name",
        type=str,
        metavar="[species name]",
        help="""The scientific name of the species to be added.
            Case sensitive. Wrap the name in quotes.""",
        required=True,
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="""If the files for the species already exist, should they be overwritten?
            If flag NOT provided, no overwrite performed.""",
    )

    return parser.parse_args()


def create_dirs(dir_name: str) -> tuple[Path, Path, Path]:
    """
    Create the content, data and assets directories for a species (inside Hugo).

    Return each of their locations as pathlib objects.
    """
    content_dir_path = Path(__file__).parent / f"../hugo/content/species/{dir_name}"
    content_dir_path.mkdir(parents=False, exist_ok=True)

    data_dir_path = Path(__file__).parent / f"../hugo/data/{dir_name}"
    data_dir_path.mkdir(parents=False, exist_ok=True)

    assets_dir_path = Path(__file__).parent / f"../hugo/assets/{dir_name}"
    assets_dir_path.mkdir(parents=False, exist_ok=True)

    return content_dir_path, data_dir_path, assets_dir_path


def add_content_files(species_name: str, content_dir_path: Path, tax_id: str) -> None:
    """
    Add the species name to the template content files,
    then write them to disk.
    """
    dir_name = species_name.replace(" ", "_").lower()
    for file_name in CONTENT_FILES:
        with open(TEMPLATE_DIR / file_name, "r") as file_in:
            template = file_in.read()

        template = template.replace("SPECIES_NAME", species_name)
        template = template.replace("SPECIES_FOLDER", dir_name)

        if file_name == INDEX_FILE:
            try:
                gbif_taxon_key = get_gbif_taxon_key(species_name=species_name)
                template = template.replace("GBIF_TAXON_ID", gbif_taxon_key)
            except (requests.exceptions.HTTPError, KeyError):
                print(
                    f"""WARNING: Failed to get GBIF key for species: {args.species_name}.
                    Not to worry,
                    you can instead add it manually to the _index.md file in the species directory."""
                )
                template = template.replace("GBIF_TAXON_ID", "[EDIT]")

            if tax_id:
                goat_link = make_goat_weblink(species_name=species_name, tax_id=tax_id)
                template = template.replace("GOAT_WEBPAGE", goat_link)
            else:
                template = template.replace("GOAT_WEBPAGE", "[EDIT]")

        output_file_path = content_dir_path / file_name

        with open(output_file_path, "w") as file_out:
            file_out.write(template)
        print(f"File created: {output_file_path.resolve()}")


def add_stats_file(data_dir_path: Path) -> None:
    """
    Add the species name to the template data files,
    then write them to disk.
    """
    for file_name in DATA_FILES:
        template_file_path = TEMPLATE_DIR / file_name
        output_file_path = data_dir_path / file_name
        shutil.copy(template_file_path, output_file_path)
        print(f"File created: {output_file_path.resolve()}")


def add_data_tracks_json(assets_dir_path: Path) -> None:
    """
    The download page of each species contains an info table about each of the data tracks avaialble.
    This function creates a template JSON file (to fill in) for this table.
    This file is stored in the assets folder and at build time, a duplicate it placed in the static folder.
    """
    template_file_path = TEMPLATE_DIR / DATA_TRACKS_FILE
    output_file_path = assets_dir_path / DATA_TRACKS_FILE
    shutil.copy(template_file_path, output_file_path)
    print(f"File created: {output_file_path.resolve()}")


def get_gbif_taxon_key(species_name: str) -> str:
    """
    Get the GBIF "usageKey" / "taxonKey" given a species name.

    The "usageKey" is a unique identifier for the species in the GBIF database.
    """
    species_name = species_name.replace(" ", "%20").lower()
    url = f"{GBIF_ENDPOINT}{species_name}"
    response = requests.get(url)
    response.raise_for_status()
    return str(response.json()["usageKey"])


def make_goat_weblink(species_name: str, tax_id: str | int) -> str:
    """
    Return the webpage to the GOAT database for a specific species.
    """
    species_name = species_name.replace(" ", "%20").lower()
    return rf"https://goat.genomehubs.org/record?recordId={str(tax_id)}&result=taxon&taxonomy=ncbi#{species_name}"


if __name__ == "__main__":
    args = run_argparse()

    dir_name = args.species_name.replace(" ", "_").lower()
    content_dir_path, data_dir_path, assets_dir_path = create_dirs(dir_name)

    if (not args.overwrite) and ((content_dir_path / INDEX_FILE).exists()):
        raise FileExistsError(
            f"""
            It appears that a species entry already exists for: "{args.species_name}",
            If you are sure you want to overwrite these files, add the flag "--overwrite".
            Exiting..."""
        )

    print("Retriveing taxonomy information, this shouldn't take more than a minute...")
    try:
        tax_id = get_taxonomy(species_name=args.species_name, overwrite=args.overwrite)
    except EbiRestException:
        tax_id = None
        print(
            f"""WARNING: Failed to get taxonomy information for species: {args.species_name}
            All other files will now be generated except this file"""
        )

    add_stats_file(data_dir_path=data_dir_path)
    add_data_tracks_json(assets_dir_path=assets_dir_path)
    add_content_files(species_name=args.species_name, content_dir_path=content_dir_path, tax_id=tax_id)
