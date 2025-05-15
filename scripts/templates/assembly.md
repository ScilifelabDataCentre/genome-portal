---
# The params below were auto-generated, you should not need to edit them...
# unless you were warned by the add_new_species.py script.
key_info:
  - "Assembly Name": ${assembly_name}
  - "Assembly Type": ${assembly_type}
  - "Assembly Level": ${assembly_level}
  - "Genome Representation": ${genome_representation}
  - "Accession": ${assembly_accession}

title: "Genome assembly"
layout: "species_assembly"
url: "${species_slug}/assembly"
weight: 2

stats_data_path: "${species_slug}/species_stats"
lineage_data_path: "${species_slug}/taxonomy"
---

Notes: Assembly statistics were calculated for the primary genome assembly ${assembly_accession}. ([EDIT:genome_assembly_filename]) using Quast (v5.2.0; Mikheenko et al. 2018). Busco statistics (Manni et al., 2021) were taken from [EDIT:publication_reference]. Annotation statistics were calculated for [EDIT:annotation_file_name] using AGAT (v1.4.1; Dainat, 2024).

BUSCO notation: C: Complete; S: Single-copy; D: Duplicated; F: Fragmented; M: Missing; n: Total BUSCO genes included in the dataset (here: [EDIT:ODB_database]). See also [the official BUSCO manual](https://busco.ezlab.org/busco_userguide.html#interpreting-the-results).

### Publication(s)

The data for *${species_name}* displayed in the genome portal comes from:

```{style=citation}
${publication}
```

The tools used by to calculate the statistics shown on top of this page are described in:

- Dainat J. (2024). AGAT: Another Gff Analysis Toolkit to handle annotations in any GTF/GFF format.
(Version v1.4.1). Zenodo. <https://www.doi.org/10.5281/zenodo.3552717>

- Manni, M., Berkeley, M. R., Seppey, M., Simão, F. A., & Zdobnov, E. M. (2021). BUSCO Update: Novel and Streamlined Workflows along with Broader and Deeper Phylogenetic Coverage for Scoring of Eukaryotic, Prokaryotic, and Viral Genomes. Molecular Biology and Evolution, 38(10), 4647–4654. <https://doi.org/10.1093/molbev/msab199>

- Mikheenko, A., Prjibelski, A., Saveliev, V., Antipov, D., & Gurevich, A. (2018). Versatile genome assembly evaluation with QUAST-LG. Bioinformatics, 34(13), i142–i150. <https://doi.org/10.1093/bioinformatics/bty266>

### Funding

*The study in which the genome data was generated ([EDIT:publication_reference]) acknowledge funding by:*

${funding}
