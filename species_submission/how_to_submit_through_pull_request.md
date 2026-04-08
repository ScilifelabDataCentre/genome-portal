# How to submit a new species to the Swedish Reference Genome Portal through a pull request 

This guide describes the full workflow for creating pages for a new species in the Genome Portal. The guide is written with bioinformatics-skilled users or staff in mind and includes every step from filling out the submission forms and generating the files needed for the website and JBrowse configurartion, to building a local test instance of the new pages and eventually opening a Pull Request for review.

Throughout the guide there will be a tutorial case that uses public data from the algae _Volvox carteri_. If this is your first time adding a species to the Genome Portal, you may want to follow along by trying out those commands.

If you run into any issues or have question, don't hesitate to contact the Genome Portal staff as described in the [main README at the top of the repository](https://github.com/ScilifelabDataCentre/genome-portal).

## 1. Setup

This workflow expects a UNIX-computer with Docker installed. We reccomend [Rancher Desktop](https://rancherdesktop.io/) (full open-source software) or [Docker Desktop](https://www.docker.com/products/docker-desktop/) (open-source software with paid elements) for ease of installation. 

Start by cloning the repository. `git` is commonly included in UNIX systems, but you might need to install it on your computer if not already present. Choose a directory of your liking and clone the main branch of the Genome Portal into it with:

```bash
git clone https://github.com/ScilifelabDataCentre/genome-portal.git
```

Create a new branch. You can name this anything, but we reccomend `add-<species-name>`. Example: `add-volvox-carteri`.

```bash
git checkout -b add-<species-name>
```

## 2. Fill out the submisison forms and crop your picture to 4:3-ratio

The species ingestion pipeline takes two submission forms and one picture file and uses that to create and populate the pages for the species. In order for this to work, all data from the species that are to be displayed in JBrowse needs to be publicly available in an end-repository, such as ENA/NCBI, Zenodo, or SciLifeLab Data Repository (Figshare). This allows the ingestion pipeline to download the data, and ensures that that the data is properly archived in an end-repository.

Fill out the forms and prepare the picture of the species as described in sections [2.1](#21-submission-forms) and [2.2](#22-species-picture) below. Save the final files to `species_submission/local_inputs`. This directory has a special meaning for the Docker images we will be using, and it not under source control since we do not need the particular files to be commited to the repository.

### 2.1. Submission forms

To be able to accomdate a wide range of user with different technical skillsets, the Genome Portal submission forms are provided in MS Office format (`.docx` and `.xlxs`). Note that the form ingestion pipeline that we will be using below has only been tested with forms that have been edited with MS Word and MS Excel; your milage may therefore vary if you use other document editing software to fill out the forms.

The submission form templates are located in `species_submission/submission_form_templates`. Make a copy of the forms, for instance at `species_submission/local_inputs`, and fill them out based on the instructions contained with in the forms. Start with `01-species-submission_v1.3.docx`; that form will eventually tell you to switch to `02-data-tracks_v1.3.xlsx`.

https://github.com/ScilifelabDataCentre/genome-portal/tree/main/species_submission/submission_form_templates



There is one special mandatory case that we would like to emphasize here: namely the Genome row in the spread sheet.


TODO explan the GCA and BUSCO










### 2.2. Species picture

max file size

.webp

## 3. Run the form ingestion workflow

There are three Docker images that need to be built in order to run the workflow to add a new species to the Genome Portal. The following two image are enough to build once every time main branch of the GitHub repo has been updated. In practice, that means it should be enough to build them once at the start of the species submission workflow. 

```bash
./scripts/dockerbuild -k add_species -t local && \
./scripts/dockerbuild -u -t local -k data
```

The third Docker image contains the website data, and needs to be run everytime you make an update to the content or data of the webpages. The guide will tell you when that Docker build step needs to be run.

To follow along with the Example, copy two pre-filled test forms to `species_submission/local_inputs`:

```bash
cp scripts/add_new_species/tests/fixtures/submission_form_example/01-test-species-submission_v1.3.docx species_submission/local_inputs/ && \
cp scripts/add_new_species/tests/fixtures/submission_form_example/02-test-data-tracks_v1.3.xlsx species_submission/local_inputs/
```



### 3.1. Option 1: Run the whole workflow with a "I'm feeling lucky" script

Your milage may vary.

This will currently not work on quantiative tracks were a score column needs to be declared. For those tracks, please follow the step-by-step apporach in section 3.2. instead.

```bash
bash scripts/full_species_ingestion_workflow.sh \
-f /local_inputs/01-test-species-submission_v1.3.docx \
-d /local_inputs/02-test-data-tracks_v1.3.xlsx \
-i /scripts/add_new_species/templates/placeholder_image_4-3_ratio.webp 
```


### 3.2. Option 2: Run the workflow step-by-step

TODO needed for finetuning some tracks

A recurring parameter is `<species_name>` which is the lowercase, underscored binomial species name. For instance,  _Volvox carteri_  becomes `volvox_carteri`.

We will use example data for this. 

#### 3.2.1. Build the add-new-species Docker container


```bash
./scripts/dockerbuild -k add_species -t local 
```

#### 3.2.2. Run the add_new_species script

Example: 

```bash
./scripts/dockeraddspecies python scripts/add_new_species --species-submission-form=/local_inputs/01-test-species-submission_v1.3.docx --data-tracks-sheet=/local_inputs/02-test-data-tracks_v1.3.xlsx --species-image=/scripts/add_new_species/templates/placeholder_image_4-3_ratio.webp --overwrite 

# add the option --print-species-slug-only to have the script only print the species_name as output. This can be useful if scripting with the species_slug, which is the case of the script in section 3.1
```

#### 3.2.3. Build the data builder Docker container

```bash
./scripts/dockerbuild -u -t local -k data
```

#### 3.2.4. Use the data builder to download the data

Example:

```bash
./scripts/dockermake -t local SPECIES=volvox_carteri
```

#### 3.2.5. Create a defaultSession configuration for the species

Manual step to turn on tracks!

Manually configute the quantiative tracks!

This requires that the genome assembly has been downloaded, therefore it needs to be run after dockermake (step 3.2.4.)

Example:

```bash
./scripts/dockeraddspecies python scripts/configure_defaultSession --yaml config/volvox_carteri/config.yml -o && \
./scripts/dockermake -t local SPECIES=volvox_carteri jbrowse-config
```

Note! Ensure that both commands have been run.

#### 3.2.6. Collect statisics from the assembly and the protein-coding genes annotation

TODO

Example:

```bash
./scripts/dockeraddspecies python scripts/generate_species_stats --yaml config/volvox_carteri/config.yml
```


#### 3.2.7. Build the hugo image and view the output in localhost

This takes the specific files, so unlike the dockeraddspecies and dockerbuild, this image needs to be rebuilt every time you make changes to the species data

```bash
./scripts/dockerbuild -u -t local -k hugo 
```

```bash
docker rm -f "genome-portal"; ./scripts/dockerserve -t local
```



#### 3.2.8. Make refinements

Step 3.2.1. and 3.2.3. (build Docker images for `dockeraddnewspecies` and `dockerbuild`) can most likely be skipped here. But if long time has passed since you last made changes to the branch, it would be good practice to rebuild these images too

### 3.3. When files need to be deleted

Note! run the dockermake clean uninstall first
If you have only used the add_new_species script, you can skip the dockermake

Example:

```bash
./scripts/dockermake SPECIES=volvox_carteri clean uninstall && python scripts/add_new_species/removespecies.py -s volvox_carteri -f
```


## 4. Make a Pull Request

TODO: add text here. Maybe a checklist.