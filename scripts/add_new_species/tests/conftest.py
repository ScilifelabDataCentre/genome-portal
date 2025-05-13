import shutil
import tempfile
from pathlib import Path

import pytest
from add_new_species.form_parser import UserFormData
from add_new_species.get_assembly_metadata_from_ENA_NCBI import AssemblyMetadata

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
def user_form_data() -> UserFormData:
    """
    Fixture that provides a mock UserFormData instance for testing.
    """
    return UserFormData(
        species_name="Aspergillus nidulans",
        species_slug="aspergillus_nidulans",
        common_name="A species of mold",
        description="Aspergillus nidulans is a filamentous fungus widely used as a model organism in genetics and cell biology.",
        references="- Reference 1: https://doi.org/10.1234/reference1\n- Reference 2: https://doi.org/10.5678/reference2",
        publication="Published in Journal of Mycology, 2025.",
        funding="- Grant 1: National Science Foundation\n- Grant 2: European Research Council",
        img_attrib_text="Image courtesy of Dr. John Doe.",
        img_attrib_link="https://example.com/image_attribution",
    )


@pytest.fixture
def assembly_metadata() -> AssemblyMetadata:
    """
    Fixture that provides an AssemblyMetadata instance for testing.
    """
    return AssemblyMetadata(
        species_name="Aspergillus nidulans",
        species_name_abbrev="A. nidulans",
        assembly_name="ASM1142v1",
        assembly_level="Chromosome",
        genome_representation="full",
        assembly_accession="GCA_000011425.1",
        assembly_type="haploid",
    )


@pytest.fixture
def data_tracks_list_of_dicts() -> list[dict]:
    """
    Fixture that provides a list of dictionaries representing the data tracks from the user spreadsheet.
    """
    return [
        {
            "dataTrackName": "Genome",
            "description": "Reference genome sequence",
            "links": [
                {"Download": "https://example.com/genome.fasta"},
                {"Website": "https://doi.org/10.1234/repository"},
                {"Article": "https://doi.org/10.1234/article"},
            ],
            "accessionOrDOI": "GCA_000011425.1",
            "fileName": "genome.fasta",
            "principalInvestigator": "John Doe",
            "principalInvestigatorAffiliation": "University of Example",
        },
        {
            "dataTrackName": "Protein-coding genes",
            "description": "Structural annotation of protein-coding genes",
            "links": [
                {"Download": "https://example.com/track1.gff"},
                {"Website": "https://doi.org/10.5678/repository"},
                {"Article": "https://doi.org/10.5678/article"},
            ],
            "accessionOrDOI": "doi:10.5678/track1",
            "fileName": "track1.gff",
            "principalInvestigator": "John Doe",
            "principalInvestigatorAffiliation": "University of Example",
        },
        {
            "dataTrackName": "Repeats",
            "description": "Annotation of the repetitive regions",
            "links": [
                {"Download": "https://example.com/track2.gff"},
                {"Website": "https://doi.org/10.9101/repository"},
                {"Article": "https://doi.org/10.9101/article"},
            ],
            "accessionOrDOI": "doi:10.9101/track2",
            "fileName": "track2.gff",
            "principalInvestigator": "John Doe",
            "principalInvestigatorAffiliation": "University of Example",
        },
    ]
