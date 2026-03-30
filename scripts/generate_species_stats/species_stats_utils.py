import gzip
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import yaml

ZIP_EXTENSIONS = {"gz", "zip", "bgz"}
TRACK_EXTENSION_NORMALIZATION = {
    "fasta": "fna",
    "fa": "fna",
    "gff3": "gff",
}  # Map file type extensions synonyms to the standardized extension given by the makefile


@dataclass
class ResolvedInputs:
    species_slug: str
    fasta_path: Path
    gff_path: Path
    yaml_path: Path


@dataclass
class WorkDirs:
    base_dir: Path
    temp_dir: Path
    quast_logs_dir: Path
    agat_logs_dir: Path


def _get_work_dirs(base_dir: Path) -> WorkDirs:
    """Get the working directories for temporary files and logs, creating them if they don't exist."""
    temp_dir = base_dir / "temp"
    quast_logs_dir = base_dir / "logs" / "quast"
    agat_logs_dir = base_dir / "logs" / "agat"
    temp_dir.mkdir(parents=True, exist_ok=True)
    quast_logs_dir.mkdir(parents=True, exist_ok=True)
    agat_logs_dir.mkdir(parents=True, exist_ok=True)

    return WorkDirs(
        base_dir=base_dir,
        temp_dir=temp_dir,
        quast_logs_dir=quast_logs_dir,
        agat_logs_dir=agat_logs_dir,
    )


def _prepare_output_dir(output_dir: Path, force: bool) -> None:
    """
    Prepare the output directory for a tool run.
    As a workaround when a tool does not support force/overwrite, delete the existing outpur dir if force=True
    """
    if output_dir.exists():
        if force:
            shutil.rmtree(output_dir)
        else:
            raise FileExistsError(
                f"Output directory already exists: {output_dir}. "
                "Re-run with --force to overwrite existing tool outputs."
            )
    output_dir.parent.mkdir(parents=True, exist_ok=True)


def _prepare_agat_input_gff(gff_path: Path, temp_dir: Path) -> tuple[Path, bool]:
    """Return an AGAT-compatible GFF path.

    AGAT can consume plain `.gff` and typically `.gff.gz` directly in our environment.
    For `.bgz` inputs, create a temporary decompressed `.gff` and return that path.
    The boolean indicates whether a temp file was created and should be cleaned up.
    """
    if gff_path.suffix != ".bgz":
        return gff_path, False

    temp_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=temp_dir,
        prefix=f"{gff_path.stem}.",
        suffix=".gff",
        delete=False,
    ) as handle:
        temp_path = Path(handle.name)
    with gzip.open(gff_path, "rb") as source, open(temp_path, "wb") as target:
        shutil.copyfileobj(source, target)
    return temp_path, True


def normalize_filename_to_makefile_conventions(filename: str) -> str:
    """Normalize a filename by standardizing known track extensions to match the makefile behaviorand ensuring it ends with a recognized zip extension."""
    normalized_filename = filename
    for original_ext, std_ext in TRACK_EXTENSION_NORMALIZATION.items():
        pattern = rf"\.{re.escape(original_ext)}(?=\.|$)"
        if re.search(pattern, normalized_filename):
            normalized_filename = re.sub(pattern, f".{std_ext}", normalized_filename, count=1)
            break

    last_ext = normalized_filename.rsplit(".", 1)[-1] if "." in normalized_filename else normalized_filename
    if last_ext not in ZIP_EXTENSIONS:
        normalized_filename = f"{normalized_filename}.nozip"
    return normalized_filename


def load_yaml_documents(yaml_path: Path) -> list[dict]:
    """Config.yml may contain one or more YAML documents. Load and return them as a list of dicts."""
    with open(yaml_path, "r", encoding="utf-8") as handle:
        docs = list(yaml.safe_load_all(handle))
    docs = [doc for doc in docs if doc]
    if not docs:
        raise ValueError(f"No YAML documents found in {yaml_path}")
    return docs


def _get_filename_from_yaml_entry(entry: dict) -> str:
    """Extract a filename from a YAML entry, which may have either a "fileName" or "url" field.
    The "fileName" field takes precedence if both are present.
    """
    file_name = entry.get("fileName")
    if file_name:
        return str(file_name)

    url = entry.get("url")
    if not url:
        raise ValueError("Expected either fileName or url in config entry.")

    parsed = urlparse(str(url))
    basename = Path(parsed.path).name
    if not basename:
        raise ValueError(f"Could not derive filename from url: {url}")
    return basename


def get_annotation_track_filename(config_doc: dict) -> str:
    """From the first YAML document, find the track named "protein coding genes" and return its filename."""
    tracks = config_doc.get("tracks", [])
    if not isinstance(tracks, list) or not tracks:
        raise ValueError("No tracks found in YAML document 1.")

    expected_name = "protein coding genes"
    matching_tracks: list[dict] = []
    for track in tracks:
        raw_name = str(track.get("name", ""))
        normalized_name = re.sub(r"[-_]", " ", raw_name)
        normalized_name = re.sub(r"\s+", " ", normalized_name).strip().lower()
        if normalized_name == expected_name:
            matching_tracks.append(track)

    if len(matching_tracks) == 1:
        annotation_file_name = _get_filename_from_yaml_entry(entry=matching_tracks[0])
        return annotation_file_name
    if not matching_tracks:
        raise ValueError("Expected exactly one track named 'protein-coding genes' in YAML document 1.")

    raise ValueError("Found multiple tracks named 'protein-coding genes' in YAML document 1.")


def _resolve_data_path(repo_root: Path, species_slug: str, file_name: str) -> Path:
    """Given a species slug and a filename, resolve to the expected data path under the repo,
    trying both the original and normalized filename."""
    data_dir = repo_root / "data" / species_slug
    normalized = normalize_filename_to_makefile_conventions(file_name)
    # Check both the normalized and original filename, since the makefile may have renamed the file with a normalized name but the YAML may still reference the original name.
    candidates = [data_dir / normalized, data_dir / file_name]
    for candidate in candidates:
        if candidate.exists():
            # Return the first candidate that exists, i.e. prioritize the normalized filename if it exists, otherwise fall back to the original filename if it exists.
            return candidate
    raise FileNotFoundError(
        f"Could not find expected data file for species '{species_slug}': "
        f"checked {candidates[0]} and {candidates[1]}"
    )


def _resolve_relative_or_absolute_path(path_str: str, *, repo_root: Path, fallback_to_cwd: bool) -> Path:
    """Resolve a path string that may be either absolute or relative. If relative, first resolve against
    the repo root, then optionally against the current working directory if not found in the repo."""
    path = Path(path_str)
    if path.is_absolute():
        return path

    repo_relative = repo_root / path
    if repo_relative.exists():
        return repo_relative
    if fallback_to_cwd:
        return (Path.cwd() / path).resolve()
    return repo_relative.resolve()


def resolve_inputs(
    repo_root: Path,
    yaml_path: str,
    fasta: str | None,
    gff: str | None,
) -> ResolvedInputs:
    """Resolve input paths and species slug from YAML, with optional fasta/gff overrides."""

    yaml_path_obj = _resolve_relative_or_absolute_path(path_str=yaml_path, repo_root=repo_root, fallback_to_cwd=False)
    resolved_slug = yaml_path_obj.parent.name
    docs = load_yaml_documents(yaml_path_obj)
    doc1 = docs[0]

    if "assembly" not in doc1:
        raise ValueError(f"YAML document 1 has no 'assembly' section: {yaml_path_obj}")

    assembly_file_name = _get_filename_from_yaml_entry(entry=doc1["assembly"])
    annotation_file_name = get_annotation_track_filename(config_doc=doc1)

    # If fasta/gff overrides are provided, resolve them as either absolute paths or paths relative to the repo root
    # If no overrides are provided, resolve the expected data paths based on the species slug and filenames from the YAML.
    if fasta:
        fasta_path = _resolve_relative_or_absolute_path(path_str=fasta, repo_root=repo_root, fallback_to_cwd=True)
    else:
        fasta_path = _resolve_data_path(
            repo_root=repo_root,
            species_slug=resolved_slug,
            file_name=assembly_file_name,
        )
    if gff:
        gff_path = _resolve_relative_or_absolute_path(path_str=gff, repo_root=repo_root, fallback_to_cwd=True)
    else:
        gff_path = _resolve_data_path(
            repo_root=repo_root,
            species_slug=resolved_slug,
            file_name=annotation_file_name,
        )

    return ResolvedInputs(
        species_slug=resolved_slug,
        fasta_path=fasta_path,
        gff_path=gff_path,
        yaml_path=yaml_path_obj,
    )
