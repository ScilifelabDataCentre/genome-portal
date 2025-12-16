# configure_defaultSession README

This document is describes what the configure_defaultSession package is designed to do, outlines supported key-value pairs (Table 1), gives an example that can be tried out with test fixtures, and an generalized example of how it fits in with other packages and scripts to generate a new species page in the Genome Portal.

## What is the defaultSession used for?

The Genome Portal uses a makefile for processing and building the data that is displayed in the JBrowse pages of the portal. The makefile takes a species' `./config/config.yml` and generates the `data/{species_name}/config.json` that JBrowse uses to display data in genome browser instance. However, loading this `config.json` in JBrowse results in a very barebones display: the user will need to manually select linear view, select the assembly, turn on the tracks, and set the zoom-level. To make the experience more user-friendly, we configure a defaultSession in `./config/config.json` that is taken into account by the makefile.

In short, in this document "defaultSession" refers to a range of settings that need to be added to different levels of the JSON:
- general info and setup, in `.defaultSession`
- assembly FASTA related info, such as zoom-level and which scaffold to display by default, in `.defaultSession.views`,
- track-related info in `.defaultSession.views[{view_number}].tracks` and `.tracks`.

A challenge with creating the defaultSession is that tracks need to be defined in two places (`.defaultSession.views[...].tracks`and `.tracks`). The `jbrowse add-track` call in the makefile handles the latter for standard tracks, but is insufficient for non-standard tracks where we need to configure both `.defaultSession.views[...].tracks`and `.tracks`. Examples of this include tracks that need plugins (such as the population genomics tracks), special track types, or adapters (such as bedgraph tracks). The makefile is configured to omit passing tracks to `data/{species_name}/config.json` when `addTrack: False` in added to track in `config.yml`. This skips the `jbrowse add-track` recipe of the makefile, but still runs the recipies for downloading and processing the tracks.  At the moment, `addTrack: False` is needed in `config.yaml` for GWAS and bedgraph tracks, in combination with the keys `displayType` and `scoreColumn` (see Table 1 below).

Another complexity is that the makefile supports multi-assembly `config.yml` using the YAML document syntax. This essentially means that a new `.defaultSession.views` needs to be created for each assembly that is to be displayed in the JBrowse instance. The configure_defaultSession package will take care of that.


## Design
The `configure_defaultSession` is meant to be used in sequence with the makefile. Input to the package is `config/{species_name}/config.yml` and output is hard-coded as  `/config/{species_name}/config.json` since this is where the makefile expects to find the file.

The package can read a downloaded FASTA and make guesstimates for some parameter values needed in  `.defaultSession.views`. This requires that the makefile to have been run once for the species before running the package so that files are downloaded. The module looks for the fasta file name given in `config.yml` in `data/{species_name}/`. Essentially, this means that the makefile needs to be run once before and once after `configure_defaultSession` to properly create the final `data/{species_name}/config.json`.

The package is relying on `config/{species_name}/config.yml` being correctly set. Running the add_new_species package will create a basic `config.yml` from the user submitted forms, but there are special use-cases where manual editing is needed. The table below lists the `config.yml` keys that are used by the defaultSession package.

**Table 1. Overview of config.yml keys that are recognised by `configure_defaultSession`**
| Key | Description |
| ------------- | ------------- |
| `assembly.defaultScaffold: str`   | Optional. Allows to specify which scaffold that will be displayed when opening the JBrowse page. If not set, the first scaffold of the FASTA will be shown.   |
| `assembly.bpPerPx: int = 50`  | This is the "zoom level" in the JBrowse view. Longer scaffolds tend to need a larger value. The script will make a guess based on the length of the assembly, but this key often needs manual adjustment to dial in a good view based on gene annotation density of the scaffold.  |
| `{assembly,track}.fileName: str` | if not specified, the package will try to deduce the name from the url, but this key takes precedence if specified. Needed for tracks from Figshare that otherwise would be named whatever value they store the file as. |
| `track.defaultSession: Bool` | if True then the track is enabled by default when the user opens the JBrowse page. Ignored by protein-coding gene tracks since they are mandatory. |
| `addTrack [True/False]` | If False, the makefile will download and process the file but will not run `jbrowse add-track`. This allows the package to add `.track` level configs to `data/{species_name}/config.json`. Must be set to `False` for GWAS and bedgraph tracks to work as intended with the makefile.|
| `track.displayType: ["linear", "arc", "gwas", "wiggle"]` |  Sets the display type of the track. Will default to LinearBasicDisplay if not set. LinearArcDisplay, gwas = LinearManhattanDisplay, wiggle= LinearWiggleDisplay. Note! `addTrack: False` needs to also be used for `"gwas"` and `"wiggle"`.|
| `track.scoreColumn: str` |  Quantitative tracks, such as BED(-like), often needs the name of the column in the track that should be displayed. |

- Depreciated keys that was used by the earlier `/scripts/data_stewardship/configure_defaultSession.py` script: `track.GWAS`, `track.scoreColumnGWAS`.

## Example usage with test fixtures
The package is meant to be run after `add_new_species` package has been run an thus initated a `config.yml` for the new species. But to test the defaultSession package on its own, the following commands and fixture can be used:

(Might want to run `./scripts/dockerbuild -u -t local -k data` and `./scripts/dockerbuild -u -t local -k hugo` to ensure images are up to date first)
```
mkdir config/tiny_herb

cp tests/fixtures/tiny_herb/config.yml config/tiny_herb

./scripts/dockermake -t local SPECIES=tiny_herb

python scripts/configure_defaultSession --yaml config/tiny_herb/config.yml -o

./scripts/dockermake -t local SPECIES=tiny_herb

docker rm -f "genome-portal"; ./scripts/dockerserve -t local
```

Then visit: http://localhost:8080/genome-browser/?config=%2Fdata%2Ftiny_herb%2Fconfig.json

which should now have tracks that together cover the keys described in Table 1.

Note! The `./config/tiny_herb` folder has been added to the `.gitignore`, but you could just as well delete it after trying this out.

## Example of a full workflow to create a new species page

To put this into a bigger perspective, these are the steps needed to create a new species entry in the Genome Portal. (Your Milage May Vary if the data tracks require formatting or other troubleshooting).

```
git checkout -b add-new_species

# Create the Hugo pages and initiate a basic config.yaml
python scripts/add_new_species \
  --species-submission-form="path/to/user_form.docx" \
  --data-tracks-sheet="path/to/user_spreadsheet.xlsx" \
  --species-image="path/to/image_4_3.png" \

# Build the data builder image (can be skipped if already up-to-date)
./scripts/dockerbuild -u -t local -k data

# download the data to make it available to the defaultSession script
./scripts/dockermake -t local SPECIES=<SPECIES_NAME>

# make manual edits to config.yaml if needed, as described in Table 1 in this PR

# Generate the defaultSession settings in config/<SPECIES_NAME>/config.json
python scripts/configure_defaultSession --yaml config/<SPECIES_NAME>/config.yml

# Update ./data/<SPECIES_NAME>/config.json with the defaultSession settings from config/<SPECIES_NAME>/config.json
./scripts/dockermake -t local SPECIES=<SPECIES_NAME>

# Calculate bioinformatics stats for the hugo pages and copy them over to the destination
bash ./scripts/data_stewardship/generate_assembly_and_annotation_statistics.sh --fasta ./data/<SPECIES_NAME>/<ASSEMBLY_NAME>.fna.gz --gff ./data/<SPECIES_NAME>/<PROTEIN_CODING_GENES_TRACK>.gff.nozip

cp scripts/data_stewardship/temp/species_stats_<ASSEMBLY_NAME>.fna.gz.yml ./hugo/data/<SPECIES_NAME>/species_stats.yml

# Build the hugo server image (can be skipped if already up-to-date)
./scripts/dockerbuild -u -t local -k hugo

docker rm -f "genome-portal"; ./scripts/dockerserve -t local

pytest playwright/tests/ --base-url http://localhost:8080
```