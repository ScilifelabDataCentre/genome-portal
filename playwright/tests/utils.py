"""
Useful functions for testing.
"""

from datetime import datetime
from pathlib import Path


def validate_date_format(date: str, date_format: str) -> None:
    """
    Validate the format of a date on the website is as expected.
    Returns nothing if fine, will raise Error otherwise, causing test fail.
    """
    ALLOWED_DATE_FORMATS = ["%d %B %Y", "%d/%m/%Y"]

    if date_format not in ALLOWED_DATE_FORMATS:
        raise ValueError(f"Date format: {date_format} is not supported")

    try:
        datetime.strptime(date, date_format)
    except ValueError as exc:
        raise AssertionError("Date format is incorrect") from exc


def get_list_of_species() -> list[str]:
    """
    Search the Hugo content directory to get all the species shown.
    This helper function is used to test each species page in the same way.
    """
    HUGO_SPECIES_DIR = Path(__file__).parent.parent.parent / "hugo/content/species"

    species = []
    for folder in HUGO_SPECIES_DIR.iterdir():
        if folder.is_dir():
            species.append(folder.name)

    return species
