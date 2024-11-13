"""
Test the species names are shown in italics.
Covers both "Parnassius mnemosyne" and "P. mnemosyne" cases.

This test does not use playwright, but instead checks the markdown files directly.
This is because the tables and filenames in the HTML part of each page do not need to be checked, (and it is easier to check this way).
"""

import re
from pathlib import Path

import pytest
from utils import HUGO_SPECIES_DIR, SPECIES_LIST


def is_italicized(line: str, word: str) -> bool:
    """
    Check if a word is wrapped in <i>, <em>, _ or * tags - making it italicized.
    (Used on the species names).
    Can handle multiple italicized words in the same line.
    """
    ITALIC_FORMATS = [
        f"<i>{word}</i>",
        f"<em>{word}</em>",
        f"<i> {word} </i>",
        f"<em> {word} </em>",
        f"_{word}_",
        f"*{word}*",
    ]

    for match in re.finditer(word, line):
        # max and min used to handle if start or end of line
        context_start = max(match.span()[0] - 4, 0)
        context_end = min(match.span()[1] + 5, len(line))
        word_context = line[context_start:context_end]

        if not any(format in word_context for format in ITALIC_FORMATS):
            return False
    return True


def prepare_species_pages_names() -> dict[str, tuple[str, str]]:
    """
    Helper function to prepare the all the species markdown files to check,
    alongside the associated long form and short form of the species name.
    """

    species_pages_to_check = {}
    for species_path in SPECIES_LIST:
        intro_md_file = HUGO_SPECIES_DIR / species_path / "_index.md"
        assembly_md_file = HUGO_SPECIES_DIR / species_path / "assembly.md"
        download_md_file = HUGO_SPECIES_DIR / species_path / "download.md"

        species_name = species_path.replace("_", " ").capitalize()
        first_word, rest = species_name.split(" ", 1)
        species_name_short = f"{first_word[0]}. {rest}"

        species_pages_to_check[intro_md_file] = (species_name, species_name_short)
        species_pages_to_check[assembly_md_file] = (species_name, species_name_short)
        species_pages_to_check[download_md_file] = (species_name, species_name_short)

    return species_pages_to_check


species_pages_to_check = prepare_species_pages_names()


@pytest.mark.parametrize("markdown_file, species_names", species_pages_to_check.items())
def test_species_names_italics(markdown_file: Path, species_names: tuple[str, str]) -> None:
    """
    Test the species names are provided in italics.
    Covers both "Parnassius mnemosyne" and "P. mnemosyne" cases.
    Counts as one test per species page.
    """
    species_name, species_name_short = species_names

    with markdown_file.open() as file_in:
        content = file_in.read()
    # Excludes the front matter toml content
    markdown_content = content.split("---\n")[2]

    for line in markdown_content.split("\n"):
        if species_name in line:
            assert is_italicized(line, species_name), (
                f"The file: {markdown_file} does not appear to have italicised the species name: {species_name} correctly. "
                f"This is the context: {line}"
            )

        elif species_name_short in line:
            assert is_italicized(line, species_name_short), (
                f"The file: {markdown_file} does not appear to have italicised the species name: {species_name_short} correctly. "
                f"This is the context: {line}"
            )
