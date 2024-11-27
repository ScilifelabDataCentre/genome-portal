---
title: Supported data file formats
toc: true
---

## Supported data file formats

This page contains a description of some of the data file formats currently supported for display on the Swedish Reference Genome Portal. The text assumes some familiarity with biological terms, bioinformatics, and command line tools. Definitions of common terms used on this website can be found on the <a href="/glossary">Glossary</a> page. The Genome Portal staff is also available to discuss file format options and offer advice on file format conversion. Please email us at [dsn-eb@scilifelab.se](mailto:dsn-eb@scilifelab.se) or reach out through the <a href="/contact">Contact</a> page.

The Genome Portal uses the <a href="https://jbrowse.org/jb2/" target="_blank">JBrowse 2</a> genome browser to display genomic datasets. <a href="https://jbrowse.org/jb2/features/#supported-data-formats" target="_blank">JBrowse supports several formats</a> that are commonly used in genomics, which could therefore be displayed in the Genome Portal. However, at the moment, **we do not accept complete BAM files derived from shotgun sequencing** for display in the Genome Portal, as they can be quite large and may impact performance. Users can, however, add and visualise BAM files as local data tracks in the Genome Portal’s genome browser.

Readers who have reviewed the list of file formats supported by JBrowse may have noticed the mention of index files. File indexing is handled on the server side of the Genome Portal, so **index files do not need to be provided by users when submitting data to the Genome Portal**. For users familiarised with the command line, a description of how file indexing can be performed is available in the [Additional Resources](#additional-resources) section below.

The Genome Portal advocates for the FAIR principles for data sharing. Therefore, all datasets are required to be publicly available in repositories that provide persistent identifiers. We encourage researchers interested in contributing to the Genome Portal to read the <a href="/contribute/recommendations_for_making_data_public">recommendations for making data files publicly available</a>, when appropriate.

The data displayed in the genome browser can be divided into two categories: [genome assemblies](#genome-assemblies) and [data tracks (genome annotations)](#data-tracks). Below are specific recommendations to ensure that the data is compatible with JBrowse.

### Genome assemblies

The assemblies should contain a nucleotide sequence formatted in <a href="https://www.ncbi.nlm.nih.gov/genbank/fastaformat/" target="_blank">FASTA format</a>. The file should preferably be compressed using gzip since assembly files are often large.

#### Primary assemblies

Most scientific journals require open sharing of genome assembly data to accept scientific manuscripts for publication. This typically means that the assembly and annotation of protein-coding genes must be submitted to one of the international nucleotide databases, such as the <a href="https://www.ebi.ac.uk/ena/browser/home" target="_blank">European Nucleotide Archive (ENA)</a> or <a href="https://www.ncbi.nlm.nih.gov/genbank/" target="_blank">NCBI GenBank</a>. For assemblies available in these two discipline-specific repositories, providing the Accession Number to us will suffice.

- Example of a typical genome assembly file name: `GCA_900323705.1_C.harengus_genomic.fna.gz`

- Example of an ENA/NCBI accession number: `GCA_900323705`

As the Genome Portal is developed and maintained by a European institution, we use the ENA version of genome assemblies by default. Since ENA and NCBI mirror their data, an assembly downloaded from either of the two databases will contain the same nucleotide sequence. They will however differ in how the FASTA headers are formatted; this can create some incompatibilities with data tracks that assume a certain header format, but this is handled in the Genome Portal by using so-called <a href="https://jbrowse.org/jb2/docs/config_guides/assemblies/#configuring-reference-name-aliasing" target="_blank">refNameAlias</a> files. Alias files and the process of generating them are described in the [Additional Resources](#additional-resources) section below.

Sometimes, a researcher may prefer to use a version of a genome assembly in the Genome Portal other than the one available on ENA/NCBI. Such requests will be assessed on a case-by-case basis. We could accommodate this as long as the data is publicly available and has a persistent identifier. Currently, the Genome Portal allows to display one primary genome assembly version per species at a time. However, it is possible for a species to have more than one assembly version in the Genome Portal.

#### Organelle assemblies

It is also possible to display separate assemblies from organelles in the genome browser, such as mitochondria and chloroplasts. In order to display organelle assemblies, we require that they have a gene annotation. Please note that we do not display just organelles in the Genome Portal: there also has to be a primary genome assembly from the same species. The same file format recommendations as for primary genome assemblies apply: FASTA files that are preferably gzip-compressed.

### Data tracks

In the context of the genome browser we use (JBrowse 2), all compatible data that describe the assembly is referred to as data tracks. These include annotations of genomic features such as protein-coding genes, repeats, conservation scores, transcripts, CpG islands, genetic variants, genetic diversity, among others. Some data types are commonly available in specific formats (such as VCF for nucleotide variants), while others can be provided  in various formats. The Genome Portal requires file formats currently supported by JBrowse. Researchers can thus to a large extent follow their domain-specific conventions when choosing data formats.

As with genome assemblies, it is possible to include multiple versions of a data track in the Genome Portal if desired. For instance, a researcher might have a version of the protein-coding genes track that uses in-house annotations of the gene names differing from the naming format of the version available at ENA/NCBI. In such cases, we recommend including both tracks, as it enhances clarity and facilitates comparison between the track versions.

In the subsections below we list specific recommendations for some commonly used data track file formats.

#### GFF (and GTF)

One of the most common formats for storing annotations for genomic features is GFF (General Feature Format). NCBI for instance uses this for protein-coding genes. JBrowse 2 specifically supports the <a href="https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md" target="_blank">GFF3</a> version, and older GFF formats thus need to be converted to GFF3 as described below.

<a href="https://agat.readthedocs.io/en/latest/gxf.html" target="_blank">GTF</a> is another format for storing annotations that is very similar to GFF. Despite not being listed in the <a href="https://jbrowse.org/jb2/features/#supported-data-formats" target="_blank">table of supported formats</a>, JBrowse 2 can be configured to display GTF files. GTFs can thus be used in the Genome Portal, but loading times in the JBrowse window could be slightly longer for GTF compared to GFF files due to the current lack of support for indexed GTF files. Therefore, we recommend researchers to use GFF instead of GTF files, if possible.

There are several bioinformatics tools that can convert GTF and older GFF versions to GFF3. We recommend using <a href="https://agat.readthedocs.io" target="_blank">AGAT</a>. This is a command line toolkit designed by the National Bioinformatics Infrastructure Sweden (NBIS) at SciLifeLab. The AGAT script `agat_convert_sp_gxf2gxf.pl` is used to achieve conversions from GFF and GTF to GFF3.

```
# Usage example based on the AGAT documentation
# https://agat.readthedocs.io/en/latest/tools/agat_convert_sp_gxf2gxf.html

agat_convert_sp_gxf2gxf.pl -g annotation_file1.gtf --output annotation_file1.gff
```

#### BED

Another common format for describing genomic features is <a href="https://samtools.github.io/hts-specs/BEDv1.pdf" target="_blank">BED</a> (Browser Extensible Data). BED files have a less complicated version history than GFF/GTF, but there are variations of BED that use a different delimiter format. For compatibility with JBrowse 2, the BED files need to be tab-delimited, and not white-space delimited. If needed, a white-space delimited file can be converted to be tab-delimited using for instance:

```
awk '{$1=$1}1' OFS='\t' data.ws_delimited.bed > data.tab_delimited.bed
```

Note that BED documentation sometimes discusses BED followed with a number, such as BED3, BED6, BED12. The numbers indicate the number of the established BED columns that are included in that particular BED file. The first three columns are mandatory, meaning that BED3 is the minimal formatting for a BED file. JBrowse 2 supports BED versions with different number of columns as long as the number of columns are consistent across the rows within each BED file.

JBrowse 2 also supports the bigBED format, which is a binary, indexed format that is recommended for large BED-formatted datasets in order to improve performance. Please see the <a href="https://genome.ucsc.edu/goldenPath/help/bigBed.html" target="_blank">bigBED documentation</a> for how to convert BED to bigBED.

#### EMBL

JBrowse 2 does not support the European Molecular Biology Laboratory (EMBL) annotation format, but it can be converted to GFF with the AGAT toolkit that was discussed in the GFF/GTF section above. Note that a different AGAT script is needed for converting EMBL files: `agat_convert_sp_gxf2gxf.pl`.

```
# Usage example based on the AGAT documentation
# https://agat.readthedocs.io/en/latest/tools/agat_convert_embl2gff.html

agat_converter_embl2gff.pl --embl annotation_file2.embl --output annotation_file2.gff
```

#### RepeatMasker output format (.out files)

A common methodology to predict repeated sequences (“repeats”) in genome assemblies is to use the <a href="https://www.repeatmasker.org/" target="_blank">RepeatModeller and RepeatMasker software</a>. The default setting of the RepeatModeller/RepeatMasker pipeline is to output an annotation file in the proprietary format <a href="https://www.genome.iastate.edu/bioinfo/resources/manuals/RepeatMasker.html" target="_blank">OUT (.out)</a>, which is not supported by JBrowse 2. Thus, we recommend one of these two options: convert to BED or convert to GFF.

BED: A .out file is very similar to BED in its formatting and can easily be converted using established bioinformatics tools. Below is an example of how to use the `convert2bed` function of the  <a href="https://bedops.readthedocs.io/" target="_blank">BEDOPS toolkit</a> to perform the conversion.

```
# Usage example based on the BEDOPS documentation
# https://bedops.readthedocs.io/en/latest/content/reference/file-management/conversion/convert2bed.html

convert2bed --input=rmsk --output=bed < repeats.out > repeats.bed
```

GFF: The RepeatMasker GitHub contains a script found at `util/rmOutToGFF3.pl` for conversion of .out to GFF3. It is also possible to (re-)run RepeatMasker with the `--gff` flag to have the software produce both an .out and a .gff file. However, this output will be formatted according to GFF2, and thus need to be converted to GFF3 for compatibility with JBrowse 2 (e.g. with AGAT as described above).

#### BAM

<a href="https://samtools.github.io/hts-specs/SAMv1.pdf" target="_blank">BAM</a> (Binary Alignment Map) is the compressed binary format of <a href="https://samtools.github.io/hts-specs/SAMv1.pdf" target="_blank">SAM</a> (Sequence Alignment Map), a compact and indexable representation of nucleotide sequence alignments.

As mentioned before, **we do not display Binary Alignment Map (BAM) files** in the Genome Portal as they can be quite large and might affect performance. However, you can temporarily upload and visualise your own BAM files on the genome browser, provided the data shares the same genomic coordinates (i.e., it was mapped to the same species genome assembly). To do this, please follow the instructions on <a href="/faqs">how to add a data track to the genome browser</a>. Note that once the web browser is closed, the data is lost and must be re-uploaded.

#### VCF

<a href="https://samtools.github.io/hts-specs/VCFv4.5.pdf" target="_blank">VCF</a> (Variant Call Format) is a standardised text format used to represent various types of genetic variants, including Single Nucleotide Polymorphisms (SNPs), deletions, insertions, and structural variants.

{{< info_block >}}
We encourage you to review the <a href="https://github.com/samtools/hts-specs" target="_blank">samtools/hts-specs repository</a>, as it contains valuable information on various high-throughput sequencing file formats specifications not covered here.
{{< /info_block >}}

### Additional resources

#### Data file indexing

FASTA, GFF, BED, and VCF files need to be indexed in order to be displayed within the JBrowse genome browser. Index files enable that parts of a large file are rapidly accessed without having to sequentially browse the entire file, which is often time consuming. As mentioned above, **this is done on the server side** when a dataset is added to the Genome Portal. However, if a user wants to download the datasets and view them in the <a href="https://jbrowse.org/jb2/download/" target="_blank">JBrowse 2 Desktop client</a>, the index files need to be supplied by the user.

The bioinformatics toolkit <a href="https://www.htslib.org/" target="_blank">SAMtools</a> can be used to handle all the required indexing. It is a command line tool, and will thus require some knowledge on how to run and install this kind of software.

FASTA files can be indexed using the `samtools faidx` command.

```
# Example of standard fasta indexing with SAMtools:
# this command will index the file 'assembly.fasta' and create an
# index file named 'assembly.fasta.fai' in the same directory as the fasta

samtools faidx path/to/assembly.fasta
```

Furthermore, it is common to compress the FASTA file before indexing to save storage space. SAMtools comes with the bgzip compression tool, which compresses the file in a manner similar to gzip but with optimization suitable for genomics data. Note that JBrowse 2 only supports bgzipped files and not regular gzipped files. This means that fasta.gz files downloaded from ENA and NCBI might not be displayable without first unzipping them and re-compressing them with bgzip.

```
# Example of bgzipping and indexing of fasta files with SAMtools:
# faidx supports bgzipped files as input, so the code can be modified as:
# (the resulting file will be named assembly.fasta.bgz.fai)

bgzip < path/to/assembly.fasta > path/to/assembly.fasta.bgz
samtools faidx path/to/assembly.fasta.bgz
```

GFF files need to be indexed using tabix, which also is part of SAMtools. However, tabix requires that the GFF file has been sorted and bgzipped. This can be achieved using the `grep` and `sort` utilities that come packed with most UNIX-like systems:

```
# Example of GFF indexing with tabix:
# the | ("pipe") character sends the output of the previous command as
# input to the next command. The \ character is used for making long
# commands more readable by splitting them across multiple lines

(grep "^#" path/to/annotation.gff ; grep -v "^#" path/to/annotation.gff | \
sort -t"`printf '\t'`" -k1,1 -k4,4n) | \
bgzip >  path/to/annotation.sorted.gff.bgz
tabix -p gff path/to/annotation.sorted.gff.bgz
```

BED files also need to be indexed with tabix in a manner very similar to that of GFF files, but with a few differences. BED files do not have headers, and thus the `grep` step can be omitted. The sorting parameters are different as well, since the two formats store the scaffold and coordinate information in different column positions.

```
# Example of BED indexing with tabix:

sort -k1,1 -k2,2n annotation.bed | bgzip > annotation.sorted.bed.bgz
tabix -p bed annotation.sorted.bed.bgz
```

The above examples were adapted from the manual pages for <a href="http://www.htslib.org/doc/samtools-faidx.html" target="_blank">faidx</a>, <a href="https://www.htslib.org/doc/bgzip.html" target="_blank">bgzip</a>, and <a href="https://www.htslib.org/doc/tabix.html" target="_blank">tabix</a>.

#### refNameAlias - display data tracks on an assembly when the FASTA header formatting differs

When assemblies and genomic annotations are uploaded to ENA or NCBI, some repository-specific reformatting of FASTA headers may occur. The original header will be replaced by a new version that is based on the Accession Number that the upload is given once accepted in the ENA or NCBI databases. If a data track does not use the same FASTA header as the assembly, it cannot be displayed in JBrowse 2. However, not all data tracks are or even can be uploaded to ENA or NCBI, and there are therefore many use-cases where a data track might not follow the ENA or NCBI FASTA header formatting.

To be able to display data tracks that use a different version of the formatting, a refNameAlias (“alias”) file is needed. The alias file contains links between each FASTA header in the assembly and all their known synonymous names. It is a tab separated file where the first column contains the FASTA header from the version of the assembly that will be used in JBrowse 2, and each following column, the synonyms.

- Example from the Clouded Apollo refNameAlias file:

```
#ENA_formatted_header   #NCBI_formatted_header  #original_header
ENA|CAVLGL010000001|CAVLGL010000001.1   CAVLGL010000001.1   scaffold_1
ENA|CAVLGL010000002|CAVLGL010000002.1   CAVLGL010000002.1   scaffold_10
ENA|CAVLGL010000003|CAVLGL010000003.1   CAVLGL010000003.1   scaffold_100
ENA|CAVLGL010000004|CAVLGL010000004.1   CAVLGL010000004.1   scaffold_101
```

For genome assemblies that contain a low number of scaffolds (say, less than 10-20), this file can easily be generated by hand. But some scripting might be needed for cases that contain a higher number of scaffolds. During the process of adding a new dataset to the Genome Portal, the staff will generate the alias file. The file will then be publicly shared in the <a href="https://figshare.scilifelab.se/" target="_blank">SciLifeLab Data Repository</a>.
