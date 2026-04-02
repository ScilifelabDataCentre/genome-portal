import subprocess
from pathlib import Path

import pytest
from form_parser import (
    create_markdown_content,
    extract_species_names,
    normalize_species_name,
    parse_user_form,
    slug_from_species_name,
    validate_species_name_is_binomial,
    validate_species_slug,
)


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


def test_parse_user_form_fails_for_unfilled_template(example_user_forms: dict[str, Path]) -> None:
    """
    Test that an unfilled v1.3 template docx fails validation for required species name.
    """
    input_form_file = example_user_forms["docx_form"]
    with pytest.raises(
        ValueError,
        match="Species name must be binomial \\(Genus species\\). Remove any extra descriptors from the species field.",
    ):
        parse_user_form(input_form_file)


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


@pytest.mark.parametrize(
    ("raw_name", "expected"),
    [
        ("Volvox carteri", "Volvox carteri"),
        ("  Volvox   carteri  ", "Volvox carteri"),
        ("Volvox\u00a0carteri", "Volvox carteri"),
    ],
)
def test_normalize_species_name(raw_name: str, expected: str) -> None:
    """
    Test that species names are normalized for odd DOCX spacing/unicode.
    """
    assert normalize_species_name(raw_name) == expected


def test_slug_from_species_name() -> None:
    """
    Test slug derivation from normalized species name.
    """
    assert slug_from_species_name("Volvox carteri") == "volvox_carteri"


@pytest.mark.parametrize("valid_slug", ["volvox_carteri", "linum_grandiflorum", "a_b"])
def test_validate_species_slug_success(valid_slug: str) -> None:
    """
    Test accepted slug formats.
    """
    validate_species_slug(valid_slug)


@pytest.mark.parametrize(
    "invalid_slug", ["", "volvox/carteri", "volvox carteri", "volvox@carteri", "volvox-carteri", "V2_1"]
)
def test_validate_species_slug_fail(invalid_slug: str) -> None:
    """
    Test rejected slug formats.
    """
    with pytest.raises(
        ValueError,
        match="Invalid species slug:",
    ):
        validate_species_slug(invalid_slug)


def test_extract_species_names_normalizes_and_validates_slug() -> None:
    """
    Test species extraction + normalization + slug creation in one flow.
    """
    markdown_content = "\n".join(
        [
            "| Scientific name |",
            "| Scientific name (Genus species): | Volvox\u00a0carteri |",
            "| English (common) name: | green algae |",
            "| Additional descriptor (optional): | FGSC A4 |",
            "| Species description |",
        ]
    )
    species_names = extract_species_names(markdown_content)

    assert species_names["species_name"] == "Volvox carteri"
    assert species_names["species_slug"] == "volvox_carteri"
    assert species_names["common_name"] == "green algae"
    assert species_names["additional_descriptor"] == "FGSC A4"


def test_extract_species_names_handles_empty_optional_descriptor_placeholder() -> None:
    markdown_content = "\n".join(
        [
            "| Scientific name |",
            "| Scientific name (Genus species): | Volvox carteri |",
            "| English (common) name: | green algae |",
            "| Additional descriptor (optional): | Click or tap here to enter text. |",
            "| Species description |",
        ]
    )

    species_names = extract_species_names(markdown_content)

    assert species_names["species_name"] == "Volvox carteri"
    assert species_names["species_slug"] == "volvox_carteri"
    assert species_names["common_name"] == "green algae"
    assert species_names["additional_descriptor"] == ""


def test_extract_species_names_unescapes_markdown_in_additional_descriptor() -> None:
    markdown_content = "\n".join(
        [
            "| Scientific name |",
            "| Scientific name (Genus species): | Volvox carteri |",
            "| English (common) name: | green algae |",
            r"| Additional descriptor (optional): | f\. nagariensis Eve |",
            "| Species description |",
        ]
    )

    species_names = extract_species_names(markdown_content)
    assert species_names["additional_descriptor"] == "f. nagariensis Eve"


def test_extract_species_names_supports_legacy_scientific_name_key() -> None:
    markdown_content = "\n".join(
        [
            "| Scientific name |",
            "| Scientific name: | Volvox carteri |",
            "| English (common) name: | green algae |",
            "| Additional descriptor (optional): | FGSC A4 |",
            "| Species description |",
        ]
    )

    species_names = extract_species_names(markdown_content)

    assert species_names["species_name"] == "Volvox carteri"
    assert species_names["species_slug"] == "volvox_carteri"
    assert species_names["common_name"] == "green algae"
    assert species_names["additional_descriptor"] == "FGSC A4"
