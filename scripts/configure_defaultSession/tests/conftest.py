import pytest


@pytest.fixture
def example_names() -> dict[str, str]:
    species_name_variants = {
        "species_name": "Aspergillus nidulans",
        "species_slug": "aspergillus_nidulans",
        "species_abbreviation": "anid",
    }
    return species_name_variants


@pytest.fixture
def config_protein_coding_genes():
    return {
        "organism": "Aspergillus nidulans",
        "assembly": {
            "name": "ASM1142v1",
            "displayName": "A. nidulans genome assembly GCA_000011425.1",
            "accession": "GCA_000011425.1",
            "url": "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/011/425/GCF_000011425.1_ASM1142v1/GCF_000011425.1_ASM1142v1_genomic.fna.gz",
            "fileName": "GCF_000011425.1_ASM1142v1_genomic.fna.gz",
        },
        "tracks": [{"name": "Protein-coding genes", "url": "www.example.com/track.gff.gz", "fileName": "track.gff.gz"}],
    }
