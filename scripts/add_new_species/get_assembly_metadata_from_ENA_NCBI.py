"""
Submodule to get select genome assembly metadata from ENA and NCBI and store it in a dictionary.

The accession must be a GenBank assembly accession. NCBI RefSeq assembly accessions are not
accessible from/mirrored on ENA.

Notably, the ENA metadata lacks one field (assembly_type) that is present in the NCBI metadata.
Hence, this submodule queries both ENA and NCBI APIs to get the desired metadata fields.
"""

from xml.etree import ElementTree

import requests

ENA_API_XML_URL = r"https://www.ebi.ac.uk/ena/browser/api/xml"
NCBI_API_JSON_URL = "https://api.ncbi.nlm.nih.gov/datasets/v2/genome/accession"


def get_ena_assembly_metadata_xml(accession: str) -> dict:
    """
    Get the metadata from ENA for a given genome assembly accession
    and extract the name, assembly level, and genome representation fields.
    """
    url = f"{ENA_API_XML_URL}/{accession}"

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get metadata for {accession} from the ENA API. Response code: {response.status_code}"
        )

    tree = ElementTree.fromstring(response.content)

    name_element = tree.find(".//NAME")
    assembly_level_element = tree.find(".//ASSEMBLY_LEVEL")
    genome_representation_element = tree.find(".//GENOME_REPRESENTATION")

    return {
        "name": name_element.text.strip(),
        "assembly_level": assembly_level_element.text.strip(),
        "genome_representation": genome_representation_element.text.strip(),
    }


def get_ncbi_assembly_metadata_json(accession: str) -> dict:
    """
    Get the metadata from NCBI Datasets API for a given genome assembly accession
    and extract the assembly_type field that is needed for assembly.md.

    NB! The NCBI API returns a 200 OK status even for invalid accessions
    (tested with curl -i -X GET), so a different error handling is used
    here compared to the above function for the ENA API query.
    """
    url = f"{NCBI_API_JSON_URL}/{accession}/dataset_report"
    headers = {"accept": "application/json"}

    response = requests.get(url, headers=headers)

    ncbi_json = response.json()

    if not ncbi_json.get("reports"):
        raise Exception(f"No results found for accession {accession}. The accession may be invalid.")

    assembly_type = ncbi_json.get("reports", [{}])[0].get("assembly_info", {}).get("assembly_type")
    return assembly_type


def fetch_assembly_metadata(accession: str) -> dict:
    """
    Fetch assembly metadata from ENA and NCBI for a given GenBank genome assembly
    accession number. Return a dictionary that will be used to populate the YAML
    front matter in assembly.md and a few fields in config.yml.
    """
    assembly_metadata_dict = {}
    assembly_metadata_dict = get_ena_assembly_metadata_xml(accession)
    assembly_metadata_dict["assembly_type"] = get_ncbi_assembly_metadata_json(accession)

    return assembly_metadata_dict
