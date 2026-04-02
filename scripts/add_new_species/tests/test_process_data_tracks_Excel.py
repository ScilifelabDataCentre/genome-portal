import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest
from get_assembly_metadata_from_ENA_NCBI import MissingGenomeAccessionError, extract_genome_accession
from process_data_tracks_Excel import (
    EXPECTED_EXCEL_COLUMNS,
    df_row_to_json,
    parse_excel_file,
    populate_data_tracks_json,
    validate_excel_columns,
)


def test_parse_excel_file_with_comments(example_excel_files: dict[str, Path]) -> None:
    """
    Test that fails on processing a Excel file since the file contains comments.
    (The openpyxl library does not support such kind of XML.)
    """
    input_excel_file = example_excel_files["excel_form_with_comments"]
    sheet_name = "Sheet1"
    # list_of_dicts=parse_excel_file(input_excel_file, sheet_name)

    with pytest.raises(
        ValueError, match="Your spreadsheet likely contains comments/invalid XML. Remove comments and re-run."
    ):
        parse_excel_file(input_excel_file, sheet_name)


def test_parse_excel_file_without_comments(example_excel_files: dict[str, Path]) -> None:
    """
    Test that successfully processes a Excel file since after all comments have been removed.
    """
    input_excel_file = example_excel_files["excel_form_wo_comments"]
    sheet_name = "Sheet1"
    list_of_dicts = parse_excel_file(input_excel_file, sheet_name)

    assert isinstance(list_of_dicts, list), "The output is not a list"


def test_validate_excel_columns_missing_required_column() -> None:
    """
    Test that missing required columns fail validation.
    """

    columns = list(EXPECTED_EXCEL_COLUMNS - {"principal_investigator_name"})

    df = pd.DataFrame(columns=columns)

    with pytest.raises(ValueError, match="Invalid columns in data tracks sheet"):
        validate_excel_columns(df)


def test_validate_excel_columns_rejects_unexpected_column() -> None:
    """
    Test that unexpected columns are rejected.
    """
    columns = list(EXPECTED_EXCEL_COLUMNS) + ["added_extra_column"]
    df = pd.DataFrame(columns=columns)

    with pytest.raises(ValueError, match="Invalid columns in data tracks sheet"):
        validate_excel_columns(df)


def test_validate_excel_columns_rejects_case_and_whitespace_variants() -> None:
    """
    Test that non-exact column variants are rejected.
    """

    columns = list(EXPECTED_EXCEL_COLUMNS - {"data_track_name"}) + [" Data Track Name "]

    df = pd.DataFrame(columns=columns)

    with pytest.raises(ValueError, match="Invalid columns in data tracks sheet"):
        validate_excel_columns(df)


def test_df_row_to_json_sets_default_first_date_on_portal_format(data_tracks_template_json: str) -> None:
    """
    Test that missing firstDateOnPortal is set to format: dd Month yyyy.
    """
    row = pd.Series({"data_track_name": "Genome"})

    output = df_row_to_json(row, data_tracks_template_json)
    datetime.strptime(output["firstDateOnPortal"], "%d %B %Y")


def test_df_row_to_json_uses_assembly_GCA_accession_for_genome(data_tracks_template_json: str) -> None:
    """
    Test that Genome track accession is taken from assembly_GCA_accession, not DOI URL parsing.
    """
    row = pd.Series(
        {
            "data_track_name": "Genome",
            "assembly_GCA_accession": "GCA_000011425.1",
            "doi_link_to_repository": "https://doi.org/10.17044/example",
        }
    )

    output = df_row_to_json(row, data_tracks_template_json)

    assert output["assemblyGCAAccession"] == "GCA_000011425.1"
    assert output["accessionOrDOI"] == "GCA_000011425.1"


def test_df_row_to_json_does_not_set_accession_from_doi_for_non_genome(data_tracks_template_json: str) -> None:
    """
    Test that doi_link_to_repository is ingested as Website only and not converted to accessionOrDOI.
    """
    row = pd.Series(
        {
            "data_track_name": "Repeats",
            "doi_link_to_repository": "https://doi.org/10.17044/example",
        }
    )

    output = df_row_to_json(row, data_tracks_template_json)

    assert output["links"][1]["Website"] == "https://doi.org/10.17044/example"
    assert output["accessionOrDOI"] == "[EDIT]"


def test_df_row_to_json_ingests_optional_busco_stats(data_tracks_template_json: str) -> None:
    row = pd.Series(
        {
            "data_track_name": "Genome",
            "BUSCO_stats": "C:99% [S:97.8%, D:1.2%], F:0.2%, M:0.8%, n:5286 (lepidoptera_odb10)",
        }
    )
    output = df_row_to_json(row, data_tracks_template_json)
    assert output["buscoStats"] == "C:99% [S:97.8%, D:1.2%], F:0.2%, M:0.8%, n:5286 (lepidoptera_odb10)"


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

    user_data_tracks[0]["assemblyGCAAccession"] = "GCF_000011425.1"

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

    user_data_tracks[0]["assemblyGCAAccession"] = invalid_value

    with pytest.raises(
        MissingGenomeAccessionError, match="Genome assembly accession is mandatory for ENA/NCBI metadata lookup."
    ):
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
