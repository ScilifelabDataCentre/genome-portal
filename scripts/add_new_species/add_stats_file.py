import re
from pathlib import Path

import yaml
from add_content_files import TEMPLATE_DIR

STATS_FILE = "species_stats.yml"
# BUSCO short format used in Genome Portal: C:% [S:%, D:%], F:%, M:%, n: (odb_database_version)
BUSCO_NUMERIC = r"(?:\d+(?:\.\d+)?)"
BUSCO_FORMAT = re.compile(
    rf"""
    ^\s*
    C\s*:\s*{BUSCO_NUMERIC}\s*%\s*
    \[\s*S\s*:\s*{BUSCO_NUMERIC}\s*%\s*,\s*D\s*:\s*{BUSCO_NUMERIC}\s*%\s*\]\s*,\s*
    F\s*:\s*{BUSCO_NUMERIC}\s*%\s*,\s*
    M\s*:\s*{BUSCO_NUMERIC}\s*%\s*,\s*
    n\s*:\s*\d+\s*
    \(\s*[^)]+\s*\)\s*
    $
    """,
    flags=re.VERBOSE,
)


def _normalize_track_name(track_name: str) -> str:
    return re.sub(r"[-_]", " ", track_name).strip().lower()


def _get_valid_busco_for_track(user_data_tracks: list[dict], target_track_name: str) -> str | None:
    normalized_target = _normalize_track_name(target_track_name)
    for track in user_data_tracks:
        track_name = str(track.get("dataTrackName", ""))
        if _normalize_track_name(track_name) != normalized_target:
            continue
        busco_value = str(track.get("buscoStats", "")).strip()
        if busco_value and BUSCO_FORMAT.fullmatch(busco_value):
            return busco_value
    return None


def add_stats_file(data_dir_path: Path, user_data_tracks: list[dict]) -> None:
    """
    Add a species_stats.yml file based on template and optional BUSCO values from the user spreadsheet.
    """
    template_file_path = TEMPLATE_DIR / STATS_FILE
    output_file_path = data_dir_path / STATS_FILE

    with open(template_file_path, "r", encoding="utf-8") as handle:
        stats_data = yaml.safe_load(handle)

    genome_busco = _get_valid_busco_for_track(user_data_tracks=user_data_tracks, target_track_name="Genome")
    if genome_busco:
        for row in stats_data.get("assembly", []):
            for key in row:
                if key.startswith("BUSCO %"):
                    row[key] = genome_busco

    protein_coding_busco = _get_valid_busco_for_track(
        user_data_tracks=user_data_tracks,
        target_track_name="Protein-coding genes",
    )
    if protein_coding_busco:
        stats_data.setdefault("annotation", []).append({"BUSCO % [EDIT]": protein_coding_busco})

    with open(output_file_path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(stats_data, handle, sort_keys=False, default_flow_style=False, explicit_start=True)
    print(f"File created: {output_file_path.resolve()}")
