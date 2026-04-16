import gzip
from pathlib import Path

import pytest
from species_stats_utils import _prepare_agat_input_gff, normalize_filename_to_makefile_conventions, resolve_inputs


def test_normalize_filename_to_makefile_conventions_matches_make_behavior() -> None:
    assert normalize_filename_to_makefile_conventions("assembly.fasta.gz") == "assembly.fna.gz"
    assert normalize_filename_to_makefile_conventions("genes.gff3.gz") == "genes.gff.gz"
    assert normalize_filename_to_makefile_conventions("genes.gff") == "genes.gff.nozip"


def test_resolve_inputs_uses_doc1_and_protein_coding_track(tmp_path: Path) -> None:
    repo_root = tmp_path
    yaml_path = repo_root / "config" / "linum_grandiflorum" / "config.yml"
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    yaml_path.write_text(
        "\n".join(
            [
                "organism: Linum grandiflorum",
                "assembly:",
                "  fileName: Lgrand_primary_v1.fasta.gz",
                "tracks:",
                "- name: Protein-coding genes",
                "  fileName: Lgrand_primary_v1_genes.gff.gz",
                "---",
                "assembly:",
                "  fileName: should_not_be_used.fasta.gz",
                "tracks:",
                "- name: Protein-coding genes",
                "  fileName: should_not_be_used.gff.gz",
            ]
        ),
        encoding="utf-8",
    )

    expected_fasta = repo_root / "data" / "linum_grandiflorum" / "Lgrand_primary_v1.fna.gz"
    expected_gff = repo_root / "data" / "linum_grandiflorum" / "Lgrand_primary_v1_genes.gff.gz"
    expected_fasta.parent.mkdir(parents=True, exist_ok=True)
    expected_fasta.write_text(">", encoding="utf-8")
    expected_gff.write_text("##gff-version 3\n", encoding="utf-8")

    resolved = resolve_inputs(
        repo_root=repo_root,
        yaml_path=str(yaml_path),
        fasta=None,
        gff=None,
    )
    assert resolved.species_slug == "linum_grandiflorum"
    assert resolved.fasta_path == expected_fasta
    assert resolved.gff_path == expected_gff


def test_resolve_inputs_requires_protein_coding_genes_track(tmp_path: Path) -> None:
    repo_root = tmp_path
    yaml_path = repo_root / "config" / "species_x" / "config.yml"
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    yaml_path.write_text(
        "\n".join(
            [
                "assembly:",
                "  fileName: asm.fna.gz",
                "tracks:",
                "- name: RepeatMasker",
                "  fileName: repeats.bed.gz",
                "- name: Generic annotation",
                "  fileName: annotation.gff3.gz",
            ]
        ),
        encoding="utf-8",
    )
    fasta = repo_root / "data" / "species_x" / "asm.fna.gz"
    gff = repo_root / "data" / "species_x" / "annotation.gff.gz"
    fasta.parent.mkdir(parents=True, exist_ok=True)
    fasta.write_text(">", encoding="utf-8")
    gff.write_text("##gff-version 3\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Expected exactly one track named 'protein-coding genes'"):
        resolve_inputs(
            repo_root=repo_root,
            yaml_path=str(yaml_path),
            fasta=None,
            gff=None,
        )


def test_resolve_inputs_accepts_case_insensitive_protein_coding_track_name(tmp_path: Path) -> None:
    repo_root = tmp_path
    yaml_path = repo_root / "config" / "species_x" / "config.yml"
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    yaml_path.write_text(
        "\n".join(
            [
                "assembly:",
                "  fileName: asm.fna.gz",
                "tracks:",
                "- name: PROTEIN-CODING GENES",
                "  fileName: annotation.gff3.gz",
            ]
        ),
        encoding="utf-8",
    )
    fasta = repo_root / "data" / "species_x" / "asm.fna.gz"
    gff = repo_root / "data" / "species_x" / "annotation.gff.gz"
    fasta.parent.mkdir(parents=True, exist_ok=True)
    fasta.write_text(">", encoding="utf-8")
    gff.write_text("##gff-version 3\n", encoding="utf-8")

    resolved = resolve_inputs(
        repo_root=repo_root,
        yaml_path=str(yaml_path),
        fasta=None,
        gff=None,
    )
    assert resolved.gff_path == gff


def test_resolve_inputs_allows_yaml_with_gff_override(tmp_path: Path) -> None:
    repo_root = tmp_path
    yaml_path = repo_root / "config" / "species_x" / "config.yml"
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    yaml_path.write_text(
        "\n".join(
            [
                "assembly:",
                "  fileName: asm.fna.gz",
                "tracks:",
                "- name: protein-coding genes",
                "  fileName: annotation.gff.gz",
            ]
        ),
        encoding="utf-8",
    )
    fasta = repo_root / "data" / "species_x" / "asm.fna.gz"
    fasta.parent.mkdir(parents=True, exist_ok=True)
    fasta.write_text(">", encoding="utf-8")

    gff = repo_root / "data" / "species_x" / "annotation.gff.gz"
    gff.write_text("##gff-version 3\n", encoding="utf-8")
    override_gff = repo_root / "custom" / "override.gff.gz"
    override_gff.parent.mkdir(parents=True, exist_ok=True)
    override_gff.write_text("##gff-version 3\n", encoding="utf-8")

    resolved = resolve_inputs(
        repo_root=repo_root,
        yaml_path=str(yaml_path),
        fasta=None,
        gff=str(override_gff),
    )
    assert resolved.species_slug == "species_x"
    assert resolved.fasta_path == fasta
    assert resolved.gff_path == override_gff


def test_resolve_inputs_allows_yaml_with_fasta_override(tmp_path: Path) -> None:
    repo_root = tmp_path
    yaml_path = repo_root / "config" / "species_x" / "config.yml"
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    yaml_path.write_text(
        "\n".join(
            [
                "assembly:",
                "  fileName: asm.fna.gz",
                "tracks:",
                "- name: protein-coding genes",
                "  fileName: annotation.gff.gz",
            ]
        ),
        encoding="utf-8",
    )
    gff = repo_root / "data" / "species_x" / "annotation.gff.gz"
    gff.parent.mkdir(parents=True, exist_ok=True)
    gff.write_text("##gff-version 3\n", encoding="utf-8")

    fasta = repo_root / "data" / "species_x" / "asm.fna.gz"
    fasta.parent.mkdir(parents=True, exist_ok=True)
    fasta.write_text(">", encoding="utf-8")
    override_fasta = repo_root / "custom" / "override.fna.gz"
    override_fasta.parent.mkdir(parents=True, exist_ok=True)
    override_fasta.write_text(">", encoding="utf-8")

    resolved = resolve_inputs(
        repo_root=repo_root,
        yaml_path=str(yaml_path),
        fasta=str(override_fasta),
        gff=None,
    )
    assert resolved.species_slug == "species_x"
    assert resolved.fasta_path == override_fasta
    assert resolved.gff_path == gff


def test_resolve_inputs_yaml_mode_requires_existing_data_files(tmp_path: Path) -> None:
    repo_root = tmp_path
    yaml_path = repo_root / "config" / "species_x" / "config.yml"
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    yaml_path.write_text(
        "\n".join(
            [
                "assembly:",
                "  fileName: asm.fna.gz",
                "tracks:",
                "- name: protein-coding genes",
                "  fileName: annotation.gff.gz",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(FileNotFoundError, match="Could not find expected data file for species 'species_x'"):
        resolve_inputs(
            repo_root=repo_root,
            yaml_path=str(yaml_path),
            fasta=None,
            gff=None,
        )


def test_prepare_agat_input_gff_passes_through_gff_gz(tmp_path: Path) -> None:
    gff_gz = tmp_path / "annotation.gff.gz"
    with gzip.open(gff_gz, "wt", encoding="utf-8") as handle:
        handle.write("##gff-version 3\n")

    input_path, created_temp_file = _prepare_agat_input_gff(gff_path=gff_gz, temp_dir=tmp_path / "temp")
    assert input_path == gff_gz
    assert created_temp_file is False


def test_prepare_agat_input_gff_decompresses_bgz(tmp_path: Path) -> None:
    gff_bgz = tmp_path / "annotation.gff.bgz"
    with gzip.open(gff_bgz, "wt", encoding="utf-8") as handle:
        handle.write("##gff-version 3\nchr1\tsrc\tgene\t1\t10\t.\t+\t.\tID=g1\n")

    input_path, created_temp_file = _prepare_agat_input_gff(gff_path=gff_bgz, temp_dir=tmp_path / "temp")
    assert created_temp_file is True
    assert input_path != gff_bgz
    assert input_path.exists()
    assert input_path.suffix == ".gff"
    assert "##gff-version 3" in input_path.read_text(encoding="utf-8")
