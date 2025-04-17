import shutil
import tempfile
from pathlib import Path

import pytest


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
    base_dir = Path(__file__).parent / "fixtures" / "example_images"
    image_files = {
        "image_4_3": base_dir / "image_4_3.png",
        "image_close_to_4_3": base_dir / "image_close_to_4_3.jpg",
        "image_not_4_3": base_dir / "image_not_4_3.png",
    }
    return image_files


@pytest.fixture
def example_excel_files() -> dict[str, Path]:
    """
    Paths to example Excel files for testing.
    """
    base_dir = Path(__file__).parent / "fixtures" / "submission_form_example"
    excel_files = {
        "excel_form_with_comments": base_dir / "02-Data_Tracks_Form_v1.1.0.xlsx",
        "excel_form_wo_comments": base_dir / "02-Data_Tracks_Form_v1.1.0_fix.xlsx",
    }
    return excel_files


@pytest.fixture
def assembly_metadata_dict():
    return {
        "name": "ASM1142v1",
        "assembly_level": "Chromosome",
        "genome_representation": "full",
        "assembly_type": "haploid",
        "accession": "GCA_000011425.1",
        "species_name": "Aspergillus nidulans",
        "species_name_abbrev": "A. nidulans",
    }
