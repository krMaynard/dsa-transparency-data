#!/usr/bin/env python3
"""
Incrementally append new services to an existing vlop-dsa.json WITHOUT
rebuilding the services that are already present.

Why this exists (instead of just re-running convert.py):
The committed vlop-dsa.json predates this archive and was generated from an
older snapshot of some source CSVs (notably the Google services, where it is
also affected by a glob-ordering ambiguity in convert.find_table_file over the
`*_Ads.csv` variants). A full `convert.py` rebuild therefore changes existing
Google numbers in ways that cannot be validated here. To add the adult-content
VLOPs without disturbing the live data, this script reuses convert.py's exact
table parsers but seeds them from the existing JSON and only processes
SERVICE_DEFS entries that are not already present.

Usage: python3 append_platforms.py
Output: ../krMaynard.github.io/data/vlop-dsa.json (in place)
"""

import json
from datetime import date

import convert

OUT_FILE = convert.OUT_FILE


def main():
    with open(OUT_FILE) as f:
        data = json.load(f)

    # Seed convert.py's module-level accumulators from the existing JSON so that
    # intern() preserves every existing index and only appends new entries.
    convert.services = data["services"]
    convert.service_platforms = data["service_platforms"]
    convert.categories = data["categories"]
    convert.sections = data["sections"]
    convert.indicators = data["indicators"]
    convert.scopes = data["scopes"]
    convert.t3_rows = data["t3"]
    convert.t4_rows = data["t4"]
    convert.t5_rows = data["t5"]
    convert.t6_rows = data["t6"]
    convert.t7_rows = data["t7"]

    existing = set(convert.services)
    added = []
    for svc_def in convert.SERVICE_DEFS:
        name = svc_def["name"]
        if name in existing:
            continue
        if "dir" not in svc_def:
            print(f"  SKIP {name}: only directory-based reports are supported here")
            continue
        d = convert.REPORTS_DIR / svc_def["dir"]
        if not d.exists():
            print(f"  WARNING: missing {d}")
            continue
        print(f"Appending {name}...")
        idx = convert.intern(convert.services, name)
        if len(convert.service_platforms) <= idx:
            convert.service_platforms.append(svc_def["platform"])
        convert.process_service_from_dir(idx, d)
        added.append((name, svc_def["dir"]))

    # Backfill category labels for any category codes newly introduced by the
    # appended services, sourcing descriptions from their 2_categories_names.csv.
    labels = data["category_labels"]
    missing = [c for c in convert.categories if c not in labels]
    if missing:
        for _, dirname in added:
            path = convert.REPORTS_DIR / dirname / "2_categories_names.csv"
            if not path.exists():
                continue
            for row in convert.read_csv(path):
                code = (convert.get(row, "Category of illegal content / incompatible with the terms and conditions") or "").strip()
                desc = (convert.get(row, "Category description") or "").strip()
                if code in missing and desc and code not in labels:
                    labels[code] = desc
        still_missing = [c for c in convert.categories if c not in labels]
        if still_missing:
            print(f"  NOTE: {len(still_missing)} new categories have no label: {still_missing}")

    out = {
        "meta": {
            "period": data["meta"]["period"],
            "generated": date.today().isoformat(),
        },
        "services": convert.services,
        "service_platforms": convert.service_platforms,
        "categories": convert.categories,
        "category_labels": labels,
        "sections": convert.sections,
        "indicators": convert.indicators,
        "scopes": convert.scopes,
        "t3": convert.t3_rows,
        "t4": convert.t4_rows,
        "t5": convert.t5_rows,
        "t6": convert.t6_rows,
        "t7": convert.t7_rows,
    }

    with open(OUT_FILE, "w") as f:
        json.dump(out, f, separators=(",", ":"))

    print(f"\nAppended {len(added)} service(s): {[a[0] for a in added]}")
    print(f"Written to {OUT_FILE}")
    print(f"  services: {len(convert.services)}")
    print(f"  t3 rows: {len(convert.t3_rows)}  t4: {len(convert.t4_rows)}  "
          f"t5: {len(convert.t5_rows)}  t6: {len(convert.t6_rows)}  t7: {len(convert.t7_rows)}")


if __name__ == "__main__":
    main()
