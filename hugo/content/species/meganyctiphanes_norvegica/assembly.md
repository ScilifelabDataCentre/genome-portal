---
key_info:
  - "Assembly Name": "Mnor_HA_v2"
  - "Assembly Type": "Haploid"
  - "Assembly Level": "Scaffold"
  - "Genome Representation": "Full"
  - "Accession": "GCA_964058975.1"


# The params below were auto-generated, you should not need to edit them...
# unless you were warned by the add-new-species.py script.
title: "Genome assembly"
layout: "species_assembly"
url: "meganyctiphanes_norvegica/assembly"
weight: 2

stats_data_path: "meganyctiphanes_norvegica/species_stats"
lineage_data_path: "meganyctiphanes_norvegica/taxonomy"
---

|||||| Content divider - do not remove ||||||

Notes: Assembly statistics were calculated for the primary genome assembly GCA_964058975.1. Busco statistics were taken from Unneberg et al. (2024). Annotation statistics were calculated using [EDIT].

BUSCO notation: C: Complete; S: Single-copy; D: Duplicated; F: Fragmented; M: Missing; n: Total BUSCO genes included in the dataset (here: arthropoda_odb10). See also [the official BUSCO manual](https://busco.ezlab.org/busco_userguide.html#interpreting-the-results).

### Publication(s)

The *Meganyctiphanes norvegica* data displayed in the genome portal comes from:

- <p> Unneberg, P., Larsson, M., Olsson, A., Wallerman, O., Petri, A., Bunikis, I., Vinnere Pettersson, O., Papetti, C., Gislason, A., Glenner, H., Cartes, J. E., Blanco-Bercial, L., Eriksen, E., Meyer, B., & Wallberg, A. (2024). Ecological genomics in the Northern krill uncovers loci for local adaptation across ocean basins. Nature Communications, 15(1), 6297. <a href="https://doi.org/10.1038/s41467-024-50239-7"> https://doi.org/10.1038/s41467-024-50239-7</a></p>

### Methods

*Below is a brief summary of the methodology used to produce the genome data, based on Unneberg et al. (2024).*

#### Samples

Tail muscle tissue from a single female specimen (Sample "K20"; Gullmarsfjord, Sweden) was used for producing the main *de novo* genome assembly. DNA from K20 was used to generate long-read (Oxford Nanopore PromethION) and linked-read data (10x Genomics Chromium sequencing). RNA/cDNA short-read (Illumina NovaSeq 6000 SP) and long-read (Oxford Nanopore PromethION and MinION) data from K20 were used for scaffolding and annotation purposes. Short-read sequences from 74 additional specimens (36 males; 32 females; 7 undetermined) were collected from eight locations in the  North Atlantic Ocean and the Mediterranean Sea and used to create a popilation dataset for studying genetic varation.

#### Genome assembly

The *M. norvegica* genome was assembled using the long-read data. Long-read and linked-reads were used for polishing and scaffolding. A preliminary mitochondrial assembly generated from Oxford Nanopore MinION reads from another specimen (K4) was used to identify mitochondrial scaffolds in the assembly.

#### Genome annotation

Gene models were produced using Illumina RNA-seq data, Trinity assembled transcripts, and genomic data from other crustaceans. A non-redundant repeat library was generated with the identified simple, tandem and interspersed repeats and transposable elements.

### Funding

*The study in which the genome data was generated (Unneberg et al. 2024) was funded by:*

- Swedish Research Council Formas [2017-00413](https://www.vr.se/english/swecris.html#/project/2017-00413_Formas)

- U.S. National Science Foundation, Division Of Ocean Sciences (NSF OCE) grants [1316040](https://www.nsf.gov/awardsearch/showAward?AWD_ID=1316040) and [1948162](https://www.nsf.gov/awardsearch/showAward?AWD_ID=1948162)

- Knut and Alice Wallenberg Foundation as part of the National Bioinformatics Infrastructure Sweden at SciLifeLab, grant ID KAW 2017.0003.

### Acknowledgements

*The study in which the genome data was generated (Unneberg et al. 2024) acknolowledges the following support:*

- Computations were performed in project SNIC 2022/5-472 provided by the National Academic Infrastructure for Supercomputing in Sweden (NAISS) and the Swedish National Infrastructure for Computing (SNIC) at UPPMAX and the PDC Center for High Performance Computing partially funded by the Swedish Research Council through grant agreements no. 2022-06725 and no. 2018-05973.
