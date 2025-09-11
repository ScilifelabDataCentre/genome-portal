"""
This module is used to get the taxonomy information for a species and store it as a dictionary.

There are two primary functions in this module that are used by add_new_species.
- get_taxonomy - get the taxonomy information for a species and store it as a dictionary.
- save_taxonomy_file - save the taxonomy information to a JSON file.

### Overview of what get_taxonomy() does:
1) Obtains the taxonomy id (tax_id) for a species using the ENA REST API.
2) Uses this tax_id to get the full lineage information for each species which is only available in XML format.
    (The xml format includes the rank of each species which is why it is needed)
3) Stores the lineage information in a dictionary, ready to be saved to a JSON file.

### The dictionary contains taxonomic information for the following levels:
- Superkingdom (Domain)
- Kingdom
- Phylum
- Class
- Order
- Family
- Genus
- Species
"""

import json
import re
from pathlib import Path
from xml.etree import ElementTree

import requests

ENDPOINT_URL = r"https://www.ebi.ac.uk/ena/taxonomy/rest/scientific-name"
ENA_XML_URL = r"https://www.ebi.ac.uk/ena/browser/api/xml"
ENA_BASE_URL = r"https://www.ebi.ac.uk/ena/browser/view/Taxon:"
NCBI_BASE_URL = r"https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id="

TAXONOMIC_RANKS = [
    "genus",
    "family",
    "order",
    "class",
    "phylum",
    "kingdom",
    "domain",
]


class EbiRestException(Exception):
    """
    Used when the EBI REST API fails to return a response
    or returns a response that we can't use
    """

    pass


def create_endpoint_url(scientific_name: str) -> str:
    """
    Create the endpoint URL for the given scientific name.
    """
    return f"{ENDPOINT_URL}/{scientific_name.replace(' ', '%20')}"


def get_tax_id(scientific_name: str) -> str:
    """
    Get the taxonomy id from the scientific name.
    Search by name is case insensitive.

    Returns the taxonomy id as a string.
    """
    url = create_endpoint_url(scientific_name)
    response = requests.get(url)

    if response.status_code != 200:
        raise EbiRestException(
            f"Failed to get taxonomy info for {scientific_name}, response code: {response.status_code}"
        )

    response_json = response.json()

    if len(response_json) == 0:
        raise EbiRestException(f"No taxonomy info found for {scientific_name}")

    if len(response_json) > 1:
        raise EbiRestException(f"Multiple taxonomy results found for {scientific_name}")

    full_taxon_info = response_json[0]

    return str(full_taxon_info["taxId"])


def get_lineage_section(tax_id: str | int) -> str:
    """
    Obtain the taxonomy information for a species using the taxonomy id.
    This returns the lineage section of the XML response as a string.
    """
    try:
        ena_url = f"{ENA_XML_URL}/{str(tax_id)}"
        response = requests.get(ena_url)
    except requests.exceptions.RequestException as e:
        raise EbiRestException from e(
            f"""Failed to get lineage info for tax_id: {str(tax_id)}.
            Error is as follows:
            {e}"""
        )

    tree = ElementTree.fromstring(response.content)
    lineage_element = tree.find(".//lineage")
    lineage_section = ElementTree.tostring(lineage_element).decode()

    return lineage_section


def append_lineage_info(taxonomy_dict: dict[str, dict[str, str]], lineage_section: str) -> dict[str, dict[str, str]]:
    """
    Add lineage information to each species.
    Each species has a dictionary with the form shown in: TEMPLATE_LINEAGE_DICT

    This function appends lineage information to this dictionary
    and returns the updated dictionary.
    """
    for line in lineage_section.split("\n"):
        for tax_rank in TAXONOMIC_RANKS:
            tax_rank_caps = tax_rank.capitalize()

            rank = rf'rank="{tax_rank}"'
            if rank in line:
                name_match = re.search(r'scientificName="([^"]*)"', line)
                if name_match:
                    taxonomy_dict[tax_rank_caps]["science_name"] = name_match.group(1)

                taxid_match = re.search(r'taxId="([^"]*)"', line)
                if taxid_match:
                    tax_id = taxid_match.group(1)
                    taxonomy_dict[tax_rank_caps]["tax_id"] = tax_id
                    taxonomy_dict[tax_rank_caps]["ena_link"] = ENA_BASE_URL + tax_id
                    taxonomy_dict[tax_rank_caps]["ncbi_link"] = NCBI_BASE_URL + tax_id

    return taxonomy_dict


def get_taxonomy(species_name: str, template_file_path: Path) -> dict[str, dict[str, str]]:
    """
    Main process to get taxonomy info. Puts all components together.

    Parameters
    ----------
    species_name : str
        The name of the species for which you want to retrieve taxonomy information.

    template_file_path : Path
        Path to the template json formated file used to build the output.

    Returns
    -------
    dict
        A dictionary containing the taxonomy information for the species.
    """
    try:
        tax_id = get_tax_id(species_name)
    except EbiRestException as e:
        print(f"""The search for a taxonomy entry for the species: "{species_name}" failed.
            Please check the spelling of the species name.
            Error type is: {type(e).__name__}""")
        raise e

    # Create and populate the species dictionary
    with open(template_file_path, "r") as file:
        taxonomy_dict = json.load(file)

    taxonomy_dict["Species"]["science_name"] = species_name
    taxonomy_dict["Species"]["tax_id"] = tax_id
    taxonomy_dict["Species"]["ena_link"] = ENA_BASE_URL + tax_id
    taxonomy_dict["Species"]["ncbi_link"] = NCBI_BASE_URL + tax_id

    # get the lineage information for all the taxonomic ranks
    try:
        lineage_section = get_lineage_section(tax_id)
    except EbiRestException as e:
        print(f"""The lineage search for the species: "{species_name}" failed.
        Error type is: {type(e).__name__}""")
        raise e

    taxonomy_dict = append_lineage_info(taxonomy_dict=taxonomy_dict, lineage_section=lineage_section)
    return taxonomy_dict


def save_taxonomy_file(taxonomy_dict: dict[str, dict[str, str]], output_file_path: Path) -> None:
    """
    Save a generated taxonomy.json file for the species.
    """
    with open(output_file_path, "w") as file:
        json.dump(taxonomy_dict, file, indent=4)
    print(f"File created: {output_file_path.resolve()}")
