---
title: Recommendations of how to make data files publicly available
---

The Genome Portal uses the FAIR principles as a guidance for sharing of research data. FAIR encourages researchers to make their data Findable, Accessible, Interoperable, and Reusable. One of the ways that we encourage this is by requiring that all data that is displayed in the Genome Portal is submitted to external research data repositories. In this way, we hope that many valuable datasets that otherwise might not be shared via the main nucleotide repositories can be made public.

- For more information on the FAIR principles, we recommend <a href="https://data-guidelines.scilifelab.se/topics/fair-principles/ ">this page</a> from SciLifeLab.

Below we list three recommendations of how to share research data in a manner that follows the FAIR principles and facilitates the integration with the Genome Portal. For information relating to the data files themselves, please also see the <a href="/add_genome/recommendations_for_file_formats"> recommendations for file formats</a> for displaying data on the Genome Portal.

#### Recommendations

1. The files should be uploaded to a repository that provides a persistent identifier, such as a DOI.

    - Assemblies and annotation of protein coding genes should be uploaded to a specialized repository such as ENA (European Nucleotide Archive) and NCBI GenBank. This is a *de facto* standard in genomics and is often a requirement for submission of manuscripts to scientific journals. Files uploaded to these repositories will get a persistent identifier in the form of an Accession Number.

    - For other data types that can be displayed in the Genome Portal, there are likely no specialized repositories. Therefore, such files can be submitted to a general purpose repository, such as <a href="https://figshare.scilifelab.se/">SciLifeLab Data Repository</a>, and <a href="https://zenodo.org/">Zenodo</a>.

        - The Genome Portal is developed and maintained as part of the Data-Drive Life Science (DDLS) program at SciLifeLab, and we recommend users to use SciLifeLab Data Repository since we are able to give detailed advice on how to make submissions there.

        - GitHub or cloud-based storage services such as Google Drive, Dropbox, etc., **are not suitable** due to the lack of agreements for persistence of files and identifiers.

2. Each data file should be accessible with a unique download URL that points to that file only, and not to an archive containing several files.

    - This facilitates file handling both for the Genome Portal server, and for users that want to access a specific file from a repository.

    - Note! The persistent identifier can refer to a collection of data files, e.g. an Acession Number on ENA/NCBI or a DOI to a SciLifeLab Data Repository submission, but each file that is connected to that persistent identifier need to have its own download URL.

3. The files should be compressed to save disk size. It is recommended to use gzip (.gz) since this is very common compression format used in bioinformatics. It is for instance used by the major repositories ENA (European Nucleotide Archive) and NCBI GenBank for storing and sharing genome assembly data.

    - Gzip itself only supports single files as input, which helps adhere to the bullet number 2 above.

    - It might be tempting to add multiple files to an archive (e.g. .tar) and compressing them together (e.g. .tar.gz), but this not suitable for compatibility with the Genome Portal.

#### Example

Let’s say that a user wants to make three files publicly available by submitting them to SciLifeLab Data Repository. Assume that the files are called `data_track1.gff`, `data_track2.bed`, and `data_track3.gff`. After gziping each file on their own, there will be three files ready to be uploaded during the SciLifeLab Data Repository submission process:

- `data_track1.gff.gz` (the gzipped version of the file `data_track1.gff`)

- `data_track2.bed.gz` (the gzipped version of the file `data_track2.bed`)

- `data_track3.gff.gz` (the gzipped version of the file `data_track3.gff`)

#### Questions?

 We are happy to discuss and advice on how to best practices for making research data available. Please see our <a href="/contact" target="_blank">contact details</a> for information on how to get in touch with us.
