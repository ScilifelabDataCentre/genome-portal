"""
Submodule for handling the opening, substituring and saving of template files.
"""

from collections import defaultdict
from pathlib import Path
from string import Template


def render(
    template_text: str,
    required_replacements: dict[str, str],
    optional_replacements: dict[str, str] = None,
) -> str:
    """
    Use Python's string.Template.substitute method to fill in placeholders in a given template file.
    Both required and optional replacements can be made.

    Required replacements will result in an error if value is None.
    Optional replacements will be replaced with "[EDIT]" if value is None.
    """
    # If value was None and no check, Template.substitute() will replace text with "None"
    for key, value in required_replacements.items():
        if value is None:
            raise ValueError(f"Template key '{key}' has a value of None.")

    cleaned_replacements = defaultdict(lambda: "[EDIT]")
    if optional_replacements:
        for key, value in optional_replacements.items():
            cleaned_replacements[key] = value

    # pipe order so if duplicate keys, required_replacements takes precedence
    replacements = cleaned_replacements | required_replacements

    template = Template(template_text)
    content = template.substitute(replacements)

    return content


def read_text_file(file_path: Path) -> str:
    """
    Read a txt file and return its content as a string.
    """
    with open(file_path, "r") as file_in:
        template_txt = file_in.read()
    return template_txt


def save_text_file(content: str, output_file_path: Path) -> None:
    """
    Save a string of text to a file.
    """
    with open(output_file_path, "w") as file_out:
        file_out.write(content)
    print(f"File created: {output_file_path.resolve()}")
