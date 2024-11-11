"""
Useful functions for testing.
"""

from datetime import datetime
from pathlib import Path


def get_hugo_species_dir() -> Path:
    """
    Get the Hugo species directory.
    """
    return Path(__file__).parent.parent.parent / "hugo/content/species"


def get_list_of_species() -> list[str]:
    """
    Search the Hugo content directory to get all the species on the website.
    This helper function is useful for testing each species page in the same way.

    The function also validates each page is not in draft mode (wont show up on website yet)
    """
    HUGO_SPECIES_DIR = get_hugo_species_dir()

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


def all_intro_page_paths() -> list[str]:
    """
    Return all species intro page paths as strings.
    """
    return SPECIES_LIST


def all_assembly_page_paths() -> list[str]:
    """
    Return all species assembly page paths as strings.
    """
    assembly_paths = []
    for species in SPECIES_LIST:
        assembly_paths.append(f"{species}/assembly")
    return assembly_paths


def all_download_page_paths() -> list[str]:
    """
    Return all species download page paths as strings.
    """
    download_paths = []
    for species in SPECIES_LIST:
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
        "contribute/recommendations_for_file_formats",
        "contribute/recommendations_for_making_data_public",
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
