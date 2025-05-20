import json
from pathlib import Path

import pytest
from get_assembly_metadata_from_ENA_NCBI import extract_genome_accession
from process_data_tracks_Excel import parse_excel_file, populate_data_tracks_json


def test_parse_excel_file_with_comments(example_excel_files: dict[str, Path]) -> None:
    """
    Test that fails on processing a Excel file since the file contains comments.
    (The openpyxl library does not support such kind of XML.)
    """
    input_excel_file = example_excel_files["excel_form_with_comments"]
    sheet_name = "Sheet1"
    # list_of_dicts=parse_excel_file(input_excel_file, sheet_name)

    with pytest.raises(ValueError, match="Unable to read workbook"):
        parse_excel_file(input_excel_file, sheet_name)


def test_parse_excel_file_without_comments(example_excel_files: dict[str, Path]) -> None:
    """
    Test that successfully processes a Excel file since after all comments have been removed.
    """
    input_excel_file = example_excel_files["excel_form_wo_comments"]
    sheet_name = "Sheet1"
    list_of_dicts = parse_excel_file(input_excel_file, sheet_name)

    assert isinstance(list_of_dicts, list), "The output is not a list"


def test_extract_genome_accession_genbank_accession(user_data_tracks: list[dict]) -> None:
    """
    Test that sucessfully extracts the GenBank accession from a fixture that
    representes a list of dictionaries created from the Excel file with parse_excel_file().
    """

    genome_assembly_accession = extract_genome_accession(user_data_tracks)

    assert genome_assembly_accession == "GCA_000011425.1", "Genome assembly accession not found in the user spreadsheet"


def test_extract_genome_accession_not_genbank_accession(user_data_tracks: list[dict]) -> None:
    """
    Test that fails since the genome assembly accession is not a GenBank accession.
    (For fun, here we use the NCBI RefSeq accession for the equivalent strain found in GCA_000011425.1)
    """

    user_data_tracks[0]["accessionOrDOI"] = "GCF_000011425.1"

    with pytest.raises(
        ValueError, match="does not look like a GenBank genome assembly accession. It must start with 'GCA'"
    ):
        extract_genome_accession(user_data_tracks)


@pytest.mark.parametrize("invalid_value", ["", None, "[EDIT]"])
def test_extract_genome_accession_blank_accession(user_data_tracks: list[dict], invalid_value: str | None) -> None:
    """
    Test that fails on a missing genome assembly accession.
    (parametrize is technically overkill here since the function that creates user_data_tracks
    will currently always resort to the placeholder value "[EDIT]" if the spreadsheet is blank.)
    """

    user_data_tracks[0]["accessionOrDOI"] = invalid_value

    with pytest.raises(ValueError, match="Genome assembly accession not found in the user spreadsheet."):
        extract_genome_accession(user_data_tracks)


def test_populate_data_tracks_json(user_data_tracks: list[dict], tmp_path: Path) -> None:
    """
    Test that sucessfully creates a JSON file from the list of dictionaries
    """

    populate_data_tracks_json(user_data_tracks, tmp_path)

    temp_json_file_path = tmp_path / "data_tracks.json"

    assert temp_json_file_path.exists(), "Output file was not created"

    with open(temp_json_file_path, "r") as f:
        updated_json = json.load(f)
    assert len(updated_json) == len(
        user_data_tracks
    ), "The number of data tracks in the JSON file does not match the input data tracks list."
