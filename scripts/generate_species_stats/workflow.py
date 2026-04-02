import logging
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from species_stats_utils import _get_work_dirs, _prepare_agat_input_gff, _prepare_output_dir
from stats_parsers import extract_template_metric_keys, parse_agat_report, parse_quast_report, render_stats_yaml

logger = logging.getLogger(__name__)


@dataclass
class WorkflowOptions:
    repo_root: Path
    species_slug: str
    fasta_path: Path
    gff_path: Path
    script_base_dir: Path
    skip_quast: bool
    skip_agat: bool
    force: bool


def _safe_name(value: str) -> str:
    """Convert a string to a safe filename by replacing non-alphanumeric characters with underscores."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value)


def _display_path(path: Path, repo_root: Path) -> str:
    """
    Return a user-friendly string representation of a path, relative to the repo root if possible.
    Ensures that if the script is run in with dockeraddnewspecies, the path does not include swedgene/.
    """
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def _agat_log_name(gff_path: Path) -> str:
    name = gff_path.name
    for suffix in (".gff.bgz", ".gff.gz", ".gff.nozip", ".gff3.bgz", ".gff3.gz", ".gff3", ".gff"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return gff_path.stem


def _warn_if_stale_report(report_path: Path, input_path: Path, label: str, repo_root: Path) -> None:
    """Log a warning if the report file is older than the input file, indicating that the cached report may be stale."""
    if not report_path.exists() or not input_path.exists():
        return
    if report_path.stat().st_mtime < input_path.stat().st_mtime:
        logger.warning(
            "Using stale %s cache: report %s is older than input %s.",
            label,
            _display_path(report_path, repo_root),
            _display_path(input_path, repo_root),
        )


def _publish_output_file_to_hugo_dir(temp_output: Path, destination: Path) -> None:
    """Move the generated species_stats.yml from the temporary location to the Hugo data directory, creating parent directories if needed."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination_tmp = destination.with_suffix(f"{destination.suffix}.tmp")
    shutil.copy2(temp_output, destination_tmp)
    # Atomic replacement to avoid issues with Hugo reading a partially written file.
    destination_tmp.replace(destination)


def _read_cached_report_or_placeholder(
    skip: bool,
    report_path: Path,
    input_path: Path,
    force: bool,
    output_dir: Path,
    tool_name: str,
    repo_root: Path,
    parse_report: Callable[[Path], dict[str, str | None]],
) -> dict[str, str | None] | None:
    """Check if we can use a cached report or if we need to run the tool.
    If --skip is requested, return cached stats or placeholders.
    If not skipping, return cached stats if valid, otherwise None to indicate the tool needs to be run.
    """

    if skip:
        if report_path.exists():
            _warn_if_stale_report(report_path, input_path, tool_name, repo_root)
            return parse_report(report_path)
        logger.warning(
            "--skip-%s requested, but no previous %s report found at %s. Using placeholders.",
            tool_name.lower(),
            tool_name,
            _display_path(report_path, repo_root),
        )
        return {}

    if report_path.exists() and not force:
        logger.warning(
            "%s output already exists at %s. Reusing cached report. Use --force to regenerate.",
            tool_name,
            _display_path(output_dir, repo_root),
        )
        _warn_if_stale_report(report_path, input_path, tool_name, repo_root)
        return parse_report(report_path)

    return None


def run_quast(fasta_path: Path, output_dir: Path, force: bool) -> None:
    """Run Quast on the given FASTA file, writing output to the specified directory."""

    _prepare_output_dir(output_dir=output_dir, force=force)

    cmd = [
        "quast",
        "--split-scaffolds",
        str(fasta_path),
        "--min-contig",
        "0",
        "--no-plots",
        "--no-html",
        "--output-dir",
        str(output_dir),
    ]
    subprocess.run(cmd, check=True)


def run_agat(gff_path: Path, output_dir: Path, force: bool, temp_dir: Path) -> None:
    """Run AGAT functional statistics on the given GFF file, writing output to the specified directory."""

    _prepare_output_dir(output_dir=output_dir, force=force)

    temp_dir.mkdir(parents=True, exist_ok=True)
    gff_input_path, created_temp_file = _prepare_agat_input_gff(gff_path, temp_dir)
    try:
        cmd = [
            "agat_sp_functional_statistics.pl",
            "--gff",
            str(gff_input_path),
            "--output",
            str(output_dir),
        ]
        subprocess.run(cmd, check=True, cwd=temp_dir)
    finally:
        if created_temp_file and gff_input_path.exists():
            gff_input_path.unlink()


def _collect_quast_stats(
    skip_quast: bool,
    quast_report: Path,
    fasta_path: Path,
    quast_dir: Path,
    force: bool,
    repo_root: Path,
) -> dict[str, str | None]:
    """Collect Quast statistics, either by parsing an existing report or by running Quast if needed."""

    cached_stats = _read_cached_report_or_placeholder(
        skip=skip_quast,
        report_path=quast_report,
        input_path=fasta_path,
        force=force,
        output_dir=quast_dir,
        tool_name="Quast",
        repo_root=repo_root,
        parse_report=parse_quast_report,
    )
    if cached_stats is not None:
        return cached_stats

    if not fasta_path.exists():
        raise FileNotFoundError(f"Quast input file not found: {_display_path(fasta_path, repo_root)}")

    # Handle the case where the output directory exists but the report is missing.
    if quast_dir.exists() and not force:
        logger.warning(
            "Quast output directory exists but no report found at %s. Cleaning and forcing a re-run of Quast.",
            _display_path(quast_report, repo_root),
        )
    effective_force = force or quast_dir.exists()

    logger.info("Running Quast on %s", _display_path(fasta_path, repo_root))
    run_quast(fasta_path=fasta_path, output_dir=quast_dir, force=effective_force)

    return parse_quast_report(quast_report)


def _collect_agat_stats(
    skip_agat: bool,
    agat_report: Path,
    gff_path: Path,
    agat_dir: Path,
    force: bool,
    temp_dir: Path,
    repo_root: Path,
) -> dict[str, str | None]:
    """Collect AGAT statistics, either by parsing an existing report or by running AGAT if needed."""

    cached_stats = _read_cached_report_or_placeholder(
        skip=skip_agat,
        report_path=agat_report,
        input_path=gff_path,
        force=force,
        output_dir=agat_dir,
        tool_name="AGAT",
        repo_root=repo_root,
        parse_report=parse_agat_report,
    )
    if cached_stats is not None:
        return cached_stats

    if not gff_path.exists():
        raise FileNotFoundError(f"AGAT input file not found: {_display_path(gff_path, repo_root)}")

    # Handle the case where the output directory exists but the report is missing.
    if agat_dir.exists() and not force:
        logger.warning(
            "AGAT output directory exists but no report found at %s. Cleaning and forcing a re-run of AGAT.",
            _display_path(agat_report, repo_root),
        )
    effective_force = force or agat_dir.exists()

    logger.info("Running AGAT on %s", _display_path(gff_path, repo_root))
    run_agat(gff_path=gff_path, output_dir=agat_dir, force=effective_force, temp_dir=temp_dir)

    return parse_agat_report(agat_report)


def run_stats_workflow(options: WorkflowOptions) -> tuple[str, list[str]]:
    """Run the full workflow to generate species stats. Returns the display path of the published stats file and a list of any unresolved placeholders."""

    work_dirs = _get_work_dirs(base_dir=options.script_base_dir)

    quast_log_key = options.fasta_path.name
    agat_log_key = _agat_log_name(options.gff_path)
    quast_dir = work_dirs.quast_logs_dir / _safe_name(quast_log_key)
    quast_report = quast_dir / "report.tsv"
    agat_dir = work_dirs.agat_logs_dir / _safe_name(agat_log_key)
    agat_report = agat_dir / "stat_features.txt"

    quast_stats = _collect_quast_stats(
        skip_quast=options.skip_quast,
        quast_report=quast_report,
        fasta_path=options.fasta_path,
        quast_dir=quast_dir,
        force=options.force,
        repo_root=options.repo_root,
    )

    agat_stats = _collect_agat_stats(
        skip_agat=options.skip_agat,
        agat_report=agat_report,
        gff_path=options.gff_path,
        agat_dir=agat_dir,
        force=options.force,
        temp_dir=work_dirs.temp_dir,
        repo_root=options.repo_root,
    )

    # Prefer existing hugo/data species_stats.yml as template source (preserves BUSCO/custom rows),
    # then fall back to the canonical add_new_species template.
    output_file_destination = options.repo_root / "hugo" / "data" / options.species_slug / "species_stats.yml"
    canonical_template_path = options.repo_root / "scripts" / "add_new_species" / "templates" / "species_stats.yml"
    template_path = output_file_destination if output_file_destination.exists() else canonical_template_path

    # Use selected species_stats.yml template as source of truth for which metrics to include in the final report.
    template_keys = extract_template_metric_keys(template_path=template_path)
    combined_values: dict[str, str | None] = {key: None for key in template_keys}
    combined_values.update(quast_stats)
    combined_values.update(agat_stats)

    temp_output = work_dirs.temp_dir / f"species_stats_{options.species_slug}.yml"

    unresolved_placeholders = render_stats_yaml(
        template_path=template_path, output_path=temp_output, values=combined_values
    )

    _publish_output_file_to_hugo_dir(temp_output=temp_output, destination=output_file_destination)
    if temp_output.exists():
        temp_output.unlink()

    display_destination = _display_path(path=output_file_destination, repo_root=options.repo_root)
    return display_destination, unresolved_placeholders
