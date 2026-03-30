#!/usr/bin/env python3

"""
Delete files created for a species by scripts/add_new_species.

The script runs in dry-run mode by default, showing the paths that would be removed for a given species slug.
To actually delete the files, add the -f/--force flag.

Note! This does not act on files created by the makefile.
To clean those, run: dockermake SPECIES=<SPECIES_NAME> clean uninstall

Usage:
    python scripts/removespecies.py -s <species_slug> [-f]


"""

import argparse
import shutil
import sys

from add_new_species.form_parser import validate_species_slug
from add_new_species.species_paths import get_species_paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Delete files created by scripts/add_new_species for one species.",
    )

    parser.add_argument("-s", "--species-slug", required=True, help="Species slug, e.g. volvox_carteri")

    parser.add_argument("-f", "--force", action="store_true", help="Delete files listed in the preview")

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    slug = args.species_slug

    try:
        validate_species_slug(slug)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    paths = get_species_paths(slug)
    targets_to_delete = [
        paths.content_dir_path,
        paths.data_dir_path,
        paths.assets_dir_path,
        paths.config_dir_path,
        paths.image_file_path,
    ]
    existing = [p for p in targets_to_delete if p.exists()]

    if not existing:
        print(f"No matching paths found for species slug: {slug}")
        return 0

    print(f"Species slug: {slug}")
    print("Paths to remove:")
    for path in existing:
        print(f"  - {path}")

    if not args.force:
        print("Preview only. No files removed. Re-run with -f to delete.")
        return 0

    for path in existing:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink(missing_ok=True)

    print(f"Removed {len(existing)} path(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
