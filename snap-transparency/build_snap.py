#!/usr/bin/env python3
"""Build snap-transparency.json from Snap's per-period transparency CSVs.

Snap publishes its Transparency Report data as a per-reporting-period CSV
(linked from each values.snap.com/privacy/transparency-<period> page, hosted on
Contentful). The CSV is already **tidy-long** — one row per measured value:

  period, section, category, sub_category_1, sub_category_2, metric, value

covering T&S enforcements, ads moderation, appeals, CSEA, DMCA / trademark
notices, governmental content & account removal requests, information requests
(incl. US national-security), bilateral data-access requests, and a regional /
country overview. We pass that shape straight through to:

  { source, coverage, columns: [...], rows: [[period, section, category,
    sub_category_1, sub_category_2, metric, value], ...] }

`value` is parsed to a number (counts + a few medians); the handful of
non-numeric/blank cells are dropped. Pure stdlib; deterministic from the
archived raw/ CSVs (rows sorted). `--download` refreshes raw/ from the curated
per-period URLs.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import urllib.request

SOURCE_URL = "https://values.snap.com/privacy/transparency"
HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, "raw")
OUT_JSON = os.path.join(HERE, "snap-transparency.json")

COLUMNS = ["period", "section", "category", "sub_category_1", "sub_category_2",
           "metric", "value"]

# Curated period -> (raw filename, Contentful CSV URL). Each per-period
# values.snap.com page embeds its own CSV asset link; add new periods here as
# Snap publishes them (the tidy schema is stable across the current periods).
SOURCES = {
    "2024-H1": ("Snap_Transparency_Report_H1-2024.csv",
                "https://assets.ctfassets.net/kw9k15zxztrs/1lHFTspWwHmVCAKT236Oo1/"
                "8105fc04c43056397fdbf240e07fa92e/Snap_Transparency_Report_H1-2024.csv"),
    "2024-H2": ("Snap_Transparency_Report_H2-2024.csv",
                "https://assets.ctfassets.net/kw9k15zxztrs/59JIr8caki5HjwkGRXXY2u/"
                "9a009d4ee87d0217cc2e1bc8421a3f5b/Snap_Transparency_Report_H2-2024.csv"),
}


def _num(v):
    s = (v or "").strip().replace(",", "")
    if not s:
        return None
    try:
        f = float(s)
    except ValueError:
        return None
    if not math.isfinite(f):  # drop NaN / +-inf ("nan"/"inf" parse as float)
        return None
    return int(f) if f.is_integer() else f


def build(raw_dir: str, source_url: str = SOURCE_URL) -> dict:
    rows = []
    periods = []
    for period, (fname, _url) in SOURCES.items():
        path = os.path.join(raw_dir, fname)
        if not os.path.isfile(path):
            raise SystemExit(f"missing expected CSV: {path}")
        with open(path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != COLUMNS:
                raise SystemExit(f"{fname}: unexpected header {reader.fieldnames}; "
                                 f"expected {COLUMNS}")
            for r in reader:
                value = _num(r["value"])
                if value is None:
                    continue  # blank / non-numeric cell — nothing to record
                # A short row leaves later columns as None (DictReader restval);
                # coerce to "" before stripping so malformed rows don't crash.
                rows.append([(r["period"] or "").strip(), (r["section"] or "").strip(),
                             (r["category"] or "").strip(), (r["sub_category_1"] or "").strip(),
                             (r["sub_category_2"] or "").strip(), (r["metric"] or "").strip(),
                             value])
        periods.append(period)
    rows.sort(key=lambda x: (x[0], x[1], x[2], x[3], x[4], x[5]))
    return {
        "source": source_url,
        "coverage": max(periods) if periods else None,
        "columns": COLUMNS,
        "rows": rows,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", default=RAW_DIR, help="Dir of archived Snap CSVs")
    ap.add_argument("--out", default=OUT_JSON, help="Output dataset JSON path")
    ap.add_argument("--download", action="store_true",
                    help="Refresh raw/ from the curated per-period CSV URLs first")
    args = ap.parse_args()
    if args.download:
        os.makedirs(args.raw, exist_ok=True)
        for _period, (fname, url) in SOURCES.items():
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as resp, \
                    open(os.path.join(args.raw, fname), "wb") as f:
                f.write(resp.read())
        print(f"downloaded {len(SOURCES)} CSVs -> {args.raw}")
    data = build(args.raw)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {args.out}: {len(data['rows'])} rows across {len(SOURCES)} periods "
          f"(coverage {data['coverage']})")


if __name__ == "__main__":
    main()
