#!/bin/bash

set -o pipefail
shopt -s nullglob


species_count=0
species_slugs=()
total_tracks=0

ROOT_DIR="${ROOT_DIR:-hugo}"
OUTPUT_FILE="${ROOT_DIR}/static/api/metrics.json"


### 1. Identify all species that does not have status draft:true in their YAML front matter.

for file in hugo/content/species/*/_index.md; do
    slug="$(basename "$(dirname "$file")")"

    # Handle legacy "draft" key: skip a species if the _index.md contains "draft: true" in the front matter block (between first two --- lines)
    front_matter="$(sed -n '/^---[[:space:]]*$/,/^---[[:space:]]*$/p' "$file")"
    if echo "$front_matter" | grep -Eiq '^[[:space:]]*draft:[[:space:]]*true([[:space:]]*#.*)?$'; then
        continue
    fi

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
    json_file="hugo/assets/$slug/data_tracks.json"
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