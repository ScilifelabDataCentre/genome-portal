---
title: How to cite the Genome Portal and the data
toc: true
---

In line with the principles of _FAIR_ and _Open Science_, we encourage the reuse and recognition of material made available on the Swedish Reference Genome Portal.

On this page, you will find information about how to cite the Genome Portal website ([Section 1](#1-citing-the-website)), the website source code ([Section 2](#2-citing-the-source-code-of-the-website)), the specific datasets from each species ([Section 3](#3-citing-the-data-in-the-genome-portal)), and the JBrowse 2 genome browser ([Section 4](#4-citing-the-jbrowse-2-genome-browser)).

### 1. Citing the website

#### 1.1. Citing the Genome Portal

To cite the Swedish Reference Genome Portal, please use the following:

**APA format**:\
{{< citation_block >}}
Swedish Reference Genome Portal (DATE_ACCESSED), SciLifeLab Data Centre, version VERSION_NUMBER from <https://genomes.scilifelab.se>, [RRID:SCR_026008](https://rrid.site/data/record/nlx_144509-1/SCR_026008/resolver?q=rrid:scr_026008).
{{< /citation_block >}}

Since the information on the portal is updated continuously, we ask you to specify the version number of the Genome Portal and the date you accessed the Portal in the citation. The citation block above has the date accessed set to today's date and the version number to the current version of the website you are viewing. You can also find the version number of the portal at the bottom of the footer on any page, as well as a <a target="_blank" href="https://github.com/ScilifelabDataCentre/genome-portal/releases">list of all of our previous versions in our GitHub repository</a>.

#### 1.2. Citing a species page in the Genome Portal

You can also cite a specific species page from the Genome Portal. The easiest way to find the citation information for a species page is to go to its _Description_ tab and copy the citation text. If you have used the data from a species page in your own work, please also consider citing the authors of the data ([Section 3](#3-citing-the-data-in-the-genome-portal)).

The general pattern for citing a species page can also be filled out using the following template:

**In-text citation (APA format)**:\
{{< citation_block >}}
The <span class="highlight">[_Species name_]</span> page in the Swedish Reference Genome Portal (DATE_ACCESSED).
{{< /citation_block >}}

where [_Species name_] is a placeholder that should be replaced with the binomial name of the species in italics, and Swedish Reference Genome Portal with the access date provided is the APA formatted in-text pointer to the reference stated above in [Section 1.1](#11-citing-the-genome-portal).

#### 1.3. In-text citation in the Data Availability Statement of a manuscript

Researchers who have submitted their data to the Genome Portal may want to include the following text in the Data Availability statement in their research manuscript(s).

{{< citation_block >}}
"Visualisations of the genome assembly and annotation tracks from this publication can be found in the Swedish Reference Genome Portal (DATE_ACCESSED) at <https://genomes.scilifelab.se/[species_name]>."
{{< /citation_block >}}

where [species_name] should be replaced with the binomial name of the species in lower case letters and an underscore, and Swedish Reference Genome Portal with the access date provided is the APA formatted in-text pointer to the reference stated above in [Section 1.1](#11-citing-the-genome-portal).

### 2. Citing the source code of the website

The Genome Portal is operated by the <a target="_blank" href="https://scilifelab.se/data">SciLifeLab Data Centre</a> and partners. All of the source code used to generate the website is available on [GitHub](https://github.com/ScilifelabDataCentre/genome-portal/). The code is published under an MIT license. If you have reused the code or otherwise want to cite the code, please use the following:

**APA format:**\
{{< citation_block >}}
SciLifeLab Data Centre (YEAR). genome-portal. Version: VERSION_NUMBER [Software]. Zenodo. <https://doi.org/10.5281/zenodo.14049736>.
{{< /citation_block >}}

using the year and version number of the code release you want to cite. The current year and version of the software is included in the citation block. Older versions of the software can be found in our <a target="_blank" href="https://github.com/ScilifelabDataCentre/genome-portal/releases">GitHub repository</a> or our <a target="_blank" href="https://doi.org/10.5281/zenodo.14049736">Zenodo record</a>.

### 3. Citing the data in the Genome Portal

Giving proper credit to the authors of the data is central to the principles of _FAIR_ and _Open Science_. Therefore, if you have used any data displayed on the Genome Portal (genome assemblies and annotation tracks) in your own work, we kindly ask you to cite the data.

All datasets included in the Genome Portal are public, but the means as to how to cite them can vary from dataset to dataset. Instructions for how to cite each dataset is found on the _Description_ tab of each species. In general, many datasets in the Swedish Reference Genome Portal have been published as part of a research article and for those cases, we recommend that you cite the original publication. For datasets that do not have an associated publication, please go to the _Download_ page for the species, click the _Show reduced table view_ button and use the accession number(s) or DOI(s) to refer to the data.

### 4. Citing the JBrowse 2 genome browser

You might also want to consider citing the JBrowse 2 genome browser, especially if you have used the genome browser to work with the data. The developers provide their own citation information on the [JBrowse website](https://jbrowse.org/). At the time of writing, the JBrowse developers ask users to cite the following publication:

**APA format:**\
{{< citation_block >}}
Diesh, C., Stevens, G. J., Xie, P., De Jesus Martinez, T., Hershberg, E. A., Leung, A., Guo, E., Dider, S., Zhang, J., Bridge, C., Hogue, G., Duncan, A., Morgan, M., Flores, T., Bimber, B. N., Haw, R., Cain, S., Buels, R. M., Stein, L. D., & Holmes, I. H. (2023). JBrowse 2: A modular genome browser with views of synteny and structural variation. Genome Biology, 24(1), 74. [https://doi.org/10.1186/s13059-023-02914-z](https://doi.org/10.1186/s13059-023-02914-z)
{{< /citation_block >}}
