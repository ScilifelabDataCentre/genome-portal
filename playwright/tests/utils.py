"""
Useful functions and constants for testing.
"""

from datetime import datetime
from pathlib import Path

HUGO_SPECIES_DIR = Path(__file__).parent.parent.parent / "hugo/content/species"
ALLOWED_DATE_FORMATS = ["%d %B %Y", "%d/%m/%Y"]


def get_list_of_species() -> list[str]:
    """
    Search the Hugo content directory to get all the species on the website.
    This helper function is useful for testing each species page in the same way.

    The function also validates each page is not in draft mode (wont show up on website yet)
    """
    species = []
    for folder in HUGO_SPECIES_DIR.iterdir():
        if not folder.is_dir():
            continue

        index_file = folder / "_index.md"
        if not index_file.exists():
            continue

        with index_file.open() as file_in:
            content = file_in.read()
            if "draft: true" not in content:
                species.append(folder.name)

    return species


SPECIES_LIST = get_list_of_species()

INTRO_PAGE_PATHS = SPECIES_LIST
ASSEMBLY_PAGE_PATHS = [f"{species}/assembly" for species in SPECIES_LIST]
DOWNLOAD_PAGE_PATHS = [f"{species}/download" for species in SPECIES_LIST]

ALL_NON_SPECIES_PAGES_PATHS = [
    "home",
    "about",
    "about/sv",
    "citation",
    "contact",
    "contribute",
    "contribute/supported_file_formats",
    "contribute/recommendations_for_making_data_public",
    "faqs",
    "glossary",
    "privacy",
    "terms",
    "user-guide",
]

ALL_PAGE_PATHS = ALL_NON_SPECIES_PAGES_PATHS + INTRO_PAGE_PATHS + ASSEMBLY_PAGE_PATHS + DOWNLOAD_PAGE_PATHS


def validate_date_format(date: str, date_format: str) -> None:
    """
    Validate the format of a date on the website is as expected.
    Returns nothing if fine, will raise Error otherwise, causing test fail.
    """
    if date_format not in ALLOWED_DATE_FORMATS:
        raise ValueError(f"Date format: {date_format} is not supported")

    try:
        datetime.strptime(date, date_format)
    except ValueError as exc:
        raise AssertionError("Date format is incorrect") from exc
