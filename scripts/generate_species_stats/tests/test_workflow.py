import subprocess
from pathlib import Path

import pytest
import workflow
import yaml
from workflow import WorkflowOptions, run_stats_workflow


def _write_template(repo_root: Path) -> None:
    template = repo_root / "scripts" / "add_new_species" / "templates" / "species_stats.yml"
    template.parent.mkdir(parents=True, exist_ok=True)
    template.write_text(
        "\n".join(
            [
                "---",
                "assembly:",
                '  - "Assembly length (Mbp)": [EDIT]',
                '  - "GC %": [EDIT]',
                "annotation:",
                '  - "Gene #": [EDIT]',
            ]
        ),
        encoding="utf-8",
    )


def _write_quast_report(output_dir: Path, assembly_mbp: int = 2_000_000, gc: str = "39.1") -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "report.tsv").write_text(
        "\n".join(
            [
                f"Total length (>= 0 bp)\t{assembly_mbp}",
                f"GC (%)\t{gc}",
                "contigs (>= 0 bp)\t22",
                "N50\t234000",
                "L50\t8",
                "N90\t20000",
                "L90\t20",
                "contigs (>= 10000 bp)\t7",
            ]
        ),
        encoding="utf-8",
    )


def _write_agat_report(output_dir: Path, gene_count: str = "123") -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "stat_features.txt").write_text(
        "\n".join(
            [
                f"Number of gene {gene_count}",
                "Number of mrna 456",
                "mean exons per mrna 7.3",
                "mean gene length (bp) 890",
                "mean mrna length (bp) 901",
                "mean exon length (bp) 45",
                "mean intron length (bp) 67",
            ]
        ),
        encoding="utf-8",
    )


def _options(repo_root: Path, work_base: Path, *, skip_quast: bool = False, skip_agat: bool = False) -> WorkflowOptions:
    return WorkflowOptions(
        repo_root=repo_root,
        species_slug="species_x",
        fasta_path=repo_root / "data" / "species_x" / "assembly.fna.gz",
        gff_path=repo_root / "data" / "species_x" / "annotation.gff.gz",
        script_base_dir=work_base,
        skip_quast=skip_quast,
        skip_agat=skip_agat,
        force=False,
    )


def test_full_run_publishes_and_cleans_temp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = tmp_path
    _write_template(repo_root)
    fasta = repo_root / "data" / "species_x" / "assembly.fna.gz"
    gff = repo_root / "data" / "species_x" / "annotation.gff.gz"
    fasta.parent.mkdir(parents=True, exist_ok=True)
    fasta.write_text(">", encoding="utf-8")
    gff.write_text("##gff-version 3\n", encoding="utf-8")

    monkeypatch.setattr(workflow, "run_quast", lambda fasta_path, output_dir, force: _write_quast_report(output_dir))
    monkeypatch.setattr(
        workflow, "run_agat", lambda gff_path, output_dir, force, temp_dir: _write_agat_report(output_dir)
    )

    destination_display, unresolved = run_stats_workflow(_options(repo_root, tmp_path / "work"))
    assert destination_display == "hugo/data/species_x/species_stats.yml"
    destination = repo_root / "hugo" / "data" / "species_x" / "species_stats.yml"
    assert destination.exists()
    assert not unresolved

    with open(destination, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    assert data["assembly"][0]["Assembly length (Mbp)"] == "2.00"
    assert data["annotation"][0]["Gene #"] == "123"

    temp_files = list((tmp_path / "work" / "temp").glob("species_stats_*.yml"))
    assert not temp_files


def test_skip_quast_uses_existing_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = tmp_path
    _write_template(repo_root)
    fasta = repo_root / "data" / "species_x" / "assembly.fna.gz"
    gff = repo_root / "data" / "species_x" / "annotation.gff.gz"
    fasta.parent.mkdir(parents=True, exist_ok=True)
    fasta.write_text(">", encoding="utf-8")
    gff.write_text("##gff-version 3\n", encoding="utf-8")

    work_base = tmp_path / "work"
    cached_quast_dir = work_base / "logs" / "quast" / "assembly.fna.gz"
    _write_quast_report(cached_quast_dir, assembly_mbp=4_000_000, gc="41.2")

    monkeypatch.setattr(
        workflow,
        "run_quast",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("run_quast should not be called")),
    )
    monkeypatch.setattr(
        workflow, "run_agat", lambda gff_path, output_dir, force, temp_dir: _write_agat_report(output_dir)
    )

    _, _ = run_stats_workflow(_options(repo_root, work_base, skip_quast=True))
    destination = repo_root / "hugo" / "data" / "species_x" / "species_stats.yml"
    with open(destination, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    assert data["assembly"][0]["Assembly length (Mbp)"] == "4.00"


def test_skip_agat_missing_cache_keeps_placeholder(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = tmp_path
    _write_template(repo_root)
    fasta = repo_root / "data" / "species_x" / "assembly.fna.gz"
    gff = repo_root / "data" / "species_x" / "annotation.gff.gz"
    fasta.parent.mkdir(parents=True, exist_ok=True)
    fasta.write_text(">", encoding="utf-8")
    gff.write_text("##gff-version 3\n", encoding="utf-8")

    monkeypatch.setattr(workflow, "run_quast", lambda fasta_path, output_dir, force: _write_quast_report(output_dir))
    monkeypatch.setattr(
        workflow,
        "run_agat",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("run_agat should not be called")),
    )

    _, unresolved = run_stats_workflow(_options(repo_root, tmp_path / "work", skip_agat=True))
    destination = repo_root / "hugo" / "data" / "species_x" / "species_stats.yml"
    with open(destination, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    assert data["annotation"][0]["Gene #"] == ["EDIT"]
    assert "Gene #" in unresolved


def test_failure_does_not_overwrite_existing_destination(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = tmp_path
    _write_template(repo_root)
    fasta = repo_root / "data" / "species_x" / "assembly.fna.gz"
    gff = repo_root / "data" / "species_x" / "annotation.gff.gz"
    fasta.parent.mkdir(parents=True, exist_ok=True)
    fasta.write_text(">", encoding="utf-8")
    gff.write_text("##gff-version 3\n", encoding="utf-8")

    destination = repo_root / "hugo" / "data" / "species_x" / "species_stats.yml"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("sentinel", encoding="utf-8")

    def fail_quast(fasta_path: Path, output_dir: Path, force: bool) -> None:
        raise subprocess.CalledProcessError(returncode=1, cmd="quast")

    monkeypatch.setattr(workflow, "run_quast", fail_quast)

    with pytest.raises(subprocess.CalledProcessError):
        run_stats_workflow(_options(repo_root, tmp_path / "work"))

    assert destination.read_text(encoding="utf-8") == "sentinel"


def test_existing_quast_cache_is_reused_without_skip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = tmp_path
    _write_template(repo_root)
    fasta = repo_root / "data" / "species_x" / "assembly.fna.gz"
    gff = repo_root / "data" / "species_x" / "annotation.gff.gz"
    fasta.parent.mkdir(parents=True, exist_ok=True)
    fasta.write_text(">", encoding="utf-8")
    gff.write_text("##gff-version 3\n", encoding="utf-8")

    work_base = tmp_path / "work"
    cached_quast_dir = work_base / "logs" / "quast" / "assembly.fna.gz"
    _write_quast_report(cached_quast_dir, assembly_mbp=5_000_000, gc="42.2")

    monkeypatch.setattr(
        workflow,
        "run_quast",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("run_quast should not be called")),
    )
    monkeypatch.setattr(
        workflow, "run_agat", lambda gff_path, output_dir, force, temp_dir: _write_agat_report(output_dir)
    )

    _, _ = run_stats_workflow(_options(repo_root, work_base, skip_quast=False))
    destination = repo_root / "hugo" / "data" / "species_x" / "species_stats.yml"
    with open(destination, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    assert data["assembly"][0]["Assembly length (Mbp)"] == "5.00"


def test_run_agat_uses_temp_dir_as_cwd(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gff = tmp_path / "annotation.gff"
    gff.write_text("##gff-version 3\n", encoding="utf-8")
    output_dir = tmp_path / "logs" / "agat" / "annotation"
    temp_dir = tmp_path / "temp"

    captured: dict[str, Path] = {}

    def fake_run(cmd: list[str], check: bool, cwd: Path) -> None:
        captured["cwd"] = cwd
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "stat_features.txt").write_text("Number of gene 1\n", encoding="utf-8")

    monkeypatch.setattr("workflow.subprocess.run", fake_run)
    workflow.run_agat(gff_path=gff, output_dir=output_dir, force=False, temp_dir=temp_dir)

    assert captured["cwd"] == temp_dir


def test_existing_hugo_species_stats_template_is_preferred_and_preserves_busco_rows(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = tmp_path
    _write_template(repo_root)

    destination = repo_root / "hugo" / "data" / "species_x" / "species_stats.yml"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        "\n".join(
            [
                "---",
                "assembly:",
                '  - "Assembly length (Mbp)": [EDIT]',
                '  - "GC %": [EDIT]',
                '  - "BUSCO % [EDIT]": "C:99% [S:98%, D:1%], F:0.5%, M:0.5%, n:5286 (odb)"',
                "annotation:",
                '  - "Gene #": [EDIT]',
                '  - "BUSCO % [EDIT]": "C:98% [S:96%, D:2%], F:1.0%, M:1.0%, n:255 (odb)"',
            ]
        ),
        encoding="utf-8",
    )

    fasta = repo_root / "data" / "species_x" / "assembly.fna.gz"
    gff = repo_root / "data" / "species_x" / "annotation.gff.gz"
    fasta.parent.mkdir(parents=True, exist_ok=True)
    fasta.write_text(">", encoding="utf-8")
    gff.write_text("##gff-version 3\n", encoding="utf-8")

    monkeypatch.setattr(workflow, "run_quast", lambda fasta_path, output_dir, force: _write_quast_report(output_dir))
    monkeypatch.setattr(
        workflow, "run_agat", lambda gff_path, output_dir, force, temp_dir: _write_agat_report(output_dir)
    )

    run_stats_workflow(_options(repo_root, tmp_path / "work"))
    with open(destination, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    assert data["assembly"][0]["Assembly length (Mbp)"] == "2.00"
    assert data["annotation"][0]["Gene #"] == "123"
    assert data["assembly"][-1]["BUSCO % [EDIT]"] == "C:99% [S:98%, D:1%], F:0.5%, M:0.5%, n:5286 (odb)"
    assert data["annotation"][-1]["BUSCO % [EDIT]"] == "C:98% [S:96%, D:2%], F:1.0%, M:1.0%, n:255 (odb)"
