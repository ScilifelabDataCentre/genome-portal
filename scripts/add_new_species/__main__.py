"""
Use this script to create a new species entry for the website.

This script will create new folders in the Hugo content, data and assets directories.
Then template files for these directories will be added which can be filled in.
Places to fill in will be marked with: "[EDIT]"
"""

import argparse
from pathlib import Path

from add_config_yml import populate_config_yml
from add_content_files import add_assembly_md, add_download_md, add_index_md
from add_stats_file import add_stats_file
from form_parser import parse_user_form
from get_assembly_metadata_from_ENA_NCBI import fetch_assembly_metadata
from image_processer import process_species_image
from process_data_tracks_Excel import parse_excel_file, populate_data_tracks_json


def run_argparse() -> argparse.Namespace:
    """
    Run argparse and return the user arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        "-f",
        "--species-submission-form",
        type=Path,
        metavar="[user form location]",
        help="The path to the filled in user form, a word document.",
        required=True,
    )

    parser.add_argument(
        "-d",
        "--data-tracks-sheet",
        type=Path,
        metavar="[user spreadsheet location]",
        help="The path to the filled in user spreadsheet, an excel file.",
        required=True,
    )

    parser.add_argument(
        "-n",
        "--data-tracks-sheet-name",
        type=str,
        metavar="[user spreadsheet sheet name]",
        help="The name of the sheet in the user spreadsheet to be processed.",
        default="Sheet1",
        required=False,
    )
    parser.add_argument(
        "-i",
        "--species-image",
        type=Path,
        metavar="[image file location]",
        help="Path to the species image to be added. The image must be 4:3 aspect ratio.",
    )

    parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        help="""If the files for the species already exist, should they be overwritten?
            If flag NOT provided, no overwrite performed.""",
    )

    return parser.parse_args()


def all_dir_paths(species_slug: str) -> dict[str, Path]:
    """
    Make a dict of all the output folder paths for the species.
    Makes sure that any folders that need to be created are created.
    """
    content_dir_path = Path(__file__).parent / f"../../hugo/content/species/{species_slug}"
    data_dir_path = Path(__file__).parent / f"../../hugo/data/{species_slug}"
    assets_dir_path = Path(__file__).parent / f"../../hugo/assets/{species_slug}"
    image_dir_path = Path(__file__).parent / "../../hugo/static/img/species"
    config_dir_path = Path(__file__).parent / f"../../config/{species_slug}"

    for path in (content_dir_path, data_dir_path, assets_dir_path, config_dir_path):
        path.mkdir(parents=False, exist_ok=True)

    return {
        "content_dir_path": content_dir_path,
        "data_dir_path": data_dir_path,
        "assets_dir_path": assets_dir_path,
        "image_dir_path": image_dir_path,
        "config_dir_path": config_dir_path,
    }


def check_dirs_empty(all_dir_paths: dict[str, Path], species_name: str) -> None:
    """
    If overwrite mode not specificed in args, check that the folders are empty.
    Raise error if not.
    """

    empty_dirs = [
        all_dir_paths["content_dir_path"],
        all_dir_paths["data_dir_path"],
        all_dir_paths["assets_dir_path"],
        all_dir_paths["config_dir_path"],
    ]
    for dir_path in empty_dirs:
        if any(dir_path.iterdir()):
            raise FileExistsError(
                f"""
                It appears that a species entry already exists for: "{species_name}",
                If you are sure you want to overwrite these files, add the flag "--overwrite".
                Exiting..."""
            )


if __name__ == "__main__":
    args = run_argparse()

    user_form_data = parse_user_form(form_file_path=args.species_submission_form)

    output_dir_paths = all_dir_paths(user_form_data.species_slug)
    if not args.overwrite:
        check_dirs_empty(all_dir_paths=output_dir_paths, species_name=user_form_data.species_name)

    user_data_tracks = parse_excel_file(
        spreadsheet_file_path=args.data_tracks_sheet,
        sheet_name=args.data_tracks_sheet_name,
    )

    assembly_metadata = fetch_assembly_metadata(
        user_data_tracks=user_data_tracks,
        species_name=user_form_data.species_name,
    )

    add_index_md(
        user_form_data=user_form_data,
        content_dir_path=output_dir_paths["content_dir_path"],
        data_dir_path=output_dir_paths["data_dir_path"],
    )

    add_assembly_md(
        user_form_data=user_form_data,
        assembly_metadata=assembly_metadata,
        content_dir_path=output_dir_paths["content_dir_path"],
    )

    add_download_md(
        species_slug=user_form_data.species_slug,
        content_dir_path=output_dir_paths["content_dir_path"],
    )

    add_stats_file(
        data_dir_path=output_dir_paths["data_dir_path"],
    )

    populate_data_tracks_json(user_data_tracks, assets_dir_path=output_dir_paths["assets_dir_path"])

    populate_config_yml(
        assembly_metadata=assembly_metadata,
        user_data_tracks=user_data_tracks,
        config_dir_path=output_dir_paths["config_dir_path"],
    )

    out_img_path = output_dir_paths["image_dir_path"] / f"{user_form_data.species_slug}.webp"
    process_species_image(in_img_path=Path(args.species_image), out_img_path=out_img_path)
