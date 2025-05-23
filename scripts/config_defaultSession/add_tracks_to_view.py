from dataclasses import dataclass, field
from typing import Any

from utils import get_fasta_header_and_scaffold_length, get_track_adapter_config, get_track_file_name


@dataclass
class DefaultSession:
    """
    Class used to create a defaultSession JSON object based on a config.yml.
    """

    species_name: str
    species_abbreviation: str
    species_slug: str
    views: list[dict[str, Any]] = field(default_factory=list)
    top_level_tracks: list[dict[str, Any]] = field(default_factory=list)
    plugins: list[dict[str, Any]] = field(default_factory=list)

    def make_defaultSession_dict(self) -> dict[str, any]:
        data = {
            "defaultSession": {
                "id": f"{self.species_abbreviation}_default_session",
                "name": self.species_name,
                "widgets": {
                    "hierarchicalTrackSelector": {
                        "id": "hierarchicalTrackSelector",
                        "type": "HierarchicalTrackSelectorWidget",
                        "view": f"{self.species_abbreviation}_default_session_view_0",
                        "faceted": {"showSparse": False, "showFilters": True, "showOptions": False, "panelWidth": 400},
                    }
                },
                "activeWidgets": {"hierarchicalTrackSelector": "hierarchicalTrackSelector"},
                "views": self.views,
            },
            "configuration": {"disableAnalytics": True},
        }
        if self.top_level_tracks:
            data["tracks"] = self.top_level_tracks
        if self.plugins:
            data["plugins"] = self.plugins
        return data

    def add_view(
        self,
        assembly_counter: int,
        config: dict[str, Any],
        default_scaffold: str = None,
        scaffold_length: int = None,
        bpPerPx: int = 50,
    ) -> None:
        view = {
            "id": f"{self.species_abbreviation}_default_session_view_{assembly_counter}",
            "minimized": False,
            "type": "LinearGenomeView",
            "trackLabels": "offset",
            "offsetPx": 0,
            "bpPerPx": bpPerPx,
            "displayedRegions": [
                {
                    "refName": default_scaffold if default_scaffold else "[EDIT: SCAFFOLD_HEADER]",
                    "start": 0,
                    "end": scaffold_length if scaffold_length else 100000,
                    "reversed": False,
                    "assemblyName": config["assembly"]["name"],
                }
            ],
            "tracks": [],
        }
        self.views.append(view)

    def add_track_to_view(self, assembly_counter: int, track_params: dict[str, Any]) -> None:
        """
        Optional tracks are those that are set to defaultSession: true in the config.yml.
        They are called 'optional' since the only mandatory track in the Genome Portal is the protein-coding genes track (in the first assembly, if multiple).
        """
        new_track = [
            {
                "id": track_params["track_view_id"],
                "type": "FeatureTrack" if not track_params["is_quantiative_track"] else "QuantitativeTrack",
                "configuration": track_params["track_config"],
                "minimized": False,
                "displays": [
                    {
                        "id": f"{track_params["track_view_id"]}_display",
                        "type": track_params["track_type"],
                        "heightPreConfig": 150,
                        "configuration": track_params["display_config"],
                    }
                ],
            }
        ]
        self.views[assembly_counter]["tracks"].extend(new_track)

    def add_track_to_top_level_tracks(self, track_params: dict[str, Any]) -> None:
        """
        This function is used for tracks that are configured in config.yml with addTrack: false,
        which means that the makefile skips the step of adding them to the final config.json with
        JBrowse CLI. This is useful for tracks that need more complex defaultSession settings.
        """
        adapter_config = get_track_adapter_config(track_params=track_params)

        new_top_level_track = {
            "type": "FeatureTrack" if not track_params["is_quantiative_track"] else "QuantitativeTrack",
            "trackId": track_params["track_top_id"],
            "name": track_params["track_name"],
            "assemblyNames": track_params["assemblyNames"],
            "adapter": {
                "type": adapter_config["adapter_type"],
                adapter_config["location_key"]: {"uri": adapter_config["adapter_location"]},
                "index": {"location": {"uri": adapter_config["index_location"]}, "indexType": "CSI"},
            },
            "displays": [
                {
                    "type": track_params["track_type"],
                    "displayId": f"{track_params["track_top_id"]}-{track_params["track_type"]}",
                }
            ],
        }
        if "score_column" in track_params and track_params["score_column"] is not None:
            new_top_level_track["adapter"]["scoreColumn"] = track_params["score_column"]

        self.top_level_tracks.append(new_top_level_track)

    def add_plugin(self, plugin_call: dict[str, str]) -> None:
        if plugin_call not in self.plugins:
            self.plugins.append(plugin_call)


def create_view(
    default_session: DefaultSession, config: dict[str, Any], assembly_counter: int, skip_reading_fasta: bool
) -> DefaultSession:
    if skip_reading_fasta:
        default_scaffold = None
        scaffold_length = None
    else:
        default_scaffold, scaffold_length = get_fasta_header_and_scaffold_length(
            config=config,
            species_slug=default_session.species_slug,
        )
    bpPerPx = config["assembly"].get("bpPerPx", 50)

    default_session.add_view(
        assembly_counter=assembly_counter,
        config=config,
        default_scaffold=default_scaffold,
        scaffold_length=scaffold_length,
        bpPerPx=bpPerPx,
    )
    return default_session


def check_if_plugin_needed(track_params: dict[str, Any]) -> dict[str, str] | None:
    """
    Check if a plugin is needed for the track based on known requirements.
    """
    if track_params.get("track_type") == "LinearManhattanDisplay":
        plugin_call = {
            "name": "GWAS",
            "url": "https://unpkg.com/jbrowse-plugin-gwas/dist/jbrowse-plugin-gwas.umd.production.min.js",
        }
    else:
        plugin_call = None

    return plugin_call


def get_track_display_type(track: dict[str, Any]) -> str:
    """
    Get the optional key track_type from the track.
    """
    track_type = track.get("displayType")
    track_type = track_type.lower() if track_type is not None else None
    if track_type is None or track_type == "linear":
        track_type = "LinearBasicDisplay"
    elif track_type == "arc":
        track_type = "LinearArcDisplay"
    elif track_type == "gwas":
        track_type = "LinearManhattanDisplay"
    elif track_type == "wiggle":
        track_type = "LinearWiggleDisplay"
    return track_type


def make_track_params(track: dict[str, Any], species_abbreviation: str) -> dict[str, Any]:
    """
    Make track parameters for the track.
    """
    track_view_id = (
        f"{species_abbreviation}_default_{track['name'].replace(' ', '_').replace('\'', '').replace(',', '')}"
    )
    track_file_name = get_track_file_name(track)
    track_type = get_track_display_type(track)
    display_config = f"{track_file_name}-{track_type}"
    score_column = track.get("scoreColumn")
    is_quantiative_track = "LinearWiggleDisplay" in track_type

    return {
        "track_view_id": track_view_id,
        "track_top_id": track_file_name,
        "track_file_name": track_file_name,
        "track_name": track["name"],
        "track_type": track_type,
        "track_config": track_file_name,
        "display_config": display_config,
        "score_column": score_column,
        "is_quantiative_track": is_quantiative_track,
    }


def process_tracks(default_session: DefaultSession, config: dict[str, Any], assembly_counter: int) -> DefaultSession:
    """
    Most tracks will be added by the makefile (calling the JBrowse CLI), but for non-standard tracks,
    they need to be added to the defaultSession JSON object. This is done with the add_track_to_top_level_tracks()
    function which is toggled in the config.yml file with addTrack.

    Protein-coding genes are mandatory in the first assembly, and will always be added to the view regardless
    of the defaultSession key.
    """
    species_abbreviation = default_session.species_abbreviation

    has_protein_coding_genes = any(
        "name" in track and track["name"].lower() in ["protein coding genes", "protein-coding genes"]
        for track in config.get("tracks", [])
    )
    if not has_protein_coding_genes and assembly_counter == 0:
        raise ValueError(
            f"The primary assembly (assembly number {assembly_counter+1}) is required to have a track named 'Protein coding genes'. Exiting."
        )

    for track in config.get("tracks", []):
        track_params = make_track_params(track, species_abbreviation)
        track_params["assemblyNames"] = [config["assembly"]["name"]]

        if "addTrack" in track and not track["addTrack"]:
            default_session.add_track_to_top_level_tracks(track_params=track_params)

        if ("defaultSession" in track and track["defaultSession"]) or (
            track.get("name", "").lower() in ["protein coding genes", "protein-coding genes"]
        ):
            default_session.add_track_to_view(assembly_counter=assembly_counter, track_params=track_params)

        plugin_call = check_if_plugin_needed(track_params=track_params)
        if plugin_call:
            default_session.add_plugin(plugin_call=plugin_call)

    return default_session
