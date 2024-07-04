---
title: Recommendations for file formats
---

## Recommendations for file formats

This page contains recommendations for the file formats that can be used for displaying data on the Genome Portal and is intended as a support for researchers that want to add a new genome to the site. The text assumes some previous knowledge about bioinformatics file formats and familiarity with command line tools. The Genome Portal staff will also be happy to discuss choice of file formats and give advice on file format conversion. Please see the <a href="/contact">Contact page</a> for how to get in touch with us.

The Genome Portal uses JBrowse 2 to display the datasets. JBrowse 2 <a href="https://jbrowse.org/jb2/features/#supported-data-formats">supports several formats</a> that are commonly used in genomics and transcriptomics and these can thus technically be displayed in the genome portal. However, at the moment we do **NOT display BAM files** in the genome portal since they can be quite big and might affect performance.

- We still encourage research groups to make their BAM files publicly available, since that enables users to load the data as a local custom tracks in their JBrowse 2 instance.

Readers that have looked at the list of file formats supported by JBrowse might have noticed the mention of index files. Indexing of files is taken care of on the server side of the Genome Portal, and therefore index files do not need to be supplied in the process of adding a new species to the portal. For advanced users, a description of how indexing can be performed is available in the [Additional Resources](#additional-resources) section below.

The Genome Portal project advocates the FAIR principles for sharing of research data. As part of this work, all datasets are required to have been made publicly available in repositories that uses persistent identifiers. We therefore encourage researchers that are interested in adding a genome to the Genome Portal to first read this guide on file format recommendations and then read the <a href="/add_genome/recommendations_for_making_data_public">recommendations for how to make the data files publicly available</a>.

The data that is displayed in JBrowse 2 can be divided in two groups: [genome assemblies](#genome-assemblies) and [data tracks](#data-tracks). Below follows specific recommendations for making sure that the data is compatible with JBrowse.

### Genome assemblies

The assemblies should contain a nucleotide sequence formatted in multi-FASTA form. The file should preferably be compressed using gzip since assembly files can often have a large size.

#### Primary assemblies

Most scientific journals enforce open sharing of genome assembly data in order to accept scientific manuscripts for publication, which typically means that the assembly and annotation of protein coding genes will be submitted to one of the international nucleotide databases, such as the European Nucleotide Archive (ENA), and NCBI GenBank. For assemblies made available in these two databases, it is sufficient to give us the Accession Number.

- Example of a typical file name: `atlantic_herring_assembly.fa.gz`

- Example of an ENA/NCBI accession number: `GCA_900323705`

Since the Genome Portal is developed at SciLifeLab, which is situated in Europe, it has been decided that the Genome Portal will use the ENA version of all genome assemblies as a default. Since ENA and NCBI mirror their data, a assembly downloaded from either of the two databases will contain the same nucleotide sequence. They will however differ in how the FASTA headers are formatted; this can create some incompatibilities with data tracks that assume a certain header format, but this is handled in the Genome Portal by using so-called refNameAlias files. Alias files and the process of generating them are described in the [Additional Resources](#additional-resources) section below.

Sometimes a research group might have reasons to use a version of their genome assembly in the Genome Portal other than the versions available on ENA/NCBI. We will likely be able to accommodate that instead of the ENA version. The Genome Portal is only able to display one primary genome assembly version per species. We still strongly encourage that a version of the assembly is made publicly available through ENA or NCBI.

#### Organelle assemblies

It is also possible to display separate assemblies from organelles in the genome browser, such as mitochondria and chloroplasts. In order to display organelle assemblies, we require that they have a gene annotation. Please note that we do not display just organelles in Genome Portal: there also has to be a primary genome assembly from the same species. The same file format recommendations as for primary genome assemblies apply: FASTA files that are preferably gzip-compressed.

### Data tracks

In the context of the genome browser, all other compatible data that describe the assembly is referred to as data tracks. These include annotation of protein coding genes, repeats, tRNA, ncRNA, transcriptome assemblies, to name a few. Some data types tend to come in a specific format (such as VCF for nucleotide variants), whereas some data types can come in several different formats. The Genome Portal does not enforce the use over a certain format over another for the data tracks as long as the format is supported by JBrowse 2. Researchers can thus to a large extent use to use their domain-specific conventions when choosing data format.

Unlike genome assemblies, it is possible to include multiple versions of a data track in the Genome Portal if desired. For instance, a research group might have a version of the Protein Coding Genes track that uses in-house annotations of the gene names that differ from naming format of the version of the track available at NCBI. For cases such as these, we recommend that both tracks are included since this increases clarity and facilitates comparison between the track versions.

In the subsections below we have collected specific recommendations for some commonly used data track file formats.

#### GFF (and GTF)

One of the most common formats for storing annotations for genomic features is GFF (General Feature Format). NCBI for instance uses this for Protein Coding Genes. JBrowse 2 specifically supports the GFF3 version, and older GFF formats thus need to be converted to GFF3 as described below.

GTF is another format for storing annotations that is very similar format to GFF. However, JBrowse 2 does support GTF files and they therefore also need to be converted to GFF3.

There are several bioinformatics tools that can convert GTF and older GFF versions to GFF3. We recommend using <a href="https://agat.readthedocs.io">AGAT</a>. This is a command line toolkit designed by the NBIS bioinformatics platform at SciLifeLab. The AGAT script `agat_convert_sp_gxf2gxf.pl` is used to achieve conversions from GFF and GTF to GFF3.

```
# Usage example based on the AGAT documentation
# https://agat.readthedocs.io/en/latest/tools/agat_convert_sp_gxf2gxf.html

agat_convert_sp_gxf2gxf.pl -g annotation_file1.gtf --output annotation_file1.gff
```

#### BED

Another very common format for describing genomic features is BED (Browser Extensible Data). BED files have a less complicated version history than GFF/GTF and should, in general, be directly compatible with JBrowse 2. Note that BED documentation sometimes discusses BED followed with a number, such as BED3, BED6, BED12. The numbers indicate the number of the established BED columns that are included in that particular BED file. The first three columns are mandatory, meaning that BED3 is the minimal formatting for a BED file. To our knowledge, JBrowse 2 supports BED versions with different number of columns as long as the number of columns are consistent across the rows within each BED file.

JBrowse 2 also supports the bigBED format which is a binary, indexed format which is recommended for large BED-formatted datasets in order to improve performance. Please see the <a href="https://genome.ucsc.edu/goldenPath/help/bigBed.html">bigBED documentation</a> for how to convert BED to bigBED.

#### EMBL

JBrowse does not support the EMBL annotation format, but it can be converted to GFF with the AGAT toolkit which was also discussed in the GFF/GTF section above. Note that a different different AGAT script is needed for converting EMBL file: `agat_convert_sp_gxf2gxf.pl`.

```
# Usage example based on the AGAT documentation
# https://agat.readthedocs.io/en/latest/tools/agat_convert_embl2gff.html

agat_converter_embl2gff.pl --embl annotation_file2.embl --output annotation_file2.gff
```

#### RepeatMasker output format (.out)

A common methodology to predict repeated sequences (“repeats”) in genome assemblies is to use the <a href="https://www.repeatmasker.org/">RepeatModeller and RepeatMasker software</a>. The default setting of the RepeatModeller/RepeatMasker pipeline is to output an annotation file in the proprietary format .out, which is not supported by JBrowse. Thus, we recommend on of these two options: convert to BED or convert to GFF.

BED: The .out format is very similar in its formatting to .bed and can easily be converted using established bioinformatics tools. Below is an example of how to use the `convert2bed` function of the  <a href="https://bedops.readthedocs.io/">BEDOPS toolkit</a> to perform the conversion.

```
# Usage example based on the BEDOPS documentation
# https://bedops.readthedocs.io/en/latest/content/reference/file-management/conversion/convert2bed.html

convert2bed --input=rmsk --output=bed < repeats.out > repeats.bed
```

GFF: The RepeatMasker GitHub contains a script `util/rmOutToGFF3.pl` for conversion of .out to GFF3. It is also possible to (re-)run RepeatMasker with the `--gff` flag to have the software produce both an .out and a .gff file. However, this output will be formatted according to GFF2, and thus need to be converted to GFF3 for compatibility with JBrowse (e.g. with AGAT as described above).

#### BAM

To repeat the message from the top of the page: At the moment we **do NOT display BAM files** in the genome portal since they can be quite big and might affect performance.

We still encourage research groups to make their .bam files publicly available, since that enables users to load the data as a local custom tracks in their JBrowse 2 instance.

### Additional resources

#### Links to format documentation

- <a href="https://www.ncbi.nlm.nih.gov/genbank/fastaformat/">FASTA definition</a>

- <a href="https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md">GFF3 definition</a> and a comprehensive <a href="ttps://agat.readthedocs.io/en/latest/gxf.html"> overview of GTF and older GFF versions</a>

- <a href="https://samtools.github.io/hts-specs/BEDv1.pdf">BED definition</a>

- <a href="https://www.genome.iastate.edu/bioinfo/resources/manuals/RepeatMasker.html">RepeatMasker .out format</a> (see Section 3 in link)

#### Indexing of data files is required for certain file formats

Fasta, GFF, BED and VCF files need to be indexed in order to be displayed with JBrowse 2. In short, indexing enables large genomes to be browsable while minimizing the negative effect on performance. As mentioned above, this will be done on the server side when a new species is added to the Genome Portal. However, if a user wants to download the datasets and view them in e.g. the  <a href="https://jbrowse.org/jb2/download/">JBrowse Desktop client</a>, the index files need to be supplied by the user.

The seminal biinformatics toolkit SAMtools can be used to handle all the required indexing.  It is a command line tool, and will thus require some knowledge on how to run and install this kind of software.

FASTA files can be indexed using the `samtools faidx` command.

```
# Example of standard fasta indexing with SAMtools:
# this command will index the file 'assembly.fasta' and create an
# index file named 'assembly.fasta.fai' in the same directory as the fasta

samtools faidx path/to/assembly.fasta
```

Furthermore, it is common to compress the FASTA file before indexing to save storage space. SAMtools comes with the bgzip compression tool, which compresses the file in a manner similar to gzip but with optimization suitable for genomics and transcriptomics data. Note that JBrowse 2 only supports bgzipped files and not regular gzipped files. This means that fasta.gz files downloaded from ENA and NCBI might not be displayable without first unzipping them and re-compressing them with bgzip.

```
# Example of bgzipping and indexing of fasta files with SAMtools
# faidx supports bgzipped files as input, so the code can be modified as:
# (the resulting file will be named assembly.fasta.bgz.fai)

bgzip < path/to/assembly.fasta > path/to/assembly.fasta.bgz
samtools faidx path/to/assembly.fasta.bgz
```

The above examples were adapted from the manual pages for <a href="http://www.htslib.org/doc/samtools-faidx.html">faidx</a>, <a href="https://www.htslib.org/doc/bgzip.html">bgzip</a>, and <a href="https://www.htslib.org/doc/tabix.html">tabix</a>.

#### refNameAlias - displaying data tracks on an assembly version when the FASTA header formatting differs

When assemblies and annotations are uploaded to ENA or NCBI, some repository-specific reformatting of FASTA headers will occur. The original header will be replaced by new version that is based on the Accession Number that the upload will be given once accepted in the ENA or NCBI databases. If a data track does not use the same FASTA header as the assembly, it cannot be displayed in JBrowse 2. However, not all data tracks are or even can be uploaded to ENA or NCBI, and there are therefore many use-cases where a data track might not follow the ENA or NCBI FASTA header formatting.

To be able to display data tracks that use a different version of the formatting, a refNameAlias (“alias”) file is needed. The alias file contains links between each FASTA header in the assembly and all their known synonymous names. It is a tab separated file where the first column contains the FASTA header from the version of the assembly that will be used in JBrowse 2, and each following column the synonyms.

- Example from the Clouded Apollo refNameAlias file:

```
#ENA_formatted_header #NCBI_formatted_header #original_header
ENA|CAVLGL010000001|CAVLGL010000001.1 CAVLGL010000001.1 scaffold_1
ENA|CAVLGL010000002|CAVLGL010000002.1 CAVLGL010000002.1 scaffold_10
ENA|CAVLGL010000003|CAVLGL010000003.1 CAVLGL010000003.1 scaffold_100
ENA|CAVLGL010000004|CAVLGL010000004.1 CAVLGL010000004.1 scaffold_101
```

For genome assemblies that contain a low number of scaffolds (say, less than 10-20), this file can easily be generate by hand. But some scripting might be needed for cases that contains a higher number. During the process of adding a new species to the Genome Portal, the staff will generate the alias file. The file will then be publicly shared in the <a href="https://figshare.scilifelab.se/">SciLifeLab Data Repository</a>.
