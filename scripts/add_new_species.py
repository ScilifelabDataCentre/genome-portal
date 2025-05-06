"""
Use this script to create a new species entry for the website.

This script will create new folders in the Hugo content, data and assets directories.
Then template files for these directories will be added which can be filled in.
Places to fill in will be marked with: "[EDIT]"
"""

import argparse
from pathlib import Path

from add_new_species.add_content_files import add_assembly_md, add_download_md, add_index_md  # noqa
from add_new_species.add_stats_file import add_stats_file
from add_new_species.form_parser import parse_user_form
from add_new_species.image_processer import process_species_image
from add_new_species.populate_assembly_metadata_fields import populate_assembly_metadata_fields
from add_new_species.process_data_tracks_Excel import (
    extract_genome_accession,
    parse_excel_file,
    populate_data_tracks_json,
)


def run_argparse() -> argparse.Namespace:
    """
    Run argparse and return the user arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        "--user_form",
        type=str,
        metavar="[user form location]",
        help="""The path to the filled in user form, a word document.""",
        required=True,
    )

    parser.add_argument(
        "--user_spreadsheet",
        type=str,
        metavar="[user spreadsheet location]",
        help="""The path to the filled in user spreadsheet, an excel file.""",
        required=True,
    )

    parser.add_argument(
        "--sheet_name",
        type=str,
        metavar="[user spreadsheet sheet name]",
        help="""The name of the sheet in the user spreadsheet to be processed.""",
        default="Sheet1",
        required=False,
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
    config_dir_path = Path(__file__).parent / f"../config/{species_slug}"

    for path in (content_dir_path, data_dir_path, assets_dir_path, config_dir_path):
        path.mkdir(parents=False, exist_ok=True)

    return {
        "content_dir_path": content_dir_path,
        "data_dir_path": data_dir_path,
        "assets_dir_path": assets_dir_path,
        "image_dir_path": image_dir_path,
        "config_dir_path": config_dir_path,
    }


def check_dirs_empty(all_dir_paths: dict[str, Path]) -> None:
    """
    if overwrite mode not specificed, check that the folders are empty.
    Raise error if not.
    """
    # TODO - check with Daniel, should config dir be empty too?
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

    user_form_data = parse_user_form(form_file_path=Path(args.user_form))

    output_dir_paths = all_dir_paths(user_form_data.species_slug)
    if not args.overwrite:
        check_dirs_empty(all_dir_paths=output_dir_paths)

    data_tracks_list_of_dicts = parse_excel_file(
        spreadsheet_file_path=Path(args.user_spreadsheet),
        sheet_name=args.sheet_name,
    )

    add_index_md(
        species_name=user_form_data.species_name,
        species_slug=user_form_data.species_slug,
        common_name=user_form_data.common_name,
        description=user_form_data.description,
        references=user_form_data.references,
        publication=user_form_data.publication,
        img_attrib_text=user_form_data.img_attrib_text,
        img_attrib_link=user_form_data.img_attrib_link,
        content_dir_path=output_dir_paths["content_dir_path"],
        data_dir_path=output_dir_paths["data_dir_path"],
    )

    add_assembly_md(
        species_name=user_form_data.species_name,
        species_slug=user_form_data.species_slug,
        funding=user_form_data.funding,
        publication=user_form_data.publication,
        content_dir_path=output_dir_paths["content_dir_path"],
        data_dir_path=output_dir_paths["data_dir_path"],
    )

    add_download_md(
        species_slug=user_form_data.species_slug,
        content_dir_path=output_dir_paths["content_dir_path"],
    )

    add_stats_file(
        data_dir_path=output_dir_paths["data_dir_path"],
    )

    populate_data_tracks_json(data_tracks_list_of_dicts, assets_dir_path=output_dir_paths["assets_dir_path"])

    out_img_path = output_dir_paths["image_dir_path"] / f"{user_form_data.species_slug}.webp"
    process_species_image(in_img_path=Path(args.species_image), out_img_path=out_img_path)

    genome_assembly_accession = extract_genome_accession(data_tracks_list_of_dicts)

    # WIP note: this function creates and popluates config.yml
    populate_assembly_metadata_fields(
        accession=genome_assembly_accession,
        species_name=user_form_data.species_name,
        config_dir_path=output_dir_paths["config_dir_path"],
        content_dir_path=output_dir_paths["content_dir_path"],
        data_tracks_list_of_dicts=data_tracks_list_of_dicts,
    )
