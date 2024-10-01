---
key_info:
  - "Assembly Name": "Parnassius_mnemosyne_n_2023_11"
  - "Assembly Type": "Haploid"
  - "Assembly Level": "Scaffold"
  - "Genome Representation": "Full"
  - "Accession": "GCA_963668995.1"


# The params below were auto-generated, you should not need to edit them...
# unless you were warned by the add-new-species.py script.
title: "Genome assembly"
layout: "species_assembly"
url: "parnassius_mnemosyne/assembly"
weight: 2

stats_data_path: "parnassius_mnemosyne/species_stats"
lineage_data_path: "parnassius_mnemosyne/taxonomy"
---

|||||| Content divider - do not remove ||||||

Notes: Assembly statistics and BUSCO percentages were calculated for the primary genome assembly GCA_963668995.1, which does not include the mitochondrial assembly (OZ075093.1). Annotation statistics were calculated using pmne_functional_edit1.gff.gz, which is the orignal version of the protein-coding genes annotation and was the version that was used for the submission to ENA.

BUSCO notation: C: Complete; S: Single-copy; D: Duplicated; F: Fragmented; M: Missing; n: Total BUSCO genes included in the dataset (here: lepidoptera_odb10). See also [the official BUSCO manual](https://busco.ezlab.org/busco_userguide.html#interpreting-the-results).

### Publication(s)

The data for *Parnassius mnemosyne* displayed in the genome portal comes from:

- <p> Höglund, J., Dias, G., Olsen, R. A., Soares, A., Bunikis, I., Talla, V., & Backström, N. (2024). A Chromosome-Level Genome Assembly and Annotation for the Clouded Apollo Butterfly (<i>Parnassius mnemosyne</i>): A Species of Global Conservation Concern. Genome Biology and Evolution, 16(2), evae031. <a href="https://doi.org/10.1093/gbe/evae031">https://doi.org/10.1093/gbe/evae031</a></p>

### Methods

*Below is a brief summary of the methodology used to produce the genome data, based on Höglund et al. (2024) and communication with bioinformatics staff who worked on the project. For more details, please refer to the original publication.*

#### Samples

Thorax muscle tissue from two female Clouded Apollo individuals (PM1 and PM2) from a captive population was used for the sequencing experiments. DNA was extracted from PM1 and PM2 and used for PacBio HiFi, and Illumina Hi-C sequencing, respectively. RNA was extracted from PM2 and used for Illumina short-read and PacBio Iso-seq sequencing.

#### Genome assembly

The *P. mnemosyne* genome was assembled using the PacBio HiFi and Illumina Hi-C data. After manual curation of selected regions, the mitochondrial genome was identified, and the assembly was split into a primary genome assembly (GCA_963668995.1) and a mitochondrial genome assembly (OZ075093.1).

#### Genome annotation

Gene prediction was performed using the Illumina RNAseq data, a database of Arthropod proteins, and the PacBio Iso-seq data. The final gene model was functionally annotated by the NBIS nextflow pipeline, resulting in the pmne_functional_edit1.gff.gz file, which is used as the default track for the protein-coding genes here in the Genome Portal. The Illumina RNAseq reads were aligned to the genome assembly and was then used to produce a transcript assembly containing the detected isoforms. Separate predictions of tRNA genes and putative pseudogenes, and non-coding RNA genes were also produced. The mitochondrial genome assembly was annotated seperatelly using specific tools for mitochondrial sequences.

### Funding

*The study in which the genome data was generated (Höglund et al. 2024) was funded by:*

- Swedish Research Council (Grant number [2019-04791](https://www.vr.se/english/swecris.html#/project/2019-04791_VR))
- NBIS/SciLifeLab long-term bioinformatics support
- Swedish Rescue Program for *P. mnemosyne* through the local administrative board (Länsstyrelsen) of Blekinge

### Acknowledgements

*The study in which the genome data was generated (Höglund et al. 2024) acknolowledges the following support:*

- Science for Life Laboratory (SciLifeLab)
- National Genomics Infrastructure (NGI)
- Uppsala Multidisciplinary Center for Advanced Computational Science (UPPMAX)
- Swedish National Infrastructure for Computing (SNIC).
- The ERGA hubs at the University of Antwerp and University of Florence
