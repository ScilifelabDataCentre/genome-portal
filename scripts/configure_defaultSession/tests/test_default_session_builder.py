from pathlib import Path
from typing import Any

from default_session_builder import (
    DefaultSession,
    TrackParams,
    create_view,
    process_tracks,
)
from default_session_utils import get_base_extension


def test_create_views_from_fixture(example_configs: list[Any], example_init_default_session: DefaultSession) -> None:
    """
    Test that successfully creates views in the DefaultSession object from inputs
    in the example config.yml sourced from ./fixtures/config.yml.
    """
    configs = example_configs
    default_session = example_init_default_session
    for assembly_counter, config in enumerate(configs):
        default_session = create_view(
            default_session=default_session,
            config=config,
            assembly_counter=assembly_counter,
        )
    assert default_session.views, "No views were created"


def test_add_track_to_view(
    example_default_session_with_view: DefaultSession, example_track_params: dict[str, TrackParams]
) -> None:
    """
    Test that successfully adds tracks to an initiated view in the DefaultSession object.
    Since the example_default_session_with_view fixture only has one view, set assembly_counter = 0.
    """
    default_session = example_default_session_with_view
    track_params = example_track_params
    assembly_counter = 0
    for param in track_params.values():
        default_session.add_track_to_view(
            assembly_counter=assembly_counter,
            track_params=param,
        )

        assert default_session.views[assembly_counter]["tracks"], "No tracks were added to the view"

        added_track = default_session.views[assembly_counter]["tracks"][-1]
        assert added_track["configuration"] == param.track_file_name
        assert added_track["type"] == ("QuantitativeTrack" if param.is_quantiative_track else "FeatureTrack")


def test_add_track_to_top_level_tracks(
    example_init_default_session: DefaultSession, example_track_params: dict[str, TrackParams]
) -> None:
    """
    Test that successfully adds tracks to the top level tracks in the DefaultSession object.
    """
    default_session = example_init_default_session
    track_params = example_track_params
    for param in track_params.values():
        default_session.add_track_to_top_level_tracks(track_params=param)

        assert default_session.top_level_tracks, "No tracks were added to the DefaultSession object"

        added_track = default_session.top_level_tracks[-1]
        assert added_track["trackId"] == param.track_file_name
        assert added_track["name"] == param.track_name
        assert added_track["type"] == ("QuantitativeTrack" if param.is_quantiative_track else "FeatureTrack")


def test_view_and_tracks_from_config_fixture(
    example_configs: list[Any], example_init_default_session: DefaultSession
) -> None:
    """
    Test that successfully creates the final DefaultSession object from inputs
    in the example config.yml sourced from ./fixtures/config.yml.
    """
    configs = example_configs
    default_session = example_init_default_session

    for assembly_counter, config in enumerate(configs):
        default_session = create_view(
            default_session=default_session,
            config=config,
            assembly_counter=assembly_counter,
        )
        default_session = process_tracks(
            default_session=default_session,
            config=config,
            assembly_counter=assembly_counter,
        )

        view = default_session.views[assembly_counter]
        assert view["displayedRegions"][0]["assemblyName"] == config["assembly"]["name"]

        view_tracks = view["tracks"]
        for track in config.get("tracks", []):
            file_name = Path(track.get("fileName"))
            file_name_cleaned = (
                file_name.with_suffix("").name if file_name.suffix in [".gz", ".zip", ".bgz"] else file_name.name
            )
            assert file_name_cleaned in [
                v_track.get("configuration") for v_track in view_tracks
            ], f"Track {track.get('fileName')} not found in view[{assembly_counter}] tracks"


def test_get_track_adapter_config(example_track_params: dict[str, TrackParams]) -> None:
    """
    Test that successfully gets the adapter config for each track type.
    """
    track_params = example_track_params
    for param in track_params.values():
        adapter_config = TrackParams.get_track_adapter_config(track_params=param)
        base_extension = get_base_extension(param.track_file_name)
        if base_extension == "gff":
            assert adapter_config["adapter_type"] == "Gff3TabixAdapter"
            assert adapter_config["location_key"] == "gffGzLocation"
        elif base_extension == "bed":
            if param.display_type == "LinearWiggleDisplay":
                assert adapter_config["adapter_type"] == "BedGraphAdapter"
                assert adapter_config["location_key"] == "bedGraphLocation"
            else:
                assert adapter_config["adapter_type"] == "BedTabixAdapter"
                assert adapter_config["location_key"] == "bedGzLocation"
