from pathlib import Path

import yaml
from stats_parsers import extract_template_metric_keys, parse_agat_report, parse_quast_report, render_stats_yaml


def test_parse_quast_report_handles_three_columns(tmp_path: Path) -> None:
    report = tmp_path / "report.tsv"
    report.write_text(
        "\n".join(
            [
                "Total length (>= 0 bp)\t1000000\t2000000",
                "GC (%)\t38.2\t39.1",
                "# contigs (>= 0 bp)\t11\t22",
                "N50\t123000\t234000",
                "L50\t4\t8",
                "N90\t10000\t20000",
                "L90\t10\t20",
                "# contigs (>= 10000 bp)\t5\t7",
            ]
        ),
        encoding="utf-8",
    )
    parsed = parse_quast_report(report)
    assert parsed["Assembly length (Mbp)"] == "1.00"
    assert parsed["Scaffold #"] == "11"
    assert parsed["Contig #"] == "22"
    assert parsed["Scaffold N50 (Mbp)"] == "0.12"


def test_parse_agat_report_supports_alternative_phrasings(tmp_path: Path) -> None:
    report = tmp_path / "stat_features.txt"
    report.write_text(
        "\n".join(
            [
                "Number of gene 123",
                "Number of transcript 456",
                "mean exons per transcript 7.3",
                "mean gene length (bp) 890",
                "mean transcript length (bp) 901",
                "mean exon length (bp) 45",
                "mean intron in cds length (bp) 67",
            ]
        ),
        encoding="utf-8",
    )
    parsed = parse_agat_report(report)
    assert parsed["Gene #"] == "123"
    assert parsed["Transcript #"] == "456"
    assert parsed["Avg exons per transcript"] == "7.3"
    assert parsed["Avg intron length (bp)"] == "67"


def test_render_stats_yaml_keeps_placeholders_for_missing_metrics(tmp_path: Path) -> None:
    template = tmp_path / "species_stats.yml"
    template.write_text(
        "\n".join(
            [
                "---",
                "assembly:",
                '  - "Assembly length (Mbp)": [EDIT]',
                "annotation:",
                '  - "Gene #": [EDIT]',
            ]
        ),
        encoding="utf-8",
    )
    output = tmp_path / "out.yml"
    unresolved = render_stats_yaml(
        template_path=template,
        output_path=output,
        values={
            "Assembly length (Mbp)": "12.34",
            "Gene #": None,
        },
    )
    with open(output, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    assert data["assembly"][0]["Assembly length (Mbp)"] == "12.34"
    assert data["annotation"][0]["Gene #"] == ["EDIT"]
    assert "Gene #" in unresolved


def test_extract_template_metric_keys_reads_assembly_and_annotation_sections(tmp_path: Path) -> None:
    template = tmp_path / "species_stats.yml"
    template.write_text(
        "\n".join(
            [
                "---",
                "assembly:",
                '  - "Assembly length (Mbp)": [EDIT]',
                '  - "GC %": [EDIT]',
                "annotation:",
                '  - "Gene #": [EDIT]',
            ]
        ),
        encoding="utf-8",
    )

    keys = extract_template_metric_keys(template_path=template)
    assert keys == ["Assembly length (Mbp)", "GC %", "Gene #"]
