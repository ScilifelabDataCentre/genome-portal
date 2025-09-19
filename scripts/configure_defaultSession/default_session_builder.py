from dataclasses import dataclass, field
from typing import Any, Optional

from default_session_utils import (
    get_base_extension,
    get_fasta_header_and_scaffold_length,
    get_species_abbreviation,
    get_track_file_name,
)


@dataclass
class TrackParams:
    """
    Class used to hold the parameters for each track that are needed to populate a DefaultSession object.
    (The pun is intentional: it contains parameters from tracks, and it tracks parameters)
    """

    track_view_id: str
    track_file_name: str
    track_name: str
    display_type_key: Optional[str]
    display_type: str
    display_config: str
    score_column: Optional[str]
    is_quantiative_track: bool
    assembly_names: list[str]

    @staticmethod
    def get_track_adapter_config(track_params: "TrackParams") -> dict[str, str]:
        """
        Determine the adapter type and related configuration based on the track parameters.
        """
        base_extension = get_base_extension(file_name=track_params.track_file_name)

        if base_extension == "gff":
            adapter_type = "Gff3TabixAdapter"
            location_key = "gffGzLocation"
        elif base_extension == "bed":
            if track_params.display_type == "LinearWiggleDisplay":
                adapter_type = "BedGraphAdapter"
                location_key = "bedGraphLocation"
            else:
                adapter_type = "BedTabixAdapter"
                location_key = "bedGzLocation"
        else:
            raise ValueError(f"Unsupported file extension: {base_extension}")

        adapter_location = track_params.track_file_name
        if adapter_location.endswith((".gz", ".zip")):
            adapter_location = adapter_location.rsplit(".", 1)[0] + ".bgz"
        elif adapter_location.endswith((".gff", ".bed")):
            adapter_location += ".bgz"

        index_location = f"{adapter_location}.csi"

        return {
            "adapter_location": adapter_location,
            "adapter_type": adapter_type,
            "index_location": index_location,
            "location_key": location_key,
        }

    @staticmethod
    def check_if_plugin_needed(track_params: "TrackParams") -> Optional[dict[str, str]]:
        """
        Check if a plugin is needed for the track based on known requirements.
        """
        if track_params.display_type == "LinearManhattanDisplay":
            return {
                "name": "GWAS",
                "url": "https://unpkg.com/jbrowse-plugin-gwas/dist/jbrowse-plugin-gwas.umd.production.min.js",
            }
        return None

    @staticmethod
    def get_display_type(track: dict[str, Any]) -> tuple[Optional[str], str]:
        """
        Determine the display_type_key and display_type based on the track's displayType.
        Used by the from_track() class method.
        """
        display_type_key = track.get("displayType")
        display_type_key = display_type_key.lower() if display_type_key is not None else None
        if display_type_key is None or display_type_key == "linear":
            display_type = "LinearBasicDisplay"
        elif display_type_key == "arc":
            display_type = "LinearArcDisplay"
        elif display_type_key == "gwas":
            display_type = "LinearManhattanDisplay"
        elif display_type_key == "wiggle":
            display_type = "LinearWiggleDisplay"
        else:
            raise ValueError(f"Unknown displayType: {display_type_key}")
        return display_type_key, display_type

    @classmethod
    def from_track(
        cls, track: dict[str, Any], track_assembly_names: list[str], species_abbreviation: str
    ) -> "TrackParams":
        """
        Create a TrackParams instance from a track dictionary.
        """
        track_view_id = (
            f"{species_abbreviation}_default_{track['name'].replace(' ', '_').replace('\'', '').replace(',', '')}"
        )
        track_file_name = get_track_file_name(track)
        display_type_key, display_type = cls.get_display_type(track)
        display_config = f"{track_file_name}-{display_type}"
        score_column = track.get("scoreColumn")
        is_quantiative_track = "LinearWiggleDisplay" in display_type

        return cls(
            track_view_id=track_view_id,
            track_file_name=track_file_name,
            track_name=track["name"],
            display_type_key=display_type_key,
            display_type=display_type,
            display_config=display_config,
            score_column=score_column,
            is_quantiative_track=is_quantiative_track,
            assembly_names=track_assembly_names,
        )


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

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "DefaultSession":
        species_name = config["organism"]
        return cls(
            species_name=species_name,
            species_abbreviation=get_species_abbreviation(species_name=species_name),
            species_slug=species_name.replace(" ", "_").lower(),
        )

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

    def add_track_to_view(self, assembly_counter: int, track_params: TrackParams) -> None:
        """
        Optional tracks are those that are set to defaultSession: true in the config.yml.
        They are called 'optional' since the only mandatory track in the Genome Portal is the protein-coding genes track (in the first assembly, if multiple).
        """
        new_track = [
            {
                "id": track_params.track_view_id,
                "type": "FeatureTrack" if not track_params.is_quantiative_track else "QuantitativeTrack",
                "configuration": track_params.track_file_name,
                "minimized": False,
                "displays": [
                    {
                        "id": f"{track_params.track_view_id}_display",
                        "type": track_params.display_type,
                        "heightPreConfig": 150,
                        "configuration": track_params.display_config,
                    }
                ],
            }
        ]
        self.views[assembly_counter]["tracks"].extend(new_track)

    def add_track_to_top_level_tracks(self, track_params: TrackParams) -> None:
        """
        This function is used for tracks that are configured in config.yml with addTrack: false,
        which means that the makefile skips the step of adding them to the final config.json with
        JBrowse CLI. This is useful for tracks that need more complex defaultSession settings.
        """
        adapter_config = TrackParams.get_track_adapter_config(track_params)

        new_top_level_track = {
            "type": "FeatureTrack" if not track_params.is_quantiative_track else "QuantitativeTrack",
            "trackId": track_params.track_file_name,
            "name": track_params.track_name,
            "assemblyNames": track_params.assembly_names,
            "adapter": {
                "type": adapter_config["adapter_type"],
                adapter_config["location_key"]: {"uri": adapter_config["adapter_location"]},
                "index": {"location": {"uri": adapter_config["index_location"]}, "indexType": "CSI"},
            },
            "displays": [
                {
                    "type": track_params.display_type,
                    "displayId": track_params.display_config,
                }
            ],
        }
        if track_params.score_column is not None:
            new_top_level_track["adapter"]["scoreColumn"] = track_params.score_column

        self.top_level_tracks.append(new_top_level_track)

    def add_plugin(self, plugin_call: dict[str, str]) -> None:
        if plugin_call not in self.plugins:
            self.plugins.append(plugin_call)


def create_view(
    default_session: DefaultSession, config: dict[str, Any], assembly_counter: int, skip_reading_fasta: bool = False
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
        track_assembly_names = [config["assembly"]["name"]]
        track_params = TrackParams.from_track(
            track=track,
            track_assembly_names=track_assembly_names,
            species_abbreviation=species_abbreviation,
        )

        if "addTrack" in track and not track["addTrack"]:
            default_session.add_track_to_top_level_tracks(track_params=track_params)

        if ("defaultSession" in track and track["defaultSession"]) or (
            track.get("name", "").lower() in ["protein coding genes", "protein-coding genes"]
        ):
            default_session.add_track_to_view(assembly_counter=assembly_counter, track_params=track_params)

        plugin_call = TrackParams.check_if_plugin_needed(track_params)
        if plugin_call:
            default_session.add_plugin(plugin_call=plugin_call)

    return default_session
