# Manual Intervention Guide for Adding Species to the Genome Portal

> **Before you start reading this guide:** The standard and recommended way to add a new species is described in [`species_submission/how_to_submit_through_pull_request.md`](how_to_submit_through_pull_request.md). That guide covers the full automated ingestion pipeline. Come back here if you run into issues with the pipeline, or if you need to understand the underlying mechanics of the Genome Portal backend. 

This guide is a collection of experiences from adding new species to the Genome Portal. It was written with Genom Portal staff as the target audience, but is presented openly for everyone. The aim is to document advice on how to handle common issues and edge-cases related to displaying the data tracks in JBrowse. Whilst this guide can be read from start to finish, readers are encouraged to jump around the guide to topics that relate to their issues.

Some familiarity with the how the Genome Portal data pipeline works will be needed to follow the guide. An overview of the subsystem can be found in [Section 2](#2-a-primer-on-how-the-genome-portal-data-pipeline-works).

## Table of contents

1. [When manual intervention is needed](#1-when-manual-intervention-is-needed)
2. [A primer on how the Genome Portal data pipeline works](#2-a-primer-on-how-the-genome-portal-data-pipeline-works)
3. [Preparing data files for JBrowse](#3-preparing-data-files-for-jbrowse)
   - [3.1 Sourcing the genome assembly FASTA](#31-sourcing-the-genome-assembly-fasta)
   - [3.2 Sourcing the protein-coding genes annotation](#32-sourcing-the-protein-coding-genes-annotation)
   - [3.3 Sourcing other data tracks](#33-sourcing-other-data-tracks)
   - [3.4 Supported file formats](#34-supported-file-formats)
   - [3.5 Indexing and compression](#35-indexing-and-compression)
   - [3.6 Generating a refNameAlias file](#36-generating-a-refnamealias-file)
4. [Spinning up a local JBrowse instance to test tracks](#4-spinning-up-a-local-jbrowse-instance-to-test-tracks)
   - [4.1 Full local site with dockerbuild + dockerserve](#41-full-local-site-with-dockerbuild--dockerserve)
   - [4.2 Alternative: JBrowse Desktop client](#42-alternative-jbrowse-desktop-client)
5. [Understanding and editing `config.yaml` manually](#5-understanding-and-editing-configyml-manually)
   - [5.1 Structure overview](#51-structure-overview)
   - [5.2 The assembly section](#52-the-assembly-section)
   - [5.3 The tracks section](#53-the-tracks-section)
   - [5.4 Configuring the defaultSession](#54-configuring-the-defaultsession)
   - [5.5 Secondary (organellar) assemblies](#55-secondary-organellar-assemblies)
6. [Adding feature tracks to `config.yaml`](#6-adding-feature-tracks-to-configyaml)
   - [6.1 Minimal example](#61-minimal-example)
   - [6.2 File format considerations](#62-file-format-considerations)
   - [6.3 Standard workflow](#63-standard-workflow)
   - [6.4 When addTrack: false is needed for a feature track](#64-when-addtrack-false-is-needed-for-a-feature-track)
   - [6.5 Enabling clickable database cross-references (dbxref plugin)](#65-enabling-clickable-database-cross-references-dbxref-plugin)
7. [Adding quantitative (GWAS/Manhattan plot) tracks to `config.yaml`](#7-adding-quantitative-gwasmanhattan-plot-tracks-to-configyaml)
   - [7.1 BED file preparation](#71-bed-file-preparation)
   - [7.2 config.yml entries](#72-configyml-entries)
   - [7.3 Workflow](#73-workflow)
   - [7.4 Verifying the track renders correctly](#74-verifying-the-track-renders-correctly)
8. [Troubleshooting JBrowse rendering issues](#8-troubleshooting-jbrowse-rendering-issues)
   - [8.1 No features rendered at all (empty track)](#81-no-features-rendered-at-all-empty-track)
   - [8.2 Error messages and how to get stack traces](#82-error-messages-and-how-to-get-stack-traces)
   - [8.3 Errors caused by file format versions](#83-errors-caused-by-file-format-versions)
   - [8.4 Bumping the JBrowse version](#84-bumping-the-jbrowse-version)
   - [8.5 Node.js uv_os_get_passwd error in Docker](#85-nodejs-uv_os_get_passwd-error-in-docker)
   - [8.6 Transient download failures in the makefile](#86-transient-download-failures-in-the-makefile)


## 1. When manual intervention is needed

The automated ingestion workflow described in `how_to_submit_through_pull_request.md` is likely to successfully handle the majority of species submissions end-to-end, given that the species submission forms are correctly filled out and the data has been made publicly available.

However, some cases inevitably require manual work to get the JBrowse instance for the species to properly render. Examples of cases described in this guide include:

- A data track does not render or renders incorrectly in JBrowse after the `makefile` pipeline has run.
- The submission contains quantitative tracks that require a custom `defaultSession` configuration (score column declarations, specific JBrowse track types).
- The assembly or annotation files exist only in a format that JBrowse does not directly support, and a format conversion is necessary before data can be made public.
- The automatic ingestion workflow fails mid-way and needs to be resumed from a specific step.
- You want to iterate quickly on the species' JBrowse configuration without rebuilding the full Hugo site each time.

## 2. A primer on how the Genome Portal data pipeline works

Many examples in this guide assume familiarity with how data processing works in the Genome Portal. This section builds that foundation before diving into specifics.

Throughout all Genome Portal documentation, the backend process that prepares input data for rendering in JBrowse goes by several names: "data builder job", "data pipeline", "data workflow", "data backend", "`makefile`", "species ingestion". These all refer to the same thing.

> **Note!** The text will often refer to running the `makefile`. There have historically been issues related to host OS when running the Genome Portal `makefile`, and a containerised version of the process was developed to address this. The recommended way to run the process locally is with `scripts/dockermake`.

### 2.1. Pipeline inputs and outputs

The Genome Portal uses `make` recipes to download and process files. A selling point of `make` is that it checks whether the required files already existing on disk, and, if so, skips processing them.

The inputs to the `makefile` are the configuration files in `config/<species_name>/`. These are intended to be generated from the species submission forms and the tools described in [`species_submission/how_to_submit_through_pull_request.md`](how_to_submit_through_pull_request.md), but they can be manually created and edited. These files are intended to be committed to source control/git.

- `config.yml`: the main configuration file.
- `config.json`: helper configuration file that stores the JBrowse `defaultSession`.

The outputs are everything written to the ``data/<species_name>/` directory by the makefile. **The `data/` directory is never committed to git** — it is always regenerated on demand by running `dockermake`.

- Downloaded and processed data files: the bgzipped FASTA and its `.fai` index; sorted, bgzipped GFF/BED files and their `.csi` indexes; `aliases.txt`.
- The final JBrowse configuration for the species: `data/<species_name>/config.json`.

At the end of a successful `dockermake` run, `data/<species_name>/` contains everything the JBrowse instance needs to render the species.

### 2.2. Local development vs Kubernetes deployment

>**Note!** The Kubernetes deployment referred to in this section is for Genome Portal staff only. Other users can skip over those parts and only read the text the refers to local development.

The `makefile` was designed to be compatible with local development and with Kubernetes (production) deployment. For technical reasons, the the `data/` directory is handled slightly differently in each environment.

**In local development:**

Locally, `./scripts/dockermake` runs `make` inside a container (the `swg-data-builder` image). The `build` target downloads and processes species files into `./data/<species_name>/` in the cloned `genome-portal` repository on the local machine. The `install` target then copies those processed files to `./hugo/static/data/`. 

However, for local testing with the `dockerserve` helper script, `./hugo/static/data/` is not used. Instead `./scripts/dockerserve` starts the Genome Portal Hugo container and bind-mounts `./data/` directly at `/usr/share/nginx/html/data/` inside the Hugo container at runtime. The `-t` flag selects which Hugo image to use (e.g. `-t stable` for the latest release, `-t local` for one you built yourself with `dockerbuild`), but the data always comes from your local `./data/` directory regardless of which image is chosen.

**On Kubernetes deployment:**

A PersistentVolumeClaim (`genome-portal-data-pvc`) is shared between the data builder job and the Hugo web server. In short, a new species branch need to be merged to `main`, becomes part of a new Genome Portal release, and the images created by the CI/CD workflow triggered by the release need to be deployed to the Kubernetes cluster. Upon deployment, the `makefile` is run as a data builder job. 

The Hugo web server deployment mounts only the `public/` subdirectory of the PVC (via Kubernetes `subPath: public`) at `/usr/share/nginx/html/data/`. Hugo never sees the raw `data/` subdirectory on the PVC — it only reads the installed, final output.

_Table 1. Differences between Local and Kubernetes paths for the data processing. Non-staff users only need to consider the Local column._ 
| | Local | Kubernetes |
|---|---|---|
| Makefile targets run | `build` (+ `install`, but not used by `dockerserve`) | `build install` |
| Where build output goes | `./data/<species_name>/` | PVC subdirectory `data/<species_name>/` |
| Where install output goes | `./hugo/static/data/` (not used by `dockerserve`) | PVC subdirectory `public/<species_name>/` |
| What Hugo/nginx reads | `./data/` (bind-mounted by `dockerserve`) | PVC `public/` subdirectory (mounted via `subPath`) |
| Path inside Hugo container | `/usr/share/nginx/html/data/` | `/usr/share/nginx/html/data/` |
| Hugo Docker image | Hugo pages only — species data **not** baked in | Same |

Important to understand is that **the Hugo Docker image never contains species data!** In both the local and Kubernetes environments, species data is always provided at runtime by mounting. This has two practical consequences:

- Locally: you can update data files and re-test without rebuilding the Hugo image — just re-run `dockermake` then `dockerserve`.
- On Kubernetes: merging a PR alone does not publish the species. The data builder job must also complete to populate the PVC's `public/` subdirectory. Any change to `config.yml` (a corrected URL, a new track) requires re-triggering the job.

The subsections below describe the parts of this process in more detail.

### 2.3. Each species has two config files and a final Jbrowse config file

Each species has two configuration files under `config/<species_name>/`:

- **`config.yml`** — the main config file. This is intended to be human-edited, but a initial version of the file is created by the `scripts/add_new_species` script that is run when ingesting the species submission forms. It defines the assembly (URL, name, accession), and the list of data tracks (URLs, file names, JBrowse display options). This is the file you edit when adding or tweaking a species.
- **`config.json`** — the generated defaultSession file. It is produced by the `configure_defaultSession` script, which reads `config.yml` and the locally downloaded FASTA and tells JBrowse which scaffold to open, at what zoom level, and with which tracks visible on page load. It is merged into the final `data/<species_name>/config.json` during the `makefile` build step (see below). You do not normally edit this file directly, but some manual interventions, such as enabling the dbxref plugin (see [Section 6.5](#65-enabling-clickable-database-cross-references-dbxref-plugin)), do require editing it.

From these two `config/<species_name>/` config files, the data pipeline generates the final config file that is read and rendered by the Genome Portal JBrowse instance. In local development, this file is created in `data/<species_name>/config.json`.

### 2.4. What the `makefile` does

The `makefile` (run locally via `./scripts/dockermake`) is the core build process. It has two main targets: `build` and `install`. The files in `config/<species_name>` are inputs; the files under `data/<species_name>` are the intermediate `build` outputs. When you run it for a species the `build` target:

1. **Downloads** each file listed in `config/<species_name>/config.yml` from its remote URL into `data/<species_name>/`.
2. **Processes** each file: sorts, bgzips, and CSI-indexes GFF and BED files; bgzips and fai-indexes the FASTA.
3. **Generates a refNameAlias file** (`data/<species_name>/aliases.txt`) by parsing the FASTA headers (automatic for ENA assemblies; see [Section 3.6](#36-generating-a-refnamealias-file)).
4. **Registers the assembly and tracks** with JBrowse by running `jbrowse add-assembly` and `jbrowse add-track`, writing the result to `data/<species_name>/config.json`.
5. **Merges** `config/<species_name>/config.json` (the defaultSession) into the final `data/<species_name>/config.json`.

The `install` target is used for the Kubernetes deployment to copies the processed files from `data/<species_name>/` to the `public/` subdirectory of the PVC. For local development with `dockerserve`, the `install` step is bypassed entirely since `dockerserve` mounts `./data/` directly (as described above).

Avoid editing `data/<species_name>/config.json` directly since any manual changes will be overwritten the next time `dockermake` runs. Since the data pipeline will be run separately on the Kubernetes deployment, all configurations for the species JBrowse render need to be recreatable from scratch from the two files in `config/<species_name>`.

>**Tip:** If the JBrowse instance is not reflecting your changes after running `dockermake` (even after clearing the cache from the web browser and reloading the page), it can help to clear the build state before re-running. The `makefile` has dedicated clean-up targets for this:
> - `./scripts/dockermake -t stable SPECIES=<species_name> clean-config` — removes `data/<species_name>/config.json` only. (You can also manually delete `data/<species_name>/config.json` to achive this.) Combining this with a rerun of the `makefile` for the species is often enough to clear stale JBrowse states. 
> - `./scripts/dockermake -t stable SPECIES=<species_name> clean` — removes all build artefacts for the species, including downloaded and indexed data files. Use this when a full reset is needed. Note that downloading and processing files can take some time, so most likely this is overkill for troubleshooting stale JBrowse states.

### 2.5. What is baked into the Docker image vs mounted at runtime?

The Genome Portal has two runtime components:

- **The Hugo website** (species pages, assembly statistics, download pages) is baked into a Docker image via `./scripts/dockerbuild -k hugo`. Changing Hugo page content requires rebuilding this image.
- **The JBrowse data** (`data/<species_name>/`) is never baked in, it is always mounted at runtime, as described in the [local vs Kubernetes overview above](#local-development-vs-kubernetes-deployment). This means you can update data files locally and serve them without rebuilding the Hugo image: just rerun `dockermake` and `dockerserve`.


## 3. Preparing data files for JBrowse

The Genome Portal itself is not a host for the data; it keeps copies of the files on its server for performance reasons, but is not a data source it itself. Therefore, it is assumed that all data tracks for a species is data is publicly available in a remote, archival repository through a persistent URL.

### 3.1 Sourcing the genome assembly FASTA

Genome assemblies are typically published in the domain-specific repositories in the [International Nucleotide Sequence Database Collaboration](https://www.insdc.org/). ENA (European Nucleotide Archive) and NCBI (National Center for Biotechnology Information, US)mirror each other to a large extent, but their respective automatic ingestion processes can make changes to headers and formatting. For the purposes of the Genome Portal, it is important to know that the FASTA header of a genome assembly are not identical between the two repositories, which has a direct effect on JBrowse since the scaffold names are part of the genomic coordinates used when the data is visualized. 

> **Note on terminology:** the docs use primary genome assembly to refer to a [non-redundant haploid representation of chromosomes, unlocalized scaffolds and unplaced scaffolds]((https://www.ncbi.nlm.nih.gov/grc/help/definitions/)). Sometimes organelle genome assemblies, such as the mitochondrial assembly, is separated from the primary assembly; those can be visualized in separate _views_ in the JBrowse 2 instance. 

Historically, the Genome Portal has used this hierarchy for choosing where to source the assembly from

1. **ENA FTP** — the default choice, for Swedish research project this is often the repository of choice for the original submission of the assembly
2. **NCBI FTP** — used when the ENA version of the assembly has known problems, e.g. incomplete number of scaffolds, issues with the FASTA headers
3. **SciLifeLab Data Repository (Figshare)** — for primary genome assemblies only resorted to for cases when neither ENA nor NCBI is usable; it is not the domain-standard for genome assemblies.

The subheadings below describe how to find the URL to a genome assembly in the different repositories. For ENA/NCBI, find the assembly by its accession number, for SciLifeLab Data Repository, find it by its DOI. The URLs should go in either the submission for or in the `config.yaml`.

> **Always use `https://`, never `ftp://`.** URLs starting with `ftp://` are not compatible with the `curl` command used in the Genome Portal `makefile` download step and also cannot be opened by browsers on the species download (Hugo) page. If you ever see `ftp://ftp.ebi.ac.uk/...` in a config, change it to `https://ftp.ebi.ac.uk/...`. The Playwright test `playwright/tests/test_data_tracks_links.py` catches `ftp://` URLs in `hugo/assets/<species>/data_tracks.json` (the download-page source), so this issue should surface during CI.

#### 3.1.1 ENA FTP (preferred source)

For assemblies submitted as whole-genome shotgun (WGS) sequences, ENA provides a direct path:

```
https://ftp.ebi.ac.uk/pub/databases/ena/wgs/public/<prefix>/<ACCESSION>.fasta.gz
```

The `<prefix>` is the first three characters of the WGS set accession, lowercased. For example, the WGS accession `CAVLGL01` gives the prefix `cav`, so the URL becomes:

```
https://ftp.ebi.ac.uk/pub/databases/ena/wgs/public/cav/CAVLGL01.fasta.gz
```

> **Note:** ENA's hostname is `ftp.ebi.ac.uk`, which can be confusing — the `ftp` is part of the hostname, not the protocol. The `curl` setup in the `makefile` handles `https://ftp` prefixed URLs.

The WGS accession is found on the assembly's ENA page (e.g. under "WGS Master" or "Assembly" fields).

> **Note:** For chromosome-level assemblies, ENA may split the FASTA into separate WGS and chromosome files. If the WGS FTP file is incomplete (missing chromosome sequences), use the ENA Browser API or the NCBI version — see below.

An alternative ENA URL format uses the Browser API, which works for chromosome-level assemblies:

```
https://www.ebi.ac.uk/ena/browser/api/fasta/<GCA_ACCESSION>?download=true&lineLimit=0&gzip=true
```

This URL requires the `fileName` field in `config.yml` because the filename is not visible in the URL path. See `config/parnassius_mnemosyne/config.yml` (mitochondrial assembly) for a real-life example.

#### 3.1.2 NCBI FTP (fallback)

Use the NCBI version when the ENA file has a known problem. Documented cases in this repo:

- **Incomplete ENA file** — `linum_trigynum`: the ENA WGS file contained only unplaced scaffolds, not the chromosome sequences. The NCBI mirror included the complete assembly.
- **Scaffold ordering in JBrowse** — `littorina_saxatilis`: NCBI orders chromosomes before unplaced scaffolds in the FASTA, which makes the JBrowse scaffold dropdown more user-friendly for species with thousands of unplaced scaffolds.

The NCBI FTP path follows a predictable pattern based on the GCA accession number. For `GCA_964030455.1`:

```
https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/964/030/455/GCA_964030455.1_<assembly_name>/GCA_964030455.1_<assembly_name>_genomic.fna.gz
```

The three directory levels split the digits of the accession number (excluding the `GCA_` prefix and the `.1` version suffix): `964030455` → `964/030/455`. The `<assembly_name>` is the genome assembly name as recorded at NCBI.

Note that NCBI files use the `.fna.gz` extension while ENA files use `.fasta.gz`; both are standard FASTA format and supported by the Genome Portal `makefile`. 

When using an NCBI assembly, the auto-generated `aliases.txt` will be empty (the `scripts/aliases` script only parses ENA-formatted headers). If data tracks refer to FASTA headers formatted differently from those in the NCBI FASTA, a manual alias file is needed — see [Section 3.6](#36-generating-a-refnamealias-file).

#### 3.1.3 SciLifeLab Data Repository / Figshare (exceptional cases)

SciLifeLab Data Repository / Figshare is used to host data tracks that does not have a domain-specific repository such as ENA or NCBI and is described in more detail in [Section 3.3](#33-sourcing-other-data-tracks). A Figshare-hosted primary genome assemblies assembly is only used for the Genome Portal when neither ENA nor NCBI is suitable (e.g. `linum_grandiflorum`, where the ENA submission had errors at the time of publication). As such, Figshare-hosted assemblies should be treated as temporary: once a corrected version is available in ENA or NCBI, the config should be updated to point there.


### 3.2 Sourcing the protein-coding genes annotation

The main source of protein-coding GFF files in the Genome Portal is NCBI. The reason for this is that ENA will split GFF files upon upload into their own `.ensembl` format to make each gene available separately, and in this process they do not preserve the original GFF file. Thankfully, ENA-submitted GFFs are mirrored to NCBI, and this is therefore the recommended source for this track type for the Genome Portal.

Following the example with accession number `GCA_964030455.1` in [Section 3.1.2](#312-ncbi-ftp-fallback), the protein-coding genes GFF will be 

```
https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/964/030/455/GCA_964030455.1_<assembly_name>/GCA_964030455.1_<assembly_name>_genomic.gff.gz
```

I.e. same base file name as the FASTA genome assembly but with `gff.gz` instead of `fna.gz`. 

### 3.3 Sourcing other data tracks

A challenge with all other data tracks than the protein-coding genes is that there seldom are any domain-specific repositories for them. The most common solution for the Genome Portal is to ask the submitting users to publish their data in SciLifeLab Data Repository. This is suitable for any data file that cannot be hosted on that ENA or NCBI - (secondary) assembly FASTA, annotation GFF, repeat BED, quantitative tracks, etc. Other archival repositories, such as Zenodo, from which individual data files can be downloaded with a URL, are also fine. 

When advising users to submit their files to these repositories, it is important that they do not pack all their data files into a single archive (`.zip`, `.tar`, `.tar.gz`). That is not compatible with how the makefile expects to download data files on a single-file basis. Each file need to be a separate object with its of URL.

> **Important: use `ndownloader.figshare.com`, not the URL shown in the browser.** When you right-click a file in the SciLifeLab Figshare web interface and copy the link, you get a URL of the form `https://figshare.scilifelab.se/ndownloader/files/<ID>`. This URL is blocked by an AWS WAF Bot Control and will fail when `curl` (and therefore the automated build pipeline) tries to download it. The correct URL for programmatic access replaces the subdomain: use `https://ndownloader.figshare.com/files/<ID>` instead; this means that the numeric file ID stays the same and only the hostname changes. When using a Figshare URL, the `fileName` key is always required in `config.yaml` since the Figshare download URLs are opaque numeric IDs that don't reveal the filename. 

### 3.4 Supported file formats

JBrowse 2 supports a range of [genomics file formats](https://jbrowse.org/jb2/features/#supported-data-formats). If JBrowse 2 supports it, by default of with a [plugin](https://www.jbrowse.org/jb2/plugin_store/), it can be displayed on the Genome Portal. The most common formats used in the Genome Portal (at the time of writing) are FASTA, GFF3, BED, and BigWig.

Some format-specific comments:

- **GTF** files are supported directly by JBrowse and the `makefile` pipeline and do not need to be coverted to GFF3. See `config/amphiura_filiformis/config.yml` for a live example. If a GTF fails to parse for any reason, [AGAT](https://github.com/NBISweden/AGAT) can convert it to GFF3:
  ```bash
  agat_convert_sp_gxf2gxf.pl -g path/to/file.gtf -o path/to/converted_file.gff
  ```
  > **GTF files are not compatible with trix text-indexing.** JBrowse's built-in feature search (which lets users jump to a gene by name) is powered by `jbrowse text-index` and only works with GFF3 files that contain `Name` or `ID` attributes. Species whose annotation is in GTF format will have an empty trix directory and no text search. GFF3 is preferred for this reason.
- **RepeatMasker `.out`** files need to be converted to BED before use. The recommended tool is [BEDOPS](https://bedops.readthedocs.io/):
  ```bash
  convert2bed --input=rmsk --output=bed < path/to/file.out > path/to/converted_file.bed
  ```
- **GFF2** files need to be converted to GFF3. This can be done with [AGAT](https://github.com/NBISweden/AGAT):
  ```bash
  agat_convert_sp_gxf2gxf.pl -g path/to/file.gff -o path/to/converted.gff3
  ```

  Note that the `.gff` extension itself does not reveal the format version (GFF1, GFF2, GFF3). An unsupported format version can cause silent failures in JBrowse — see [Section 8.3](#83-errors-caused-by-file-format-versions).

- **BAM** files have historically not been encouraged for displayed in the Genome Portal due to concern for their size and potential performance impact. However, if the user is fine with some loading times when opening the JBrowse instance, they can be included. 
- **Quantitative BED files** (Pi, Tajima's D, etc.) used as GWAS or wiggle tracks often need three preparation steps before the pipeline can process them:
  1. The first line must start with `#` — the LinearManhattanDisplay ([JBrowse 2 GWAS plugin](https://github.com/GMOD/jbrowse-plugin-gwas)) reads column names from this header line and silently shows no data if it is missing. Example fix:
     ```bash
     awk 'NR==1 {print "#" $0; next} {print}' input.bed > output.bed
     ```
  2. A dedicated end-position column (BED column 3) must exist. Example of how to add an end column:
     ```bash
     awk 'BEGIN {OFS="\t"} NR==1 {print $1, $2, "BIN_END", $3, $4} NR>1 {print $1, $2, $2, $3, $4}' input.bed > output.bed
     ```
  3. Rows with `nan` in the score column cause tabix or JBrowse parsing errors. Example of how they can be removed:
     ```bash
     awk '$NF != "nan"' input.bed > output.bed
     ```
  See [Section 7](#7-adding-quantitative-gwasmanhattan-plot-tracks) for the full workflow to add tracks of this type to a species.

- **Mitochondrial GFF files** sometimes contain features that JBrowse cannot parse. Known problematic patterns: `exon` features with anti-codon notation in the attributes column (e.g. `(tca)` in a tRNA exon). One potential fix would be to drop the offending feature types before use:
  ```bash
  awk '$3 != "exon" || /^#/' mitochondrial.gff > mitochondrial.filtered.gff
  ```


If this fixes the JBrowse visualization issues, make sure to discuss the changes with the submitting user and ask them to (re)upload the files to e.g. SciLifeLab Data Repository. 


### 3.5 Indexing and compression

Most data file types need to be indexed and (re-)compressed before JBrowse can use them. The `makefile` will automatically do this upon on file download, but if you are testing files locally or troubleshooting, here are the specific commands in isolation:

**FASTA files** — must be bgzipped (not regular gzip) and indexed with samtools:

```bash
bgzip < /path/to/file.fa > /path/to/file.fa.bgz
samtools faidx /path/to/file.fa.bgz
```

**GFF files** — must be sorted, bgzipped, and indexed with tabix:

```bash
input="/path/to/file.gff"
output="path/to/file.sorted.gff.bgz"
(grep "^#" "$input"; grep -v "^#" "$input" | sort -t$'\t' -k1,1 -k4,4n) | bgzip > "$output"
tabix -p gff "$output"
```

**BED files** — must be sorted, bgzipped, and indexed with tabix (note the sort parameters differ from GFF):

```bash
input="/path/to/file.bed"
output="path/to/file.sorted.bed.bgz"
sort -k1,1 -k2,2n "$input" | bgzip > "$output"
tabix -p bed "$output"
```

**CSI index (makefile build pipeline default)**

The build pipeline generates **CSI indexes** (not TBI) for all BED and GFF files. CSI can handle chromosomes of any length; the older TBI format cannot store positions beyond ~536 Mb (2^29 bp), a limit hit by species such as `bufotes_viridis` (chromosomes up to ~640 Mb). 

If you encounter the error below, it means a TBI index was attempted, which is no longer the default setting. This suggests that are running an outdated pipeline version/[data builder image](https://github.com/ScilifelabDataCentre/genome-portal/pkgs/container/swg-data-builder):

```
[E::hts_idx_check_range] Region X..Y cannot be stored in a tbi index. Try using a csi index
Error indexing file ...
make: *** ... Error 1
```

When **manually indexing files outside the data builder (`makefile`)**,e.g. for local testing, always use the `--csi` flag to match the pipeline:

```bash
# GFF
tabix -p gff --csi /path/to/file.sorted.gff.bgz

# BED
tabix -p bed --csi /path/to/file.sorted.bed.bgz
```

*CSI became the pipeline default for all BED and GFF files in April 2025. Older configs (e.g. `bufotes_viridis`) used manual workarounds (edits to `config.yaml`, manual upload of files to the deployment) for the previous TBI-index based pipeline. These species configs remain functional but the manual step is no longer needed for new species.*

### 3.6 Generating a refNameAlias file

When a genome assembly is uploaded to ENA or NCBI, the repository reformats the original FASTA headers to the standards of the repository. A data track annotated against the original assembly (e.g. a GFF from the research group uploaded to e.g. SciLifeLab Data Repository) may therefore use different header names than the assembly file downloaded from ENA or NCBI. The solution to this in JBrowse is to use a so-called **refNameAlias file** to map synonymous header names so that JBrowse can reconcile the different naming variants of each scaffold.

Since ENA is the recommended source for FASTA genome assemblies for the Genome Porta, there is a step in the `makefile` that automatically creates alias files for ENA sourced genome assemblies. This works since NCBI FASTA headers happen to be a substring of the ENA FASTA headers. The `makefile` helper (`scripts/aliases`) reads the downloaded FASTA and extracts the three header variants embedded in every ENA FASTA header (`>ENA|ACCESSION|ACCESSION.version description contig: original_name`), producing a `data/<species_name>/aliases.txt` file during the `build` step. The JBrowse config script (`scripts/generate_jbrowse_config`) uses this file by default when no `aliases:` key is present in `config.yml`. You do not need to do anything for ENA assemblies — the alias file is handled automatically.

A standard ENA header looks like:
> `>ENA|CAVLGL010000001|CAVLGL010000001.1 Genus species genome assembly, contig: scaffold_1`

The refNameAlias file format is tab-separated; the first column is the header used in the assembly JBrowse loads, and subsequent columns list synonymous names. For this example, the `makefile` will create an alias file with the following mapping:

```
#ENA                                   NCBI                  original
ENA|CAVLGL010000001|CAVLGL010000001.1  CAVLGL010000001.1     scaffold_1
ENA|CAVLGL010000002|CAVLGL010000002.1  CAVLGL010000002.1     scaffold_10
```

A missing or incorrect alias file is the most common cause of tracks loading silently with no features (see [Section 8.1](#81-no-features-rendered-at-all-empty-track)).

> **Exception: non-standard ENA FASTA headers.** A small number of ENA assemblies do not follow the standard header format the `scripts/aliases` script expects. When this happens the auto-generated `aliases.txt` will be empty or incorrect, and tracks will load silently with no features rendered, i.e. the same symptom as a missing alias file (see [Section 8.1](#81-no-features-rendered-at-all-empty-track)). To check whether the headers are standard, inspect a few FASTA header lines (prefixed with: `>`):
> ```bash
> zcat data/<species_name>/<assembly>.fna.gz | grep "^>" | head -5
> ```
> 
> If the headers deviate from the standard ENA header pattern (described above) you will need to generate the alias file manually and reference it with the `aliases:` key in `config.yml`. See `config/amphiura_filiformis/aliases.txt` for an example of a manually crafted alias file for a non-standard ENA assembly.
>
> *First encountered: `amphiura_filiformis` assembly (`JAZBNO01.fna.gz`), whose ENA headers did not contain the `contig:` substring that the alias script parses.*

**For NCBI-sourced assemblies** the auto-generation script skips the file since NCBI FASTA headers do not contain the ENA multi-field format and the resulting `aliases.txt` will be empty. If your data tracks use header names that differ from the NCBI assembly headers, you need to create an alias file manually and reference it in `config.yml` via the `aliases:` key. The alias file can be hosted on e.g. SciLifeLab Data Repository and called by URL just like the other data tracks.

>**Note:** For data tracks referring to the original FASTA assembly headers from before the ENA/NCBI upload not discovered by the `makefile` logic, you will need to map the scaffold names by hand.


## 4. Spinning up a local JBrowse instance to test tracks

The only reliable way to check that the JBrowse configuration created by the `makefile` works is by running it and visually inspecting it. Errors from JBrowse CLI could technically surface from the `makefile` run, but more often than not, they are only evident when running the browser. To make matters worse, some rendering issues in JBrowse are silent, so whenever you see an empty track without other errors, you should consider it as an error and investigate it (that particular case is described in more detail in [Section 8.1](#81-no-features-rendered-at-all-empty-track)). 

>**Tip:** When iterating over how changes to a species data configuration affect JBrowse, you may want to reload the web page, clear the web browser cache, or trigger a reload of the defaultSession by erasing the trailing `&session=` query suffix from the URL
>
> For example on the latter, change URL like this: 
>
>`https://genomes.scilifelab.se/genome-browser/?config=%2Fdata%2Flinum_grandiflorum%2Fconfig.json&session=local-lgra_default_session` 
>
> to and it should reload from it's latest files:
>
> `https://genomes.scilifelab.se/genome-browser/?config=%2Fdata%2Flinum_grandiflorum%2Fconfig.json`

### 4.1 Full local site with `dockerbuild` + `dockerserve`

This method builds a local Docker image that includes both the Hugo pages and the data and spins up a localhost instance. It requires that the hugo templates for the species have been added, but placeholders for these can easily generated by generated by running the `./scripts/dockeraddspecies` script once (see section on this in [how_to_submit_through_pull_request.md](how_to_submit_through_pull_request.md#321-run-the-add_new_species-script)).

After running `dockermake` for a species' `config.json` to download and prepare the data for the species to the local `data/` directory, run:

```bash
./scripts/dockerbuild -u -t local -k hugo
docker rm -f "genome-portal"; ./scripts/dockerserve -t local
```

The site will be available at `http://localhost:8080`. Use `-t local` for both commands to ensure the locally built image is used.

When iterating on changes, re-run the same `dockerbuild`, `dockerserve` commands after every edit. See section 3.3 of `how_to_submit_through_pull_request.md` for a broader discussion of the refinement loop.

### 4.2 Alternative: JBrowse Desktop client

If Docker is not available or you prefer a graphical approach, the [JBrowse 2 Desktop client](https://jbrowse.org/jb2/download/) can be used to test tracks directly from local files. This can be useful for a first sanity-check before committing to the full pipeline.

Note that performance in the Desktop client can differ from the web client used in the Genome Portal. A BAM file, for instance, may load fast in Desktop but be impractically slow on the web. Always do a final check in the Docker-served web instance before submitting a PR.

For guides on how to use the desktop client, see the [official docs](https://jbrowse.org/jb2/docs/quickstart_desktop/).


## 5. Understanding and editing config.yml manually

The species configuration file `config/<species_name>/config.yml` is the central file that the `makefile` reads in order to download, process, and configure data tracks. This file need to be edited by hand when the automated ingestion script does not or cannot produce the desired results, for instance when adding a [quantitative track](#7-adding-quantitative-gwasmanhattan-plot-tracks) with a custom defaultSession, or when tweaking track descriptions.

### 5.1 Structure overview

The file has three top-level YAML keys: `organism`, `assembly`, and `tracks`. Use two-space indentation (no tabs). Multi-word strings must be quoted; underscored strings do not need quotes. All URLs must point directly to the data file, not to a landing page.

```yaml
organism: "Genus species"

assembly:
  name: Assembly_name_from_ENA
  displayName: "G. species genome assembly GCA_XXXXXXXXX.X"
  accession: GCA_XXXXXXXXX.X
  url: "https://ftp.ebi.ac.uk/path/to/assembly.fasta.gz"
  aliases: "https://raw.githubusercontent.com/ScilifelabDataCentre/genome-portal/<commit-hash>/scripts/data_stewardship/alias_files_temp_storage/assembly.alias"
  defaultScaffold: "chr1" 

tracks:
  - name: "Protein-coding genes"
    url: "https://example.com/annotation.gff.gz"
    defaultSession: true
  - name: "Repeat annotation"
    url: "https://figshare.scilifelab.se/ndownloader/files/XXXXXXXX"
    fileName: "species_repeats.bed.gz"
    addTrack: false
  - name: "Nucleotide diversity (Pi), 5kb windows"
    url: "https://figshare.scilifelab.se/ndownloader/files/XXXXXXXX"
    fileName: "species_pi.bed.gz"
    addTrack: false
    defaultSession: true
    displayType: "gwas"
    scoreColumn: "PI"
```

### 5.2 The assembly section

| Key | Description | Required |
|-----|-------------|----------|
| `name` | Assembly name as it appears in ENA/NCBI; shown in JBrowse as the view name and in the nucleotide reference track label. | Yes |
| `displayName` | Human-friendly display name shown in the JBrowse view header. Useful when the `name` value is a long accession string. Example: `"A. filiformis genome assembly GCA_039555335.1"` | No |
| `accession` | ENA/NCBI accession number (e.g. `GCA_963668995.1`). Not displayed in JBrowse but kept for documentation. | No |
| `url` | Direct URL to the FASTA file. | Yes |
| `fileName` | Required when the URL does not contain an explicit filename. Example: `fileName: CAXEFL01.fasta.gz` | Depends on URL |
| `aliases` | Path or URL to a refNameAlias file. If omitted, the JBrowse config script defaults to the locally generated `aliases.txt` (produced automatically by `dockermake` for ENA assemblies). Only set this key when the auto-generated file is insufficient and you have manually created an alias file. | No |
| `defaultScaffold` | The FASTA header of the scaffold that JBrowse opens by default. Useful for species where the first scaffold in alphabetical order for some reason is not desired to be the default. Example: `ENA\|CAXEFL010000280\|CAXEFL010000280.1` | No |
| `bpPerPx` | Zoom level when JBrowse opens (base pairs per pixel). Default is `50`. The `configure_defaultSession` script makes an initial guess from the genome assembly FASTA, but this often needs manual tuning. Larger values zoom out more, which can be useful for species with long scaffolds or sparse annotation density. | No |

### 5.3 The tracks section

`tracks` is a list. Each item starts with `- name:`. Track order in this file determines display order in the JBrowse track selector.

| Key | Description | Required |
|-----|-------------|----------|
| `- name` | Track label shown in JBrowse. The backend expects one track to be named `"Protein-coding genes"` (since it is a mandatory track). | Yes |
| `url` | Direct URL to the data file. | Yes |
| `fileName` | Required when the URL does not contain an explicit filename. Common for Figshare download links (e.g. `https://figshare.scilifelab.se/ndownloader/files/XXXXXXXX`). | When needed |
| `defaultSession` | Set to `true` to include this track in the JBrowse defaultSession (turned on when the page loads). Omitting it leaves the track available in the selector but off by default. Protein-coding gene tracks are always enabled regardless of this key. | No |
| `addTrack` | Set to `false` to prevent `dockermake` from running `jbrowse add-track` for this track. The track is still downloaded and processed and thus allows its config to be written by `configure_defaultSession`. Required for any track that uses `displayType: "gwas"` or `displayType: "wiggle"`. See [Section 6.4](#64-when-addtrack-false-is-needed-for-a-feature-track) (feature tracks) and [Section 7](#7-adding-quantitative-gwasmanhattan-plot-tracks) (GWAS tracks). | No |
| `displayType` | Sets the JBrowse display type. One of `"linear"` (default, `LinearBasicDisplay`), `"arc"` (`LinearArcDisplay`), `"gwas"` (`LinearManhattanDisplay`, needs GWAS plugin), `"wiggle"` (`LinearWiggleDisplay`). Must be combined with `addTrack: false` for `"gwas"` and `"wiggle"`. | No |
| `scoreColumn` | Name of the column in a BED-like file to use as the plotted score. Common values: `"PI"` (nucleotide diversity), `"TajimaD"`. Only relevant for quantitative tracks with `displayType: "gwas"` or `"wiggle"`. | When needed |

> **Deprecated keys** — older configs (e.g. `config/anthophora_plagiata/config.yml`) use `GWAS: true`, `scoreColumnGWAS`, and `color`. These are no longer read by the pipeline; use `displayType: "gwas"` and `scoreColumn` instead. The deprecated keys can be left in place without breaking anything, but new tracks should use the current keys.

See [Section 5.4](#54-configuring-the-defaultsession) for how to run `configure_defaultSession` after editing these keys. Specific details for different tracks are found in [Section 6](#6-adding-feature-tracks-to-configyaml) (feature tracks) and [Section 7](#7-adding-quantitative-gwasmanhattan-plot-tracks-to-configyaml) (quantitative/GWAS tracks).

### 5.4 Configuring the defaultSession

Without a defaultSession, opening a species' JBrowse page would require the user to click though several dropdowns before they reach the genome visualisation (the JBrowse _view_). This is would be bad UX since users would have to manually select a linear view, pick the assembly, choose a scaffold, and toggle on each track. The defaultSession pre-configures all of this. The settings are stored in `config/<species_name>/config.json` and is merged into `data/<species_name>/config.json` by `dockermake`.

The `configure_defaultSession` script reads `config/<species_name>/config.yml` and the downloaded FASTA to generate `config/<species_name>/config.json`. Because it reads the local FASTA to estimate a sensible zoom level and find the name of the first scaffold in the FASTA file, `dockermake` must have been run once before running `configure_defaultSession` to create `config/<species_name>/config.json`, and then `dockermake` will need to be run once more afterwards to apply the generated defaultSession config to `data/<species_name>/config.json`.

>**Note!** There is a `jbrowse set-default-session` command in the [JBrowse CLI tool](https://jbrowse.org/jb2/docs/cli/). For various historical design choices for the `makefile` and the species `config.yaml`, the codebase does not make use that CLI command. The custom tooling gives more flexibility to the needs of the Genome Portal, but adds some complexity.

Example of a typical workflow:

```bash
# 1. Download and process data (must run first so the FASTA is available locally)
./scripts/dockermake -t stable SPECIES=<species_name>

# 2. Generate the defaultSession config
./scripts/dockeraddspecies -t stable python scripts/configure_defaultSession \
  --yaml config/<species_name>/config.yml \
  --set-default-session-all-tracks \
  -o

# 3. Re-run dockermake to incorporate the new config.json
./scripts/dockermake -t stable SPECIES=<species_name>
```

Comments on the script options:

- The `--set-default-session-all-tracks` flag writes `defaultSession: true` into every track entry in `config.yml` before generating the JSON — a convenient shortcut when you want all tracks on by default. Omit it if you have already set `defaultSession` values manually per track.

- The `-o` flag (`--overwrite`) is needed on subsequent runs to replace an existing `config/<species_name>/config.json`.

- `--skip-reading-fasta` — skips reading the FASTA to infer scaffold and zoom level. Use this if the FASTA is very large (e.g. `meganyctiphanes_norvegica`) or not yet downloaded by the `makefile`.

In addition to the track keys in [Section 5.3](#53-the-tracks-section), the `configure_defaultSession` script also reads the following `config.yml` keys:

| Key | Where | Effect |
|-----|-------|--------|
| `assembly.defaultScaffold` | assembly | Which scaffold JBrowse opens on. Defaults to the first scaffold in the FASTA. |
| `assembly.bpPerPx` | assembly | Zoom level (base pairs per pixel). Script guesses from FASTA length; often needs manual tuning. |
| `track.displayType` | track | Display type: `"linear"`, `"arc"`, `"gwas"`, `"wiggle"`. Defaults to `"linear"`. |
| `track.scoreColumn` | track | Score column name for quantitative tracks (BED-like). |
| `track.addTrack: false` | track | Tells `dockermake` to skip `jbrowse add-track`; lets `configure_defaultSession` handle the full track config instead. Required for `"gwas"` and `"wiggle"` display types. |

For the full technical reference — including how to add new display types or adapters — see [`scripts/configure_defaultSession/README.md`](../scripts/configure_defaultSession/README.md). For how this step fits into a complete track-addition workflow, see [Section 6.3](#63-standard-workflow) (feature tracks) and [Section 7.3](#73-workflow) (quantitative/GWAS tracks).

### 5.5 Secondary (organellar) assemblies

A species can have more than one assembly displayed in JBrowse. A typically case is to have a primary assembly containing the nuclear genome, and a mitochondrial genome shown in a separate JBrowse _view_. This is done using a YAML multi-document syntax: two or more YAML documents separated by `---` in the same `config.yml` file. The first document is the primary assembly; each subsequent document is a secondary assembly with its own `assembly:` and `tracks:` sections.

```yaml
organism: "Parnassius mnemosyne"

assembly:
  name: ilParMnem1.1
  url: "https://ftp.ebi.ac.uk/..."
tracks:
  - name: "Protein-coding genes"
    ...
---
assembly:
  name: ilParMnem1.1_MT
  url: "https://www.ebi.ac.uk/ena/browser/api/fasta/GCA_964186615?download=true&lineLimit=0&gzip=true"
  fileName: "parnassius_mnemosyne_mito.fasta.gz"
tracks:
  - name: "Mitochondrial annotation"
    ...
```

See `config/parnassius_mnemosyne/config.yml` for a live example.

>**Note on JBrowse track selector UX.**  When a user switches to the secondary assembly's view panel, the track selector button at the top of the page still controls the primary panel. To return to the primary panel's track selector, the user must click its own track selector button or reload the species page. This is a known JBrowse limitation with multi-panel sessions, not a configuration error.

## 6. Adding feature tracks to `config.yaml`

In JBrowse, a [FeatureTrack](https://jbrowse.org/jb2/docs/config/featuretrack/) renders discrete genomic intervals from a file and is typically used for gene annotations, repeat regions, transcript alignments, and similar data. The standard display type is `LinearBasicDisplay`, which draws coloured boxes at each feature position.

Most feature tracks require no manual intervention beyond filling out the data-tracks spreadsheet: the `full_species_ingestion_workflow.sh` wrapper (or the step-by-step workflow in [`how_to_submit_through_pull_request.md`](how_to_submit_through_pull_request.md)) handles download, compression, indexing, and JBrowse registration automatically. This section thus rather describes some edge cases where additional manual work is needed.

### 6.1 Minimal example 

A minimal feature track entry needs only `name` and `url`:

```yaml
- name: "Repeat annotation"
  url: "https://ftp.ebi.ac.uk/path/to/repeats.gff.gz"
```

Optional keys commonly used with feature tracks:

```yaml
- name: "Repeat annotation"
  url: "https://ndownloader.figshare.com/files/XXXXXXXX"
  fileName: "species_repeats.bed.gz"   # required when the URL does not reveal the filename
  defaultSession: true                  # show this track when the JBrowse page opens
```

See [Section 5.3](#53-the-tracks-section) for the full key reference.

For species submissions with only standard (non-quantitative) feature tracks, the `scripts/full_species_ingestion_workflow.sh` wrapper script will likely handle the complete workflow as described in [`how_to_submit_through_pull_request.md`](how_to_submit_through_pull_request.md).

If you are adding a track to a species that already has pages (e.g. a newly available annotation file), use the step-by-step approach:

```bash
# 1. Add the track entry to config/<species_name>/config.yml.

# 2. Download, compress, and index the new file.
./scripts/dockermake -t stable SPECIES=<species_name>

# 3. Regenerate the defaultSession (so the new track appears on page load).
./scripts/dockeraddspecies -t stable python scripts/configure_defaultSession \
  --yaml config/<species_name>/config.yml -o

# 4. Re-run dockermake to apply the updated config.json.
./scripts/dockermake -t stable SPECIES=<species_name>
```

### 6.4 When addTrack: false is needed for a feature track

For most feature tracks `addTrack` can be omitted — the pipeline runs `jbrowse add-track` automatically. The two cases where `addTrack: false` is needed are:

- **Arc display** (`displayType: "arc"`) — `jbrowse add-track` does not write a `LinearArcDisplay` entry; `configure_defaultSession` must handle it.
- **Non-standard adapters or custom display configuration** — any track that needs a config entry beyond what `jbrowse add-track` produces.

Example for an arc track:

```yaml
- name: "Long-range interactions"
  url: "https://ndownloader.figshare.com/files/XXXXXXXX"
  fileName: "species_arcs.bed.gz"
  addTrack: false
  defaultSession: true
  displayType: "arc"
```

### 6.5 Enabling clickable database cross-references (dbxref plugin)

There is a custom Genome Portal JBrowse plugin (`hugo/static/custom_jbrowse_plugins/dbxref_plugin.js`) that converts `dbxref` annotations in a GFF into clickable hyperlinks in the feature details panel.

**Supported attribute fields and databases:**

| GFF3 attribute | Databases linked |
|----------------|-----------------|
| `Dbxref=` | InterPro and its member databases (Pfam, PANTHER, Gene3D, SMART, CDD, Hamap, PIRSF, PRINTS, ProSitePatterns, ProSiteProfiles, SFLD, SUPERFAMILY, TIGRFAM), Reactome, AntiFam, MetaCyc, KEGG, FunFam |
| `Ontology_term=` | Gene Ontology (GO terms), linked via AmiGO |
| `uniprot_id=` | UniProt accessions |

Unknown accession prefixes render as plain text without a link.

At the time of writing, this plugin must be manually enabled for each species. The steps for doing so are:

1. **In `config.yml`**, set `addTrack: false` for the target track. This is required so that `configure_defaultSession` writes the complete track entry to `config/<species_name>/config.json`, where the `formatDetails` key can then be added manually (see [Section 6.4](#64-when-addtrack-false-is-needed-for-a-feature-track)):

   ```yaml
   - name: "Protein-coding genes"
     url: "https://ndownloader.figshare.com/files/XXXXXXXX"
     fileName: "species_genes.gff.gz"
     addTrack: false
   ```

2. **Run the standard workflow** (`dockermake` → `configure_defaultSession` → `dockermake`) so that `config/<species_name>/config.json` is generated with the base track entry.

3. **Manually edit `config/<species_name>/config.json`** to make two additions:

   Add the plugin to the `"plugins"` array (create the array at the top level if it does not yet exist):
   ```json
   "plugins": [
     {
       "name": "DbxrefPlugin",
       "esmUrl": "../../custom_jbrowse_plugins/dbxref_plugin.js"
     }
   ]
   ```

   Add a `"formatDetails"` key to the target track's entry in the `"tracks"` array:
   ```json
   {
     "type": "FeatureTrack",
     "trackId": "species_genes.gff",
     "name": "Protein-coding genes",
     "adapter": { "...": "..." },
     "formatDetails": {
       "subfeatures": "jexl:{dbxref:dbxrefLinkout(feature), ontology_term:ontologyLinkout(feature), uniprot_id:uniprotLinkout(feature)}"
     },
     "assemblyNames": ["AssemblyName"]
   }
   ```

4. **Re-run `dockermake`** to merge the updated `config.json` into the final `data/<species_name>/config.json`:
   ```bash
   ./scripts/dockermake -t stable SPECIES=<species_name>
   ```

> **Note!** Do not change the `esmUrl` path. `../../custom_jbrowse_plugins/dbxref_plugin.js` is relative to `data/<species_name>/config.json` and resolves to the shared plugin file served from `hugo/static/`. Changing the path will cause a 404 and silently disable the plugin.

See `config/parnassius_mnemosyne/config.json` for a complete working example.


## 7. Adding quantitative tracks to `config.yaml`

[Quantiative tracks in JBrowse](https://jbrowse.org/jb2/docs/user_guides/quantitative_track/) have score column with values for a given chromosomal region. Typically, these tracks are BED-like files that follow the first columns of the BED format with an additional a score column (see [Section 3.4](#34-supported-file-formats) for details). The name of the score column will need to be explicitly stated in the JBrowse config; for convenience, this can be controlled in `config/<species_name>/config.yml`.

Population-genomics statistics such as nucleotide diversity (Pi) and Tajima's D are displayed in the Genom Portal as Manhattan plots using the `LinearManhattanDisplay` type using by the [`jbrowse-plugin-gwas`](https://github.com/GMOD/jbrowse-plugin-gwas) plugin. All tracks that should be displayed with the Manhattan plot will need to follow the GWAS settings described in [Section 7.1](#71-configuring-configyml-for-manhattan-plot-tracks)The plugin version is pinned via the `GWAS_PLUGIN_VERSION` build argument in `docker/hugo.dockerfile` and is downloaded at image-build time into `/browser/plugins/jbrowse-plugin-gwas.umd.production.min.js`. To upgrade the plugin, change `GWAS_PLUGIN_VERSION` in that file and rebuild the Hugo image.

This section covers the manual workflow required to edit `config.yml` edits for tracks that require this configuration. Currently, the `full_species_ingestion_workflow.sh` wrapper cannot handle these cases (see Option 2 in `how_to_submit_through_pull_request.md`).

### 7.1 Configuring `config.yml` for Manhattan plot tracks 

Many quantiative tracks can be displayed well enough using the [`jbrowse-plugin-gwas`](https://github.com/GMOD/jbrowse-plugin-gwas) plugin, and thus the configuration will use the GWAS Genome Portal setting. Note that the data does not need to be from a GWAS (Genome-wide association study) experiment to use this setting; all that is needed is file with BED-like coordinates and a score column. 

A GWAS track entry requires three keys beyond the standard `name`/`url` in its `config/<species_name>/config.yml`:

```yaml
- name: "Nucleotide diversity (Pi), 5kb windows"
  url: "https://ndownloader.figshare.com/files/XXXXXXXX"
  fileName: "species_pi.bed.gz"          # required for Figshare URLs
  addTrack: false                         # skip jbrowse add-track; configure_defaultSession writes the full entry
  defaultSession: true                    # show in the default JBrowse view on page load
  displayType: "gwas"                     # render as LinearManhattanDisplay (Manhattan plot)
  scoreColumn: "PI"                       # must match the column header in the BED file's # header line
```

Why is `addTrack: false` required? There are additional configuration required in `config/<species_name>/config.json` to make these tracks display correctly and that is handled by the `configure_defaultSession` script (adapter config, `scoreColumn` binding, and plugin registration). 
The `makefile`'s logic for adding new tracks was not designed to take this into account, and instead, the `addTrack: false` option ensures that the track is skipped by the `makefile` to avoid config collision/errors.

>**Note!** There are some deprecated alternative keys older configs (e.g. `config/anthophora_plagiata/config.yml`) that use `GWAS: true`, `scoreColumnGWAS`, and `color`. These keys are no longer read by `configure_defaultSession`; use `displayType: "gwas"` and `scoreColumn` for all new tracks.

### 7.3 Building the data for for Manhattan plot tracks 

```bash
# 1. Edit config.yml — add addTrack: false, displayType: "gwas", and scoreColumn to each GWAS track.
#    Also prepare and upload the BED file (see Section 6.1 and 2.2).

# 2. Download and process the BED files (must run before configure_defaultSession
#    so the FASTA is available locally for scaffold/zoom inference).
./scripts/dockermake -t stable SPECIES=<species_name>

# 3. Generate the defaultSession config (reads config.yml and local FASTA,
#    writes config/<species_name>/config.json).
./scripts/dockeraddspecies -t stable python scripts/configure_defaultSession \
  --yaml config/<species_name>/config.yml \
  --set-default-session-all-tracks -o

# 4. Re-run dockermake to merge config.json into data/<species_name>/config.json.
./scripts/dockermake -t stable SPECIES=<species_name>

# 5. Build and serve locally to verify rendering.
./scripts/dockerbuild -u -t local -k hugo
docker rm -f "genome-portal"; ./scripts/dockerserve -t local
```

### 7.4 Verifying the track renders correctly

A correctly configured GWAS track will:
- Appear as a scatter/Manhattan plot with one point per BED window.
- Show a y-axis labelled with the score column name.

If the track is in the track selector but renders as empty or shows a flat line instead of a Manhattan plot, work through this checklist:

| Symptom | Most likely cause |
|---------|------------------|
| Track visible in selector, plot area empty | Missing `#` prefix on the BED header line; GWAS plugin cannot find column names |
| Track not visible in selector at all | `addTrack: false` was not set and `jbrowse add-track` created an entry without the plugin; delete `data/<species_name>/config.json`, fix `config.yml`, and rerun from step 2 |
| Plot renders but y-axis is blank | `scoreColumn` value does not exactly match the BED column header (check capitalisation) |
| All tracks visible but no GWAS points | `displayType: "gwas"` is missing or misspelled; track is rendering as `LinearBasicDisplay` |
| Error in browser console mentioning plugin | JBrowse version and GWAS plugin version mismatch. Typically fixed by bump both to their latest versions. |

---

## 8. Troubleshooting JBrowse rendering issues

### 8.1 No features rendered at all (empty track)

An empty track with no error message in JBrowse is a common problem and is very often caused by a missing or incorrect alias file.

What happens: the data track references FASTA header names (e.g. `scaffold_1`) that don't match the headers in the assembly being used (e.g. `ENA|CAVLGL010000001|CAVLGL010000001.1`). JBrowse silently loads the track but has nowhere to place the features.

**Checklist:**
1. Has `dockermake` been run so that `data/<species_name>/aliases.txt` exists? For ENA assemblies it is auto-generated; if the file is missing or empty, the build step may not have completed.
2. If the assembly is from NCBI (not ENA), does `config.yml` have an `aliases:` entry pointing to a manually created alias file? The auto-generated `aliases.txt` will be empty for NCBI assemblies.
3. Does the alias file actually contain the header format used by this particular track?

To quickly verify the header format in a data track, inspect the first non-comment line of the GFF or BED file:
```bash
zcat annotation.gff.gz | grep -v "^#" | head -1
```
Compare the value in column 1 (the `seqid` field) with the FASTA headers in the assembly:
```bash
zcat assembly.fasta.gz | grep "^>" | head -5
```
If they differ, the alias file must bridge them. For ENA assemblies, re-running `dockermake` should regenerate `aliases.txt` correctly. For NCBI assemblies, create a manual alias file and reference it via `aliases:` in `config.yml`, then rerun `dockermake`.

### 8.2 Error messages and how to get stack traces

When a track fails to load, JBrowse renders a **red error box directly inside the track area**. The box contains a short error message and two icon buttons on the right:

- **Show stack trace** (report/flag icon) — opens a dialog with the full source-map-resolved stack trace, the JBrowse version, and a **Copy stack trace to clipboard** button. This is the primary way to get diagnostic information; no browser developer tools are needed.
- **Retry** (refresh icon) — reloads the failed track, which can help distinguish a transient network hiccup from a persistent error.

If the entire JBrowse instance fails to initialise (e.g. a malformed top-level `config.json`), a full-screen fatal error dialog appears instead of a per-track red box.

**To get the stack trace:**

1. Locate the red error box inside the failing track.
2. Click the **report icon** on the right side of the box (tooltip: "Show stack trace").
3. In the dialog that opens, click **Copy stack trace to clipboard** or read the trace directly.

The stack trace pinpoints whether the problem is a network error (file not found), a parsing error (incorrect file format), or a config error (missing key in `config.json`). Pasting it into an AI assistant (e.g. Claude, ChatGPT) along with a short description of what you were trying to do is an efficient way to diagnose the root cause.

**Checking network requests:** If the error message is vague or the track shows nothing at all (no error box), also open the browser developer tools (`F12` or `Cmd+Option+I` on macOS) and check the **Network** tab to see whether data files are being fetched successfully (HTTP `200`) or returning errors (`404` file not found, `403` access denied, etc.).

### 8.3 Errors caused by file format versions

Some file extensions do not uniquely identify the format version. A `.gff` file, for example, might be GFF1, GFF2, or GFF3 — JBrowse only supports GFF3. In these cases the file extension passes the first check but JBrowse fails to parse the file and either shows an error or renders nothing.

To identify the format version, inspect the file header:
```bash
zcat annotation.gff.gz | head -5
```
A GFF3 file starts with `##gff-version 3`. If it shows `##gff-version 2` or no version header at all, convert it to GFF3 with AGAT:
```bash
agat_convert_sp_gxf2gxf.pl -g annotation.gff.gz -o annotation.gff3.gz
```
Ask the data provider to make the converted file publicly available so the Genome Portal can reference the corrected version.

### 8.4 Bumping the JBrowse version

In rare cases, an empty track or rendering error is caused by a bug in the specific version of JBrowse embedded in the Genome Portal rather than by the data files themselves. This has occurred in the past — certain JBrowse releases had bugs affecting specific track types or file parsing routines that were fixed in subsequent releases.

Signs that a JBrowse version bump might be needed:
- The same data files load correctly in the JBrowse Desktop client or in a newer JBrowse web sandbox, but not in the Genome Portal instance.
- The stack trace points to internal JBrowse code, not to missing files or config errors.
- The problem appeared after a previously working track stopped rendering without any data or config change.

If you suspect a JBrowse version issue, check the [JBrowse 2 changelog](https://github.com/GMOD/jbrowse-components/blob/main/CHANGELOG.md) for bug fixes in releases after the current Genome Portal version, and raise the issue with the Genome Portal team. Bumping the version requires a change in the Genome Portal's Docker build configuration and needs to be tested against all existing species before being merged.

### 8.5 Node.js `uv_os_get_passwd` error in Docker

If `jbrowse add-assembly` or `jbrowse add-track` commands fail inside Docker with:

```
SystemError [ERR_SYSTEM_ERROR]: A system error occurred: uv_os_get_passwd returned ENOENT
```

the fix is to ensure `ENV SHELL=/bin/sh` is set in `data.dockerfile`. This error appeared after certain Node.js or OS-layer updates and is macOS-specific in origin. Check the Dockerfile for this environment variable if the error resurfaces after a dependency bump.


### 8.6 Transient download failures in the makefile

If a `dockermake` run fails mid-download with a `curl` timeout or connection reset, the most likely cause is a transient server-side issue rather than a configuration error. Simply re-run `dockermake` — ENA and NCBI servers occasionally return errors that resolve within minutes. If the same URL fails across multiple retries on different days, check whether the file has moved (ENA sometimes reorganises FTP paths after accession updates) before investigating your network or config.