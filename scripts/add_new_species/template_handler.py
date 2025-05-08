"""
Submodule for handling the opening, substituring and saving of template files.
"""

from pathlib import Path
from string import Template


def process_template_file(
    template_file_path: Path,
    output_file_path: Path,
    required_replacements: dict[str, str],
    optional_replacements: dict[str, str] = None,
) -> None:
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

    if optional_replacements:
        cleaned_replacements = {}
        for key, value in optional_replacements.items():
            if value is None:
                cleaned_replacements[key] = "[EDIT]"
            else:
                cleaned_replacements[key] = value

        # pipe order so if duplicate keys, required_replacements takes precedence
        replacements = cleaned_replacements | required_replacements
    else:
        replacements = required_replacements

    with open(template_file_path, "r") as file_in:
        template_txt = file_in.read()
    template = Template(template_txt)

    content = template.substitute(replacements)

    with open(output_file_path, "w") as file_out:
        file_out.write(content)
    print(f"File created: {output_file_path.resolve()}")
