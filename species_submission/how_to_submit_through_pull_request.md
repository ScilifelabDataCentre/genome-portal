# How to submit a new species to the Swedish Reference Genome Portal through a pull request 

TODO add text here

This guide is for users, as well as for staff.

It takes the two species submission forms and uses them to create and populate the pages for the new species.

## 1. Setup

This workflow expects a UNIX-computer and Docker. We reccomend Rancher Desktop (completely open-source) or Docker Desktop for ease of installation.


```bash
git clone https://github.com/ScilifelabDataCentre/genome-portal.git
```

Create a new branch. You can name this anything, but we reccomend `add-<species-name>`. Example: `add-clupea-harengus`.

```bash
git checkout -b add-<species-name>
```


## 2. Fill out the submisison forms and crop your image to 4:3-ratio

TODO add text here

## 3. Run the form ingestion workflow

There are three Docker images that need to be built in order to run the workflow to add a new species to the Genome Portal. The following two are enough to build when the main branch of the github repo has been updated

```bash
./scripts/dockerbuild -k add_species -t local && \
./scripts/dockerbuild -u -t local -k data
```

The third one has the website data, and needs to be run everytime you make an update to the content or data of the webpages. The guide will tell you below when that docker build step needs to be run.

To follow along with the example:

cp the files from fixture to local_inputs. the docker container mounts that with /local_inputs/

### 3.1. Option 1: Run the whole workflow with a "I'm feeling lucky" script

Your milage may vary.

This will currently not work on quantiative tracks were a score column needs to be declared. For those tracks, please follow the step-by-step apporach in section 3.2. instead.

```bash
bash scripts/full_species_ingestion_workflow.sh \
-f /local_inputs/01-test-species-submission_v1.2.docx \
-d /local_inputs/02-test-data-tracks_v1.3.xlsx \
-i /scripts/add_new_species/templates/placeholder_image_4-3_ratio.webp 

```


### 3.2. Option 2: Run the workflow step-by-step

TODO needed for finetuning some tracks

A continuing parmeter is `<species_name>` which is the lowercase, underscored binomial species name. For instance _Clupea harengus_ becomes `clupea_harengus`.

We will use example data for this. 

#### 3.2.1. Build the add-new-species Docker container


```bash
./scripts/dockerbuild -k add_species -t local 
```

#### 3.2.2. Run the add_new_species script

Example: 

```bash
./scripts/dockeraddspecies python scripts/add_new_species --species-submission-form=/local_inputs/01-test-species-submission_v1.2.docx --data-tracks-sheet=/local_inputs/02-test-data-tracks_v1.3.xlsx --species-image=/scripts/add_new_species/templates/placeholder_image_4-3_ratio.webp --overwrite 

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