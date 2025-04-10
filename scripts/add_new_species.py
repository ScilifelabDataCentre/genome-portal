"""
Use this script to create a new species entry for the website.

This script will create new folders in the Hugo content, data and assets directories.
Then template files for these directories will be added which can be filled in.
Places to fill in will be marked with: "[EDIT]"
"""

import argparse
from pathlib import Path

from add_new_species.add_content_files import add_content_files
from add_new_species.add_data_tracks_file import add_data_tracks_file
from add_new_species.add_stats_file import add_stats_file
from add_new_species.image_processer import process_species_image


def run_argparse() -> argparse.Namespace:
    """
    Run argparse and return the user arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        "--species_name",
        type=str,
        metavar="[species name]",
        help="""The scientific name of the species to be added.
            Case sensitive. Wrap the name in quotes.""",
        required=True,
    )

    parser.add_argument(
        "--species_image",
        type=str,
        metavar="[image file location]",
        help="""Path to the species image to be added. The image must be 4:3 aspect ratio.""",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="""If the files for the species already exist, should they be overwritten?
            If flag NOT provided, no overwrite performed.""",
    )

    return parser.parse_args()


def all_dir_paths(species_slug: str) -> dict[str, Path]:
    """
    make a dict of all the output folder paths for the species.
    Makes sure that any folders that need to be created are created.
    """
    content_dir_path = Path(__file__).parent / f"../hugo/content/species/{species_slug}"
    data_dir_path = Path(__file__).parent / f"../hugo/data/{species_slug}"
    assets_dir_path = Path(__file__).parent / f"../hugo/assets/{species_slug}"
    image_dir_path = Path(__file__).parent / "../hugo/static/img/species"

    for path in (content_dir_path, data_dir_path, assets_dir_path):
        path.mkdir(parents=False, exist_ok=True)

    return {
        "content_dir_path": content_dir_path,
        "data_dir_path": data_dir_path,
        "assets_dir_path": assets_dir_path,
        "image_dir_path": image_dir_path,
    }


def check_dirs_empty(all_dir_paths: dict[str, Path]) -> None:
    """
    if overwrite mode not specificed, check that the folders are empty.
    Raise error if not.
    """
    empty_dirs = [all_dir_paths["content_dir_path"], all_dir_paths["data_dir_path"], all_dir_paths["assets_dir_path"]]
    for dir_path in empty_dirs:
        if any(dir_path.iterdir()):
            raise FileExistsError(
                f"""
                It appears that a species entry already exists for: "{args.species_name}",
                If you are sure you want to overwrite these files, add the flag "--overwrite".
                Exiting..."""
            )


if __name__ == "__main__":
    args = run_argparse()

    species_slug = args.species_name.replace(" ", "_").lower()
    output_dir_paths = all_dir_paths(species_slug)

    if not args.overwrite:
        check_dirs_empty(all_dir_paths=output_dir_paths)

    out_img_path = output_dir_paths["image_dir_path"] / f"{species_slug}.webp"
    process_species_image(in_img_path=Path(args.species_image), out_img_path=out_img_path)

    add_content_files(
        species_name=args.species_name,
        species_slug=species_slug,
        content_dir_path=output_dir_paths["content_dir_path"],
        data_dir_path=output_dir_paths["data_dir_path"],
    )

    add_stats_file(
        data_dir_path=output_dir_paths["data_dir_path"],
    )

    add_data_tracks_file(
        assets_dir_path=output_dir_paths["assets_dir_path"],
    )
