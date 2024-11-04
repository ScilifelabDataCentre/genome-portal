---
title: About
---

## Overview

The Swedish Reference Genome Portal is a free service for aggregating, discovering, and visualising non-human eukaryotic genome assemblies and genome annotations (co-)produced by researchers with affiliation to a Swedish institution. This service is maintained by the Data Science Node in Evolution and Biodiversity (DSN-EB), which is composed of a dedicated team of data stewards, data engineers, system developers, and bioinformaticians from the [National Bioinformatics Infrastructure Sweden (NBIS)](https://nbis.se/) and [SciLifeLab Data Centre](https://www.scilifelab.se/data/).

This service is supported by [SciLifeLab](https://www.scilifelab.se/) and the [Knut and Alice Wallenberg Foundation](https://kaw.wallenberg.org/en) through the [Data-Driven Life Science (DDLS) program](https://www.scilifelab.se/data-driven/), and also by the [Swedish Foundation for Strategic Research (SSF)](https://strategiska.se/en/).

**The Swedish Reference Genome Portal aims to:**

- Highlight and showcase genome research performed in Sweden.

- Promote sharing of annotations of genomic features that rarely get published.

- Ensure all data shown on the Genome Portal is aligned with the [FAIR principles](https://www.go-fair.org/fair-principles/) and available in public repositories.

- Make it easier to access, visualise, and interpret genome data by lowering the barriers to entry.

### Usage

Everyone is welcome to use this website but in order to include a dataset into the Genome Portal there are a few requirements. You can read about the [requirements for adding a genome project here](/contribute).

### Implementation Details

The Swedish Reference Genome Portal website was built using the static website builder, [Hugo](https://gohugo.io/). The genome browser [JBrowse2](https://jbrowse.org/jb2/) is used to display the datasets and is embedded into the static website. All data shown on the Genome Portal is available in public repositories. We retrieve a copy of the data from the repositories for display on the genome browser.

The code for the Genome Portal is publicly available on [GitHub](https://github.com/ScilifelabDataCentre/genome-portal/) under an MIT (open source) license. The Genome Portal is deployed on a Kubernetes](<https://kubernetes.io/>) cluster located at the [KTH Royal Institute of Technology](https://www.kth.se/) in Stockholm.
