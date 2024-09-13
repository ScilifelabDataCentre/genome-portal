---
title: Recommendations of how to make data files publicly available
toc: true
---

## Recommendations of how to make data files publicly available

The Swedish Reference Genome Portal uses the FAIR principles as a guidance for sharing of research data. FAIR encourages researchers to make their data Findable, Accessible, Interoperable, and Reusable. One of the ways that we encourage this is by requiring that all data that is displayed on the Genome Portal is submitted to public data repositories. In this way, we hope that many valuable datasets that otherwise might not be shared via the main nucleotide repositories can be made public.

{{< info_block >}}
Recommendations on how to find a suitable repository can be found in the <a href="https://data-guidelines.scilifelab.se/data-life-cycle/share/">SciLifeLab Research Data Management guidelines</a>.
{{< /info_block >}}

Below we list three recommendations on how to share research data in a manner that follows the FAIR principles and facilitates the integration with the Genome Portal. For information relating to the data files themselves, please also see the <a href="/contribute/recommendations_for_file_formats"> recommendations for file formats</a> for displaying data on the Genome Portal.

### Recommendations

1. The files should be uploaded to a repository that provides a persistent identifier, such as a DOI.

    - Assemblies and annotation of protein-coding genes should be uploaded to a discipline-specific repository such as the <a href="https://www.ebi.ac.uk/ena/browser/home">European Nucleotide Archive (ENA)</a>  or
    <a href=" https://www.ncbi.nlm.nih.gov/genbank/"> National Center for Biotechnology Information NCBI - GenBank</a>. This is a *de facto* standard in genomics and is often a requirement for submission of manuscripts to scientific journals. Files uploaded to these repositories will get a persistent identifier in the form of an Accession Number.

    - For other data types that can be displayed on the Genome Portal, there are likely no specialized repositories. Therefore, such files can be submitted to a general purpose repository, such as the <a href="https://figshare.scilifelab.se/">SciLifeLab Data Repository</a>, and <a href="https://zenodo.org/">Zenodo</a>.

        - The Genome Portal is developed and maintained as part of the Data-Drive Life Science (DDLS) program at SciLifeLab, and we recommend users to use SciLifeLab Data Repository since we are able to give detailed advice on how to make submissions there.

        - GitHub or cloud-based storage services such as Google Drive, Dropbox, etc., **are not suitable** due to the lack of agreements for persistence of files and identifiers.

2. Each data file should be accessible with a unique download URL that points to that file only, and not to an archive containing several files.

    - This facilitates file handling both for the Genome Portal server, and for users that want to access a specific file from a repository.

    - Note! The persistent identifier can refer to a collection of data files, e.g., an Accession Number on ENA/NCBI or a DOI to a SciLifeLab Data Repository submission, but each file that is connected to that persistent identifier needs to have its own download URL.

3. The files should be compressed to save disk size. It is recommended to use gzip (.gz) since this is a very common compression format used in bioinformatics. It is for instance used by the major repositories ENA and NCBI GenBank for storing and sharing genome assembly data.

    - Gzip itself only supports single files as input, which helps adhere to the recommendation of a single URL for each file.

    - It might be tempting to add multiple files to an archive (e.g., .tar) and compress them together (e.g., .tar.gz), but this approach is not compatible with the Genome Portal.

#### Example

Let’s assume that a user wants to make three files publicly available by submitting them to the SciLifeLab Data Repository. The files are called data_track1.gff, data_track2.bed, and data_track3.gff. After compressing each file on their own with gzip, there will be three files ready to be uploaded during the SciLifeLab Data Repository submission process:

- `data_track1.gff.gz` (the gzipped version of the file `data_track1.gff`)

- `data_track2.bed.gz` (the gzipped version of the file `data_track2.bed`)

- `data_track3.gff.gz` (the gzipped version of the file `data_track3.gff`)

### Questions?

We are happy to discuss and advise on best practices for making research data publicly available. Please send us an email to [dsn-eb@scilifelab.se](mailto:dsn-eb@scilifelab.se) or contact us through the <a href="/contact">Contact page</a>.
