from pathlib import Path
from unittest.mock import patch

import pytest
from add_new_species.process_data_tracks_Excel import process_data_tracks_excel

OUTPUT_JSON_NAME = "data_tracks.json"


def test_process_data_tracks_excel_valid_accession(example_excel_files: dict[str, Path], temp_output_dir: Path) -> None:
    """
    Test for processing a Excel file without comments, that contains a valid genome assembly accession.
    """
    input_excel_file = example_excel_files["excel_form_wo_comments"]
    sheet_name = "Sheet1"
    output_json_file = temp_output_dir / OUTPUT_JSON_NAME

    genome_assembly_accession = process_data_tracks_excel(input_excel_file, temp_output_dir, sheet_name)

    assert output_json_file.exists(), "Output file was not created"
    assert genome_assembly_accession.startswith("GCA"), "Genome assembly accession does not start with 'GCA'"


@patch("add_new_species.process_data_tracks_Excel.extract_genome_accession", return_value=None)
def test_process_data_tracks_excel_missing_accession(
    mock_extract_genome_accession, example_excel_files: dict[str, Path], temp_output_dir: Path
) -> None:
    """
    Test for processing an Excel file with a missing genome assembly accession.
    It will fail because the accession is None (simulating empty cell in spreadsheet).
    """
    input_excel_file = example_excel_files["excel_form_wo_comments"]
    sheet_name = "Sheet1"

    with pytest.raises(ValueError, match="Genome assembly accession not found in the user spreadsheet"):
        process_data_tracks_excel(input_excel_file, temp_output_dir, sheet_name)


@patch("add_new_species.process_data_tracks_Excel.extract_genome_accession", return_value="GCF_000011425.1")
def test_process_data_tracks_excel_invalid_accession(
    mock_extract_genome_accession, example_excel_files: dict[str, Path], temp_output_dir: Path
) -> None:
    """
    Test for processing an Excel file with an invalid genome assembly accession.
    It will fail because the accession does not start with "GCA".
    """
    input_excel_file = example_excel_files["excel_form_wo_comments"]
    sheet_name = "Sheet1"

    with pytest.raises(ValueError, match="The accession in the user spreadsheet"):
        process_data_tracks_excel(input_excel_file, temp_output_dir, sheet_name)


def test_process_data_tracks_excel_with_comments(example_excel_files: dict[str, Path], temp_output_dir: Path) -> None:
    """
    Test for reading an Excel file with comments.
    It will fail because of Pandas not supporting that kind of XML.
    """
    input_excel_file = example_excel_files["excel_form_with_comments"]
    sheet_name = "Sheet1"

    with pytest.raises(ValueError, match="Unable to read workbook"):
        process_data_tracks_excel(input_excel_file, temp_output_dir, sheet_name)
