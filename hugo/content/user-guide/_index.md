---
title: "User guide"
toc: true
---

## User guide

On this page, you will find documentation for the **Swedish Reference Genome Portal**, which provides a general overview of its graphical user interface, structure, and useful features.

We gratefully welcome comments or questions via [email](mailto:dsn-eb@scilifelab.se), or through our <a href="/contact" target="_blank">contact</a> form.

### 1. Website structure

The Genome Portal website consists of two main components: A **Home page** and a **Species page** for for each species entry.

### 1.1. Home page

This is the landing page of the Genome Portal. It consists of three main components: **navigation bar**, **search bar**, and **species cards** (Figure 1).

The **navigation bar** includes links to various pages:

- **Home**: The main landing page of the Genome Portal website.

- **Contribute**: Instructions on how to submit data, definition of the Genome Portal's scope, data requirements, supported file formats, and recommendations for making data files publicly available.

- **User guide**: An overview of the structure, content, and graphical user interface of the Genome Portal to help users understand how to make the best use of the service.

- **Frequently Asked Questions (FAQs)**: Answers to common questions that users may have regarding the Genome Portal.

- **Glossary**: An alphabetically arranged list providing definitions for terms on the website that might be unfamiliar to users.

- **About**: Overview of the Genome Portal service, terms of use, privacy policy, funding, and implementation details.

- **Contact**: A form to reach out to the Genome Portal's staff.

- **Cite us**: Guidelines on recommended citations for the Genome Portal website, species pages, data files, and genome browser.

<p align=center><img src="/img/user-guide/Fig01_Home_page.webp"
    alt="Figure 1. Home page of the Genome Portal"
    style="width: 80%;"></p>

<p align=center><b>Figure 1</b>. Home page of the Genome Portal.</p>

The **search bar** allows you to find or filter species displayed on the Genome Portal. Simply type the scientific or common name of a species of interest into the search bar, or use the sorting menu (to the left of the search bar) to arrange the species cards (below) in alphabetical order.

The **species cards** show brief information about each species displayed on the Genome Portal. They include a species photo, scientific and common name, and the date it was last updated. Species cards are arranged with the most recently added species shown in the leftmost position. As the list of species grow, we plan to add pagination to this section.

### 1.2. Species page

Each species included in the Genome Portal has its own Species page, which consists of four main components: **Description tab**, **Genome assembly tab**, **Download tab**, and a link to the JBrowse **genome browser**, which opens in a new window and displays annotation data tracks.

The following sections provide further details on each component.

#### Description tab

This tab presents general information about the species (Figure 2), including:

- Scientific and English common species names.

- Photo.

- Taxonomic classification (retrieved from ENA).

- Species information.

- Recommended citation.

- References.

- Link to the genome browser, which opens in a new window.

- Interactive map of observation (occurrence) data (retrieved from the Global Biodiversity Information Facility, GBIF)

- Vulnerability status (retrieved from the International Union for Conservation of Nature, IUCN, and Artdatabanken, SLU Swedish Species Information Centre, if available)

- Links to external resources such as the Swedish Biodiversity Data Infrastructure (SBDI), GBIF, and Genomes on a Tree (GoaT).

<p align=center><img src="/img/user-guide/Fig02_Species_page_Description_tab.webp"
    alt="Figure 2. Description tab of a Species page on the Genome Portal"
    style="width: 80%;"></p>

<p align=center><b>Figure 2</b>. Description tab of a Species page on the Genome Portal.</p>

##### Programmatic information retrieval

As mentioned earlier, some information shown on the Description page is programmatically retrieved from external sources. Below is a brief description of how this is accomplished.

- **Taxonomic classification**: To get taxonomic information for a species included in the Genome Portal, a Python script named `get_taxonomy.py` has been developed. This script is located in the `scripts/` folder of the <a href="https://github.com/ScilifelabDataCentre/genome-portal" target="_blank">Genome Portal's GitHub repository</a>, which hosts the website's source code. This script file is a module within another script, `add_new_species.py`, which contains the `get_taxonomy` function. This function retrieves the taxonomic information for a species and saves it to a JSON file (`.json`). The script utilises the [ENA REST API](https://ena-docs.readthedocs.io/en/latest/retrieval/programmatic-access/taxon-api.html) to obtain the species taxonomic data.

- **Map of observation (occurrence data)**: To obtain  occurrence data and add a map layer or background, the [GBIF API](https://techdocs.gbif.org/en/openapi/) is used. The occurrence data is projected onto a map using the [javascript library leaflet](https://leafletjs.com/). To retrieve the occurrence data, only the GBIF species ID is needed, which can be obtained by following the instructions below.

- **External links**: The SBDI and GBIF species ID are obtained by searching the species' scientific name using the [GBIF API](https://techdocs.gbif.org/en/openapi/). These IDs can then be used to construct web addresses, as both sites have predictable URLs for any species. For example: `https://www.gbif.org/species/[GBIF_ID_HERE]`. Similarly, for the link to GoaT, the URL can be created using the species' scientific name and NCBI (National Center for Biotechnology Information) taxonomy ID, as in: `https://goat.genomehubs.org/record?recordId={str(tax_id)}&result=taxon&taxonomy=ncbi#{species_name}`. If any of these automated searches fail, a warning is displayed, so these values can be added manually.

#### Genome assembly tab

This tab provides information about the genome assembly, including associated information from ENA (the European Nucleotide Archive), assembly and annotation statistics, the scientific article where the genome assembly was published, funding, acknowledgements, and links to the genome assembly in ENA and NCBI (Figure 3).

<p align=center><img src="/img/user-guide/Fig03_Species_page_Genome_assembly_tab.webp"
    alt="Figure 3. Genome assembly tab of a Species page on the Genome Portal."
    style="width: 80%;"></p>

<p align=center><b>Figure 3</b>. Genome assembly tab of a Species page on the Genome Portal.</p>

#### Download tab

This tab presents a table with contextual information (metadata) about the data files displayed on the Genome Portal (Figure 4), including the data track name and description, external links, accession number or DOI, file name, principal investigator and their affiliation, and the date first listed on the portal.

Use the toggle in the upper-right corner of the table to switch between the default and expanded table views.

The 'Links' column provides external link buttons to download the original data file, visit the website of the public repository where the data was obtained, and, if applicable, visit the associated scientific article(s) related to the data.

Below the table, links are provided to download the table as a JSON file, open the `refNameAlias` text file in a new window (used in JBrowse to set the aliases for differing sequence names, e.g., to define that “chr1” is an alias for “1”), and open the <a href="/glossary" target="_blank">Glossary</a> page in a new window.

<p align=center><img src="/img/user-guide/Fig04_Species_page_Download_tab.webp"
    alt="Figure 4. Download tab of a Species page on the Genome Portal."
    style="width: 80%;"></p>

<p align=center><b>Figure 4</b>. Download tab of a Species page on the Genome Portal.</p>

#### Genome browser

When you click the **Browse the genome** button located in the upper-right corder of a **Species page**, the JBrowse genome browser opens in a new web browser window, displaying the data tracks of the current species (Figure 5).

In the genome browser, the data tracks are displayed stacked horizontally.

To navigate along the genome, use the pan and zoom buttons on the top of the window.

<p align=center><img src="/img/user-guide/Fig05_Species_page_Genome_browser.webp"
    alt="Figure 5. View of the embedded JBrowse genome browser in the Genome Portal."
    style="width: 80%;"></p>

<p align=center><b>Figure 5</b>. View of the embedded JBrowse genome browser in the Genome Portal. (1) FILE menu; (2) ADD menu; (3) TOOLS menu; (4) HELP menu; (5) SHARE link; (6) Browser menu; (7) Pan buttons to scroll left or right; (8) Zoom buttons or slider to zoom on the view; (9) Click and drag the handle indicated by six vertical dots to vertically reorder tracks; (10) Click the data track menu indicated by three vertical dots to display; (11) Filter tracks; (12) Available tracks</p>

Further information can be found in the <a href="[/contact](https://jbrowse.org/jb2/docs/user_guides/basic_usage/)" target="_blank">JBrowse documentation - basic usage</a> page.

### 2. Useful genome browser features

Please check the <a href="/faqs" target="_blank">Frequently Asked Questions</a> page.

#### Search a genomic location

Navigation, scrolling, searching a genomic location <https://jbrowse.org/jb2/docs/quickstart_web/#indexing-feature-names-for-searching>

You can search a location in several ways when typing in the search box:

- Searching by region and location, e.g. chr1:1..100 or chr1:1-100 or chr1 1 100
- Searching by assembly, region, and location, e.g. {hg19}chr1:1-100
- Searching discontinuous regions, delimited by a space, and opening them side-by-side, e.g. chr1:1..100 chr2:1..100
- Searching in any of the above ways and appending [rev] to the end of the region will horizontally flip it, e.g. chr1:1-100\
- If configured, searching by gene name or feature keywords, e.g. BRCA1

#### Opening track

<https://jbrowse.org/jb2/docs/quickstart_web/#indexing-feature-names-for-searching>

#### Sharing sessions

<https://jbrowse.org/jb2/docs/quickstart_web/#indexing-feature-names-for-searching>

#### Recently used and favourite tracks

<https://jbrowse.org/jb2/docs/quickstart_web/#indexing-feature-names-for-searching>

#### Save a genomic view as a vectorised SVG file image

SVG export of all view types
SVG export is a highly requested feature, as it enables publication quality exports of the JBrowse 2 visualizations.

This made it so synteny views, dotplot views, breakpoint split view, and circular view were all supported by the SVG export functionality!

We're excited to introduce a new feature to JBrowse Web: built-in SVG export of track visualizations! This feature currently supports the linear genome view, and will be extended to more views in future releases.

#### Customising the data track

<https://jbrowse.org/jb2/docs/config_guides/theme/>

<https://jbrowse.org/jb2/docs/config_guides/tracks/>

### 3. Advanced features and additional resources

Visualisation of linear synteny between two genomes, HiC contact maps, CNV data, breakpoint split view of Structural Variants (SVs)

<https://jbrowse.org/jb2/gallery/>

Learn more <https://jbrowse.org/jb2/docs/>
