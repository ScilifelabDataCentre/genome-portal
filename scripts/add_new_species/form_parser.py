from pathlib import Path
from typing import Optional

from attr import dataclass


@dataclass
class UserFormData:
    """
    Class to hold the data extracted from the user form.
    For use by the downstream functions.
    """

    species_name: str
    species_slug: str
    common_name: str
    description: str
    references: str
    publication: str
    funding: str
    img_attrib_text: str
    img_attrib_link: Optional[str] = None


def parse_user_form(form_file_path: Path) -> UserFormData:
    """
    Parses the word doc provided by the user form.
    Returning an object with all the attributes that need to be extracted
    """
    markdown_content = create_markdown_content()

    species_names = extract_species_names(markdown_content)
    description = extract_description(markdown_content)
    references = extract_references(markdown_content)
    publication = extract_publication(markdown_content)
    funding = extract_funding(markdown_content)

    return UserFormData(
        species_name=species_names["species_name"],
        species_slug=species_names["species_slug"],
        common_name=species_names["common_name"],
        description=description,
        references=references,
        publication=publication,
        funding=funding,
        img_attrib_text="Image attribution text.",
        img_attrib_link="https://example.com/image_attribution",
    )


def create_markdown_content() -> str:
    """
    Convert the user form to markdown via pandoc,
    Then read the markdown file into a string for parsing.
    """
    # TODO - would run pandoc here too and file path would be param.
    file_path = Path("scripts/add_new_species/tests/fixtures/submission_form_example/converted_species_submit_form.md")

    with open(file_path, "r") as file:
        markdown_content = file.read()

    return markdown_content


def extract_species_names(markdown_content: str) -> dict[str, str]:
    """
    Extract the species names from the markdown content.
    """
    species_names = {
        "species_name": "",
        "species_slug": "",
        "common_name": "",
    }

    for line in markdown_content.splitlines():
        if "Scientific name:" in line:
            species_names["species_name"] = line.split(":")[1].strip()
        if "English (common) name:" in line:
            species_names["common_name"] = line.split(":")[1].strip()

    species_names["species_slug"] = species_names["species_name"].replace(" ", "_").lower()
    return species_names


def extract_description(markdown_content: str) -> str:
    """
    Extract the description from the markdown content.
    """
    return extract_block_of_markdown(
        start_marker="we will get back to you",
        end_marker="#### References",
        markdown_content=markdown_content,
    )


def extract_references(markdown_content: str) -> str:
    """
    Extract the references from the markdown content.
    Have to first get the section with references in order to get right block.
    """
    refs_section = extract_block_of_markdown(
        start_marker="#### References",
        end_marker="Genome assembly information",
        markdown_content=markdown_content,
    )

    raw_refs = extract_block_of_markdown(
        start_marker="sapiens",
        end_marker="Genome assembly information",
        markdown_content=refs_section,
    )

    # Make text into a markdown list
    refs = []
    for line in raw_refs.strip().splitlines():
        refs.append(f"- {line}")
    return "\n".join(refs)


def extract_publication(markdown_content: str) -> str:
    """
    Extract the publications from the markdown content.
    """
    pubs_section = extract_block_of_markdown(
        start_marker="### Publication",
        end_marker="### Funding",
        markdown_content=markdown_content,
    )

    pubs = extract_block_of_markdown(
        start_marker="sapiens",
        end_marker="### Funding",
        markdown_content=pubs_section,
    )

    return pubs.strip()


def extract_funding(markdown_content) -> str:
    """
    Extract the funding information from the markdown content.
    """
    funding_section = extract_block_of_markdown(
        start_marker="### Funding",
        end_marker="# 4. Data Tracks Form",
        markdown_content=markdown_content,
    )

    print(f"{funding_section=}")

    raw_funding = extract_block_of_markdown(
        start_marker="applicable.",
        end_marker="# 4. Data Tracks Form",
        markdown_content=funding_section,
    )

    print(f"{raw_funding=}")

    # Make text into a markdown list
    funding = []
    for line in raw_funding.strip().splitlines():
        funding.append(f"- {line}")
    return "\n".join(funding)


def extract_img_attrib(markdown_content: str) -> str:
    """
    TODO - not currently in word doc, so fake data for now...
    """
    img_attrib = {
        "text": "Image attribution text.",
        "url": "https://example.com/image_attribution",
    }
    return img_attrib


def extract_block_of_markdown(start_marker: str, end_marker: str, markdown_content: str) -> str:
    """
    Extract a block of markdown content between two markers.
    """
    block = ""
    in_block = False

    for line in markdown_content.splitlines(keepends=True):
        if start_marker in line:
            in_block = True
            continue

        if end_marker in line:
            in_block = False
            break

        if in_block:
            block += line

    return block
