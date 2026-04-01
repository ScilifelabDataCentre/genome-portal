#!/bin/bash

# Assumes that:
# ./scripts/dockerbuild -k add_species -t local and
# ./scripts/dockerbuild -u -t local -k data
# have been run, and that the generated images are available locally.
#
# "I'm feeling lucky" script to run the full species ingestion workflow in one command, for testing and development purposes.

# TODO spin up the docker container once?

set -euo pipefail

help() {
  cat <<'EOF'
Usage:
  ./scripts/full_species_ingestion_workflow.sh \
    -f <submission_form.docx> \
    -d <data_tracks.xlsx> \
    [-i <species_image.webp>] \
    [-t <tag>] \

Options:
  -f  Species submission DOCX (required)
  -d  Data tracks XLSX (required)
  -i  Species image (optional; defaults to placeholder)
  -t  Docker tag (default: local)
EOF
}

FORM=""
TRACKS=""
IMAGE="/scripts/add_new_species/templates/placeholder_image_4-3_ratio.webp"
TAG="local"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -f) FORM="$2"; shift 2 ;;
    -d) TRACKS="$2"; shift 2 ;;
    -i) IMAGE="$2"; shift 2 ;;
    -t) TAG="$2"; shift 2 ;;
    -h|--help) help; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; help; exit 1 ;;
  esac
done

[[ -n "$FORM" ]] || { echo "Missing -f" >&2; help; exit 1; }
[[ -n "$TRACKS" ]] || { echo "Missing -d" >&2; help; exit 1; }

# 1. Run the add_new_species script in a Docker container, passing the provided form, data tracks, and image. Capture the printed species slug.

echo "Running add_new_species with form: $FORM, tracks: $TRACKS, image: $IMAGE, tag: $TAG"

RAW_SPECIES_SLUG="$(
  ./scripts/dockeraddspecies -t "$TAG" python scripts/add_new_species \
    --species-submission-form="$FORM" \
    --data-tracks-sheet="$TRACKS" \
    --species-image="$IMAGE" \
    --overwrite \
    --print-species-slug-only
)"
# In the spirit of this being a "I'm feeling lucky" script, hardcode --overwrite

# docker -it output can include carriage returns; normalize to a clean slug.
SPECIES_SLUG="$(printf '%s' "$RAW_SPECIES_SLUG" | tail -n 1 | tr -d '\r\n' | xargs)"
if [[ ! "$SPECIES_SLUG" =~ ^[a-z_]+$ ]]; then
  echo "Failed to parse a valid species slug from add_new_species output: '$RAW_SPECIES_SLUG'" >&2
  exit 1
fi

echo "add_new_species step was successful. The species slug for this input data is: $SPECIES_SLUG"


# 2. Run the dockermake script to download the data tracks for the new species.

echo "Running dockermake to download data tracks for species slug: $SPECIES_SLUG"

./scripts/dockermake -t "$TAG" SPECIES="$SPECIES_SLUG"

# 3. Run the dockeraddspecies script to configure the default session for the new species.

echo "Running dockeraddspecies to configure default session for species slug: $SPECIES_SLUG"

./scripts/dockeraddspecies -t "$TAG" python scripts/configure_defaultSession \
  --yaml "config/${SPECIES_SLUG}/config.yml" \
  --set-default-session-all-tracks \
  -o && \
  ./scripts/dockermake -t local SPECIES="$SPECIES_SLUG" jbrowse-config

# 4. Run the generate_species_stats script to generate stats for the new species.

echo "Running generate_species_stats to generate stats for species slug: $SPECIES_SLUG"

./scripts/dockeraddspecies -t "$TAG" python scripts/generate_species_stats --yaml "config/${SPECIES_SLUG}/config.yml"

# 5. Rebuild and serve the Hugo site, then print the URL for the new species page.

./scripts/dockerbuild -u -t local -k hugo && \
docker rm -f "genome-portal"; ./scripts/dockerserve -t local && \
echo "The full species ingestion workflow is complete! You can now visit http://localhost:8080/species/${SPECIES_SLUG} to see the new species page"
