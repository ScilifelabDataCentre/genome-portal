# Data Stewardship scripts

This subdirectory stores scripts and workflows for the process of adding new datasets to the Genome Portal. The scripts are not intended for the deployment of the portal itself. Therefore, many of the scripts will rely heavily on external dependencies in the form of established bioinformatics tools.

Each script has its own documentation, and the easiest way to access that is to open the file in an editor. It contains a description of the purpose of the scrip, information on how to use it, and a list of the dependencies.

Some of the scripts will produce log files. These will be saved to the logs/ directory, unless otherwise specified in the code or command line call.

## List of scripts

- **compare_assembly_versions.sh**

This script performs pairwise comparison of two versions of the same genome assembly to identify if there are any differences between the nucleotide sequences (the fasta headers are not considered). This can for instance be used to spot if an alternative version of an assembly contains scaffolds not found in the version on ENA or NCBI (such as mitochondrial scaffolds). Use-case example: compare that ENA (CAVLGL01.fasta.gz) and NCBI (GCA_963668995.1_Parnassius_mnemosyne_n_2023_11_genomic.fna.gz) versions of the Clouded Apollo assembly and check if they are identical.

- **configure_default_session.py**

This script reads a config.yml from a species folder (./config/[SPECIES_NAME]/config.yml) and uses its values to generate a JBrowse 2 defaultSession configuration. The output file is intended to be copied back to the species folder as config.json when the user is satsified with the results. The settings in ./config/[SPECIES_NAME]/config.json will be used by the makefile when creating the final cconfig.json that will be used to display the genome browser for the species in the Genome Portal. The script requires the pyyaml library, which can for instance be installed with pip.

- **generate_assembly_and_annotation_statistics.sh**

This script runs Quast and AGAT analyses to collect statistics from a genome assembly FASTA and an annotation GFF from a species, and extracts the relevant statistics that are needed for the tables in the species' Assembly tab in the Genome Portal. The script is intended to be run with assembly and annotation files from the same species, but this is up to the user to control as it is not explicitly enforced by the code itself.

- **get_aliases_from_ENA_fasta.py**

This script generates a refNameAlias file from genome assemblies downloaded from ENA. It can basically be seen as a soft-link that handles synonymous names for a given fasta header. This allows for higher flexibility for displaying versions of the data tracks that use a different formatting for how they call on the headers in the assembly fasta. For instance, correlation of GFFs to its assembly is made is made based on the element in the seqid column in the GFF. Using alias files avoids having to correctly rename potentially tens-of-thousands of lines in a data track file. As of now, the alias files are stored in the alias_file_temp_storage/ directory.

- **run_config_testbed_with_localhost_jbrowse_web.sh**

This script contains a workflow for testing datasets and config.yml files for a species before added to the genome portal. It runs the makefile to download and prepare the data and generate a JBrowse2 config file. These files are then copied to a temp folder where the JBrowse web interface is installed. As per reccomendations in the [JBrowse CLI documentation](https://jbrowse.org/jb2/docs/quickstart_web/), npx serve can then be used to initate a localhost instance of JBrowse2. Note that the Genome Portal uses Hugo server for serving the JBrowse2 instance as well as the related web pages, but here npx serve is for simplicity as it only serves the JBrowse2 instance.

NOTE! The workflow is intended for assisting in the data validation process, and not as an alternative to the rest of the code base in the repository. Once a species config.yml file has been validated and is scheduled for commiting to the repository, the full workflow 'make build install' and 'hugo serve'
needs to be run to ensure that the data is correctly integrated with the rest of the Genome Portal.