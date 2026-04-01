#!/bin/bash

# This script generates a metrics.json file containing the number of species and the total number of
# data tracks (excluding genome assemblies) across all species in the Genome Portal.
# It is intended to be run in the build stage of the Hugo Docker image, so that the generated metrics
# are included in the static files served by Hugo.
#
# It can be run locally for development purposes:
# Ensure that you are in the root of the genome-portal repository
# bash scripts/generate_metrics.sh
# ./scripts/dockerbuild -u -t local -k hugo
# docker rm -f "genome-portal"; ./scripts/dockerserve -t local
# then visit http://localhost:8080/api/metrics.json

set -o pipefail
shopt -s nullglob


species_count=0
species_slugs=()
total_tracks=0

# For local dev, assume hugo root in ./hugo. Override this with ROOT_DIR=/src for the hugo Docker container.
ROOT_DIR="${ROOT_DIR:-hugo}"
OUTPUT_FILE="${ROOT_DIR}/static/api/metrics.json"


### 1. Identify all species that does not have status draft:true in their YAML front matter.

for file in "${ROOT_DIR}/content/species"/*/_index.md; do
    slug="$(basename "$(dirname "$file")")"
    species_count=$((species_count + 1))
    species_slugs+=("$slug")
done


### 2. For each species identified in step 1, read the data_tracks.json file and count the number of non-genome assembly data tracks

EXCLUDE_TRACK_PATTERNS=("genome" "assembly" "currently not displayed")

# Join array elementswith | to a single regex. Example: genome|assembly. This can be tested for in jq.
EXCLUDE_REGEX="${EXCLUDE_TRACK_PATTERNS[0]}"
for pattern in "${EXCLUDE_TRACK_PATTERNS[@]:1}"; do
    EXCLUDE_REGEX="${EXCLUDE_REGEX}|${pattern}"
done

for slug in "${species_slugs[@]}"; do
    json_file="${ROOT_DIR}/assets/$slug/data_tracks.json"
    if [[ -f "$json_file" ]]; then
        count=$(
            # Use jq to filter data tracks that do not match the exclude patterns and count them.
            jq --arg exclude_patterns "$EXCLUDE_REGEX" '
                .[]
                | select(.dataTrackName | test($exclude_patterns; "i") | not)
                | .dataTrackName
                ' "$json_file" | wc -l
        )
        total_tracks=$((total_tracks + count))
    fi
done

### 3. Write the metrics to JSON file

mkdir -p "$(dirname "$OUTPUT_FILE")"

tmp_file="$(mktemp "${OUTPUT_FILE}.tmp.XXXXXX")"

# Use jq to ensure valid JSON output
jq -n \
    --argjson species_count "$species_count" \
    --argjson data_track_count "$total_tracks" \
    '{species_count: $species_count, data_track_count_excluding_genome_assemblies: $data_track_count}' \
    > "$tmp_file"

mv "$tmp_file" "$OUTPUT_FILE"
chmod 644 "$OUTPUT_FILE" # Ensure the output file is readable by all users (the Docker container runs as a non-root user for the app)