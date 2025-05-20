from unittest.mock import MagicMock, patch

import pytest
from get_assembly_metadata_from_ENA_NCBI import (
    get_ena_assembly_metadata_xml,
    get_ncbi_assembly_metadata_json,
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
