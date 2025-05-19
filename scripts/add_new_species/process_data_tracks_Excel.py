"""
Submodule to read the data tracks Excel form (.xlsx), extract genome assembly accession number,
and populate the data_tracks.json.

NB! The Excel files cannot contain comments; if it does, pd.read_excel will fail with the error
"This is most probably because the workbook source files contain some invalid XML."

"""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
from add_content_files import TEMPLATE_DIR

JSON_FILE_NAME = "data_tracks.json"
TEMPLATE_FILE_PATH = TEMPLATE_DIR / JSON_FILE_NAME


def df_row_to_json(row: pd.Series, template_json: str) -> dict[str, str]:
    """
    Convert a row of the DataFrame to a JSON object using the JSON template.
    Handle missing values by checking if the value is None or NaN: if so,
    use the default value from the template instead. Columns that are present
    in the template but not in the row will be passed through as is.
    """

    data_track = json.loads(template_json)

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
    if "firstDateOnPortal" in row and pd.notna(row["firstDateOnPortal"]):
        data_track["firstDateOnPortal"] = row["firstDateOnPortal"]
    else:
        data_track["firstDateOnPortal"] = datetime.now().strftime("%d/%m/%Y")

    return data_track


def parse_excel_file(spreadsheet_file_path: str, sheet_name: str) -> list[dict]:
    """
    Parse the Excel file with Pandas and return a JSON-style structure (list of dicts).
    """
    df = pd.read_excel(spreadsheet_file_path, sheet_name=sheet_name, engine="openpyxl")

    with open(TEMPLATE_FILE_PATH, "r") as file:
        template_json = json.dumps(json.load(file)[0])

    data_tracks_list_of_dicts = [df_row_to_json(row, template_json) for _, row in df.iterrows()]

    return data_tracks_list_of_dicts


def populate_data_tracks_json(data_tracks_list_of_dicts: list[dict], assets_dir_path: Path) -> None:
    """
    Write the data tracks list of dictionaries to a JSON file.
    """
    output_json_path = assets_dir_path / JSON_FILE_NAME

    with open(output_json_path, "w") as json_file:
        json.dump(data_tracks_list_of_dicts, json_file, indent=2)
        print(f"File created: {output_json_path.resolve()}")
