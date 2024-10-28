"""
Useful functions for testing.
"""

from datetime import datetime
from pathlib import Path


def get_list_of_species() -> list[str]:
    """
    Search the Hugo content directory to get all the species shown.
    This helper function is useful for testing each species page in the same way.
    """
    HUGO_SPECIES_DIR = Path(__file__).parent.parent.parent / "hugo/content/species"

    species = []
    for folder in HUGO_SPECIES_DIR.iterdir():
        if folder.is_dir():
            species.append(folder.name)

    return species


def all_intro_page_paths() -> list[str]:
    """
    Return all species intro page paths as strings.
    """
    return get_list_of_species()


def all_assembly_page_paths() -> list[str]:
    """
    Return all species assembly page paths as strings.
    """
    assembly_paths = []
    for species in get_list_of_species():
        assembly_paths.append(f"{species}/assembly")
    return assembly_paths


def all_download_page_paths() -> list[str]:
    """
    Return all species download page paths as strings.
    """
    download_paths = []
    for species in get_list_of_species():
        download_paths.append(f"{species}/download")
    return download_paths


def all_non_species_pages_paths() -> list[str]:
    """
    Return all the non-species pages on the website as strings.
    """
    return [
        "home",
        "about",
        "about/sv",
        "contact",
        "contribute",
        "glossary",
        "privacy",
    ]


def all_page_paths() -> list[str]:
    """
    Return a list of all pages on the website as strings.
    """
    return (
        all_non_species_pages_paths() + all_intro_page_paths() + all_assembly_page_paths() + all_download_page_paths()
    )


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
