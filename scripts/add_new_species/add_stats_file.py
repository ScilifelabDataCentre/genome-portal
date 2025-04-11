import shutil
from pathlib import Path

from add_new_species.constants import TEMPLATE_DIR

STATS_FILE = "species_stats.yml"


def add_stats_file(data_dir_path: Path) -> None:
    """
    Add a copy of the stats template file to the correct location
    """
    template_file_path = TEMPLATE_DIR / STATS_FILE
    output_file_path = data_dir_path / STATS_FILE
    shutil.copy(template_file_path, output_file_path)
    print(f"File created: {output_file_path.resolve()}")
