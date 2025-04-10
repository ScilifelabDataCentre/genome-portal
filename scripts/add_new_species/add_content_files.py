import warnings
from pathlib import Path

import requests

from add_new_species.constants import TEMPLATE_DIR
from add_new_species.get_taxonomy import EbiRestException, get_taxonomy, save_taxonomy_file

INDEX_FILE = "_index.md"
ASSEMBLY_FILE = "assembly.md"
DOWNLOAD_FILE = "download.md"
TAXONOMY_FILE = "taxonomy.json"
CONTENT_FILES = (INDEX_FILE, ASSEMBLY_FILE, DOWNLOAD_FILE)


def add_content_files(species_name: str, species_slug: str, content_dir_path: Path, data_dir_path: Path) -> None:
    """
    Use the template files to create the content files for the species.
    Template files are modified with the species specific information.
    """
    content_dir_path.mkdir(parents=False, exist_ok=True)
    tax_id = process_taxonomy(species_name, data_dir_path)

    for file_name in CONTENT_FILES:
        with open(TEMPLATE_DIR / file_name, "r") as file_in:
            template = file_in.read()

        template = template.replace("SPECIES_NAME", species_name)
        template = template.replace("SPECIES_FOLDER", species_slug)

        if file_name == INDEX_FILE:
            try:
                gbif_taxon_key = get_gbif_taxon_key(species_name=species_name)
                template = template.replace("GBIF_TAXON_ID", gbif_taxon_key)
            except (requests.exceptions.HTTPError, KeyError):
                print(
                    f"""WARNING: Failed to get GBIF key for species: {species_name}.
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


def process_taxonomy(species_name: str, data_dir_path: Path) -> str | None:
    """
    Try to get the taxonomy information for the specified species.
    If successful:
        - save the taxonomy.json file in the data directory.
        - return the tax_id.
    If unsuccessful, print a warning message and return None.
    """
    try:
        taxonomy_dict = get_taxonomy(species_name=species_name, template_file_path=TEMPLATE_DIR / TAXONOMY_FILE)
    except EbiRestException:
        warnings.warn(
            f"Failed to get taxonomy information for species: {species_name}. "
            "All other files will now be generated except this file.",
            stacklevel=2,
        )
        return None

    save_taxonomy_file(
        taxonomy_dict=taxonomy_dict,
        output_file_path=data_dir_path / TAXONOMY_FILE,
    )
    return taxonomy_dict["Species"]["tax_id"]


def get_gbif_taxon_key(species_name: str) -> str:
    """
    Get the GBIF "usageKey" / "taxonKey" given a species name.

    The "usageKey" is a unique identifier for the species in the GBIF database.
    """
    GBIF_ENDPOINT = r"https://api.gbif.org/v1/species/match?name="

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
