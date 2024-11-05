---
title: About
---

## Overview

The Swedish Reference Genome Portal is a free national data service for aggregating, discovering, and visualising non-human eukaryotic genome assemblies and genome annotations (co-)produced by researchers affiliated with a Swedish institution.

This service is developed and maintained by the Data Science Node in Evolution and Biodiversity (DSN-EB) team as part of the <a href="https://data.scilifelab.se" target="_blank">SciLifeLab Data Platform</a>, operated by the SciLifeLab Data Centre.

The DSN-EB team comprises system developers, data stewards, and bioinformaticians affiliated with <a href="https://www.scilifelab.se/data/" target="_blank">SciLifeLab Data Centre</a> and the <a href="https://nbis.se" target="_blank">National Bioinformatics Infrastructure Sweden (NBIS)</a>, based at Uppsala University and the Swedish Museum of Natural History.

The Swedish Reference Genome Portal aims to:

- Highlight and showcase genome research performed in Sweden.
- Make it easier to access, visualise, and interpret genome data by lowering the barriers to entry.
- Promote the sharing of genomic annotations that are rarely published.
- Ensure all data displayed on the Genome Portal aligns with the <a href="https://www.go-fair.org/fair-principles/" target="_blank">FAIR principles</a> and is available in public repositories.

### Technical implementation and source code

The Swedish Reference Genome Portal website was built using the static website builder <a href="https://gohugo.io/" target="_blank">Hugo</a>. The genome browser <a href="https://jbrowse.org/jb2/" target="_blank">JBrowse 2</a> is used to display genomic datasets and is embedded into the static website. All data shown on the Genome Portal is sourced from public repositories. We retrieve a copy of this data from the repositories to display on the genome browser.

The source code for the Genome Portal is publicly available on <a href="https://github.com/ScilifelabDataCentre/genome-portal" target="_blank">GitHub</a> under an MIT (open source) license. The Genome Portal is deployed on a Kubernetes cluster located at the <a href="https://www.kth.se/" target="_blank">KTH Royal Institute of Technology</a> in Stockholm.

### Citation guidelines

The recommended citations for the Genome Portal, source code, species pages, genome browser, and source data files can be found on the <a href="/citation" target="_blank">Cite us</a>.

### Terms of use

Information about what to expect from this service, as well as disclaimers and limitations of this website and its content, can be found on the <a href="/terms" target="_blank">Terms of use</a> page.

### Privacy policy

Information about what, how, and why personal and technical data is handled and protected when using this website can be found on the <a href="/privacy" target="_blank">Privacy policy</a> page.

### Funding

This service is supported by SciLifeLab and the Knut and Alice Wallenberg Foundation through the Data-Driven Life Science (DDLS) program, as well as by the Swedish Foundation for Strategic Research (SSF).

### Getting help

For questions, comments, or issues related to the Genome Portal, please contact us via email at [dsn-eb@scilifelab.se](mailto:dsn-eb@scilifelab.se), or use the <a href="/contact" target="_blank">Contact</a> form.
