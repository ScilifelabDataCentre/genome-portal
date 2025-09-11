Swedish Reference Genome Portal
========

This repository contains the source code for the [Swedish Reference Genome Portal](https://genomes.scilifelab.se/), which:

- Showcases genome research performed in Sweden on non-model eukaryotic species.
- Lowers the barrier of entry to access, visualise, and interpret genome data.
- Encourages sharing of genomic annotations, even the seldom-published kind.
- Strives to present FAIR data, available in public repositories.


## Table of Contents

1. [Overview](#overview)
2. [Cite this portal](#cite-this-portal)
3. [Contributing](#contributing)
4. [Funding](#funding)
5. [Contact us](#contact-us)
6. [Technical overview](#technical-overview)
	- [Repository Layout](#repository-layout)
	- [Local development](#local-development)
7. [Credits](#credits)

## Overview

- The Swedish Reference Genome Portal website is built using the
[Hugo](https://gohugo.io/) static web generator.

-  The [JBrowse2](https://jbrowse.org/jb2/) genome browser is
embedded within the website to visually explore genome datasets.

- Primary data file sources are available in public repositories
(such as [ENA](https://www.ebi.ac.uk/ena/browser/home)), and prepared
for display on JBrowse by our `Makefile` recipes (essentially
compressing and indexing).

- The code for the Genome Portal is available under an MIT (open
  source) license.

- The Genome Portal website is currently hosted by the [KTH Royal
  Institute of Technology](https://www.kth.se/) in Stockholm.


## Cite this portal

<a href="https://doi.org/10.5281/zenodo.14049736"><img src="https://zenodo.org/badge/768569366.svg" alt="DOI"></a>

See 'Cite this repository' in the "About" section at the top right of this page.


## Contributing

Two types of contributions are especially welcome:

- **Datasets for display in the portal**: Consult our
[requirements](https://genomes.scilifelab.se/contribute) for including a
genome dataset to the portal, and contact us if you have any questions.

- **Source code and documentation**: We welcome contributions, small and large,
to our codebase and documentation. They will be published after review and
approval by the Genome Portal team. Fork, open a PR, or contact us to discuss ideas!


## Funding

This service is supported by [SciLifeLab](https://www.scilifelab.se/)
and the [Knut and Alice Wallenberg
Foundation](https://kaw.wallenberg.org/en) through the [Data-Driven
Life Science (DDLS) program](https://www.scilifelab.se/data-driven/),
as well as by the [Swedish Foundation for Strategic Research
(SSF)](https://strategiska.se/en/).

## Contact us

We welcome all questions and suggestions (including feature requests or bug reports).

- Email us at [dsn-eb@scilifelab.se](mailto:dsn-eb@scilifelab.se).
- [Create an issue on Github](https://github.com/ScilifelabDataCentre/genome-portal/issues/new).


## Technical overview

This section contains high-level technical documentation about the
source code.

### Repository layout

- The `config/` directory contains information about data sources
  (tracks and assemblies) displayed in the genome browser.
  - Each species subdirectory includes:
	- `config.yml` : specifies the assembly and tracks to be displayed in JBrowse2.
	- `config.json` : starting point from which to generate a complete JBrowse2
      configuration, based on `config.yaml`. A common use is to define
      default browsing sessions.

- Different `make` recipes prepare the material described in `config/`
  for use by JBrowse2. The main operations are downloading data files,
  compressing using `bgzip` and indexing with `samtools`.

- The website content resides in the `hugo` directory.
  - Most importantly, each species gets:
    1. A content subdirectory in `hugo/content/species/` (e.g. `hugo/content/species/clupea_harengus`).
	2. A data directory in `hugo/data/` (taxonomic information and statistics).
	3. An assets directory in `hugo/assets` (data inventory).

- The `scripts` folder contains executables to help:
    1. Build and serve the website using Docker.
	2. Add a new species to the website content.
	3. Add new datasets to the portal.

- The `tests` folder contains tests and fixtures, mainly covering the
  data preparation scripts.

- The `docker` folder contains two Docker files:
	1. `docker/data.dockerfile` used for data preparation (everything that `make` needs).
	2. `docker/hugo.dockerfile` used to build and serve the website.

### Local development

The steps described below requires
[`docker`](https://www.docker.com/) to be installed.

**1. Clone the repository**

```
git clone git@github.com:ScilifelabDataCentre/genome-portal.git
cd genome-portal
```

**2. Build and install the genomic data**

```bash
# Build local image from `docker/data.dockerfile`
./scripts/dockerbuild data

# Run the dockermake script to build the assets and install them locally.
./scripts/dockermake
```

You may need to be patient, some files are tens of Gigabytes. Should
only a subset of species be of interest, you can restrict the
scope of the build:

```bash
./scripts/dockermake SPECIES=clupea_harengus,linum_tenue
```

**3. Run the web application container**

Then to run the website locally, you have several options:

#### Using the latest development image

```bash
docker pull ghcr.io/scilifelabdatacentre/swg-hugo-site:dev
./scripts/dockerserve -t dev
```

#### Using a local build

```bash
./scripts/dockerbuild -t local -k hugo
./scripts/dockerserve -t local
```

#### Using the Hugo development server

This last method is adequate when you want to see changes to the
source immediately reflected in the web browser. 

It requires the additional step of installing the JBrowse static
bundle in `hugo/static/browser`:

```bash
./scripts/download_jbrowse v2.15.4 hugo/static/browser
./scripts/dockerserve -d
```

---

Either of these methods will serve you the website at `http://localhost:8080/`.



### Making a new release/updating the dev cluster

We use [kubernetes](https://kubernetes.io/) to deploy and manage both the production and development instances of the genome portal.

This repository is responsible for making the 2 docker images needed for the deployment. This is controlled by this [GH actions workflow file](https://github.com/ScilifelabDataCentre/genome-portal/blob/main/.github/workflows/publish_images.yml).

**To update the production instance we need to create a new release with GitHub:**
- Identify a commit to base the release on.
- Agree with the team on the: 
  - commit to tag.
  - the planned version number (we use semantic versioning)
  - The contents of the release, [use the previous releases as inspiration](https://github.com/ScilifelabDataCentre/genome-portal/releases) 
- Once you have the go ahead, either:
  - Create an annotated tag locally (e.g: `git tag -a v1.3.1 "v1.3.1"` ) and push the tag, Then create the release (on that tag) using GitHub's interface.
  - Create the release using GitHub's interface and specify the commit you want to use and get GitHub to automatically create the tag for you.   
- Once the release is published, a GH actions workflow will be triggered automatically to build the two images. The docker images will be tagged with the same string as used for the git tag (i.e. vX.X.X). They will also be given the tag "latest". You can see [the docker images created from this repository here](https://github.com/orgs/ScilifelabDataCentre/packages?repo_name=genome-portal). 

- With the 2 images made, you can follow the instructions in the README of our [private repository that contains the kubernetes manifest files](https://github.com/ScilifelabDataCentre/argocd-genome-portal) which we use in combination with [ArgoCD](https://argo-cd.readthedocs.io/en/stable/) to define the desired state of the cluster. 

**To update the development instance** 

- Identify the commit you want the docker images to be built off of. 
- If the commit is on the main branch a GH actions workflow run will have already built the images ([unless the commit message was prefixed to skip CI](https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-workflow-runs/skipping-workflow-runs)). The images will be tagged with the full commit hash. If the image is already built your job on this repository is already done. 
- If the commit is on any other branch you'll need to trigger a [workflow_dispatch](https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-workflow-runs/manually-running-a-workflow) to create the docker images. 
- Head to the actions tag on GitHub and to the action "Build and push both docker images to the GitHub Container Registry". From there click run manual workflow. You can choose to specify the name of the image tag if you want. Otherwise leave the input blank and it will be tagged with the full commit hash.  


**Once the images are built you can head over to our [private repository that contains the kubernetes manifest files](https://github.com/ScilifelabDataCentre/argocd-genome-portal) and follow the instructions there on how to apply your changes to the cluster.**



## Credits

The Swedish Reference Genome Portal is developed and maintained by the DDLS 
Data Science Node in Evolution and Biodiversity (DSN-EB) team as part of 
the [SciLifeLab Data Platform](https://data.scilifelab.se/), operated by the 
SciLifeLab Data Centre. Members if the DSN-EB team are affiliated 
with [SciLifeLab Data Centre](https://www.scilifelab.se/data/) 
and the [National Bioinformatics Infrastructure Sweden (NBIS)](https://nbis.se/), 
based at Uppsala University and the Swedish Museum of Natural History. 
