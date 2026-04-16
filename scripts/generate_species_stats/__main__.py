"""
Package to create a species_stats.yml file for a species based on a config.yml file and the assembly FASTA and annotation GFF.


Usage:
    python -m generate_species_stats --yaml config/<species>/config.yml

    Optional overrides:
    --fasta path/to/assembly.fasta
    --gff path/to/annotation.gff

    Optional flags:
    --skip-quast
    --skip-agat
    --force

"""

import argparse
import sys
from pathlib import Path

from species_stats_utils import resolve_inputs
from workflow import WorkflowOptions, run_stats_workflow

MODULE_DIR = Path(__file__).resolve().parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate assembly/annotation statistics and publish species_stats.yml.",
    )
    parser.add_argument(
        "--yaml",
        required=True,
        help="Path to config/<species>/config.yml. Required input mode.",
    )
    parser.add_argument("--fasta", help="Path to assembly FASTA. Optional override when --yaml is used.")
    parser.add_argument("--gff", help="Path to annotation GFF. Optional override when --yaml is used.")
    parser.add_argument(
        "--skip-quast", action="store_true", help="Skip running Quast and reuse previous report if available."
    )
    parser.add_argument(
        "--skip-agat", action="store_true", help="Skip running AGAT and reuse previous report if available."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing Quast/AGAT output directories when running those tools.",
    )
    args = parser.parse_args()
    _validate_args(parser, args)
    return args


def _validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    """Validate the combination of command-line arguments."""
    if args.force and args.skip_quast and args.skip_agat:
        parser.error("--force has no effect when both --skip-quast and --skip-agat are set.")


def main() -> None:
    args = parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    script_base_dir = repo_root / "scripts" / "generate_species_stats"

    resolved_inputs = resolve_inputs(
        repo_root=repo_root,
        yaml_path=args.yaml,
        fasta=args.fasta,
        gff=args.gff,
    )

    options = WorkflowOptions(
        repo_root=repo_root,
        species_slug=resolved_inputs.species_slug,
        fasta_path=resolved_inputs.fasta_path,
        gff_path=resolved_inputs.gff_path,
        script_base_dir=script_base_dir,
        skip_quast=args.skip_quast,
        skip_agat=args.skip_agat,
        force=args.force,
    )

    display_destination, unresolved_placeholders = run_stats_workflow(options=options)

    print(f"Published species stats to: {display_destination}")
    if unresolved_placeholders:
        print("Unresolved fields kept as '[EDIT]' placeholders:")
        for key in unresolved_placeholders:
            print(f"  - {key}")


if __name__ == "__main__":
    main()
