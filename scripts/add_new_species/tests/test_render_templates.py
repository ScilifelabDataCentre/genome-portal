from datetime import datetime
from itertools import chain

from add_content_files import TEMPLATE_DIR
from form_parser import UserFormData
from render_templates import read_text_file, render


def test_process_template_file_index_md_all_replacements(user_form_data: UserFormData) -> None:
    """
    Test that sucessfully calls process_template_file and substitutes required and optional replacements.
    """
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

    template_text = read_text_file(file_path=template_file_path)
    rendered_content = render(
        template_text=template_text,
        required_replacements=required_replacements,
        optional_replacements=optional_replacements,
    )

    for key in chain(required_replacements.keys(), optional_replacements.keys()):
        assert (
            f"${{{key}}}" not in rendered_content
        ), f"Placeholder '${{{key}}}' was not replaced in the rendered content."


def test_process_template_file_index_md_missing_optional_replacements(user_form_data: UserFormData) -> None:
    """
    Test that sucessfully ensures that optional replacements are replaced with "[EDIT]" if value is None.
    """
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

    template_text = read_text_file(file_path=template_file_path)
    rendered_content = render(
        template_text=template_text,
        required_replacements=required_replacements,
    )

    assert "${gbif_taxon_id}" not in rendered_content
    assert "${goat_webpage}" not in rendered_content
