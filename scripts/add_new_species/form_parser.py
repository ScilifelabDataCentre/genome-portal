import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


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
        img_attrib_text=img_attrib["text"],
        img_attrib_link=img_attrib["url"],
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

    species_name_section = extract_block_of_markdown(
        start_marker="| > fungus",
        end_marker="| Species description",
        markdown_content=markdown_content,
    )

    species_name_cells = extract_table_cells(species_name_section)
    species_names["species_name"] = species_name_cells.get("Scientific name:", "")
    species_names["common_name"] = species_name_cells.get("English (common) name:", "")

    species_names["species_slug"] = species_names["species_name"].replace(" ", "_").lower()
    return species_names


def extract_description(markdown_content: str) -> str:
    """
    Extract the description from the markdown content.
    """
    block_of_markdown_table = extract_block_of_markdown(
        start_marker="the designated text box below.",
        end_marker="| References",
        markdown_content=markdown_content,
    )
    return strip_table_borders(block_of_markdown_table)


def extract_references(markdown_content: str) -> str:
    """
    Extract the references from the markdown content.
    Have to first get the section with references in order to get right block.
    """
    refs_section = extract_block_of_markdown(
        start_marker="on a separate line.",
        end_marker="Scientific article (Optional)",
        markdown_content=markdown_content,
    )

    refs_section_borderless = strip_table_borders(refs_section)

    # Make text into a markdown list
    refs_raw = re.split(r"\\|\n", refs_section_borderless)
    refs = []
    for ref in refs_raw:
        ref = ref.strip()
        if ref:
            refs.append(f"- {ref}")
    return "\n".join(refs)


def extract_publication(markdown_content: str) -> str:
    """
    Extract the publications from the markdown content.

    Assumes that there is only one reference for the study.
    In the rare case of more than one publication, the captured text
    will currently need to be manually edited.
    """

    pubs_section = extract_block_of_markdown(
        start_marker="| > in [APA 7](https://apastyle.apa.org/).",
        end_marker="Funding",
        markdown_content=markdown_content,
    )

    pubs_section_borderless = strip_table_borders(pubs_section)

    return pubs_section_borderless.strip()


def extract_funding(markdown_content) -> str:
    """
    Extract the funding information from the markdown content.
    """
    funding_section = extract_block_of_markdown(
        start_marker="include grant numbers when applicable.",
        end_marker="| Species image",
        markdown_content=markdown_content,
    )

    funding_section_borderless = strip_table_borders(funding_section)

    # Make text into a markdown list
    refs_raw = re.split(r"\\|\n", funding_section_borderless)
    refs = []
    for ref in refs_raw:
        ref = ref.strip()
        if ref:
            refs.append(f"- {ref}")
    return "\n".join(refs)


def extract_img_attrib(markdown_content: str) -> dict[str, str]:
    """
    TODO - not currently in word doc, so fake data for now...
    """
    image_section = extract_block_of_markdown(
        start_marker="| > permission**. ",
        end_marker="**Submission date",
        markdown_content=markdown_content,
    )

    image_cells = extract_table_cells(image_section)
    img_text = image_cells.get("Image attribution:", "")
    img_url = image_cells.get("Image URL (optional):", "")
    if img_url == "Click or tap here to enter text.":
        img_url = ""

    return {"text": img_text, "url": img_url}


def extract_block_of_markdown(markdown_content: str, start_marker: str, end_marker: str = None) -> str:
    """
    Extract a block of markdown content between two markers.
    """
    blocks = []
    in_block = False

    for line in markdown_content.splitlines(keepends=True):
        if start_marker in line:
            in_block = True
            continue

        if end_marker and end_marker in line:
            break

        if in_block:
            blocks.append(line)

    return "".join(blocks).strip()


def strip_table_borders(table_block: str) -> str:
    """
    Removes leading/trailing vertical bars and whitespace from each line in a markdown table block.
    Removes table border lines like +-----+ or -----+ of any length, even if appended to the captured markdown.
    Joins the lines into a single string.
    """
    lines = []
    for line in table_block.splitlines():
        # Remove lines that are only borders
        if re.match(r"^\s*[\+\-]+\s*$", line):
            continue
        line = re.sub(r"[\+\-]+$", "", line)  # Remove trailing border
        line = re.sub(r"^[\+\-]+", "", line)  # Remove leading border
        line = line.strip("|").strip()
        if line:
            lines.append(line)
    return " ".join(lines)


def extract_table_cells(table_block: str) -> dict[str, str]:
    """
    Extracts cell values from a markdown table block with borders.
    Used for tables that have multiple entries, such as the species name table.
    Handles multiline fields (e.g. 'English (common) name:') and values.
    """
    cells = {}
    current_field = None
    current_value_lines = []

    for line in table_block.splitlines():
        match = re.match(r"^\|\s*(.*?)\s*\|\s*(.*?)\s*\|$", line)
        if match:
            field = match.group(1).strip()
            value = match.group(2).strip()

            # Handle multi-line field
            if current_field and field.endswith(":") and not field.startswith(">"):
                current_field = current_field + " " + field
                if value:
                    current_value_lines.append(value)
            # Handle start of field
            elif field:
                if current_field is not None:
                    cells[current_field] = " ".join(current_value_lines).strip()
                current_field = field
                current_value_lines = [value] if value else []
            # Handle multi-line case where there is no field name on the line but is a value
            elif value and not field:
                current_value_lines.append(value)

    if current_field and current_value_lines:
        cells[current_field] = " ".join(current_value_lines).strip()
    return cells
