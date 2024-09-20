#! /bin/bash

### Description ###
# This is a wrapper script that calls on quast and agat to calculate statistics for a given genome assembly and annotation file.
# It then populates a yaml template with the relevant statistics needed for deplyment on the genome portal webpage. A slightly different
# phrasing is used between the table headers in the genome portal yaml and the quast and agat reports, and one purpose of the script
# is the automate the translation between these. It should also be noted that this script does not capture BUSCO statistics, and thus
# there will always be one entry in the yaml file that is not populated. The user will need to manually fill in this information, for
# instance by citing the related publication or by talking to the person who generated the assembly file. Users are also encouraged to
# cross-check the quast and agat logs with the generated yaml file to ensure that the information transfer is correct.
# The intended use-case is that the assembly and annotation files should come from the same species; the quast and agat analyses are
# is not affected by the presence of the other file, but the yaml file is dependent on both, and thus meaningful results will only be
# obtained when the input files come from the same species. However, this is up to user discretion since there are no checks in place
# to enforce this.
#

### Dependencies ###
# quast     - used for calculating assembly statistics
# AGAT      - used for calculating annotation statistics; https://github.com/NBISweden/AGAT/
# yq        - used for reading and writing the species_stats.yml file; https://mikefarah.gitbook.io/yq
#

### Usage ###
#Usage: generate_assembly_and_annotation_statistics.sh [--fasta genome_assembly.fasta] [--gff annotation.gff] [--force]
#    Options:
#    --fasta   Specify the genome assembly FASTA file. Supports uncompressed, gzipped, and bgzipped files. (Mandatory)
#    --gff     Specify the annotation GFF file. Supports uncompressed, gzipped, and bgzipped files. (Mandatory)
#    --force   Allow overwriting of existing output directory for the AGAT log. (Optional)
#    --help    Display this help message.
#
#    Example:
#    bash generate_assembly_and_annotation_statistics.sh --fasta /path/to/assembly.fasta --gff /path/to/annotation.gff
#

### Output ###
# - a quast log for the genome assembly
# - an agat log for the annotation file
# - a yaml file populated with the relevant statistics for the genome portal website
#
### This script was developed and tested with: ###
# GNU bash, version 5.2.26(1)-release (aarch64-apple-darwin23.2.0)
# quast v5.2.0
# AGAT v1.4.0
# yq 4.43.1
#

main() {
    init_variables_and_parse_arguments "$@"
    run_quast
    run_agat_func_stats
    populate_yaml_template
}

init_variables_and_parse_arguments() {
    # Parse arguments
    while [[ "$#" -gt 0 ]]; do
        case $1 in
            --fasta) fasta="$2"; shift ;;
            --gff) gff="$2"; shift ;;
            --force) force=true ;;
            --help) echo "$help_message"; exit 0 ;;
            *) echo "Unknown parameter passed: $1"; exit 1 ;;
        esac
        shift
    done

    help_message="Usage: $0 [--fasta genome_assembly.fasta] [--gff annotation.gff] [--force]
    Options:
    --fasta   Specify the genome assembly FASTA file. Supports uncompressed, gzipped, and bgzipped files. (Mandatory)
    --gff     Specify the annotation GFF file. Supports uncompressed, gzipped, and bgzipped files. (Mandatory)
    --force   Allow overwriting of existing output directory for the AGAT log. (Optional)
    --help    Display this help message.

    Example:
    bash generate_assembly_and_annotation_statistics.sh --fasta /path/to/assembly.fasta --gff /path/to/annotation.gff
    "

    # Check if required arguments are provided
    if [[ -z "$fasta" || -z "$gff" ]]; then
        echo "$help_message"
        echo "Error: --fasta and --gff arguments are required."
        exit 1
    fi

    # Create output paths
    quast_output_dir="./logs/quast/$(basename "$fasta" .fna)"
    agat_output_dir="./logs/agat/$(basename "${gff%%.gff*}")"
}

run_quast() {
    echo -e "\n- Running quast..."
    quast --split-scaffolds "$fasta" --min-contig 0 --no-plots --no-html --output-dir "$quast_output_dir"
    echo -e "\nQuast log saved to: $quast_output_dir/report.txt"
}

run_agat_func_stats() {
    # AGAT requires the GFF file to be uncompressed. Check if the file is compressed and decompress it if necessary.
    if [[ "$gff" == *.gz || "$gff" == *.bgz ]]; then
        echo -e "\n- The GFF file seem to be compressed. Decompressing..."
        temp_gff="$(mktemp "temp/$(basename "${gff%.gz}" .bgz)..XXXXXXX")"
        gunzip -c "$gff" > "$temp_gff"
        gff="$temp_gff"
    fi

    # Setup output directory
    echo -e "\n- Running AGAT functional statistics..."

    # Check if --force is set and delete the output directory if it exists
    if [[ "$force" == true && -d "$agat_output_dir" ]]; then
        echo -e "\n- Deleting existing output directory due to --force flag..."
        rm -rf "$agat_output_dir"
    fi

    # Run AGAT functional statistics
    agat_sp_functional_statistics.pl --gff "$gff" --output "$agat_output_dir"

    echo -e "\nAGAT log saved to: $agat_output_dir/stat_features.txt"

    # Clean up the temp file
    if [[ -n "$temp_gff" ]]; then
        rm "$temp_gff"
    fi
}

extract_quast_data() {
    # Subfunction that handles the extraction of data from quast reports with two or three columns
    local query="$1"
    local file="$2"
    local is_scaffold="$3"
    local columns
    columns=$(awk -F'\t' '{print NF; exit}' "$file")

    if [[ "$columns" -eq 2 ]]; then
        grep "$query" "$file" | awk -F'\t' '{print $(NF)}'
    elif [[ "$columns" -eq 3 ]]; then
        if [[ "$is_scaffold" == "true" ]]; then
            grep "$query" "$file" | awk -F'\t' '{print $(NF-1)}'
        else
            grep "$query" "$file" | awk -F'\t' '{print $(NF)}'
        fi
    fi
}

convert_bp_to_mbp() {
    # Subfunction that convert base pairs to mega base pairs
    local value="$1"
    echo "$value" | awk '{printf "%.2f", $1 / 1000000}'
}

populate_yaml_template() {
    echo -e "\n- Populating YAML template..."
    git_root=$(git rev-parse --show-toplevel)
    template_path="$git_root/scripts/templates/species_stats.yml"
    output_path="temp/species_stats_$(basename "$fasta" .fna).yml"

    # Extract relevant information from the quast report
    total_length=$(extract_quast_data "Total length (>= 0 bp)" "$quast_output_dir/report.tsv" "false")
    gc_content=$(extract_quast_data "GC (%)" "$quast_output_dir/report.tsv" "false")
    total_contigs=$(extract_quast_data "contigs (>= 0 bp)" "$quast_output_dir/report.tsv" "false")
    contig_N50=$(extract_quast_data "N50" "$quast_output_dir/report.tsv" "false")
    contig_L50=$(extract_quast_data "L50" "$quast_output_dir/report.tsv" "false")
    contig_N90=$(extract_quast_data "N90" "$quast_output_dir/report.tsv" "false")
    contig_L90=$(extract_quast_data "L90" "$quast_output_dir/report.tsv" "false")
    total_scaffolds=$(extract_quast_data "contigs (>= 0 bp)" "$quast_output_dir/report.tsv" "true")
    scaffold_N50=$(extract_quast_data "N50" "$quast_output_dir/report.tsv" "true")
    scaffold_L50=$(extract_quast_data "L50" "$quast_output_dir/report.tsv" "true")
    scaffold_N90=$(extract_quast_data "N90" "$quast_output_dir/report.tsv" "true")
    scaffold_L90=$(extract_quast_data "L90" "$quast_output_dir/report.tsv" "true")
    scaffold_above10k=$(extract_quast_data "contigs (>= 10000 bp)" "$quast_output_dir/report.tsv" "true")

    # Extract relevant information from the AGAT report. Allow for alternative phrasings in the AGAT report.
    total_genes=$(grep "Number of gene " "$agat_output_dir/stat_features.txt" | awk '{print $(NF)}')
    total_transcripts=$(grep "Number of mrna " "$agat_output_dir/stat_features.txt" | awk '{print $(NF)}')
    if [ -z "$total_transcripts" ]; then
        total_transcripts=$(grep "Number of transcript" "$agat_output_dir/stat_features.txt" | awk '{print $(NF)}')
    fi
    avg_exons_per_transcript=$(grep "mean exons per mrna" "$agat_output_dir/stat_features.txt" | awk '{print $(NF)}')
    if [ -z "$avg_exons_per_transcript" ]; then
        avg_exons_per_transcript=$(grep "mean exons per transcript" "$agat_output_dir/stat_features.txt" | awk '{print $(NF)}')
    fi
    avg_gene_length=$(grep "mean gene length (bp)" "$agat_output_dir/stat_features.txt" | awk '{print $(NF)}')
    avg_transcript_length=$(grep "mean mrna length (bp)" "$agat_output_dir/stat_features.txt" | awk '{print $(NF)}')
    if [ -z "$avg_transcript_length" ]; then
        avg_transcript_length=$(grep "mean transcript length (bp)" "$agat_output_dir/stat_features.txt" | awk '{print $(NF)}')
    fi
    avg_exon_length=$(grep "mean exon length (bp)" "$agat_output_dir/stat_features.txt" | awk '{print $(NF)}')
    avg_intron_length=$(grep "mean intron length (bp)" "$agat_output_dir/stat_features.txt" | awk '{print $(NF)}')
    if [ -z "$avg_intron_length" ]; then
        avg_intron_length=$(grep "mean intron in cds length (bp)" "$agat_output_dir/stat_features.txt" | awk '{print $(NF)}')
    fi

    # Make an array of variable names. Loop through the array and format the variables.
    # Use indirect expansion to get values. Export variables to make them available for yq.
    bp_variables=(total_length contig_N50 contig_N90 scaffold_N50 scaffold_N90)
    for var in "${bp_variables[@]}"; do
        value=${!var}
        mbp_value=$(convert_bp_to_mbp "$value")
        export "${var}"="$mbp_value"
    done


    #Commented out the below code since, since we decided not to use thousands separators in the yaml file.
    #
    # # Function to format numbers with commas
    # format_number() {
    #     echo "$1" | awk '{printf "%\047d\n", $1}'
    # }

    # # Make an array of variable names. Loop through the array and format the variables.
    # # Only format numbers that do no have decimals
    # variables=(total_length gc_content total_contigs contig_N50 contig_L50 contig_N90 contig_L90 \
    #             total_scaffolds scaffold_N50 scaffold_L50 scaffold_N90 scaffold_L90 scaffold_above10k \
    #             total_genes total_transcripts avg_exons_per_transcript avg_gene_length avg_transcript_length \
    #             avg_exon_length avg_intron_length)
    # for var in "${variables[@]}"; do
    #     value=${!var}
    #     if [[ $value != *.* ]]; then
    #         formatted_value=$(format_number "$value")
    #         export "$var"="$formatted_value"
    #     else
    #         export "$var"="$value"
    #     fi
    # done

    # The below line is technically not needed since the loops already export variables for use with yq.
    # But having the line complies with style suggestions from ShellCheck, and thus it is kept.
    export total_length gc_content total_contigs contig_N50 contig_L50 contig_N90 contig_L90 \
        total_scaffolds scaffold_N50 scaffold_L50 scaffold_N90 scaffold_L90 scaffold_above10k \
        total_genes total_transcripts avg_exons_per_transcript avg_gene_length avg_transcript_length \
        avg_exon_length avg_intron_length

    # Populate the YAML template with values from the quast and agat reports
    yq eval '
    (.assembly[] | select(has("Assembly length (Mbp)")) | .["Assembly length (Mbp)"]) = strenv(total_length) |
    (.assembly[] | select(has("GC %")) | .["GC %"]) = strenv(gc_content) |
    (.assembly[] | select(has("Contig #")) | .["Contig #"]) = strenv(total_contigs) |
    (.assembly[] | select(has("Contig N50 (Mbp)")) | .["Contig N50 (Mbp)"]) = strenv(contig_N50) |
    (.assembly[] | select(has("Contig L50")) | .["Contig L50"]) = strenv(contig_L50) |
    (.assembly[] | select(has("Contig N90 (Mbp)")) | .["Contig N90 (Mbp)"]) = strenv(contig_N90) |
    (.assembly[] | select(has("Contig L90")) | .["Contig L90"]) = strenv(contig_L90) |
    (.assembly[] | select(has("Scaffold #")) | .["Scaffold #"]) = strenv(total_scaffolds) |
    (.assembly[] | select(has("Scaffold N50 (Mbp)")) | .["Scaffold N50 (Mbp)"]) = strenv(scaffold_N50) |
    (.assembly[] | select(has("Scaffold L50")) | .["Scaffold L50"]) = strenv(scaffold_L50) |
    (.assembly[] | select(has("Scaffold N90 (Mbp)")) | .["Scaffold N90 (Mbp)"]) = strenv(scaffold_N90) |
    (.assembly[] | select(has("Scaffold L90")) | .["Scaffold L90"]) = strenv(scaffold_L90) |
    (.assembly[] | select(has("Scaffolds >= 10 kb")) | .["Scaffolds >= 10 kb"]) = strenv(scaffold_above10k) |
    (.annotation[] | select(has("Gene #")) | .["Gene #"]) = strenv(total_genes) |
    (.annotation[] | select(has("Transcript #")) | .["Transcript #"]) = strenv(total_transcripts) |
    (.annotation[] | select(has("Avg exons per transcript")) | .["Avg exons per transcript"]) = strenv(avg_exons_per_transcript) |
    (.annotation[] | select(has("Avg gene length (bp)")) | .["Avg gene length (bp)"]) = strenv(avg_gene_length) |
    (.annotation[] | select(has("Avg transcript length (bp)")) | .["Avg transcript length (bp)"]) = strenv(avg_transcript_length) |
    (.annotation[] | select(has("Avg exon length (bp)")) | .["Avg exon length (bp)"]) = strenv(avg_exon_length) |
    (.annotation[] | select(has("Avg intron length (bp)")) | .["Avg intron length (bp)"]) = strenv(avg_intron_length)
    ' "$template_path" > "$output_path.tmp" && mv "$output_path.tmp" "$output_path"

    echo "Relevant statistics from the Quast and AGAT reports have been saved to: $output_path"
    echo -e "\nPlease review the file and, if satisfied, copy the content to $git_root/hugo/data[SPECIES_NAME]/species_stats.yml \nfor deployment on the genome portal website."
}

set -e
main "$@"; exit