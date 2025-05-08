import shutil
import tempfile
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
IMG_FIXTURES_DIR = FIXTURES_DIR / "example_images"
FORM_FIXTURES_DIR = FIXTURES_DIR / "submission_form_example"


@pytest.fixture
def temp_output_dir():
    """
    Create a temporary directory for output files during tests.
    """
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def example_images() -> dict[str, Path]:
    """
    Paths to example image files for testing.
    """
    image_files = {
        "image_4_3": IMG_FIXTURES_DIR / "image_4_3.png",
        "image_close_to_4_3": IMG_FIXTURES_DIR / "image_close_to_4_3.jpg",
        "image_not_4_3": IMG_FIXTURES_DIR / "image_not_4_3.png",
    }
    return image_files


@pytest.fixture
def example_excel_files() -> dict[str, Path]:
    """
    Paths to example Excel files for testing.
    """
    excel_files = {
        "excel_form_with_comments": FORM_FIXTURES_DIR / "02-Data_Tracks_Form_v1.1.0.xlsx",
        "excel_form_wo_comments": FORM_FIXTURES_DIR / "02-Data_Tracks_Form_v1.1.0_fix.xlsx",
    }
    return excel_files


@pytest.fixture
def example_user_forms() -> dict[str, Path]:
    """
    Paths to example user form files for testing.
    """
    form_files = {
        "markdown_form": FORM_FIXTURES_DIR / "converted_species_submit_form.md",
        "docx_form": FORM_FIXTURES_DIR / "01-species_submission_form_v1.1.0.docx",
    }
    return form_files


@pytest.fixture
def assembly_metadata_dict() -> dict[str, str]:
    return {
        "name": "ASM1142v1",
        "assembly_level": "Chromosome",
        "genome_representation": "full",
        "assembly_type": "haploid",
        "accession": "GCA_000011425.1",
        "species_name": "Aspergillus nidulans",
        "species_name_abbrev": "A. nidulans",
    }
