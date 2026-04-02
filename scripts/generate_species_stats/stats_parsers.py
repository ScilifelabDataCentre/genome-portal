import re
from pathlib import Path

import yaml

QUAST_METRIC_QUERIES = [
    # (metric_key, query_substring, is_scaffold, needs_mbp)
    ("Assembly length (Mbp)", "Total length (>= 0 bp)", True, True),
    ("GC %", "GC (%)", False, False),
    ("Contig #", "contigs (>= 0 bp)", False, False),
    ("Contig N50 (Mbp)", "N50", False, True),
    ("Contig L50", "L50", False, False),
    ("Contig N90 (Mbp)", "N90", False, True),
    ("Contig L90", "L90", False, False),
    ("Scaffold #", "contigs (>= 0 bp)", True, False),
    ("Scaffold N50 (Mbp)", "N50", True, True),
    ("Scaffold L50", "L50", True, False),
    ("Scaffold N90 (Mbp)", "N90", True, True),
    ("Scaffold L90", "L90", True, False),
    ("Scaffolds >= 10 kb", "contigs (>= 10000 bp)", True, False),
]

AGAT_PATTERNS = {
    "Gene #": [r"Number of gene\s+"],
    "Transcript #": [r"Number of mrna\s+", r"Number of transcript"],
    "Avg exons per transcript": [r"mean exons per mrna", r"mean exons per transcript"],
    "Avg gene length (bp)": [r"mean gene length \(bp\)"],
    "Avg transcript length (bp)": [r"mean mrna length \(bp\)", r"mean transcript length \(bp\)"],
    "Avg exon length (bp)": [r"mean exon length \(bp\)"],
    "Avg intron length (bp)": [r"mean intron length \(bp\)", r"mean intron in cds length \(bp\)"],
}


def _to_mbp(value: str) -> str:
    """Convert a numeric string representing base pairs to a string representing megabase pairs with two decimal places."""
    try:
        return f"{float(value) / 1_000_000:.2f}"
    except ValueError:
        return value


def parse_quast_report(quast_report_path: Path) -> dict[str, str | None]:
    """Parse a Quast report file to extract relevant assembly statistics based on predefined queries."""
    if not quast_report_path.exists():
        raise FileNotFoundError(f"Quast report not found: {quast_report_path}")

    rows: list[list[str]] = []
    with open(quast_report_path, "r", encoding="utf-8") as handle:
        for line in handle:
            parts = line.rstrip("\n").split("\t")
            if parts:
                rows.append(parts)

    def extract(query: str, is_scaffold: bool) -> str | None:
        for row in rows:
            label = row[0].strip()
            # Match legacy shell script behavior that used `grep "$query"` (substring match),
            # which is needed for labels like "# contigs (>= 0 bp)".
            if query not in label:
                continue
            if len(row) == 2:
                return row[-1].strip()
            if len(row) >= 3:
                return row[-2].strip() if is_scaffold else row[-1].strip()
        return None

    stats: dict[str, str | None] = {}
    for metric_key, query, is_scaffold, needs_mbp in QUAST_METRIC_QUERIES:
        value = extract(query, is_scaffold)
        if value is not None and needs_mbp:
            value = _to_mbp(value)
        stats[metric_key] = value
    return stats


def parse_agat_report(agat_report_path: Path) -> dict[str, str | None]:
    """Parse an AGAT report file to extract relevant annotation statistics based on predefined patterns."""
    if not agat_report_path.exists():
        raise FileNotFoundError(f"AGAT report not found: {agat_report_path}")

    with open(agat_report_path, "r", encoding="utf-8") as handle:
        lines = handle.readlines()

    stats: dict[str, str | None] = {}
    for metric_key, patterns in AGAT_PATTERNS.items():
        value: str | None = None
        for line in lines:
            for pattern in patterns:
                if re.search(pattern, line, flags=re.IGNORECASE):
                    tokens = line.strip().split()
                    if tokens:
                        value = tokens[-1]
                    break
            if value is not None:
                break
        stats[metric_key] = value

    return stats


def render_stats_yaml(
    template_path: Path,
    output_path: Path,
    values: dict[str, str | None],
) -> list[str]:
    """Render a YAML report based on a template, filling in values and tracking any unresolved keys."""

    with open(template_path, "r", encoding="utf-8") as handle:
        template_data = yaml.safe_load(handle)

    def is_edit_placeholder(raw_value: object) -> bool:
        if raw_value == "[EDIT]":
            return True
        if isinstance(raw_value, list) and raw_value == ["EDIT"]:
            return True
        return False

    unresolved_placeholders: list[str] = []
    for section in ("assembly", "annotation"):
        for row in template_data.get(section, []):
            for key in row:
                if key not in values:
                    continue
                value = values[key]
                if value is None:
                    # Keep pre-filled template values (e.g. BUSCO from add_new_species)
                    # and only mark unresolved when the field still has an [EDIT] placeholder.
                    if is_edit_placeholder(row[key]):
                        unresolved_placeholders.append(key)
                else:
                    row[key] = str(value)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(template_data, handle, sort_keys=False, default_flow_style=False, explicit_start=True)

    return unresolved_placeholders


def extract_template_metric_keys(template_path: Path) -> list[str]:
    """Extract metric keys from assembly/annotation sections of species_stats template."""
    with open(template_path, "r", encoding="utf-8") as handle:
        template_data = yaml.safe_load(handle)

    keys: list[str] = []
    for section in ("assembly", "annotation"):
        for row in template_data.get(section, []):
            keys.extend(row.keys())
    return keys
