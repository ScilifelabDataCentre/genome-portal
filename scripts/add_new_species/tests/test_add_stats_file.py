from pathlib import Path

import yaml
from add_stats_file import add_stats_file


def _read_stats(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def test_add_stats_file_populates_genome_busco(tmp_path: Path) -> None:
    user_data_tracks = [
        {
            "dataTrackName": "Genome",
            "buscoStats": "C:99% [S:97.8%, D:1.2%], F:0.2%, M:0.8%, n:5286 (lepidoptera_odb10)",
        }
    ]
    add_stats_file(data_dir_path=tmp_path, user_data_tracks=user_data_tracks)

    stats = _read_stats(tmp_path / "species_stats.yml")
    assembly_busco_rows = [row for row in stats["assembly"] if "BUSCO % [EDIT]" in row]
    assert (
        assembly_busco_rows[0]["BUSCO % [EDIT]"]
        == "C:99% [S:97.8%, D:1.2%], F:0.2%, M:0.8%, n:5286 (lepidoptera_odb10)"
    )


def test_add_stats_file_appends_annotation_busco_for_protein_coding_genes(tmp_path: Path) -> None:
    user_data_tracks = [
        {
            "dataTrackName": "Protein-coding genes",
            "buscoStats": "C:98% [S:96.5%, D:1.5%], F:0.9%, M:1.1%, n:255 (eukaryota_odb10)",
        }
    ]
    add_stats_file(data_dir_path=tmp_path, user_data_tracks=user_data_tracks)

    stats = _read_stats(tmp_path / "species_stats.yml")
    assert stats["annotation"][-1] == {
        "BUSCO % [EDIT]": "C:98% [S:96.5%, D:1.5%], F:0.9%, M:1.1%, n:255 (eukaryota_odb10)"
    }


def test_add_stats_file_ignores_invalid_or_non_target_busco(tmp_path: Path) -> None:
    user_data_tracks = [
        {
            "dataTrackName": "Repeats",
            "buscoStats": "C:99% [S:97.8%, D:1.2%], F:0.2%, M:0.8%, n:5286 (lepidoptera_odb10)",
        },
        {
            "dataTrackName": "Genome",
            "buscoStats": "not a valid busco string",
        },
    ]
    add_stats_file(data_dir_path=tmp_path, user_data_tracks=user_data_tracks)

    stats = _read_stats(tmp_path / "species_stats.yml")
    assembly_busco_rows = [row for row in stats["assembly"] if "BUSCO % [EDIT]" in row]
    assert assembly_busco_rows[0]["BUSCO % [EDIT]"] == "[EDIT]"
    assert all("BUSCO % [EDIT]" not in row for row in stats["annotation"])


def test_add_stats_file_accepts_busco_with_extra_spaces_and_int_float_mix(tmp_path: Path) -> None:
    messy_busco = "C : 99 % [ S : 97.8 % , D:1 % ] , F : 0.2 % , M: 1 % , n : 5286 ( lepidoptera_odb10 )"
    user_data_tracks = [
        {
            "dataTrackName": "Genome",
            "buscoStats": messy_busco,
        }
    ]
    add_stats_file(data_dir_path=tmp_path, user_data_tracks=user_data_tracks)

    stats = _read_stats(tmp_path / "species_stats.yml")
    assembly_busco_rows = [row for row in stats["assembly"] if "BUSCO % [EDIT]" in row]
    assert assembly_busco_rows[0]["BUSCO % [EDIT]"] == messy_busco
