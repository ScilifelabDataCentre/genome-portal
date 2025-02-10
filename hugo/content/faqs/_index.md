---
title: Frequently Asked Questions
---

### FAQ

#### About the Genome Portal

<div class="accordion mb-4" id="accordion-1">

{{< faq_block accordionID="accordion-1" title="How does the Swedish Reference Genome Portal differ from other genome portal initiatives? (e.g., Ensembl, UCSC)" >}}
The Swedish Reference Genome Portal (SRGP) does not replace existing genome portal initiatives, as it has specific aims and scope:

- The SRGP targets the Swedish research community and is restricted to non-human eukaryotic species. Therefore, the species displayed here are typically limited to those submitted by researchers affiliated with Swedish institutions. In contrast, global genome portals such as Ensembl and UCSC have much broader taxonomic scope, aiming to include species from around the world, including humans and prokaryotes.

- The SRGP's primary goal is to facilitate access, visualisation, and interpretation of genomic data, with a focus on offering a powerful genome browser. SRGP facilitates access and discovery by aggregating links to datasets associated with each genome assembly in a single page. Global genome portals like Ensembl and UCSC might, however, offer their own specific features besides their genome browser capabilities, such as support for comparative genomics analyses.

- The minimal requirement is that the species has a genome assembly in FASTA file format and an annotation of the protein-coding genes, preferably in GFF format. Other than that, the SRGP is unique in that it allows researchers to decide what, when, and how their genomic data is displayed on the Genome Portal. While global genome portals can also address researchers' inquiries, users can generally expect much shorter processing times with the SRGP, as it is maintained by a local team.

- The SRGP displays unique genomic annotations (annotation tracks) that are rarely published. Global genome portals often index and retrieve data from public genomic repositories such as NCBI or ENA, which means they may overlook the specific genomic annotations contributed by researchers in Sweden.
{{< /faq_block >}}

{{< faq_block accordionID="accordion-1" title="What are the benefits of using the Swedish Reference Genome Portal?" >}}
By using the Genome Portal, a free national data service, you can benefit from:

- Increasing the visibility of your research, which could lead to more citations and collaborations.

- Making your genomic data visualisations accessible to everyone, whether they have skills in bioinformatics or not.

- Save yourself time by not having to install a genome browser or download large data files to your local computer.

- Having the flexibility to decide what, when, and how you want your genomic data be displayed on the Genome Portal.

- Having a weblink to your data displayed on the Genome Portal, which can be included in the Data Accessibility Statement of your scientific publication.

- Receiving assistance with sharing valuable genomic annotations in the SciLifeLab Data Repository that are rarely published.

- Enhancing your team work by being able to easily share links to genomic regions of interest with your colleagues.
{{< /faq_block >}}

{{< faq_block accordionID="accordion-1" title="How can I get my data displayed on the Genome Portal?" >}}
Please begin by checking that your data meets the minimal requirements listed on the <a href="/contribute">Contribute</a> page.

If it does, feel free to reach out via email to <dsn-eb@scilifelab.se> or through the <a href="/contact">Contact</a> form. We would be happy to learn more about your genomic project, and will provide a brief form to collect additional details about your data.
{{< /faq_block >}}

{{< faq_block accordionID="accordion-1" title="What data file formats are supported for display on the Genome Portal?" >}}
The Genome Portal uses the JBrowse 2 genome browser to display genomic datasets. <a href="https://jbrowse.org/jb2/features/#supported-data-formats">JBrowse 2 supports several formats</a> that are commonly used in genomics (e.g., BED, VCF, FASTA, GFF, among others), which could therefore be displayed in the Genome Portal. However, at the moment, we do not accept complete BAM files derived from shotgun sequencing, as they can be quite large and may impact performance. Users can, however, add and visualise BAM files as local data tracks in the Genome Portal’s genome browser.
{{< /faq_block >}}

{{< faq_block accordionID="accordion-1" title="Can unpublished data be displayed on the Genome Portal?" >}}
No, we require data be publicly available. However, we can begin adding data under embargo that will soon become available once the manuscript is accepted for publication. More details can be found in the next question.
{{< /faq_block >}}

{{< faq_block accordionID="accordion-1" title="Is it possible to add my data to the Genome Portal while a manuscript is under review?" >}}
Yes, we accept data under embargo expected to become available after the manuscript under review is approved for publication. The data should be deposited in a public repository and have a reserved DOI and/or accession number. This allows you to indicate in the Data Availability Statement of your manuscript that your data can be visualised on the Genome Portal. Planning is key! Reach out to us via email <dsn-eb@scilifelab.se> or through the <a href="/contact">Contact</a> form as soon as you wish to start this process.
{{< /faq_block >}}

{{< faq_block accordionID="accordion-1" title="How long does it take for my data to be displayed on the Genome Portal?" >}}
Once we have received the form listing the links and metadata associated with your genomic datasets, the webpage implementation process generally takes around one week. Please note that this may take a bit longer during public holidays and summer.
{{< /faq_block >}}

</div>

#### About the genome browser

<div class="accordion mb-4" id="accordion-2">

{{< faq_block accordionID="accordion-2" title="What is a genome browser, and what is it used for?" >}}
A genome browser provides a graphical representation of diverse genomic and genetic data mapped to a common reference genome assembly of a species. This ensures that various datasets are accurately positioned on the same axis, as they share identical genomic coordinates. Each dataset appears on a separate data track. In a typical linear genome view, a genome browser displays multiple data tracks stacked horizontally in alignment with the genome assembly sequence. Among the data types that are often visualised in a genome browser are: genetic variation, transcription, various regulatory factors like methylation and transcription factor binding, contact maps, among others.

Genome browsers are essential tools for interpreting data, developing hypotheses, and communicating discoveries about relationships between various data types. By allowing different types of data to be viewed in relation to each another, genome browsers can provide valuable insights into potential correlations. For example, they can be used to infer phenotype-genotype associations when comparing genomic data from normal individuals versus diseased individuals.
{{< /faq_block >}}

{{< faq_block accordionID="accordion-2" title="Why is JBrowse 2 the genome browser used in the Genome Portal?" >}}
We chose JBrowse 2 for several reasons. It is a robust, open-source genome browser with powerful features for visualising genomic data. It receives active maintenance and support from both system developers and the research community. Additionally, it is highly customisable and allows for the creation of new view types via a plugin system, making it more than a genome browser — it serves as a versatile platform for development.
{{< /faq_block >}}

{{< faq_block accordionID="accordion-2" title="Is it possible to customise how data tracks are displayed on the genome browser?" >}}
Yes, it is possible to modify several of the data track attributes, such as colors, labels, descriptions, groups, and more. To do this, it is necessary to change the settings of the JBrowse 2 default session by editing the `config.json` file associated with the species. Please contact us by email to <dsn-eb@scilifelab.se> or through the <a href="/contact">Contact</a> form to help you with the customisation of your data tracks.
{{< /faq_block >}}

{{< faq_block accordionID="accordion-2" title="How can I open a data track within the genome browser of a species in the Genome Portal?" >}}
To open a new data track within the genome browser for a species in the Genome Portal:

1. Access the 'Add a track' form by clicking on the **File** menu, then **Open track**, or by clicking the **circular plus (+) icon** in the bottom right corner of the 'Available tracks widget' (right-side panel).
2. In the 'Add a track' form, provide a URL to a file to load, or open a file stored in your local machine.

Remember that your data should have the same genomic coordinates as the genome assembly available in the Genome Portal.

In some cases, you need to provide an index file for your data (e.g., a tabix files is required for VCF/GFF/BED files). Guidance on generating index files can be found in the <a href="/contribute/supported_file_formats/#data-file-indexing">data file indexing section of the Supported data file formats</a> page.
{{< /faq_block >}}

{{< faq_block accordionID="accordion-2" title="How can I share a genome browser session?" >}}
To share a session with others:

1. Click the **Share** link at the top center of the window.
2. A window will appear displaying a URL for your session. To copy the URL, click on the **Copy to clipboard** button.

Only the URL generated here should be shared with others. Sharing your browser's URL won't work.
{{< /faq_block >}}

{{< faq_block accordionID="accordion-2" title="How can I create and share bookmarks for genomic regions of interest?" >}}
The **Bookmark regions widget** allows you to save a list of specific regions you want to revisit later.

To create a bookmark, click and drag on the top of the linear genome view, and select **Bookmark region**. The new bookmark will be displayed on the **Bookmark regions widget** (right-side panel).

To customise a specific bookmark, make sure it is selected with a check box, then click the row corresponding to the **Label** column and type labels/notes/annotations/comments, or click the row of the **Highlight** column to change the highlight color.

To export bookmarks as a BED or TSV file, click the **Bookmark regions widget** menu on the top-left corner (seen as three gray horizontal lines), select the preferred format, and click **Download**. The file will be saved in the Downloads folder on your local computer.

To import bookmarks from a BED or TSV file, click **Bookmark regions widget** menu, select **Import** and **Import from file**.

To share bookmarks via a URL link, click the **Bookmark regions widget** menu, select **Share** and **Copy share link**.

To import bookmarks from a shared URL link, click the **Bookmark regions widget** menu, select **Import** and **Import from share link**.

To delete bookmarks from your computer, select the desired bookmarks using the left checkboxes, the **Bookmark regions widget** menu, and select **Delete**.

As the bookmarks rely on the reference genome of a given species, it is recommended that you first share your session (the species genome browser), and then the bookmarks that apply to that session (species).
{{< /faq_block >}}

{{< faq_block accordionID="accordion-2" title="How can I export genomic visualisation as an SVG file?" >}}
To export genome browser visualisations as publication-quality images in SVG (Scalable Vector Graphics) format:

1. Click the **View** menu at the top-left corner of the window (seen as three horizontal lines on the purple banner)
2. Click **Export SVG**. Choose a filename, a 'Track level' positioning and a 'Theme', and press **Submit**.

The SVG file will be saved to the Downloads folder on your machine.

The advantage of using vector files is that, unlike pixel-based raster files such as JPG or PNG, vector files store images using mathematical formulas based on points and lines on a grid. This allows SVG images to be scaled and modified without any loss of quality. SVG files can be easily edited using a variety of graphic software, such as Inkscape or Illustrator.
{{< /faq_block >}}

{{< faq_block accordionID="accordion-2" title="How can I obtain the full sequence or the coding sequence of a gene?" >}}
To view details or annotations for a specific genomic feature:

1. Click on the genomic feature of interest (e.g., a protein-coding gene). A **Feature details** widget will appear on the right, in the Widget side panel area.
2. Scroll down to browse the feature details. To obtain the full gene sequence, click the **Show feature sequence** button of the top panel, which corresponds to the gene. To obtain the coding sequence (CDS), go down to the **Subfeatures** section, and click on the correspondent **Show feature sequence** button.
{{< /faq_block >}}

{{< faq_block accordionID="accordion-2" title="What could be causing my data to display slowly?" >}}
The genome browser tracks may display slowly for various reasons, including having too many tracks open at once, viewing a large genomic window, a high number of custom tracks, numerous large data files, or a slow/unstable internet connection. If the problems persist, please do not hesitate to contact us at <dsn-eb@scilifelab.se> or through the <a href="/contact">Contact</a> form.
{{< /faq_block >}}

</div>

#### About citation guidelines

<div class="accordion mb-4" id="accordion-3">

{{< faq_block accordionID="accordion-3" title="How can I cite the Genome Portal content?" >}}
Depending on how you use the Genome Portal in your work (e.g., manuscript, presentation, etc.), there are various options for citing its content. For example, you can cite: the Genome Portal website, the website source code, the specific datasets from each species, or the JBrowse 2 genome browser. More details on citation guidelines can be found on the <a href="/citation">Cite us</a> page.
{{< /faq_block >}}

</div>
