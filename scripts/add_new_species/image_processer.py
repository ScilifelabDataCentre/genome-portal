"""
Submodule to handle the processing of the species image.

Each species image is to be:
- formatted 4:3,
- have Webp format
- have size less than cutoff defined in MAX_SIZE_KB
"""

import io
import warnings
from pathlib import Path

from PIL import Image

MAX_SIZE_KB = 500  # Maximum size in KB for the output image
MIN_WEBP_QUALITY = 0  # Minimum quality score for webp conversion


def process_species_image(in_img_path: Path, out_img_path: Path):
    """
    Process image from start to finish:
    - Check image is 4:3
    - save as webp format under MAX SIZE_LIMIT
    """
    ori_image = Image.open(in_img_path)

    if not image_4_by_3(ori_image.size):
        raise ValueError("Input image is not formatted to be 4:3. Skipping processing.")

    convert_save_webp(ori_image, out_img_path)

    print(f"Species image saved to {out_img_path}")


def image_4_by_3(size: tuple[int, int]) -> bool:
    """
    Validate image is 4:3 or very close to it.
    """
    width, height = size
    aspect_ratio = round(width / height, 2)

    if aspect_ratio == 1.33:
        return True

    elif 1.3 <= aspect_ratio <= 1.36:
        warnings.warn(
            message=f"Aspect ratio is not exactly 4:3 but close enough ({aspect_ratio:.2f}). "
            "Please verify the image looks correct.",
            category=UserWarning,
            stacklevel=2,
        )
        return True

    return False


def convert_save_webp(ori_image: Image.Image, target_path: Path) -> None:
    """
    Convert image to webp format, making sure the image size is less than max allowed size.
    Notes: quality is between 0 and 100, with 100 being the best quality.

    Size check is done by writing the image to a memory and checking its size.
    So output image only saved IF the size is less than max allowed size.
    """
    quality = 100
    while quality > MIN_WEBP_QUALITY:
        buffer = io.BytesIO()
        ori_image.save(buffer, format="webp", quality=quality)
        size_kb = buffer.tell() / 1024

        if size_kb <= MAX_SIZE_KB:
            with open(target_path, "wb") as f:
                f.write(buffer.getvalue())
            return

        quality -= 5

    raise ValueError(
        f"Failed to save the species image under the size limit of {MAX_SIZE_KB} KB. "
        "Consider compressing the image first or manully increasing the size limit."
    )
