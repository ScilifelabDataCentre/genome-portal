---
title: About us
---

## Overview

The Swedish Reference Genome Portal is a service for aggregating, discovering, and visualising non-human genome assemblies and associated genomic data produced by researchers in Sweden. This service is maintained by the Data Science Node in Evolution and Biodiversity (DSN-EB), which is composed of a dedicated team of bioinformaticians, data stewards, data engineers, and system developers from the National Bioinformatics Infrastructure Sweden (NBIS) and SciLifeLab Data Centre.

This service is offered free of charge to individuals associated to Swedish researcher institutions. This service is supported by SciLifeLab and the Knut and Alice Wallenberg foundation through the Data-Driven Life Science (DDLS) program, and also by the Swedish Foundation for Strategic Research (SSF).

**The Swedish Reference Genome Portal aims to:**

- Highlight and showcase genomics research performed in Sweden.

- Make available data that would be otherwise not be published/provided. All data hosted on the Genome Portal is aligned with the [FAIR principles](https://www.go-fair.org/fair-principles/).

- Make it easier to access, visualise and interpret genomics research by lowering the barrier(s) to entry.

### Usage

Everyone is welcome to use the Portal but in order to host a genome project, there are several requirements, including that the research has been performed at least partially at a Swedish research institution. You can read more about the [requirements for adding a genome project here](/contribute)

### Implementation Details

The Swedish Reference Genome Portal website was built using the static website builder, [Hugo](https://gohugo.io/). The genome browser [JBrowse2](https://jbrowse.org/jb2/) is used to display the genomics datasets and is embedded into the static website. All genomic data shown on our Genome Portal is publicly available in scientific repositories such as the ENA, NCBI, SciLifeLab Figshare repository and Zenodo. We use a copy of these datasets (downloaded directly from the repository) in order to display on the browser.

The code for the Genome Portal is  publicly available on [GitHub](https://github.com/ScilifelabDataCentre/swedgene/) under an MIT (open source) license. The Genome Portal is deployed on a [Kubernetes](https://kubernetes.io/) cluster located at the [KTH Royal Institute of Technology](https://www.kth.se/) in Stockholm.
