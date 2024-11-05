---
title: "User guide"
toc: true
---

## User guide

[ Version 01, last update: 2024-10-19 ]

Welcome to the Swedish Reference Genome Portal!
This document summarises a brief description of the genome portal’s content and structure, along with some useful functionalities.
Your feedback is important to us, as it help us improve and provide an optimal service to researchers in Sweden.
Please share any questions or comments via email to: <dsn-eb@scilifelab.se>.

## Website structure

### Home page

The landing page of the genome portal. It consists of three main components: a navigation bar, a search bar, and species cards (Figure 1).

In the navigation bar you can find links to various pages:

- About: Overview of the genome portal service, terms of use, privacy policy, and implementation details.

- Contact: Form to reach out the team behind the genome portal.

- Cite us: Instructions on recommended citation for the genome portal, species pages, data files, and genome browser.

- Contribute: Instructions on how to submit data, definition of the scope of the genome portal, and recommendations on data file formats and how to make data files publicly available.

- User guide: A guide to help users understand how to make the best use of the service.

- Frequently Asked Questions (FAQs):

- Glossary: A list arranged in alphabetical order, providing definitions for words or phrases in the website that may be unusual in common language.

<img src="/img/user-guide/Fig01_Home_page.webp"
    alt="Figure 1. Home page of the genome portal"
    style="width: 100%;">

Figure 1. Home page of the genome portal.

Use the search bar to filter the species in the genome portal. Type the scientific or common name of a species of interest into the search bar, or use the sorting menu to the left of the search bar to arrange the species cards below in alphabetical order.

The species cards illustrate some of the species displayed on the portal, where the most recently added species shown on the leftmost position.

### Species pages

Each species included in the genome portal has a dedicated webpage called Species page consisting of four main components: three information tabs (Description, Genome assembly, and Download) and a link to an embedded JBrowse genome browser displaying the annotation data track files. The following sections provide a more detailed description of these main components.

#### Description tab

This tab presents information about the species, including scientific and common names, a photo, a map showing species occurrences from the Global Biodiversity Information Facility (GBIF), taxonomic classification retrieved from XX, vulnerability status from the International Union for Conservation of Nature (IUCN) and Artdatabanken (SLU Swedish Species Information Centre), species information and references, recommended citation, and links to external resources such as GBIF, the Swedish Biodiversity Data Infrastructure (SBDI), and Genomes on a Tree (GoaT) (Figure 2).

<img src="/img/user-guide/Fig02_Species_page_Description_tabo.webp"
    alt="Figure 2. Description tab of a Species page on the genome portal"
    style="width: 100%;">

Figure 2. Description tab of a Species page on the genome portal.

**TO DO**
On <https://scilifelab.atlassian.net/wiki/spaces/DSNEB/pages/2838790174/Getting+taxonomy+information+for+all+species>
Occurrence map
External links

#### Genome assembly tab

This tab presents information about the genome assembly, including a general description from the European Nucleotide Archive (ENA), assembly and annotation statistics obtained with BUSCO, scientific article where the genome assembly was published, funding, acknowledgements, and links to genome assembly in ENA and the National Center for Biotechnology Information (NCBI) (Figure 3).

<img src="/img/user-guide/Fig03_Species_page_Genome_assembly_tab.webp"
    alt="Figure 3. Genome assembly tab of a Species page on the genome portal."
    style="width: 100%;">

Figure 3. Genome assembly tab of a Species page on the genome portal.

#### Download tab

This tab shows a table listing the contextual information (metadata) of the data files displayed on the genome portal (Figure 4).

In the Links column, you can find external link buttons to download the original data file, go to the website of the source repository from where the data was fetched, and (if applicable) the associated scientific article(s) to the data.
Use the toggle on the upper-right corner of the table to switch between the default and the expanded table view.
Below the table, you can find links to download the table as a JSON file, open (in a new tab) the refNameAlias text file used in JBrowse to set the aliases for reference sequence names (e.g., to define that “chr1” is an alias for “1”), and open (in a new tab) the Glossary page.

<img src="/img/user-guide/Fig04_Species_page_Download_tab.webp"
    alt="Figure 4. Download tab of a Species page on the genome portal."
    style="width: 100%;">

Figure 4. Download tab of a Species page on the genome portal

#### Genome browser

When you click the Browse the genome button located on the upper-right side of a Species page, an embedded JBrowse genome browser opens in a new web browser tab (Figure 5).
In the genome browser, the data tracks are displayed stacked horizontally.

<img src="/img/user-guide/Fig05_Species_page_Genome_browser.webp"
    alt="Figure 5. View of the embedded JBrowse genome browser in the genome portal."
    style="width: 100%;">

Figure 5. View of the embedded JBrowse genome browser in the genome portal.
(1) FILE menu
(2) ADD menu
(3) TOOLS menu
(4) HELP menu
(5) SHARE link
(6) Browser menu
(7) Pan buttons to scroll left or right.
(8) Zoom buttons or slider to zoom on the view.
(9) Click and drag the handle indicated by six vertical dots to vertically reorder tracks.
(10) Click the data track menu indicated by three vertical dots to display …
(11) Filter tracks
(12) Available tracks
More information on the JBrowse genome browser can be found in <https://jbrowse.org/jb2/docs/user_guides/basic_usage/>.

### Useful features

#### How to share a genomic region of interest

The data files of each species are displayed on an embedded JBrowse genome browser with full functionalities (Figure 5).

#### How to add non-permanent data tracks to the genome browser

TBA.

#### How to learn more features of the JBrowse2 genome browser

TBA.
