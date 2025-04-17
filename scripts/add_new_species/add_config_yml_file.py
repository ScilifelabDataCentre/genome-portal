"""
Submodule to copy the config.yml template to the species config directory.
config.yml is used by the data builder pipeline to download and
prepare the genomic data for display in JBrowse.
"""

import shutil
from pathlib import Path

from add_new_species.constants import TEMPLATE_DIR

CONFIG_YML_FILE = "config.yml"


def add_config_yml_file(config_dir_path: Path) -> None:
    """
    Copy config.yml template to location.
    """
    template_file_path = TEMPLATE_DIR / CONFIG_YML_FILE
    output_file_path = config_dir_path / CONFIG_YML_FILE
    shutil.copy(template_file_path, output_file_path)
    print(f"File created: {output_file_path.resolve()}")
