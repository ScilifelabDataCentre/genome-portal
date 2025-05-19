import warnings
from datetime import datetime
from pathlib import Path

import requests
from form_parser import UserFormData
from get_assembly_metadata_from_ENA_NCBI import AssemblyMetadata
from get_taxonomy import EbiRestException, get_taxonomy, save_taxonomy_file
from template_handler import process_template_file

TEMPLATE_DIR = Path(__file__).parent / "templates"
INDEX_FILE = "_index.md"
ASSEMBLY_FILE = "assembly.md"
DOWNLOAD_FILE = "download.md"
TAXONOMY_FILE = "taxonomy.json"


def add_index_md(
    user_form_data: UserFormData,
    content_dir_path: Path,
    data_dir_path: Path,
) -> None:
    """
    Use the template _index.md file to create the _index.md file for the species.
    Template files are modified with the species specific information.
    """
    template_file_path = TEMPLATE_DIR / INDEX_FILE
    output_file_path = content_dir_path / INDEX_FILE

    todays_date = datetime.now().strftime("%d/%m/%Y")
    species_name = user_form_data.species_name
    try:
        gbif_taxon_id = get_gbif_taxon_key(species_name=species_name)
    except (requests.exceptions.HTTPError, KeyError):
        gbif_taxon_id = None
        warnings.warn(
            f"Failed to get GBIF key for species: {species_name}. "
            "Not to worry, you can instead add it manually to the _index.md file in the species directory.",
            stacklevel=2,
        )

    tax_id = process_taxonomy(species_name, data_dir_path)
    if tax_id:
        goat_webpage = make_goat_weblink(species_name=species_name, tax_id=tax_id)
    else:
        goat_webpage = None

    process_template_file(
        template_file_path=template_file_path,
        output_file_path=output_file_path,
        required_replacements={
            "species_name": species_name,
            "species_slug": user_form_data.species_slug,
            "common_name": user_form_data.common_name,
            "description": user_form_data.description,
            "references": user_form_data.references,
            "publication": user_form_data.publication,
            "img_attrib_text": user_form_data.img_attrib_text,
            "img_attrib_link": user_form_data.img_attrib_link,
            "todays_date": todays_date,
        },
        optional_replacements={"gbif_taxon_id": gbif_taxon_id, "goat_webpage": goat_webpage},
    )


def add_assembly_md(user_form_data: UserFormData, assembly_metadata: AssemblyMetadata, content_dir_path: Path) -> None:
    """
    Use the template assembly.md file to create the assembly.md file for the species.
    Template files are modified with the species specific information.
    """
    template_file_path = TEMPLATE_DIR / ASSEMBLY_FILE
    output_file_path = content_dir_path / ASSEMBLY_FILE

    process_template_file(
        template_file_path=template_file_path,
        output_file_path=output_file_path,
        required_replacements={
            "species_name": user_form_data.species_name,
            "species_slug": user_form_data.species_slug,
            "funding": user_form_data.funding,
            "publication": user_form_data.publication,
            "assembly_name": assembly_metadata.assembly_name,
            "assembly_type": assembly_metadata.assembly_type,
            "assembly_level": assembly_metadata.assembly_level,
            "genome_representation": assembly_metadata.genome_representation,
            "assembly_accession": assembly_metadata.assembly_accession,
        },
    )


def add_download_md(
    species_slug: str,
    content_dir_path: Path,
) -> None:
    """
    Use the template download.md file to create the download.md file for the species.
    Template files are modified with the species specific information.
    """
    template_file_path = TEMPLATE_DIR / DOWNLOAD_FILE
    output_file_path = content_dir_path / DOWNLOAD_FILE

    process_template_file(
        template_file_path=template_file_path,
        output_file_path=output_file_path,
        required_replacements={
            "species_slug": species_slug,
        },
    )


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
