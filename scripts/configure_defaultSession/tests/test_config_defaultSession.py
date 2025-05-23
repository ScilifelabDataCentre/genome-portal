import pytest
from default_session_builder import (
    get_protein_coding_gene_file_name,
)

# def test_initiate_defaultSession(example_names: dict[str, str]) -> None:
#     assembly_counter = 0
#     data = initiate_defaultSession(
#         species_name_variants=example_names,
#         assembly_counter=assembly_counter,
#     )
#     assert data["defaultSession"]["id"].startswith(example_names["species_abbreviation"])
#     assert data["defaultSession"]["name"] == example_names["species_name"]
#     assert (
#         data["defaultSession"]["widgets"]["hierarchicalTrackSelector"]["view"]
#         == f"{example_names["species_abbreviation"]}_default_session_view_{assembly_counter}"
#     )


def test_get_protein_coding_gene_valid_config(config_protein_coding_genes):
    config = config_protein_coding_genes
    assembly_counter = 0

    protein_coding_gene_file_name = get_protein_coding_gene_file_name(config, assembly_counter)
    assert protein_coding_gene_file_name is not None


def test_get_protein_coding_gene_invalid_config(config_protein_coding_genes):
    """
    The first assembly in the config (assembly_counter = 0) needs to have a protein-coding gene track.
    The second assembly (assembly_counter = 1) is allowed to not have a protein-coding gene track (i.e. `is None`).
    """
    config = config_protein_coding_genes
    config["tracks"][0]["name"] = config["tracks"][0]["name"].replace("Protein-coding genes", "repeats")

    assembly_counter = 0
    with pytest.raises(ValueError, match="The primary assembly"):
        get_protein_coding_gene_file_name(config, assembly_counter)

    assembly_counter = 1
    protein_coding_gene_file_name = get_protein_coding_gene_file_name(config, assembly_counter)
    assert protein_coding_gene_file_name is None
