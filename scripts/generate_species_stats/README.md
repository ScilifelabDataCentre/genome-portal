# generate_species_stats

Generate and publish `species_stats.yml` for a species.

## Recommended usage

```bash
python scripts/generate_species_stats --yaml config/<species_slug>/config.yml
```

This command:

1. Resolves assembly/annotation inputs from YAML document 1.
2. Runs Quast and AGAT.
3. Writes a temporary YAML in `scripts/generate_species_stats/temp/`.
4. Publishes to `hugo/data/<species_slug>/species_stats.yml`.
5. Deletes only the temporary YAML on success.

## Input overrides

You can override either input while still using `--yaml`:

```bash
python scripts/generate_species_stats \
  --yaml config/<species_slug>/config.yml \
  --fasta data/<species_slug>/custom.fna.gz \
  --gff data/<species_slug>/custom.gff.gz
```

## Skip mode and cache reuse

- `--skip-quast`: reuse previous Quast report if available.
- `--skip-agat`: reuse previous AGAT report if available.

If skipped cache is missing, placeholders are kept (`[EDIT]`) and the script continues.
If cached reports are older than input files, a warning is printed and cached values are still used.

