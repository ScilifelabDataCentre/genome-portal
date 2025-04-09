from pathlib import Path

import pytest
from add_new_species.process_data_tracks_Excel import generate_data_tracks_json

OUTPUT_JSON_NAME = "output_data_tracks.json"


def test_generate_data_tracks_json(example_excel_files: dict[str, Path], temp_output_dir) -> None:
    """
    Test the generation of a JSON file from a valid Excel file.
    """
    input_excel_file = example_excel_files["excel_form_wo_comments"]
    sheet_name = "Sheet1"
    output_json_file = temp_output_dir / OUTPUT_JSON_NAME

    # Call the function to generate the JSON file
    generate_data_tracks_json(input_excel_file, sheet_name, output_json_file)

    # Assert that the output file exists
    assert output_json_file.exists(), "Output file was not created"


def test_fails_with_comments_in_excel_file(example_excel_files: dict[str, Path], temp_output_dir) -> None:
    """
    Test reading an Excel file with comments. It will fail because of Pandas not supporting that kind of XML.
    """
    input_excel_file = example_excel_files["excel_form_with_comments"]
    sheet_name = "Sheet1"
    output_json_file = temp_output_dir / OUTPUT_JSON_NAME

    with pytest.raises(ValueError, match="Error reading Excel file:"):
        generate_data_tracks_json(input_excel_file, sheet_name, output_json_file)
