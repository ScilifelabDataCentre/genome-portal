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
