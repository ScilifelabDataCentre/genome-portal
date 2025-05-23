from pathlib import Path
from typing import Any

from default_session_builder import (
    DefaultSession,
    check_if_plugin_needed,
    create_view,
    process_tracks,
)


def test_create_views_from_fixture(example_configs: list[Any], example_init_default_session: DefaultSession) -> None:
    """
    Test that successfully creates views in the DefaultSession object from inputs
    in the example config.yml sourced from ./fixtures/config.yml.
    """
    configs = example_configs
    default_session = example_init_default_session
    assembly_counter = 0
    for assembly_counter, config in enumerate(configs):
        default_session = create_view(
            default_session=default_session,
            config=config,
            assembly_counter=assembly_counter,
        )
    assert default_session.views, "No views were created"


def test_add_track_to_view(
    example_default_session_with_view: DefaultSession, example_track_params: dict[str, Any]
) -> None:
    """
    Test that successfully adds tracks an initiated view in the DefaultSession object.
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
        for param_key, param_value in param.items():
            if param_key in added_track:  # not all track_params are used in the tested function
                assert (
                    added_track[param_key] == param_value
                ), f"{param_key} does not match: {added_track[param_key]} != {param_value}"


def test_add_track_to_top_level_tracks(
    example_init_default_session: DefaultSession, example_track_params: dict[str, dict[str, Any]]
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
        for param_key, param_value in param.items():
            if param_key in added_track:  # not all track_params are used in the tested function
                assert (
                    added_track[param_key] == param_value
                ), f"{param_key} does not match: {added_track[param_key]} != {param_value}"
                if param.get("display_type") == "LinearWiggleDisplay":
                    assert added_track["type"] == "QuantitativeTrack"
                else:
                    assert added_track["type"] == "FeatureTrack"


def test_add_plugin(
    example_init_default_session: DefaultSession, example_track_params: dict[str, dict[str, Any]]
) -> None:
    """
    Test that successfully adds a plugin call to the DefaultSession object.
    """

    default_session = example_init_default_session
    track_params = example_track_params
    for param in track_params.values():
        plugin_call = check_if_plugin_needed(track_params=param)
        if plugin_call:
            default_session.add_plugin(plugin_call=plugin_call)
            assert default_session.plugins, "No plugins were added to the DefaultSession object"


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
