"""
The download page of each species contains an info table about each of the data tracks avaialble.
This module creates a template JSON file (to fill in) for this table.

This file is stored in the assets folder and at build time, a duplicate of it is placed in the static folder.
"""

import shutil
from pathlib import Path

from add_new_species.constants import TEMPLATE_DIR

DATA_TRACKS_FILE = "data_tracks.json"


def add_data_tracks_file(assets_dir_path: Path) -> None:
    """
    Template file just copied over for now.
    """
    template_file_path = TEMPLATE_DIR / DATA_TRACKS_FILE
    output_file_path = assets_dir_path / DATA_TRACKS_FILE
    shutil.copy(template_file_path, output_file_path)
    print(f"File created: {output_file_path.resolve()}")
