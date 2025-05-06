"""
Submodule to get select genome assembly metadata from ENA and NCBI and store it in a dictionary.

The accession must be a GenBank assembly accession. NCBI RefSeq assembly accessions are not
accessible from/mirrored on ENA.

Notably, the ENA metadata lacks one field (assembly_type) that is present in the NCBI metadata.
Hence, this submodule queries both ENA and NCBI APIs to get the desired metadata fields.
"""

from typing import Optional
from xml.etree import ElementTree

import requests
from attr import dataclass

ENA_API_XML_URL = r"https://www.ebi.ac.uk/ena/browser/api/xml"
NCBI_API_JSON_URL = "https://api.ncbi.nlm.nih.gov/datasets/v2/genome/accession"


@dataclass
class AssemblyMetadata:
    """
    Class to hold the genome assembly metadata.
    For use by the downstream functions.
    """

    assembly_name: str
    assembly_level: str
    genome_representation: str
    accession: str
    assembly_type: Optional[str] = None
    species_name: Optional[str] = None
    species_name_abbrev: Optional[str] = None


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

    return AssemblyMetadata(
        assembly_name=name_element.text.strip(),
        assembly_level=assembly_level_element.text.strip(),
        genome_representation=genome_representation_element.text.strip(),
        accession=accession,
    )


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


def extract_genome_accession(data_tracks_list_of_dicts: list[dict]) -> str:
    """
    Extract the value of 'accessionOrDOI' for the top-level key 'Genome' from the list of dictionaries.
    """

    genome_assembly_accession = None
    for data_track in data_tracks_list_of_dicts:
        if data_track.get("dataTrackName") == "Genome":
            genome_assembly_accession = data_track.get("accessionOrDOI", None)
            break
    if genome_assembly_accession is None:
        raise ValueError(
            "Genome assembly accession not found in the user spreadsheet. Please check the field is not empty."
        )
    if not genome_assembly_accession.startswith("GCA"):
        raise ValueError(
            f"The accession in the user spreadsheet, {genome_assembly_accession}, "
            "does not look like a GenBank genome assembly accession. It must start with 'GCA'."
        )

    return genome_assembly_accession


def fetch_assembly_metadata(data_tracks_list_of_dicts: dict, species_name: str) -> dict:
    """
    Fetch assembly metadata from ENA and NCBI for a given GenBank genome assembly
    accession number. Return a dictionary that will be used to populate the YAML
    front matter in assembly.md and a few fields in config.yml.
    """
    accession = extract_genome_accession(data_tracks_list_of_dicts)

    assembly_metadata = get_ena_assembly_metadata_xml(accession)
    assembly_metadata.assembly_type = get_ncbi_assembly_metadata_json(accession)

    species_name_words = species_name.split()
    species_name_abbrev = f"{species_name_words[0][0].upper()}. {species_name_words[1]}"
    assembly_metadata.species_name = species_name
    assembly_metadata.species_name_abbrev = species_name_abbrev

    return assembly_metadata
