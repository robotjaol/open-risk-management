"""Write research/paper_catalog.csv and datasets/catalog.csv. Run: python tools/render_catalogs.py"""

import csv
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
import build_modules  # noqa: E402
import refs  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def used_by():
    table = {}
    for spec in build_modules.all_specs():
        for key in spec["refs"]:
            table.setdefault(key, []).append(spec["module"])
    return table


def write_paper_catalog():
    usage = used_by()
    path = ROOT / "research" / "paper_catalog.csv"
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["key", "kind", "year", "title", "authors", "venue", "link", "verified",
                         "verified_on", "verification_source", "status", "used_by_modules", "contribution"])
        for key, record in refs.REFS.items():
            writer.writerow([
                key, record["kind"], record["year"] or "", record["title"], record["authors"],
                record["venue"], record["link"] or "", "yes" if record["verified"] else "no",
                refs.VERIFIED_ON if record["verified"] else "", record["source"], record["status"],
                ";".join(usage.get(key, [])), record["contribution"],
            ])
    return path


def write_dataset_catalog():
    path = ROOT / "datasets" / "catalog.csv"
    rows = []
    cards = []
    for folder in ["synthetic", "raw", "processed"]:
        cards += sorted((ROOT / "datasets" / folder).glob("*.yaml"))
    for card in cards:
        meta = yaml.safe_load(card.read_text())
        rows.append([meta["name"], meta["kind"], meta["file"], meta["rows"], len(meta["columns"]),
                     meta["license"], meta["sha256"], meta["title"], meta.get("source_url", "generated in this repository")])
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["name", "kind", "file", "rows", "columns", "license", "sha256", "title", "source"])
        writer.writerows(rows)
    return path


if __name__ == "__main__":
    print("wrote", write_paper_catalog())
    print("wrote", write_dataset_catalog())
