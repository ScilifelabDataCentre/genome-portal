---
title: How to cite the Genome Portal and the data
---

In line with the principles of _FAIR_ and _Open Science_, we encourage the reuse and recognition of material made available on the Swedish Reference Genome Portal.
On this page, you will find information about how to cite the portal when reusing and referencing the content. Please note that the information on the portal is
updated continuously, therefore it is important to refer to specific versions (or to provide access dates) within citations.

Below are instructions for how to cite different aspects of the Genome Portal. These include:

- Citing the the Swedish Reference Genome Portal website

- Citing a specific species entry in the Genome Portal

- Citing the data in the Genome Portal

- Citing the underlying code of the Genome Portal, including its dependency on JBrowse 2

### 1. Citing the Swedish Reference Genome Portal website

The Resource Identification Portal was created in support of the <a target="_blank" href="https://www.rrids.org/">Resource Identification Initiative</a>.
It aims to promote the identification, discovery, and reuse of research resources. Research Resource Identifiers (**RRIDs**) are persistent and unique identifiers for
referencing a research resource. For official guidance see the [SciCrunch page on RRID citations](https://scicrunch.org/resources/about/guidelines).

The RRID for the Swedish Reference Genome Portal is [**XXXXXXXX**](https://XXXXXXXXXX).

By citing the portal using the RRID, you will facilitate further reuse of the portal, enable us to track that activity, and allow others to easily find the _Summary Report_
for usage of the Swedish Reference Genome Portal.

**In-text citation (APA format)**:\
Swedish Reference Genome Portal (SciLifeLab Data Centre; _version number_; RRID: XXXXXXXXX).

**Reference list (APA format)**:\
Swedish Reference Genome Portal (_access date_), SciLifeLab Data Centre. Version (version number). <https://genomes.scilifelab.se>, RRID:XXXXXXXX. [Species DOI].

You will find the version number of the portal at XXXXXthe bottom of the footer on any pageXXXXXX, or on our
<a target="_blank" href="https://github.com/ScilifelabDataCentre/genome-portal/">genome-portal repository</a> under 'releases'.

### 2. Citing a specific species entry

If you would like to refer to a specific species entry from the Genome Portal, you can do so by taking the Genome Portal citation (Section 1) and adding the species name and the
DOI pointing to its associated metadata in SciLifeLab Data Repository:

**In-text citation (APA format)**:\
The [_Species name_] entry in the Swedish Reference Genome Portal (SciLifeLab Data Centre; _version number_; RRID: XXXXXXXXX; [Species DOI]).

**Reference list (APA format)**:\
Swedish Reference Genome Portal, [_Species name_] entry (_access date_). SciLifeLab Data Centre. Version (version number). <https://genomes.scilifelab.se/[species_name>], RRID:XXXXXXXX. [DOI].

where `[species_name]` should be replaced with the binomal name of your species in lower case letters and an underscore, and `[DOI]` with the DOI of the associated metadata in SciLifeLab Data Repository.

#### Data availability statement for submitting researchers

Researchers who have submitted their data to the Genome Portal may want to include the following text for the Data Availability statement in their research manuscript.

"Visualisations of the genome assemby and annotation tracks from this publication can be found in the Swedish Reference Genome Portal at <https://genomes.scilifelab.se/[species_name>].
The accompanying metadata for this entry in the portal can be found at [DOI]."

where `[species_name]` and `[DOI]` should be replaced as described above.

The Genome Portal staff can help you reserve an entry on the portal and a DOI for the metadata already during the manuscript submission stage. When the manuscript is accepted for publication and the data has been
made public, we will activate the entry on the Swedish Reference Genome Portal. If you have any questions about this, please contact us through the <a href="/contact">Contact page</a>.

### 3. Citing the data in the portal

Giving proper credit to the authors of the data is central to the principles of _FAIR_ and _Open Science_. Therefore, if you have used any data displayed on the Genome Portal
(genome assemblies and annotaiton tracks) for your own work, we kindly ask you to cite the data in addition to citing the Swedish Reference Genome Portal (Section 1-2).

All datasets included in the Genome Portal are public, but the means as to how to cite them can vary from dataset to dataset. Instructions for how to cite each data is found on
the _Description_ page of each species. In general, many datasets in the Swedish Reference Genome Portal have been published as part of a research article and for those cases,
we reccomend that you cite the original publication. For datasets that do not have an associated publication, please go to the _Download_ page for the species, click the *Show reduced table view*
button and see if there is an accession number or a DOI that can be used to refer to the dataset.

### 4. Citing the underlying code

#### Citing the Genome Portal code

The Genome Portal is operated by the <a target="_blank" href="https://scilifelab.se/data">SciLifeLab Data Centre</a> and partners. All of the source code used on the website is available on GitHub.
The code used to produce the website is available in our <a target="_blank" href="https://github.com/ScilifelabDataCentre/genome-portal/">genome-portal repository</a>.
All of the code that we have produced is available for reuse under an MIT licence. If you have reused the code or otherwise want to cite the code, please use the following:

**APA format:**\
SciLifeLab Data Centre (year) genome-portal. version: [version number](Software). Zenodo. XXXXXXX<XXXXXXX>.

#### Citing the JBrowse 2 genome browser

The Swedish Reference Genome Portal uses the JBrowse 2 genome browser for interactive visualization of genome assemblies and their associated annotation tracks.
The latest citation instructions can be found at [https://jbrowse.org/](https://jbrowse.org/). At the time of writing, the JBrowse developers ask users to cite the following publication:

**APA format:**\
Diesh, C., Stevens, G. J., Xie, P., De Jesus Martinez, T., Hershberg, E. A., Leung, A., Guo, E., Dider, S., Zhang, J., Bridge, C., Hogue, G., Duncan, A., Morgan, M., Flores, T., Bimber, B. N., Haw, R., Cain, S., Buels, R. M., Stein, L. D., & Holmes, I. H. (2023). JBrowse 2: A modular genome browser with views of synteny and structural variation. Genome Biology, 24(1), 74. [https://doi.org/10.1186/s13059-023-02914-z](https://doi.org/10.1186/s13059-023-02914-z)
