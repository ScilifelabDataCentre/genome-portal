from datetime import datetime
from itertools import chain
from pathlib import Path

from add_new_species.form_parser import UserFormData
from add_new_species.template_handler import process_template_file

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "templates"


def test_process_template_file_index_md_all_replacements(temp_output_dir: Path, user_form_data: UserFormData) -> None:
    """
    Test that sucessfully calls process_template_file and substitutes required and optional replacements.
    """
    output_file_path = temp_output_dir / "output.txt"
    template_file_path = TEMPLATE_DIR / "_index.md"

    required_replacements = {
        "species_name": user_form_data.species_name,
        "species_slug": user_form_data.species_slug,
        "common_name": user_form_data.common_name,
        "description": user_form_data.description,
        "references": user_form_data.references,
        "publication": user_form_data.publication,
        "img_attrib_text": user_form_data.img_attrib_text,
        "img_attrib_link": user_form_data.img_attrib_link,
        "todays_date": datetime.now().strftime("%d/%m/%Y"),
    }

    optional_replacements = {
        "gbif_taxon_id": "12345",
        "goat_webpage": "www.example.com",
    }

    process_template_file(
        template_file_path=template_file_path,
        output_file_path=output_file_path,
        required_replacements=required_replacements,
        optional_replacements=optional_replacements,
    )

    assert output_file_path.exists(), "The output file was not created."

    updated_index_md = output_file_path.read_text()

    for key in chain(required_replacements.keys(), optional_replacements.keys()):
        assert f"${{{key}}}" not in updated_index_md, f"Placeholder '${{{key}}}' was not replaced in the output file."


def test_process_template_file_index_md_missing_optional_replacements(
    temp_output_dir: Path, user_form_data: UserFormData
) -> None:
    """
    Test that sucessfully ensures that optional replacements are replaced with "[EDIT]" if value is None.
    """
    output_file_path = temp_output_dir / "output.txt"
    template_file_path = TEMPLATE_DIR / "_index.md"

    required_replacements = {
        "species_name": user_form_data.species_name,
        "species_slug": user_form_data.species_slug,
        "common_name": user_form_data.common_name,
        "description": user_form_data.description,
        "references": user_form_data.references,
        "publication": user_form_data.publication,
        "img_attrib_text": user_form_data.img_attrib_text,
        "img_attrib_link": user_form_data.img_attrib_link,
        "todays_date": datetime.now().strftime("%d/%m/%Y"),
    }

    process_template_file(
        template_file_path=template_file_path,
        output_file_path=output_file_path,
        required_replacements=required_replacements,
    )

    assert output_file_path.exists(), "The output file was not created."

    updated_index_md = output_file_path.read_text()

    assert "${gbif_taxon_id}" not in updated_index_md
    assert "${goat_webpage}" not in updated_index_md
