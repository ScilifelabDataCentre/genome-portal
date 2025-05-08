import shutil
from pathlib import Path

import yaml
from add_new_species.populate_assembly_metadata_fields import (
    populate_assembly_md_with_assembly_metadata,
    populate_config_yml_with_assembly_metadata,
)


def test_populate_config_yml_with_assembly_metadata(temp_output_dir, assembly_metadata_dict):
    """
    Test that copies the template config.yml file to temp test dir
    and populates it from assembly metadata fixture.
    """

    template_config_path = Path(__file__).parent / "../../templates/config.yml"
    temp_config_path = temp_output_dir / "config.yml"
    shutil.copy(template_config_path, temp_config_path)

    populate_config_yml_with_assembly_metadata(assembly_metadata_dict, temp_output_dir)

    with open(temp_config_path, "r") as f:
        updated_config = yaml.safe_load(f)

    assert updated_config["organism"] == "Aspergillus nidulans"
    assert updated_config["assembly"]["name"] == "ASM1142v1"
    assert updated_config["assembly"]["displayName"] == "A. nidulans genome assembly GCA_000011425.1"
    assert updated_config["assembly"]["accession"] == "GCA_000011425.1"


def test_populate_assembly_md_with_assembly_metadata(temp_output_dir, assembly_metadata_dict):
    """
    Test that copies the template assembly.yml file to temp test dir
    and populates it from assembly metadata fixture.
    """
    template_assembly_md_path = Path(__file__).parent / "../../templates/assembly.md"
    temp_assembly_md_path = temp_output_dir / "assembly.md"
    shutil.copy(template_assembly_md_path, temp_assembly_md_path)

    populate_assembly_md_with_assembly_metadata(assembly_metadata_dict, temp_output_dir)

    updated_assembly_md = temp_assembly_md_path.read_text()

    assert "ASSEMBLY_NAME" not in updated_assembly_md
    assert "ASSEMBLY_TYPE" not in updated_assembly_md
    assert "ASSEMBLY_LEVEL" not in updated_assembly_md
    assert "GENOME_REPRESENTATION" not in updated_assembly_md
    assert "ASSEMBLY_ACCESSION" not in updated_assembly_md

    assert "ASM1142v1" in updated_assembly_md
    assert "haploid" in updated_assembly_md
    assert "Chromosome" in updated_assembly_md
    assert "full" in updated_assembly_md
    assert "GCA_000011425.1" in updated_assembly_md
