from pathlib import Path

import pytest
from add_new_species.image_processer import process_species_image

OUTPUT_IMAGE_NAME = "output_image.webp"


def test_process_species_image(example_images: dict[str, Path], temp_output_dir):
    """
    Test a valid image file.
    """
    input_image = example_images["image_4_3"]
    output_image = temp_output_dir / OUTPUT_IMAGE_NAME

    try:
        process_species_image(input_image, output_image)
    except Exception as e:
        pytest.fail(f"process_species_image raised an exception: {e}")

    assert output_image.exists(), "Output file was not created"


def test_warns_with_close_aspect_ratio(example_images: dict[str, Path], temp_output_dir) -> None:
    """
    Test get a warning if the aspect ratio is not ideal but close enough to 4:3.
    """
    input_image = example_images["image_close_to_4_3"]
    output_image = temp_output_dir / OUTPUT_IMAGE_NAME

    with pytest.warns(UserWarning, match="Aspect ratio is not exactly 4:3 but close enough"):
        process_species_image(input_image, output_image)


def test_fails_with_bad_aspect_ratio(example_images: dict[str, Path], temp_output_dir) -> None:
    """
    Test image with bad aspect ratio.
    """
    input_image = example_images["image_not_4_3"]
    output_image = temp_output_dir / OUTPUT_IMAGE_NAME

    with pytest.raises(ValueError, match="Input image is not formatted to be 4:3. Skipping processing."):
        process_species_image(input_image, output_image)
