import re

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


def normalize_track_name(track_name: str) -> str:
    return re.sub(r"[-_]", " ", track_name).strip().lower()


def get_valid_busco_for_track(user_data_tracks: list[dict], target_track_name: str) -> str | None:
    normalized_target = normalize_track_name(target_track_name)
    for track in user_data_tracks:
        track_name = str(track.get("dataTrackName", ""))
        if normalize_track_name(track_name) != normalized_target:
            continue
        busco_value = str(track.get("buscoStats", "")).strip()
        if busco_value and BUSCO_FORMAT.fullmatch(busco_value):
            return busco_value
    return None


def extract_odb_database_from_busco(busco_value: str) -> str | None:
    match = re.search(r"\(\s*([^)]+?)\s*\)\s*$", busco_value)
    if not match:
        return None
    return match.group(1)


def select_odb_database_from_tracks(user_data_tracks: list[dict]) -> str | None:
    for track_name in ("Genome", "Protein-coding genes"):
        busco_value = get_valid_busco_for_track(user_data_tracks=user_data_tracks, target_track_name=track_name)
        if busco_value:
            odb_database = extract_odb_database_from_busco(busco_value)
            if odb_database:
                return odb_database
    return None
