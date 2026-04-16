#!/bin/bash

# This is a wrapper script to run the full species ingestion workflow in a single command.
# In spirit, it is an "I'm feeling lucky" script: if species submission forms are correctly filled out, this should will
# in many case produce the full species pages with out any need for manual intervention.
# If there are any issues, users will need to manually troubleshoot and run the remaining step of the workflow. Either by deleting all files produced by
# earlier runs of this script and re-running it, or by running the individual steps of the workflow manually. See also the documentation on how to
# add a new species though a pull request for more details.
#
# Assumes that the add-speces and data-builder images are available on the local machine. This can be acheieved with:
#
# docker pull ghcr.io/scilifelabdatacentre/swg-add-species:stable && \
# docker pull ghcr.io/scilifelabdatacentre/swg-data-builder:stable
#
# or with:
#
# ./scripts/dockerbuild -k -t local add_species && \
# ./scripts/dockerbuild -u -t local -k data
#

set -euo pipefail

help() {
  cat <<'EOF'
Usage:
  ./scripts/full_species_ingestion_workflow.sh \
    -f <submission_form.docx> \
    -d <data_tracks.xlsx> \
    [-i <species_image.webp>] \
    [-t <tag>] \
    [--skip-assembly-metadata-fetch] \

Options:
  -f  Species submission DOCX (required)
  -d  Data tracks XLSX (required)
  -i  Species image (optional; defaults to placeholder)
  -t  Docker tag (default: local)
  --skip-assembly-metadata-fetch
      Option for add_new_species package. Skip ENA/NCBI assembly metadata lookup and use [EDIT] placeholders in metadata fields.
      Useful when the primary genome assembly does not have a public ENA/NCBI accession number.
EOF
}

FORM=""
TRACKS=""
IMAGE="/scripts/add_new_species/templates/placeholder_image_4-3_ratio.webp"
TAG="stable"
SKIP_ASSEMBLY_METADATA_FETCH=0

require_local_image() {
  local image="$1"
  local build_hint="$2"
  if ! docker image inspect "${image}:${TAG}" >/dev/null 2>&1; then
    echo "Missing required image: ${image}:${TAG}" >&2
    echo "Build it with:" >&2
    echo "  ${build_hint}" >&2
    exit 1
  fi
}

check_required_images() {
  require_local_image \
    "ghcr.io/scilifelabdatacentre/swg-add-species" \
    "./scripts/dockerbuild -t \"${TAG}\" -k add_species"
  require_local_image \
    "ghcr.io/scilifelabdatacentre/swg-data-builder" \
    "./scripts/dockerbuild -u -t \"${TAG}\" -k data"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -f) FORM="$2"; shift 2 ;;
    -d) TRACKS="$2"; shift 2 ;;
    -i) IMAGE="$2"; shift 2 ;;
    -t) TAG="$2"; shift 2 ;;
    --skip-assembly-metadata-fetch) SKIP_ASSEMBLY_METADATA_FETCH=1; shift ;;
    -h|--help) help; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; help; exit 1 ;;
  esac
done

[[ -n "$FORM" ]] || { echo "Missing -f" >&2; help; exit 1; }
[[ -n "$TRACKS" ]] || { echo "Missing -d" >&2; help; exit 1; }
check_required_images

# 1. Run the add_new_species script in a Docker container, passing the provided form, data tracks, and image. Capture the printed species slug.

echo "Running add_new_species with form: $FORM, tracks: $TRACKS, image: $IMAGE, tag: $TAG"

# In the spirit of this being a "I'm feeling lucky" script, hardcode --overwrite
add_new_species_args=(
  --species-submission-form="$FORM"
  --data-tracks-sheet="$TRACKS"
  --species-image="$IMAGE"
  --overwrite
  --print-species-slug-only
)

if ((SKIP_ASSEMBLY_METADATA_FETCH)); then
  add_new_species_args+=(--skip-assembly-metadata-fetch)
fi

RAW_SPECIES_SLUG="$(
  ./scripts/dockeraddspecies -t "$TAG" python scripts/add_new_species \
    "${add_new_species_args[@]}"
)"

# Normalize the species slug
SPECIES_SLUG="$(printf '%s' "$RAW_SPECIES_SLUG" | tail -n 1 | xargs)"
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
  ./scripts/dockermake -t "$TAG" SPECIES="$SPECIES_SLUG" jbrowse-config

# 4. Run the generate_species_stats script to generate stats for the new species.

echo "Running generate_species_stats to generate stats for species slug: $SPECIES_SLUG"

./scripts/dockeraddspecies -t "$TAG" python scripts/generate_species_stats --yaml "config/${SPECIES_SLUG}/config.yml"

# 5. Rebuild and serve the Hugo site, then print the URL for the new species page.

./scripts/dockerbuild -u -t local -k hugo && \
docker rm -f "genome-portal"; ./scripts/dockerserve -t local && \
echo "The full species ingestion workflow is complete! You can now visit http://localhost:8080/${SPECIES_SLUG} to see the new species page"
