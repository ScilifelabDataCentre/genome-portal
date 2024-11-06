---
title: Frequently Asked Questions
---

### FAQs

#### About the Genome Portal

{{< faq_block title="How does the Swedish Reference Genome Portal differ from other genome portal initiatives? (e.g., Ensembl, UCSC)" >}}
The Swedish Reference Genome Portal (SRGP) does not replace existing genome portal initiatives, as it has specific aims and scope:

The SRGP targets the Swedish research community and is restricted to non-human eukaryotic species. Therefore, the species displayed here are typically limited to those submitted by researchers affiliated with Swedish institutions. In contrast, global genome portals such as Ensembl and UCSC have much broader taxonomic scope, aiming to include species from around the world, including humans and prokaryotes.

- The SRGP's primary goal is to facilitate access, visualisation, and interpretation of genomic data, with a focus on offering a powerful genome browser. SRGP facilitates access and discovery by aggregating links to datasets associated with each genome assembly in a single page. Global genome portals like Ensembl and UCSC might, however, offer their own specific features besides their genome browser capabilities, such as support for comparative genomics analyses.

- The minimal requirement is that the species has a genome assembly in FASTA file format and an annotation of the protein-coding genes, preferably in GFF format. Other than that, the SRGP is unique in that it allows researchers to decide what, when, and how their genomic data is displayed on the Genome Portal. While global genome portals can also address researchers' inquiries, users can generally expect much shorter processing times with the SRGP, as it is maintained by a local team.

- The SRGP displays unique genomic annotations (annotation tracks) that are rarely published. Global genome portals often index and retrieve data from public genomic repositories such as NCBI or ENA, which means they may overlook the specific genomic annotations contributed by researchers in Sweden.
{{< /faq_block >}}

{{< faq_block title="What are the benefits of using the Swedish Reference Genome Portal?" >}}
By using the Genome Portal, a free national data service, you can benefit from:

- Increasing the visibility of your research, which could lead to more citations and collaborations.

- Making your genomic data visualisations accessible to everyone, whether they have skills in bioinformatics or not.

- Save yourself time by not having to install a genome browser or download large data files to your local computer.

- Having the flexibility to decide what, when, and how you want your genomic data be displayed on the Genome Portal.

- Having a weblink to your data displayed on the Genome Portal, which can be included in the Data Accessibility Statement of your scientific publication.

- Receiving assistance with sharing valuable genomic annotations in the SciLifeLab Data Repository that are rarely published.

- Enhancing your team work by being able to easily share links to genomic regions of interest with your colleagues.
{{< /faq_block >}}

{{< faq_block title="How can I get my data displayed on the Genome Portal?" >}}
Please begin by checking that your data meets the minimal requirements listed on the <a href="/contribute" target="_blank">Contribute</a> page.

If it does, feel free to reach out via email to <dsn-eb@scilifelab.se> or through the <a href="/contact" target="_blank">Contact</a> form. We would be happy to learn more about your genomic project, and will provide a brief form to collect additional details about your data.
{{< /faq_block >}}

{{< faq_block title="What data file formats are supported for display on the Genome Portal?" >}}
The Genome Portal uses the JBrowse 2 genome browser to display genomic datasets. <a href="https://jbrowse.org/jb2/features/#supported-data-formats" target="_blank">JBrowse supports several formats</a> that are commonly used in genomics (e.g., BED, VCF, FASTA, GFF, among others), which could therefore be displayed in the Genome Portal. However, at the moment, we do not accept complete BAM files derived from shotgun sequencing, as they can be quite large and may impact performance. Users can, however, add and visualise BAM files as local data tracks in the Genome Portal’s genome browser.
{{< /faq_block >}}

{{< faq_block title="How can I add a data track to the genome browser of an existing Species page?" >}}
To add a new track to the genome browser, you have two options:

1. Go to the menu bar (top-left corner) and open the form for adding a track by selecting `File > Open Track`.

2. Use the action button (circular `+`) inside the track selector (bottom-right corner) to access the `Add track` form, where you can provide a URL or select a local file to load. More details on <a href="https://jbrowse.org/jb2/docs/tutorials/config_gui/#adding-a-track" target="_blank">adding a data track</a> can be found in the JBrowse User Guide.

*Note that for either of these options to work, your data must have the same genomic coordinates as the genome assembly available on the Genome Portal.*
{{< /faq_block >}}

{{< faq_block title="Can unpublished data be displayed on the Genome Portal?" >}}
No, we require data be publicly available. However, we can begin adding data under embargo that will soon become available once the manuscript is accepted for publication. More details can be found in the next question.
{{< /faq_block >}}

{{< faq_block title="Is it possible to add my data to the Genome Portal while a manuscript is under review?" >}}
Yes, we accept data under embargo expected to become available after the manuscript under review is approved for publication. The data should be deposited in a public repository and have a reserved DOI and/or accession number. This allows you to indicate in the Data Availability Statement of your manuscript that your data can be visualised on the Genome Portal. Planning is key! Reach out to us via email <dsn-eb@scilifelab.se> or through the <a href="/contact" target="_blank">Contact</a> form as soon as you wish to start this process.
{{< /faq_block >}}

{{< faq_block title="How long does it take for my data to be displayed on the Genome Portal?" >}}
Once we have received the form listing the links and metadata associated with your genomic datasets, the webpage implementation process generally takes around one week. Please note that this may take a bit longer during public holidays and summer.
{{< /faq_block >}}

#### About the genome browser

{{< faq_block title="Why is JBrowse the genome browser used in the Genome Portal?" >}}
We chose JBrowse 2 for several reasons. It is a robust, open-source genome browser with powerful features for visualizing genomic data. It receives active maintenance and support from both system developers and the research community. Additionally, it is highly customizable and allows for the creation of new view types via a plugin system, making it more than a genome browser — it serves as a versatile platform for development.
{{< /faq_block >}}

{{< faq_block title="Is it possible to customise how data tracks are displayed on the genome browser?" >}}
Yes, it is to possible to modify attributes such as data track color or label. For this is necessary to change the settings of the JBrowse default session by editing the `config.json`. Please contact us by email to <dsn-eb@scilifelab.se> or through the <a href="/contact" target="_blank">Contact</a> form to help you with the customisation of your data tracks.
{{< /faq_block >}}

{{< faq_block title="What could be causing my data to display slowly?" >}}
The genome browser tracks may display slowly for various reasons, including having too many tracks open at once, viewing a large genomic window, a high number of custom tracks, numerous large data files, or a slow/unstable internet connection. If the problems persist, please do not hesitate to contact us at <dsn-eb@scilifelab.se> or through the <a href="/contact" target="_blank">Contact</a> form.
{{< /faq_block >}}

#### About citation guidelines

{{< faq_block title="How can I cite the Genome Portal content?" >}}
Depending on how you use the Genome Portal in your work (e.g., manuscript, presentation, etc.), there are various options for citing its content. For example, you can cite: the Genome Portal website, the website source code, the specific datasets from each species, or the JBrowse 2 genome browser. More details on citation guidelines can be found on the <a href="/citation" target="_blank">Cite us</a> page.
{{< /faq_block >}}
