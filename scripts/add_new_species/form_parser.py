import subprocess
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
    markdown_content = create_markdown_content(form_file_path)

    species_names = extract_species_names(markdown_content)
    description = extract_description(markdown_content)
    references = extract_references(markdown_content)
    publication = extract_publication(markdown_content)
    funding = extract_funding(markdown_content)
    img_attrib = extract_img_attrib(markdown_content)

    return UserFormData(
        species_name=species_names["species_name"],
        species_slug=species_names["species_slug"],
        common_name=species_names["common_name"],
        description=description,
        references=references,
        publication=publication,
        funding=funding,
        img_attrib_text=img_attrib[
            "text"
        ],  # TODO - not currently in docx,example text hardcoded in extract_img_attrib()
        img_attrib_link=img_attrib[
            "url"
        ],  # TODO - not currently in docx,example text hardcoded in extract_img_attrib()
    )


def create_markdown_content(form_file_path: Path) -> str:
    """
    Convert the user form to markdown via pandoc,
    return as string via subprocess stdout.
    """

    pandoc_result = subprocess.run(
        ["pandoc", "--from=docx", "--to=markdown", str(form_file_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )

    return pandoc_result.stdout


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
            # v1.1.0 of the docx template italicizes the species name, which is returned as *species_name* by pandoc
            species_names["species_name"] = line.split(":")[1].replace("*", "").strip()
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

    raw_funding = extract_block_of_markdown(
        start_marker="applicable.",
        end_marker="# 4. Data Tracks Form",
        markdown_content=funding_section,
    )

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
