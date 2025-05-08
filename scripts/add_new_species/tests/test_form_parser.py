import subprocess
from pathlib import Path

import pytest
from add_new_species.form_parser import create_markdown_content, parse_user_form


def test_create_markdown_content_docx_success(example_user_forms: dict[str, Path], temp_output_dir: Path) -> None:
    """
    Test that sucessfully converts docx to markdown-formatted string by calling pandoc with subprocess.run.
    """
    input_form_file = example_user_forms["docx_form"]
    markdown_content = create_markdown_content(input_form_file)

    assert isinstance(markdown_content, str), "Did not return markdown content as string"
    assert markdown_content.strip(), "Markdown content is empty"


def test_create_markdown_content_docx_fail(example_user_forms: dict[str, Path], temp_output_dir: Path) -> None:
    """
    Test that fails upon input of markdown file when the function expects docx.
    In the function, the 'check=True' argument is used to raise a CalledProcessError.
    """
    input_form_file = example_user_forms["markdown_form"]

    with pytest.raises(subprocess.CalledProcessError):
        create_markdown_content(input_form_file)


def test_parse_user_form_success(example_user_forms: dict[str, Path], temp_output_dir: Path) -> None:
    input_form_file = example_user_forms["docx_form"]
    UserFormData = parse_user_form(input_form_file)

    assert UserFormData.species_name, "Species name is empty"
    assert UserFormData.species_slug, "Species slug is empty"
    assert UserFormData.common_name, "Common name is empty"
    assert UserFormData.description, "Description is empty"
    assert UserFormData.references, "References are empty"
    assert UserFormData.publication, "Publication is empty"
    assert UserFormData.funding, "Funding is empty"
    assert UserFormData.img_attrib_text, "Image attribution text is empty"
