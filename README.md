genome-portal - The repository for the Swedish Reference Genome Portal
========

The Swedish Reference Genome Portal (https://genomes.scilifelab.se/) is a platform facilitating access and discovery of genome data of non-model eukaryotic species studied in Sweden. 

**The Swedish Reference Genome Portal aims to:**

- Highlight and showcase genome research performed in Sweden.
- Promote sharing of annotations of genomic features that rarely get published.
- Ensure all data shown on the Genome Portal is aligned with the FAIR principles and available in public repositories.
- Make it easier to access, visualise, and interpret genome data by lowering the barriers to entry.


## Table of Contents

1. [Implementation overview](#implementation-overview)
2. [Contact us](#contact-us)
3. [Contributing](#contributing)
4. [Cite this portal](#cite-this-portal)
5. [Funding](#funding)
6. [Developement information](#development-information)
	- [Repository Layout](#repository-layout)
	- [Local development setup](#local-development-setup)
	- [Up and running!](#org6eb5bf4)


## Implementation overview

The Swedish Reference Genome Portal website was built using the static website builder, [Hugo](https://gohugo.io/). The genome browser [JBrowse2](https://jbrowse.org/jb2/) is used to display the datasets and is embedded into the static website. All data shown on the Genome Portal is available in public repositories. We retrieve a copy of the data from the repositories for display on the genome browser. To download and prepare the genomic data files we use different `make` recipes which are included in this repository. 

The code for the Genome Portal is available under an MIT (open source) license. The Genome Portal is deployed on a [Kubernetes](<https://kubernetes.io/>) cluster located at the [KTH Royal Institute of Technology](https://www.kth.se/) in Stockholm.


TODO - perhaps we can add a gif/screenshot of the website in action? 


## Contact us

We welcome all questions and suggestions regarding The Swedish Reference Genome Portal. This include feature requests or bug reports. 

There are several ways to get in contact with us, please choose the option most convienent for you:

- Email us at [dsn-eb@scilifelab.se](mailto:dsn-eb@scilifelab.se).
- Fill out our [contact form on the website](https://genomes.scilifelab.se/contact/).
- [Create an issue in](https://github.com/ScilifelabDataCentre/genome-portal/issues/new) this GitHub repository. 


## Contributing 

Contributions are very welcome and can be split into two main types.  

- **Contributing a dataset into the Genome Portal**: In order to include a dataset into the Genome Portal there are a few requirements. You can read about the [requirements for adding a genome project here](https://genomes.scilifelab.se/contribute). Please Feel free to contact us if you have any questions regarding this. 

- **Contributions to the codebase**: We welcome both small and large contributions to the codebase. For larger changes we encourage you to first [get in contact with us](https://genomes.scilifelab.se/contact/) to discuss the idea. PLease read below for details about the project. 


## Cite this portal

<a href="TODO"><img src="https://zenodo.org/badge/256458920.svg" alt="zenodo DOI"></a>

Click on 'Cite this repository' near the top right of this repository to see how to formally cite this repository.

## Funding

This service is supported by [SciLifeLab](https://www.scilifelab.se/) and the [Knut and Alice Wallenberg Foundation](https://kaw.wallenberg.org/en) through the [Data-Driven Life Science (DDLS) program](https://www.scilifelab.se/data-driven/), and also by the [Swedish Foundation for Strategic Research (SSF)](https://strategiska.se/en/).


## Development Info

TODO - placeholder here... 


### Repository Layout

- Each organism has it's own sub-directory inside `config/`, for example `config/clupea_harengus`.
- This configuration sub-directory includes: 
	- a `config.yml` file specifying the assembly and tracks to be displayed in JBrowse.
	- a `config.json` An optional file specifying how the default JBrowse session should look like.

- Different `make` recipes (documented below) use this information to download and prepare genome files when necessary, and generate a `config.json` configuration file used by JBrowse. When ran locally, a .gitignored folder called `data` (e.g. `data/clupea_harengus`) will be created to store the output of these `make` recipes. 

- All those generated assets inside `data` are then moved by `make install` to the `hugo/static` directory, and thus made accessible to the Hugo site.

- The static website is located inside the folder `hugo`, with each species having 3 sub-directories inside this folder: 
	1. The species specific webpage content inside `hugo/content/species/`, e.g. `hugo/content/species/clupea_harengus`. The three markdown files inside each orgnaism's folder give rise to the three pages/tabs per species as seen on the website.
	2. A `data` folder inside the Hugo site (e.g. `hugo/data/clupea_harengus`). 
	3. A `assets` folder inside the Hugo site (e.g. `hugo/assets/clupea_harengus`). 

- The `scripts` folder contains: 
	1. The `make` recipes and associated scripts/files
	2. Python scripts to help with adding new species. 
	3. The `data_stewardship` subdirectory stores scripts and workflows for the process of adding new datasets to the Portal. 

- The `tests` folder contains tests using [Bats (Bash Automated Testing System)](https://github.com/bats-core/bats-core). 

- The `docker` folder contains two docker files that are used the deployment: 
	1. `docker/data.dockerfile` - An image that can be used to download and prepare the genome data files using different `make` recipes. The resulting data files are stored in a persistent volume on the Kubernetes cluster. 
	2. `docker/hugo.dockerfile` - An image containing the static website. The data on the persistent volume is accesible to the container running this image. 


### Branches 

This repository contains two permenant branches:
- `main`: Branch to be deployed in development, images built on this branch are tagged `dev`.
- `prod`: Branch to be deployed in production, images built on this branch are tagged `dev`.

Generally, work should be performed on a feature branch (typically checked out from main) and a PR should be made to merge this work into main. Changes from main will be merged into prod (via a PR) periodically. 


### Local development setup

As a prerequisite to running the site locally, [`docker`](https://www.docker.com/) and [`hugo`](https://gohugo.io/) should be installed. 

**1. Clone the repository:**

```
git clone git@github.com:ScilifelabDataCentre/genome-portal.git
cd genome-portal
```

**2. Build and install the datasets used by JBrowse locally:**

```bash 
# Build local `docker/data.dockerfile` docker image
./scripts/dockerbuild.sh data

# Run the dockermake script to build the assets and install them locally. 
SWG_DOCKER_TAG=local ./scripts/dockermake.sh
```

Note that the build step can take sometime for the first run (or if you delete the .gitignored data folder created by the `make build` step). You can therefore selectively build the assets for a particular species as follows: 

```bash
# Builds JBrowse assets for the herring (aka clupea harengus) only
./scripts/dockermake.sh SPECIES=clupea_harengus build
```


**3. Run the Hugo site locally**

```bash
cd hugo
hugo server --disableFastRender --noHTTPCache --ignoreCache # flags recommended in development mode 
```
The website will be then visible to you at the address: http://localhost:1313/ on your web browser.

Alternatively, you can use docker to build the Hugo image and run that locally 

```bash 
# build the hugo image
./scripts/dockerbuild.sh hugo
# You can run then run this image locally as follows: 
docker run -p 8080:8080 ghcr.io/scilifelabdatacentre/swg-hugo-site:local
```

The website will be then visible to you at the address: http://localhost:8080/ on your web browser. 









################################################## NOT SURE WHERE THE BELOW STUFF SHOULD GO ############################

### Data operations

Primary sources for genomic assemblies and annotations tracks should
be hosted remotely. However, for some data formats such as `FASTA` and
`GFF`, JBrowse expects acompanying index files.

Therefore, remote `FASTA` and `GFF` files need to be downloaded for
indexing. We keep local copies of those files and ensure they are
compressed using the block gzip format.





### Docker 


#### 1. `docker/hugo.dockerfile` : Builds a docker image containing the hugo website ready to be run. 
You can obtain the latest version of this image from the [packages section of this repository](https://github.com/orgs/ScilifelabDataCentre/packages?repo_name=genome-portal). 

To build an run the Hugo site yourself/locally you can do the following from the root directory of the repository. 

_Please note that you need to be in the root of the repository for this to work_

```bash 
docker build -t swg-hugo-site:local -f docker/hugo.dockerfile .
```

You can run then run this image locally as follows: 

```bash 
docker run -p 8080:8080 swg-hugo-site:local
```

The site will be then visible to you at the address: http://localhost:8080/ on your web browser. 



#### 2. `docker/data.dockerfile` : Builds a Docker image that can be used to download and process the data assets needed for the JBrowse section of the website. 

As above, you can obtain the latest version of this image from the [packages section of this repository](https://github.com/orgs/ScilifelabDataCentre/packages?repo_name=genome-portal). 

Then to use the image to build all the data files you can use the provided script: 

```bash 
./scripts/dockermake.sh build
```

If you want to specfiy the image and/or tag used you can specify them via enviroment variables
For example:

```bash 
SWG_DOCKER_IMAGE=ghcr.io/scilifelabdatacentre/swg-data-builder SWG_DOCKER_TAG=docker-dir ./scripts/dockermake.sh build
```







### pre-commit

This repository uses [`pre-commit`](https://pre-commit.com/) which can be used to automatically test the changes made between each commit to check your code. Things like linting and bad formatting can be spott

To setup `pre-commit` for this repositoryyou'll need to install the python package `pre-commit`.

```
# 
pip install -r requirements.txt

# Install the precommit hooks (run from the root of the GitHub repository). 
pre-commit install
```

### Commiting with pre-commit installed: 

Now when you commit with pre-commit installed you're commits will be tested against the pre-commit hooks included in this branch and if everything goes well it will look something like this:

``` 
$ git commit 
Check Yaml...............................................................Passed
Check JSON...............................................................Passed
Check for added large files..............................................Passed
Fix End of Files.........................................................Passed
Trim Trailing Whitespace.................................................Passed
markdownlint-fix.........................................................Passed
ruff.....................................................................Passed
ruff-format..............................................................Passed
[add-precommit-ghactions 71c6541] Run: "pre-commit run --all-files"
 39 files changed, 59 insertions(+), 67 deletions(-)
```

If one of the tests failed your commit will be blocked If a check fails during the `pre-commit` process, the commit will be blocked and will not proceed. The `pre-commit` tool will output a message indicating which hook failed and often provide some information about what caused the failure. 

Pre-commit will fix most issues itself the developer is expected to fix the issues that caused the failure and then attempt the commit again. Once all hooks pass, the commit will be allowed to proceed.


Whilst not ideal, if you need to bypass the failing test, you could edit the `.pre-commit-config.yaml` file or skip running pre-commit on this test. 

``` 
git commit --no-verify 
``` 

### pre-commit and GitHub actions
The pre-commit tests are also run using GitHub actions as a way to ensure the code commited passes the pre-commit tests (pre-commit is run locally on each developers PC). In some cases new rules/exceptions should be added to the pre-commit tests as they may be too strict we run so don't take it personally if your code fails a check.  

