from pathlib import Path

import yaml
from add_content_files import TEMPLATE_DIR
from busco_utils import get_valid_busco_for_track

STATS_FILE = "species_stats.yml"


def add_stats_file(data_dir_path: Path, user_data_tracks: list[dict]) -> None:
    """
    Add a species_stats.yml file based on template and optional BUSCO values from the user spreadsheet.
    """
    template_file_path = TEMPLATE_DIR / STATS_FILE
    output_file_path = data_dir_path / STATS_FILE

    with open(template_file_path, "r", encoding="utf-8") as handle:
        stats_data = yaml.safe_load(handle)

    genome_busco = get_valid_busco_for_track(user_data_tracks=user_data_tracks, target_track_name="Genome")
    if genome_busco:
        for row in stats_data.get("assembly", []):
            for key in row:
                if key.startswith("BUSCO %"):
                    row[key] = genome_busco

    protein_coding_busco = get_valid_busco_for_track(
        user_data_tracks=user_data_tracks,
        target_track_name="Protein-coding genes",
    )
    if protein_coding_busco:
        stats_data.setdefault("annotation", []).append({"BUSCO % [EDIT]": protein_coding_busco})

    with open(output_file_path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(stats_data, handle, sort_keys=False, default_flow_style=False, explicit_start=True)
    print(f"File created: {output_file_path.resolve()}")
