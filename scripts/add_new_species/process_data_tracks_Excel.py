"""
Submodule to read the data tracks Excel form (.xlsx) and populate the data_tracks.json.

The Excel files cannot contain comments.

Dependencies:
pip install pandas
pip install openpyxl

"""

import json
from pathlib import Path

import pandas as pd

JSON_TEMPLATE_FILE_NAME = "data_tracks.json"
TEMPLATE_FILE_PATH = Path(__file__).parent.parent / "templates" / JSON_TEMPLATE_FILE_NAME


def read_excel_file(file_path: Path, sheet_name: str) -> pd.DataFrame:
    """
    Read the Excel file and return a DataFrame.
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")
        return df
    except ValueError as e:
        raise ValueError(f"Error reading Excel file: {e}") from e


def row_to_json(row: pd.Series, template_json: str) -> dict:
    """
    Convert a row of the DataFrame to a JSON object using the JSON template.
    """
    # Reinitialize the data_track dict for each row by parsing the JSON string for each row
    data_track = json.loads(template_json)

    # Update the fields that are present in the row. Skip the ones that are not present or are NaN
    if "data_track_name" in row and pd.notna(row["data_track_name"]):
        data_track["dataTrackName"] = row["data_track_name"]
    if "data_track_description" in row and pd.notna(row["data_track_description"]):
        data_track["description"] = row["data_track_description"]
    if "direct_link_to_file" in row and pd.notna(row["direct_link_to_file"]):
        data_track["links"][0]["Download"] = row["direct_link_to_file"]
    if "doi_link_to_repository" in row and pd.notna(row["doi_link_to_repository"]):
        data_track["links"][1]["Website"] = row["doi_link_to_repository"]
    if "doi_link_to_scientific_article" in row and pd.notna(row["doi_link_to_scientific_article"]):
        data_track["links"][2]["Article"] = row["doi_link_to_scientific_article"]
    if "accesion_number_or_doi" in row and pd.notna(row["accesion_number_or_doi"]):
        data_track["accessionOrDOI"] = row["accesion_number_or_doi"]
    if "filename" in row and pd.notna(row["filename"]):
        data_track["fileName"] = row["filename"]
    if "principal_investigator_name" in row and pd.notna(row["principal_investigator_name"]):
        data_track["principalInvestigator"] = row["principal_investigator_name"]
    if "principal_investigator_affiliation" in row and pd.notna(row["principal_investigator_affiliation"]):
        data_track["principalInvestigatorAffiliation"] = row["principal_investigator_affiliation"]

    return data_track


def generate_data_tracks_json(file_path: str, sheet_name: str, output_json_path: Path) -> None:
    """
    Generate a JSON file from the data tracks Excel file.
    """
    try:
        # Read the Excel file
        df = read_excel_file(file_path, sheet_name)

        # Load the JSON template as a string
        with open(TEMPLATE_FILE_PATH, "r") as file:
            template_json = json.dumps(json.load(file)[0])

        # Generate a list of JSON objects from the DataFrame
        data_tracks_list_of_dicts = [row_to_json(row, template_json) for _, row in df.iterrows()]

        # Write the data to a JSON file
        with open(output_json_path, "w") as json_file:
            json.dump(data_tracks_list_of_dicts, json_file, indent=2)

        print(f"Data successfully written to {output_json_path}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise
