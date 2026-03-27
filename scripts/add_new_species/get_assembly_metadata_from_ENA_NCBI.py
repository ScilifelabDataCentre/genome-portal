"""
Submodule to get select genome assembly metadata from ENA and NCBI and store it in a dictionary.

The accession must be a GenBank assembly accession. NCBI RefSeq assembly accessions are not
accessible from/mirrored on ENA.

Notably, the ENA metadata lacks one field (assembly_type) that is present in the NCBI metadata.
Hence, this submodule queries both ENA and NCBI APIs to get the desired metadata fields.
"""

import re
from dataclasses import dataclass
from xml.etree import ElementTree

import requests

ENA_API_XML_URL = r"https://www.ebi.ac.uk/ena/browser/api/xml"
NCBI_API_JSON_URL = "https://api.ncbi.nlm.nih.gov/datasets/v2/genome/accession"
PLACEHOLDER_VALUE = "[EDIT]"
REQUEST_TIMEOUT = (5, 30)


@dataclass
class AssemblyMetadata:
    """
    Class to hold the genome assembly metadata.
    For use by the downstream functions.
    """

    assembly_name: str
    assembly_level: str
    genome_representation: str
    assembly_accession: str
    assembly_type: str
    species_name: str
    species_name_abbrev: str


class AssemblyMetadataApiException(Exception):
    """
    Raised when ENA/NCBI assembly metadata API calls fail or return unusable responses.
    """

    pass


class MissingGenomeAccessionError(ValueError):
    """
    Raised when assembly_CGA_accession is missing for the Genome row.
    """

    pass


def abbreviate_species_name(species_name: str) -> str:
    """
    Convert a species name to abbreviated form, e.g. 'Aspergillus nidulans' -> 'A. nidulans'.
    Falls back to the original value for single-word names.
    """
    species_name_words = species_name.split()
    if len(species_name_words) >= 2:
        return f"{species_name_words[0][0].upper()}. {species_name_words[1]}"
    if len(species_name_words) == 1:
        return species_name_words[0]
    return PLACEHOLDER_VALUE


def build_assembly_metadata(
    species_name: str,
    assembly_accession: str,
    assembly_name: str,
    assembly_level: str,
    genome_representation: str,
    assembly_type: str,
) -> AssemblyMetadata:
    """
    Construct AssemblyMetadata with consistently generated species abbreviation.
    Used for both the ENA/NCBI fetch and the placeholder metadata creation to ensure the same format.
    """
    return AssemblyMetadata(
        assembly_name=assembly_name,
        assembly_level=assembly_level,
        genome_representation=genome_representation,
        assembly_accession=assembly_accession,
        assembly_type=assembly_type,
        species_name=species_name,
        species_name_abbrev=abbreviate_species_name(species_name),
    )


def extract_genome_accession_or_placeholder(user_data_tracks: list[dict]) -> str:
    """
    Try to extract genome accession from tracks, otherwise return placeholder.
    """
    try:
        return extract_genome_accession(user_data_tracks)
    except (ValueError, AttributeError):
        return PLACEHOLDER_VALUE


def placeholder_assembly_metadata(user_data_tracks: list[dict], species_name: str) -> AssemblyMetadata:
    """
    Build placeholder assembly metadata when ENA/NCBI lookup is intentionally skipped.
    """
    return build_assembly_metadata(
        species_name=species_name,
        assembly_accession=extract_genome_accession_or_placeholder(user_data_tracks),
        assembly_name=PLACEHOLDER_VALUE,
        assembly_level=PLACEHOLDER_VALUE,
        genome_representation=PLACEHOLDER_VALUE,
        assembly_type=PLACEHOLDER_VALUE,
    )


def get_ena_assembly_metadata_xml(accession: str) -> dict:
    """
    Get the metadata from ENA for a given genome assembly accession
    and extract the name, assembly level, and genome representation fields.
    """
    url = f"{ENA_API_XML_URL}/{accession}"

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.RequestException as e:
        raise AssemblyMetadataApiException(f"Failed to query ENA metadata for {accession}: {e}") from e

    if response.status_code != 200:
        raise AssemblyMetadataApiException(
            f"Failed to get metadata for {accession} from the ENA API. Response code: {response.status_code}"
        )

    tree = ElementTree.fromstring(response.content)

    def required_xml_text(xpath: str, field_name: str) -> str:
        element = tree.find(xpath)

        if element is not None:
            text = element.text
        else:
            text = None

        if text is None or not text.strip():
            raise AssemblyMetadataApiException(
                f"ENA metadata for {accession} is missing required field '{field_name}' ({xpath})."
            )
        return text.strip()

    return {
        "assembly_name": required_xml_text(".//NAME", "assembly_name"),
        "assembly_level": required_xml_text(".//ASSEMBLY_LEVEL", "assembly_level"),
        "genome_representation": required_xml_text(".//GENOME_REPRESENTATION", "genome_representation"),
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

    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.RequestException as e:
        raise AssemblyMetadataApiException(f"Failed to query NCBI metadata for {accession}: {e}") from e

    try:
        ncbi_json = response.json()
    except ValueError as e:
        raise AssemblyMetadataApiException(f"Invalid JSON response from NCBI for {accession}: {e}") from e

    if not ncbi_json.get("reports"):
        raise AssemblyMetadataApiException(f"No results found for accession {accession}. The accession may be invalid.")

    reports = ncbi_json["reports"]
    assembly_type = reports[0]["assembly_info"]["assembly_type"]

    return assembly_type


def extract_genome_accession(user_data_tracks: list[dict]) -> str:
    """
    Extract the GenBank genome assembly accession from the dedicated
    'assembly_CGA_accession' spreadsheet column (stored in JSON as 'assemblyCGAAccession')
    for the 'Genome' data track.
    """
    for data_track in user_data_tracks:
        if data_track.get("dataTrackName") == "Genome":
            accession = data_track.get("assemblyCGAAccession")
            if accession in ("", None, PLACEHOLDER_VALUE):
                raise MissingGenomeAccessionError(
                    "Genome assembly accession is mandatory for ENA/NCBI metadata lookup. "
                    "Please populate 'assembly_CGA_accession' for the 'Genome' row, "
                    "or run with '--skip-assembly-metadata-fetch' if no GCA accession is available."
                )
            if isinstance(accession, str) and accession.startswith("GCA"):
                return accession
            raise ValueError(
                f"'{accession}' does not look like a GenBank genome assembly accession. It must start with 'GCA'."
            )
    raise MissingGenomeAccessionError(
        "Genome assembly accession is mandatory for ENA/NCBI metadata lookup. "
        "Please populate 'assembly_CGA_accession' for the 'Genome' row, "
        "or run with '--skip-assembly-metadata-fetch' if no GCA accession is available."
    )


def fetch_assembly_metadata(user_data_tracks: dict, species_name: str) -> AssemblyMetadata:
    """
    Fetch assembly metadata from ENA and NCBI for a given GenBank genome assembly
    accession number. Return a dictionary that will be used to populate the YAML
    front matter in assembly.md and a few fields in config.yml.
    """
    accession = extract_genome_accession(user_data_tracks)

    partial_metadata_dict = get_ena_assembly_metadata_xml(accession)
    assembly_type = get_ncbi_assembly_metadata_json(accession)

    return build_assembly_metadata(
        species_name=species_name,
        assembly_accession=accession,
        assembly_name=partial_metadata_dict["assembly_name"],
        assembly_level=partial_metadata_dict["assembly_level"],
        genome_representation=partial_metadata_dict["genome_representation"],
        assembly_type=assembly_type,
    )


def extract_accession_from_url(url: str) -> str | None:
    """
    Extract a GenBank accession (GCA_xxxxxxx.x) from ENA/NCBI/DOI URLs.

    ENA genome accession example: https://www.ebi.ac.uk/ena/browser/view/GCA_963668995.1
    DOI pattern example: https://doi.org/10.17044/scilifelab.28606814.v1
    """

    acession_match = re.search(r"(GCA_\d+\.\d+)", url)
    if acession_match:
        return acession_match.group(1)

    doi_match = re.search(r"doi\.org/([\w\.\-/]+)", url)
    if doi_match:
        return doi_match.group(1)
    return None
