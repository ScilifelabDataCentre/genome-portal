"""Shared species-specific path definitions used by add/remove scripts."""

from dataclasses import dataclass
from pathlib import Path


def get_repo_root() -> Path:
    """Repository root path shared across species tooling."""
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class SpeciesPaths:
    """All repository paths tied to one species slug (underscored lowercased binomial name)."""

    species_slug: str
    repo_root: Path
    content_dir_path: Path
    data_dir_path: Path
    assets_dir_path: Path
    config_dir_path: Path
    image_file_path: Path

    def ensure_parent_dirs(self) -> None:
        """Create species output directories needed by add_new_species."""
        for path in (
            self.content_dir_path,
            self.data_dir_path,
            self.assets_dir_path,
            self.config_dir_path,
        ):
            path.mkdir(parents=False, exist_ok=True)


def get_species_paths(species_slug: str, repo_root: Path | None = None) -> SpeciesPaths:
    """Build SpeciesPaths based on the repository root."""
    repo_root = repo_root or get_repo_root()
    image_dir_path = repo_root / "hugo" / "static" / "img" / "species"

    return SpeciesPaths(
        species_slug=species_slug,
        repo_root=repo_root,
        content_dir_path=repo_root / "hugo" / "content" / "species" / species_slug,
        data_dir_path=repo_root / "hugo" / "data" / species_slug,
        assets_dir_path=repo_root / "hugo" / "assets" / species_slug,
        config_dir_path=repo_root / "config" / species_slug,
        image_file_path=image_dir_path / f"{species_slug}.webp",
    )
