#!/usr/bin/env python3
"""
Add the per-row "surface" dimension to tables 6 & 7 of an existing vlop-dsa.json,
in place, without disturbing anything else.

Google publishes tables 6/7 as several disjoint sub-reports per service
(organic "Core", "Ads", and for Search a breakdown by action level). The old
pipeline kept only one file per table and silently dropped the rest. This
script:

  * appends a `surfaces` lookup (index 0 = "All" = no breakdown),
  * tags every existing t6/t7 row with surface 0,
  * and for each surfaced service (Google) replaces its t6/t7 rows with the
    full set parsed from every sub-report, each tagged with its surface.

Non-surfaced services and tables 3/4/5 are left byte-for-byte unchanged, so the
existing category/scope/service ordering (and every other number) is preserved.
A full `convert.py` rebuild would instead re-intern everything and reorder the
indices; this keeps the diff to exactly what changed.

Usage: python3 add_surfaces.py
"""

import json
import os
import sys
from datetime import date

import convert

OUT_FILE = convert.OUT_FILE


def main():
    if not OUT_FILE.exists():
        print(f"Error: {OUT_FILE} does not exist. Run convert.py first.", file=sys.stderr)
        sys.exit(1)

    with open(OUT_FILE) as f:
        data = json.load(f)

    if data["t6"] and len(data["t6"][0]) > 18:
        print("Already has a surface dimension; nothing to do.")
        return

    # Seed convert's accumulators from the existing JSON so intern() preserves
    # every existing index and only appends genuinely new categories/scopes.
    convert.services = data["services"]
    convert.service_platforms = data["service_platforms"]
    convert.categories = data["categories"]
    convert.sections = data["sections"]
    convert.indicators = data["indicators"]
    convert.scopes = data["scopes"]
    convert.surfaces = ["All"]
    ALL = convert.intern(convert.surfaces, "All")  # 0

    # Map service name -> (index, SERVICE_DEF) for surfaced, directory-based services.
    surfaced = {}
    for sd in convert.SERVICE_DEFS:
        if sd.get("surfaces") and "dir" in sd and sd["name"] in convert.services:
            surfaced[convert.services.index(sd["name"])] = sd

    def rebuild(table_key, table_n, reprocess):
        existing = data[table_key]
        out = []
        setattr(convert, f"t{table_n}_rows", out)
        # Reprocess surfaced services first (keeps the Google block at the front,
        # matching the original service-ordered layout).
        for idx in sorted(surfaced):
            d = convert.REPORTS_DIR / surfaced[idx]["dir"]
            for path, surface in convert.table_files(d, table_n, True):
                reprocess(idx, convert.read_csv(path), surface, out)
        # Carry over every non-surfaced row unchanged, tagged "All".
        for r in existing:
            if r[0] not in surfaced:
                out.append(r + [ALL])
        return out

    new_t6 = rebuild("t6", 6, lambda idx, rows, surface, out: convert.process_t5_t6(
        idx, rows, "Category of incompatibility with the provider's terms and conditions",
        out, surface=surface))
    new_t7 = rebuild("t7", 7, lambda idx, rows, surface, out: convert.process_t7(
        idx, rows, surface=surface))

    # Backfill labels for any categories newly introduced by the extra sub-reports.
    labels = data.get("category_labels", {})
    missing = [c for c in convert.categories if c not in labels]
    if missing:
        path = convert.REPORTS_DIR / "google/maps/2_categories_names.csv"
        if path.exists():
            try:
                for row in convert.read_csv(path):
                    code = (convert.get(row, "Category of illegal content / incompatible with the terms and conditions") or "").strip()
                    desc = (convert.get(row, "Category description") or "").strip()
                    if code in missing and desc and code not in labels:
                        labels[code] = desc
            except Exception as e:
                print(f"  WARNING: label backfill failed: {e}")

    out = {
        "meta": {"period": data["meta"]["period"], "generated": date.today().isoformat()},
        "services": convert.services,
        "service_platforms": convert.service_platforms,
        "categories": convert.categories,
        "category_labels": labels,
        "sections": convert.sections,
        "indicators": convert.indicators,
        "scopes": convert.scopes,
        "surfaces": convert.surfaces,
        "t3": data["t3"],
        "t4": data["t4"],
        "t5": data["t5"],
        "t6": new_t6,
        "t7": new_t7,
    }

    tmp = OUT_FILE.with_suffix(".tmp")
    try:
        with open(tmp, "w") as f:
            json.dump(out, f, separators=(",", ":"))
        os.replace(tmp, OUT_FILE)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise

    print(f"Surfaces: {convert.surfaces}")
    print(f"t6: {len(data['t6'])} -> {len(new_t6)} rows | t7: {len(data['t7'])} -> {len(new_t7)} rows")
    print(f"Written to {OUT_FILE}")


if __name__ == "__main__":
    main()
