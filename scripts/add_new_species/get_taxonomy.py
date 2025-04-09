"""
This file is a module used in the script: "add_new_species.py".
It contains the function: "get_taxonomy",
which is used to get the taxonomy information for a species and save it to a JSON file.
It also returns the taxonomy id of the species as a string.

To do this, "get_taxonomy" does the following:
1) Obtains the taxonomy id (tax_id) for a species using the ENA REST API.
2) Uses this tax_id to get the full lineage information for each species which is only available in XML format.
    (The xml format includes the rank of each species which is why it is needed)
3) Saves the lineage information for each species into a JSON file which can be used by Hugo.

The script has one 3rd party library dependency (requests) which can be installed as follows:
$ python -m pip install requests

You should use a recent version of Python though (this was tested on Python 3.11).

### Output:
The .json file contains taxonomic information for the following levels:
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

FILE_NAME = "taxonomy.json"
TEMPLATE_FILE_PATH = Path(__file__).parent.parent / "templates" / FILE_NAME

TAXONOMIC_RANKS = [
    "genus",
    "family",
    "order",
    "class",
    "phylum",
    "kingdom",
    "superkingdom",
]


class EbiRestException(Exception):
    """
    Used when the EBI REST API fails to return a response
    or returns a response that we can't use
    """

    pass


def prep_out_dir(out_dir: str | None, species_name: str) -> Path:
    """
    If not defined, output dir built from species name.
    Makes the output folder if it doesn't exist, and returns a pathlib object.
    """
    if out_dir is None:
        folder_name = species_name.replace(" ", "_").lower()
        out_dir_path = Path(__file__).parent.parent / f"../hugo/data/{folder_name}"
    else:
        out_dir_path = Path(out_dir)

    if not out_dir_path.exists():
        Path.mkdir(out_dir_path)

    return out_dir_path


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


def append_lineage_info(species_dict: dict[str, dict[str, str]], lineage_section: str) -> dict[str, dict[str, str]]:
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
                    species_dict[tax_rank_caps]["science_name"] = name_match.group(1)

                taxid_match = re.search(r'taxId="([^"]*)"', line)
                if taxid_match:
                    tax_id = taxid_match.group(1)
                    species_dict[tax_rank_caps]["tax_id"] = tax_id
                    species_dict[tax_rank_caps]["ena_link"] = ENA_BASE_URL + tax_id
                    species_dict[tax_rank_caps]["ncbi_link"] = NCBI_BASE_URL + tax_id

    return species_dict


def get_taxonomy(species_name: str, output_dir: str = None, overwrite: bool = False) -> None:
    """
    Main process to get taxonomy info. Puts all components together.
    Output written to disk by default at: "hugo/data/[species_name]/taxonomy.json"

    Parameters
    ----------
    species_name : str
        The name of the species for which you want to retrieve taxonomy information.

    output_dir : str, optional
        The directory where you want to save the JSON files.
        You don't need to provide this unless debugging

    overwrite: bool, optional
        If set to True, The  JSON file can be overwritten. Default is False.

    Returns
    -------
    None
        The output is written to disk instead.


    Examples
    --------
    >>> get_taxonomy(species_name="Homo sapiens", overwrite=True)
    File created: /path/to/output/Homo_sapiens.json
    """
    out_dir_path = prep_out_dir(out_dir=output_dir, species_name=species_name)

    # build the output file path first so can check if file already exists
    output_file_path = Path(out_dir_path) / FILE_NAME

    if (not overwrite) and (output_file_path.exists()):
        raise FileExistsError(
            f"""A lineage file already exists for species: {species_name},
            Add the flag "--overwrite" to overwrite the file,"""
        )

    try:
        tax_id = get_tax_id(species_name)
    except EbiRestException as e:
        print(f"""The search for a taxonomy entry for the species: "{species_name}" failed.
            Please check the spelling of the species name.
            Error type is: {type(e).__name__}""")
        raise e

    # Create and populate the species dictionary
    with open(TEMPLATE_FILE_PATH, "r") as file:
        species_dict = json.load(file)

    species_dict["Species"]["science_name"] = species_name
    species_dict["Species"]["tax_id"] = tax_id
    species_dict["Species"]["ena_link"] = ENA_BASE_URL + tax_id
    species_dict["Species"]["ncbi_link"] = NCBI_BASE_URL + tax_id

    # get the lineage information for all the taxonomic ranks
    try:
        lineage_section = get_lineage_section(tax_id)
    except EbiRestException as e:
        print(f"""The lineage search for the species: "{species_name}" failed.
        Error type is: {type(e).__name__}""")
        raise e

    species_dict = append_lineage_info(species_dict=species_dict, lineage_section=lineage_section)

    with open(output_file_path, "w") as file:
        json.dump(species_dict, file, indent=4)

    print(f"File created: {output_file_path.resolve()}")

    return tax_id
