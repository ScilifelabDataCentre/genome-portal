from typing import Any

from utils import (
    get_base_extension,
    get_track_adapter_config,
)


def test_get_track_adapter_config(example_track_params: dict[str, dict[str, Any]]) -> None:
    """
    Test that successfully gets the adapter config for each track type.
    """
    track_params = example_track_params
    for param in track_params.values():
        adapter_config = get_track_adapter_config(track_params=param)
        base_extension = get_base_extension(param["track_file_name"])
        if base_extension == "gff":
            assert adapter_config["adapter_type"] == "Gff3TabixAdapter"
            assert adapter_config["location_key"] == "gffGzLocation"
        elif base_extension == "bed":
            if param.get("display_type") == "LinearWiggleDisplay":
                assert adapter_config["adapter_type"] == "BedGraphAdapter"
                assert adapter_config["location_key"] == "bedGraphLocation"
            else:
                assert adapter_config["adapter_type"] == "BedTabixAdapter"
                assert adapter_config["location_key"] == "bedGzLocation"
