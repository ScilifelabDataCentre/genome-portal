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

### 3.1. Option 1: Run the whole workflow with a "I'm feeling lucky" script

Your milage may vary.


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

Example:

```bash
python scripts/add_new_species/removespecies.py -s volvox_carteri -f

dockermake SPECIES=volvox_carteri clean uninstall

```

## 4. Make a Pull Request

TODO: add text here. Maybe a checklist.