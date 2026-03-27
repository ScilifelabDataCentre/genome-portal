from unittest.mock import MagicMock, patch

import pytest
from get_assembly_metadata_from_ENA_NCBI import (
    build_assembly_metadata,
    get_ena_assembly_metadata_xml,
    get_ncbi_assembly_metadata_json,
    placeholder_assembly_metadata,
)

VALID_ACCESSION = "GCA_000011425.1"
INVALID_ACCESSION = "GCA_000011425.9"


@patch("get_assembly_metadata_from_ENA_NCBI.requests.get")
def test_get_ena_assembly_metadata_xml_mock_valid_accession(mock_get: MagicMock):
    """
    Test sucessfully calls get_ena_assembly_metadata_xml with a valid accession.
    """
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = """
    <ASSEMBLY_SET>
        <ASSEMBLY accession="GCA_000011425.1" alias="ASM1142v1">
            <NAME>ASM1142v1</NAME>
            <ASSEMBLY_LEVEL>Chromosome</ASSEMBLY_LEVEL>
            <GENOME_REPRESENTATION>full</GENOME_REPRESENTATION>
        </ASSEMBLY>
    </ASSEMBLY_SET>
    """
    result = get_ena_assembly_metadata_xml(VALID_ACCESSION)

    assert mock_get.return_value.status_code == 200
    assert isinstance(result, dict)
    assert result["assembly_name"] == "ASM1142v1"
    assert result["assembly_level"] == "Chromosome"
    assert result["genome_representation"] == "full"


@patch("get_assembly_metadata_from_ENA_NCBI.requests.get")
def test_get_ena_assembly_metadata_xml_mock_invalid_accession(mock_get: MagicMock):
    """
    Test that fails get_ena_assembly_metadata_xml with an invalid accession.
    """
    mock_get.return_value.status_code = 404

    with pytest.raises(Exception, match="Failed to get metadata"):
        get_ena_assembly_metadata_xml(INVALID_ACCESSION)


@patch("get_assembly_metadata_from_ENA_NCBI.requests.get")
def test_get_ncbi_assembly_metadata_json_mock_valid_accession(mock_get: MagicMock):
    """
    Test sucessfully calls get_ncbi_assembly_metadata_json with a valid accession.
    """
    mock_get.return_value.json.return_value = {"reports": [{"assembly_info": {"assembly_type": "haploid"}}]}
    result = get_ncbi_assembly_metadata_json(VALID_ACCESSION)
    assert result


@patch("get_assembly_metadata_from_ENA_NCBI.requests.get")
def test_test_get_ncbi_assembly_metadata_json_mock_invalid_accession(mock_get: MagicMock):
    """
    Test that fails get_ncbi_assembly_metadata_json with an invalid accession.
    """
    mock_get.return_value.json.return_value = {"reports": []}

    with pytest.raises(ValueError, match="No results found for accession"):
        get_ncbi_assembly_metadata_json(INVALID_ACCESSION)


def test_placeholder_assembly_metadata_with_extractable_accession() -> None:
    """
    Test that placeholder metadata keeps a valid GCA accession from assemblyCGAAccession.
    """
    user_data_tracks = [
        {
            "dataTrackName": "Genome",
            "assemblyCGAAccession": "GCA_000011425.1",
        }
    ]

    metadata = placeholder_assembly_metadata(user_data_tracks=user_data_tracks, species_name="Aspergillus nidulans")

    assert metadata.assembly_accession == "GCA_000011425.1"
    assert metadata.assembly_name == "[EDIT]"
    assert metadata.assembly_level == "[EDIT]"
    assert metadata.genome_representation == "[EDIT]"
    assert metadata.assembly_type == "[EDIT]"
    assert metadata.species_name_abbrev == "A. nidulans"


def test_placeholder_assembly_metadata_without_extractable_accession() -> None:
    """
    Test that placeholder metadata falls back to [EDIT] accession when it is missing.
    """
    user_data_tracks = [
        {
            "dataTrackName": "Genome",
            "assemblyCGAAccession": "",
        }
    ]

    metadata = placeholder_assembly_metadata(user_data_tracks=user_data_tracks, species_name="Aspergillus nidulans")

    assert metadata.assembly_accession == "[EDIT]"


def test_build_assembly_metadata_sets_expected_fields() -> None:
    """
    Test that the shared metadata builder populates all fields and species abbreviation.
    """
    metadata = build_assembly_metadata(
        "Aspergillus nidulans",
        "GCA_000011425.1",
        "ASM1142v1",
        "Chromosome",
        "full",
        "haploid",
    )

    assert metadata.species_name == "Aspergillus nidulans"
    assert metadata.species_name_abbrev == "A. nidulans"
    assert metadata.assembly_accession == "GCA_000011425.1"
    assert metadata.assembly_name == "ASM1142v1"
    assert metadata.assembly_level == "Chromosome"
    assert metadata.genome_representation == "full"
    assert metadata.assembly_type == "haploid"
