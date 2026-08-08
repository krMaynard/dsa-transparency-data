#!/usr/bin/env python3
"""Union the normalized California and New York ToS statistics."""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DST = os.path.join(HERE, "state_tos_stats.csv")
COLS = ["jurisdiction", "law", "company", "period", "category",
        "original_label", "geographic_scope", "content_format", "grain",
        "metric", "submetric", "value", "unit", "page", "source_file"]
CA_COMPANIES = {
    "discord": "discord-inc", "linkedin": "linkedin-corporation",
    "reddit": "reddit-inc", "roblox": "roblox-corporation",
    "snap": "snap-inc", "tiktok": "tiktok-inc",
}


def main():
    rows = []
    ca_path = os.path.join(ROOT, "ca-ab587", "ca_ab587_normalized.csv")
    with open(ca_path, encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append({
                "jurisdiction": "California", "law": "AB 587",
                "company": CA_COMPANIES[row["company"]], "period": row["period"],
                "category": row["ab587_category"],
                "original_label": row["original_label"],
                "geographic_scope": row["geographic_scope"],
                "content_format": row["content_format"], "grain": row["grain"],
                "metric": row["metric"], "submetric": row["submetric"],
                "value": row["value"], "unit": row["unit"],
                "page": row["page"], "source_file": row["source_file"],
            })
    ny_path = os.path.join(ROOT, "ny-tos-reports", "ny_tos_normalized.csv")
    with open(ny_path, encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append({
                "jurisdiction": "New York", "law": "GBS 1102 (S895B)",
                "company": row["company"], "period": row["period"],
                "category": row["shha_category"],
                "original_label": row["original_label"],
                "geographic_scope": "reported", "content_format": row["content_format"],
                "grain": row["grain"], "metric": row["metric"],
                "submetric": row["submetric"], "value": row["value"],
                "unit": row["unit"], "page": row["page"],
                "source_file": "2025-q3-" + row["company"] + ".pdf",
            })
    rows.sort(key=lambda row: tuple(row[col] for col in COLS))
    with open(DST, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} state ToS statistic cells -> {DST}")


if __name__ == "__main__":
    main()
