import os
from dataclasses import dataclass
from pathlib import Path

from utils import get_fasta_header_and_sequence_length, get_track_file_name


@dataclass
class DefaultSession:
    """
    Class used to create a defaultSession JSON object based on a config.yml.
    """

    species_name: str
    species_abbreviation: str
    species_slug: str

    def make_init_dict(self, assembly_counter: int) -> dict[str, any]:
        return {
            "defaultSession": {
                "id": f"{self.species_abbreviation}_default_session",
                "name": self.species_name,
                "widgets": {
                    "hierarchicalTrackSelector": {
                        "id": "hierarchicalTrackSelector",
                        "type": "HierarchicalTrackSelectorWidget",
                        "view": f"{self.species_abbreviation}_default_session_view_{assembly_counter}",
                        "faceted": {"showSparse": False, "showFilters": True, "showOptions": False, "panelWidth": 400},
                    }
                },
                "activeWidgets": {"hierarchicalTrackSelector": "hierarchicalTrackSelector"},
            },
            "configuration": {"disableAnalytics": True},
        }


def initiate_defaultSession(species_name_variants, assembly_counter):
    """
    Subfunction that populates the outer parts of the defaultSession JSON object with the species name and abbreviation.
    Also adds disableAnalytics to the dictionary to prevent Google Analytics from being loaded when running JBrowse.
    """
    session = DefaultSession(
        species_name=species_name_variants["species_name"],
        species_abbreviation=species_name_variants["species_abbreviation"],
        species_slug=species_name_variants["species_slug"],
    )
    data = session.make_init_dict(assembly_counter)
    return data


def initiate_views_and_populate_mandatory_tracks(data, species_name_variants, config, assembly_counter):
    """
    Subfunction that adds a JBrowse view to the defaultSession JSON object. The funcion is iterated upon by main()
    so that a new view is added for each assembly in the config.yml. It then checks if the primary assembly has a
    protein-coding genes track, and if not, raises an error. For the secondary assemblies, there is no requirement to
    have a protein-coding genes track, but at least one track is required. (The populate_values_from_optional_tracks()
    is later called by main() to also ensure that the secondary assemblies have at least one track set to defaultSession: true.)
    """

    # Check if there is a protein-coding genes track configured for the current assembly
    protein_coding_gene_file_name = None
    for track in config.get("tracks", []):
        if "name" in track and track["name"].lower() in ["protein coding genes", "protein-coding genes"]:
            protein_coding_gene_file_name = get_track_file_name(track)
            break

    if not protein_coding_gene_file_name:
        # Primary assemblies are required to have a protein-coding genes track; it is optional for secondary assemblies.
        if assembly_counter == 0:
            raise ValueError(
                f"Error: The primary assembly (assembly number {assembly_counter+1}) is required to have a track named 'Protein coding genes'. Exiting."
            )
        # Secondary assemblies do not need to have a track name "Protein coding genes", but need to have at least one track.
        elif not ("tracks" in config and isinstance(config["tracks"], list) and len(config["tracks"]) > 0):
            raise ValueError(
                f"Error: There seem to be no tracks configured for assembly number {assembly_counter+1} in the config.yml. "
                "In order to configure a defaultSession, there need to be at least one track. Exiting."
            )

    species_abbreviation = species_name_variants["species_abbreviation"]
    species_slug = species_name_variants["species_slug"]
    assembly_file_name = Path(config["assembly"]["url"]).name
    assembly_file_path = (
        Path(__file__).parent.parent.parent / "data" / species_slug / assembly_file_name.replace(".fasta", ".fna")
    )

    if os.path.exists(assembly_file_path):
        # The "get" method returns None if the key is not found
        default_scaffold = config["assembly"].get("defaultScaffold")
        default_scaffold, sequence_length = get_fasta_header_and_sequence_length(assembly_file_path, default_scaffold)
    else:
        print(
            f"Assembly file {assembly_file_path} does not exist in ./data/{species_slug}/. If the assembly url has been configured, it can be downloaded by running the makefile."
        )
    views = [
        {
            "id": f"{species_abbreviation}_default_session_view_{assembly_counter}",
            "minimized": False,
            "type": "LinearGenomeView",
            "trackLabels": "offset",
            "offsetPx": 0,
            "bpPerPx": 50,
            "displayedRegions": [
                {
                    "refName": default_scaffold if default_scaffold else "[SCAFFOLD_HEADER]",
                    "start": 0,
                    "end": sequence_length if sequence_length else 100000,
                    "reversed": False,
                    "assemblyName": config["assembly"]["name"],
                }
            ],
            "tracks": [],
        }
    ]

    if "views" in data["defaultSession"]:
        data["defaultSession"]["views"].extend(views)
    else:
        data["defaultSession"]["views"] = views

    if protein_coding_gene_file_name:
        protein_coding_genes_track = [
            {
                "id": f"{species_abbreviation}_default_protein_coding_genes_view_{assembly_counter}",
                "type": "FeatureTrack",
                "configuration": protein_coding_gene_file_name,
                "minimized": False,
                "displays": [
                    {
                        "id": f"{species_abbreviation}_default_protein_coding_genes_view_{assembly_counter}_display",
                        "type": "LinearBasicDisplay",
                        "heightPreConfig": 150,
                        "configuration": f"{protein_coding_gene_file_name}-LinearBasicDisplay",
                    }
                ],
            }
        ]
        data["defaultSession"]["views"][assembly_counter]["tracks"].extend(protein_coding_genes_track)

    return data


def populate_values_from_optional_tracks(config, data, species_abbreviation, assembly_counter):
    """
    Subfunction that handles the defaultSession JSON object with tracks that have the defaultSession flag set to true. It does this by
    calling on a nested subfunction named add_defaultSession_true_tracks().

    It also supports tracks that are set to be treated as GWAS tracks. At the time this script was written, the Genome Portal
    makefile did not support adding GWAS tracks to config.json via the JBrowse CLI tools. Thus, such tracks are handled by the nested
    subfunction add_gwas_true_tracks()
    """

    def add_defaultSession_true_tracks(track, data, species_abbreviation, assembly_counter, gwas_track_id):
        track_outer_id = (
            f"{species_abbreviation}_default_{track['name'].replace(' ', '_').replace('\'', '').replace(',', '')}"
        )
        track_file_name = get_track_file_name(track)
        track_type = "LinearBasicDisplay"
        track_config = track_file_name
        display_config = f"{track_file_name}-LinearBasicDisplay"

        # For the case when a track is true for both the defaultSession and GWAS keys:
        if "GWAS" in track and track["GWAS"]:
            track_type = "LinearManhattanDisplay"
            track_config = gwas_track_id
            display_config = f"{gwas_track_id}_display"

        track_color = track.get("color", None)

        new_track = {
            "id": track_outer_id,
            "type": "FeatureTrack",
            "configuration": track_config,
            "minimized": False,
            "displays": [
                {
                    "id": f"{track_outer_id}_display",
                    "type": track_type,
                    "heightPreConfig": 150,
                    "configuration": display_config,
                }
            ],
        }

        if track_color:
            new_track["displays"][0]["color"] = track_color

        data["defaultSession"]["views"][assembly_counter]["tracks"].append(new_track)

        return data

    def add_gwas_true_tracks(track, data, species_abbreviation, assembly_name, gwas_track_id):
        # This sub-subfunction handles adding of GWAS tracks to config.json (not to the defaultSession object),
        # since the makefile currently does not support the extra configuration needed for GWAS tracks.
        if "scoreColumnGWAS" not in track:
            raise ValueError(
                f"Error: Track '{track['name']}' is configured to be treated as a GWAS track but is missing 'scoreColumnGWAS' in the config.yml. "
                "Please update this and re-run the script."
            )
        adapter_scoreColumn = track["scoreColumnGWAS"]

        def get_base_extension(file_name):
            base_name = os.path.splitext(file_name)[0] if file_name.endswith((".gz", ".zip")) else file_name
            return os.path.splitext(base_name)[1].lstrip(".")

        base_extension = get_base_extension(track["fileName"])

        # Currently, this only support BED(-like) GWAS tracks. Eventually we need to support more file types here as we encounter them.
        if base_extension == "bed":
            adapter_type = "BedTabixAdapter"
            bed_gz_location = track["fileName"]
            if bed_gz_location.endswith((".gz", ".zip")):
                bed_gz_location = bed_gz_location.replace(".gz", ".bgz").replace(".zip", ".bgz")
            if bed_gz_location.endswith(".bed"):
                # handles the case when the file stated in config.yml is an uncompressed .bed file
                bed_gz_location += ".bgz"
            index_location = f"{bed_gz_location}.csi"

        # The category value is hardcoded for now, but could be added to the config.yml in the future
        # The benefit of having definied a category is that it ensures that the GWAS tracks become sorted
        # below the protein-codon genes in the track selector.
        new_GWAS_track = {
            "type": "FeatureTrack",
            "trackId": gwas_track_id,
            "name": track["name"],
            "assemblyNames": [assembly_name],
            "category": ["GWAS"],
            "adapter": {
                "type": adapter_type,
                "scoreColumn": adapter_scoreColumn,
                "bedGzLocation": {"uri": bed_gz_location},
                "index": {"location": {"uri": index_location}, "indexType": "CSI"},
            },
            "displays": [{"displayId": f"{gwas_track_id}_display", "type": "LinearManhattanDisplay"}],
        }

        if "tracks" not in data:
            data["tracks"] = []
        data["tracks"].append(new_GWAS_track)

        return data

    plugin_added = False
    assembly_name = config.get("assembly", {}).get("name", "")

    has_at_least_one_default_session_flag = any(
        "defaultSession" in track and track["defaultSession"] for track in config.get("tracks", [])
    )

    has_protein_coding_genes_track_in_dict = any(
        (track_id := track.get("id")) and "protein_coding_genes" in track_id
        for track in data["defaultSession"]["views"][assembly_counter]["tracks"]
    )

    if has_at_least_one_default_session_flag or has_protein_coding_genes_track_in_dict:
        for track in config["tracks"]:
            gwas_track_id = None
            # First, check if there are any GWAS tracks that need to be handled. They are currently not
            # configured by the makefile, but instead are added to config.json by the if statement below.
            if "GWAS" in track and track["GWAS"]:
                if not plugin_added:
                    plugin_call = {
                        "name": "GWAS",
                        "url": "https://unpkg.com/jbrowse-plugin-gwas/dist/jbrowse-plugin-gwas.umd.production.min.js",
                    }
                    if "plugins" not in data:
                        data["plugins"] = []
                    data["plugins"].append(plugin_call)
                    plugin_added = True
                gwas_track_id = (
                    f"{species_abbreviation}_gwas_{track['name'].replace(' ', '_').replace('\'', '').replace(',', '')}"
                )
                data = add_gwas_true_tracks(track, data, species_abbreviation, assembly_name, gwas_track_id)
            # Secondly, check if there are any tracks that are set to defaultSession: true. If so, add them to the defaultSession JSON object.
            if "defaultSession" in track and track["defaultSession"]:
                # Ensure protein-coding genes are not added to the default session again if the user has happened to set it with defaultSession: true in the config.yml
                if track["name"].lower() in ["protein coding genes", "protein-coding genes"]:
                    continue
                data = add_defaultSession_true_tracks(
                    track, data, species_abbreviation, assembly_counter, gwas_track_id
                )
    else:
        if not has_protein_coding_genes_track_in_dict:
            raise ValueError(
                f"Error: There seem to be no tracks set with the defaultSession: true flag for assembly number {assembly_counter+1} in the config.yml. "
                "In order to configure a defaultSession, there need to be at least one track set to defaultSession: true "
                "(protein-coding genes tracks are treated as defaultSession: true by default). Exiting."
            )

    return data
