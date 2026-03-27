import subprocess
from pathlib import Path

import pytest
from form_parser import create_markdown_content, parse_user_form, validate_species_name_is_binomial


def test_create_markdown_content_docx_success(example_user_forms: dict[str, Path]) -> None:
    """
    Test that sucessfully converts docx to markdown-formatted string by calling pandoc with subprocess.run.
    """
    input_form_file = example_user_forms["docx_form"]
    markdown_content = create_markdown_content(input_form_file)

    assert isinstance(markdown_content, str), "Did not return markdown content as string"
    assert markdown_content.strip(), "Markdown content is empty"


def test_create_markdown_content_docx_fail(example_user_forms: dict[str, Path]) -> None:
    """
    Test that fails upon input of markdown file when the function expects docx.
    In the function, the 'check=True' argument is used to raise a CalledProcessError.
    """
    input_form_file = example_user_forms["markdown_form"]

    with pytest.raises(subprocess.CalledProcessError):
        create_markdown_content(input_form_file)


def test_parse_user_form_success(example_user_forms: dict[str, Path]) -> None:
    """
    Test that sucessfully runs the 'main' function of the module and returns a UserFormData object (dataclass).
    """
    input_form_file = example_user_forms["docx_form"]
    UserFormData = parse_user_form(input_form_file)

    for key, value in vars(UserFormData).items():
        assert value, f"Field: {key} is empty"


def test_validate_species_name_is_binomial_success() -> None:
    """
    Test that a valid binomial species name passes validation.
    """
    validate_species_name_is_binomial("Linum grandiflorum")


@pytest.mark.parametrize("invalid_name", ["Linum", "Linum grandiflorum Desf", ""])
def test_validate_species_name_is_binomial_fail(invalid_name: str) -> None:
    """
    Test that non-binomial species names fail with a clear actionable message.
    """
    with pytest.raises(
        ValueError,
        match="Species name must be binomial \\(Genus species\\). Remove any extra descriptors from the species field.",
    ):
        validate_species_name_is_binomial(invalid_name)
