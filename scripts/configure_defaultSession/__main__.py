"""
Package to create a defaultSession config.json for a species based on a config.yml file.

Assumes that the dockermake has been run once to download the files.

(The intention is that add_new_species has been run once first, but as long as there is a config.yml, this package will work)

Handles multi-assembly config.yml (YAML document) files by assembly_counter

The interaction between defaultSession and the makefile is based on track filenames,
so the filenames has to be unique across a config.yml file. If the same file needs to be used, the
fileName key can be used to specify the name that the makefile will give it upon download of the url.

Unless otherwise specified with the defaultScaffold key, the package will use the first scaffold in the FASTA for the defaultSession.

bgPerPx often needs manual adjustment based on the length of the scaffold and gene annotation density.

# Overview of config.yml keys that this script recognises:
- Supported keys:
assembly.defaultScaffold: str   (name of the scaffold to display in the defaultSession when the JBrowse instance is initialized)
assembly.bpPerPx: int = 50      (this is the "zoom level" in the JBrowse view. Longer scaffolds tend to need a larger value)
{assembly,track}.fileName: str  (if not specified, the package will try to deduce the name from the url, but this key takes precedence if specified)
track.defaultSession: Bool      (ignored by protein-coding gene tracks since they are mandatory)
track.displayType: str          (one of ["linear", "arc", "gwas"])
track.scoreColumn: str:         (name of the score column in the track file)

- Depreciated keys that was once used for the Geneom Portal build process, but is not longer in use:
track.GWAS
track.scoreColumnGWAS

# Maintenance of the code:
this script is indended to be updated and expanded as new track types are added to the Genome Portal

- to add a new display type to the code, define a new key value for displayType and add the corresponding logic to
TrackParams.get_display_type

- if a track needs a plugin, the logic can be added to TrackParams.check_if_plugin_needed

- to add a new file format adapter, modify TrackParams.get_track_adapter_config


# Example usage:

python scripts/config_defaultSession -y scripts/config_defaultSession/tests/fixtures/config.yml -o
"""

import argparse
from pathlib import Path

import yaml
from default_session_builder import DefaultSession, create_view, process_tracks
from default_session_utils import check_config_json_exists, save_json


def _is_big_binary_track(track: dict) -> bool:
    """Return True for BigBed/BigWig-like track file names/URLs."""
    track_file_or_url = str(track.get("fileName") or track.get("url") or "").strip().lower()
    track_file_or_url = track_file_or_url.split("?", 1)[0]
    return track_file_or_url.endswith((".bw", ".bigwig"))


def set_default_session_true_for_all_tracks(configs: list[dict]) -> list[dict]:
    """Set ``defaultSession: true`` for all track entries in all YAML documents."""
    for config in configs:
        if not config or not isinstance(config, dict):
            continue
        tracks = config.get("tracks", [])
        if not isinstance(tracks, list):
            continue
        for track in tracks:
            if isinstance(track, dict):
                # Skip placeholder/unset tracks to avoid creating invalid defaultSession entries.
                track_file_or_url = str(track.get("fileName") or track.get("url") or "").strip()
                if not track_file_or_url or track_file_or_url == "[EDIT]":
                    track["defaultSession"] = False
                    continue
                # Keep BigBed/BigWig tracks unchanged until their default session settings are fully supported.
                if _is_big_binary_track(track=track):
                    continue
                track["defaultSession"] = True
    return configs


def write_config_yaml(config_yml_path: Path, configs: list[dict]) -> None:
    """Write the updated YAML documents back to config.yml."""
    with open(config_yml_path, "w", encoding="utf-8") as file:
        yaml.safe_dump_all(configs, file, sort_keys=False, allow_unicode=True)
    print(f"Updated config.yml with defaultSession=true for all tracks: {config_yml_path}")


def run_argparse() -> argparse.Namespace:
    """
    Run argparse and return the user arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        "-y",
        "--yaml",
        required=True,
        type=Path,
        metavar="[Species' config.yml]",
        help="Input; the path to config.yml for the species.",
    )

    parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        help="""If the defaultSession config.json for the species already exist, should it be overwritten?
            If flag NOT provided, no overwrite performed.""",
    )

    parser.add_argument(
        "-s",
        "--skip-reading-fasta",
        action="store_true",
        help="""Skips analysing the FASTA file to get the default scaffold and sequence length.
            This is useful if the FASTA file is not available.""",
        required=False,
    )

    parser.add_argument(
        "--set-default-session-all-tracks",
        action="store_true",
        help="Set defaultSession: true for all tracks in config.yml before generating config.json.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = run_argparse()
    config_yml_path = args.yaml
    output_json_path = config_yml_path.with_suffix(".json")

    if not args.overwrite:
        check_config_json_exists(output_json_path=output_json_path)

    with open(config_yml_path, "r", encoding="utf-8") as file:
        configs = list(yaml.safe_load_all(file))

    if args.set_default_session_all_tracks:
        configs = set_default_session_true_for_all_tracks(configs=configs)
        write_config_yaml(config_yml_path=config_yml_path, configs=configs)

    if "organism" not in configs[0] or not configs[0]["organism"]:
        raise KeyError(
            "The primary assembly (assembly number 1 in config.yml) is required to have a non-empty 'organism' key. Exiting."
        )

    default_session = DefaultSession.from_config(configs[0])

    for assembly_counter, config in enumerate(configs):
        if not config:
            raise ValueError(
                f"Document number {assembly_counter+1} in the config.yml is empty. Each document must contain data. Exiting."
            )

        default_session = create_view(
            default_session=default_session,
            config=config,
            assembly_counter=assembly_counter,
            skip_reading_fasta=args.skip_reading_fasta,
        )

        default_session = process_tracks(
            default_session=default_session,
            config=config,
            assembly_counter=assembly_counter,
        )

    data = default_session.make_defaultSession_dict()
    save_json(data=data, output_json_path=output_json_path)
