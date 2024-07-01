# Data Stewardship scripts

This subdirectory stores scripts and workflows for the process of adding new datasets to the Genome Portal. The scripts are not intended for the deployment of the portal itself. Therefore, many of the scripts will rely heavily on external dependencies in the form of established bioinformatics tools.

Each script has its own documentation, and the easiest way to access that is to open the file in an editor. It contains a description of the purpose of the scrip, information on how to use it, and a list of the dependencies.

Some of the scripts will produce log files. These will be saved to the logs/ directory, unless otherwise specified in the code or command line call.

## List of scripts

- **compare_assembly_versions.sh**

This script performs pairwise comparison of two versions of the same genome assembly to identify if there are any differences between the nucleotide sequences (the fasta headers are not considered). This can for instance be used to spot if an alternative version of an assembly contains scaffolds not found in the version on ENA or NCBI (such as mitochondrial scaffolds). Use-case example: compare that ENA (CAVLGL01.fasta.gz) and NCBI (GCA_963668995.1_Parnassius_mnemosyne_n_2023_11_genomic.fna.gz) versions of the Clouded Apollo assembly and check if they are identical.

- **get_aliases_from_ENA_fasta.py**

This script generates a refNameAlias file from genome assemblies downloaded from ENA. It can basically be seen as a soft-link that handles synonymous names for a given fasta header. This allows for higher flexibility for displaying versions of the data tracks that use a different formatting for how they call on the headers in the assembly fasta. For instance, correlation of GFFs to its assembly is made is made based on the element in the seqid column in the GFF. Using alias files avoids having to correctly rename potentially tens-of-thousands of lines in a data track file. As of now, the alias files are stored in the alias_file_temp_storage/ directory.

- **run_config_testbed_with_localhost_jbrowse_web.sh**

This script contains a workflow for testing datasets and config.yml files for a species before added to the genome portal. It runs the makefile to download and prepare the data and generate a JBrowse2 config file. These files are then copied to a temp folder where the JBrowse web interface is installed. As per reccomendations in the [JBrowse CLI documentation](https://jbrowse.org/jb2/docs/quickstart_web/), npx serve can then be used to initate a localhost instance of JBrowse2. Note that the Genome Portal uses Hugo server for serving the JBrowse2 instance as well as the related web pages, but here npx serve is for simplicity as it only serves the JBrowse2 instance.

NOTE! The workflow is intended for assisting in the data validation process, and not as an alternative to the rest of the code base in the repository. Once a species config.yml file has been validated and is scheduled for commiting to the repository, the full workflow 'make build install' and 'hugo serve'
needs to be run to ensure that the data is correctly integrated with the rest of the Genome Portal.