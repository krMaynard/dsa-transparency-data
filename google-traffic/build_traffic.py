#!/usr/bin/env python3
"""Build google-traffic.json from Google's Traffic & Disruptions catalogue.

Google's Transparency Report tracked **disruptions to the availability of its
products** — government-ordered internet shutdowns, blocks and outages — at:

  https://transparencyreport.google.com/traffic/overview

The underlying catalogue is a single CSV in the archived transparency-report
export bucket (``archived-google-traffic.zip``): one row per observed
disruption of a Google product in a country, with the reporting-source
citation (news outlet + URL) that corroborates it. Google **froze** this
dataset — the last recorded disruption is late 2021 — so this is a historical
catalogue (2009-2021), not a live feed.

Unlike the other datasets in this pipeline this isn't a tidy-long metrics table
but a **flat catalogue** (like the report-locations / NY ToS catalogues): each
row is one disruption event, not a measured quantity to aggregate. Output is a
simple ``{source, coverage, columns, rows}`` snapshot — one row per event:

  country, iso2, product, start_date, end_date, year, source, source_url,
  title, excerpt, disruption_url

``iso2`` is Google's CLDR territory code; ``year`` is derived from
``start_date`` (``YYYY-MM-DD``, Pacific time, may be approximated) and is null
for the two rows Google published without a start date (only an end date).
``disruption_url`` is the deep link back into Google's interactive chart.

Deterministic: builds purely from the archived raw/ CSV (rows sorted); no
wall-clock. ``--download`` refreshes raw/ from the archived export ZIP. Pure
stdlib.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, "raw")
OUT_JSON = os.path.join(HERE, "google-traffic.json")

OVERVIEW_URL = "https://transparencyreport.google.com/traffic/overview"
DOWNLOAD_URL = "https://storage.googleapis.com/transparencyreport/archived-google-traffic.zip"
RAW_CSV = "traffic-disruptions.csv"

COLUMNS = [
    "country", "iso2", "product", "start_date", "end_date", "year",
    "source", "source_url", "title", "excerpt", "disruption_url",
]

# The archived export's own header cells -> our column names.
SRC_HEADER = [
    "Disruption URL", "CLDR Territory Code", "Region", "Product",
    "Start Date (Pacific Time; may be approximated)",
    "End Date (Pacific Time; may be approximated)",
    "Source", "Source URL", "Title", "Excerpt",
]


def _parse_csv(text: str) -> list[list]:
    reader = csv.reader(io.StringIO(text))
    header = next(reader)
    if header != SRC_HEADER:
        raise SystemExit(
            f"unexpected header in {RAW_CSV}:\n  got:      {header}\n"
            f"  expected: {SRC_HEADER}")
    rows: list[list] = []
    for lineno, rec in enumerate(reader, start=2):
        if not any(cell.strip() for cell in rec):
            continue
        if len(rec) != len(SRC_HEADER):
            raise SystemExit(f"{RAW_CSV}:{lineno}: expected {len(SRC_HEADER)} "
                             f"columns, got {len(rec)}")
        (disruption_url, iso2, country, product, start_date, end_date,
         source, source_url, title, excerpt) = (c.strip() for c in rec)
        year = start_date[:4] if len(start_date) >= 4 and start_date[:4].isdigit() else None
        rows.append([
            country, iso2, product, start_date or None, end_date or None,
            year, source or None, source_url or None, title or None,
            excerpt or None, disruption_url or None,
        ])
    return rows


def build(raw_dir: str) -> dict:
    path = os.path.join(raw_dir, RAW_CSV)
    if not os.path.isfile(path):
        raise SystemExit(f"missing expected raw file: {path}")
    with open(path, encoding="utf-8-sig") as f:
        rows = _parse_csv(f.read())
    # Sort deterministically: by start_date, then country, product (nulls last).
    rows.sort(key=lambda r: (r[3] is None, r[3] or "", r[0], r[2]))
    years = sorted({r[5] for r in rows if r[5]})
    coverage = f"{years[0]}..{years[-1]}" if years else ""
    return {
        "source": OVERVIEW_URL,
        "coverage": coverage,
        "columns": COLUMNS,
        "rows": rows,
    }


def _download(raw_dir: str) -> None:
    os.makedirs(raw_dir, exist_ok=True)
    req = urllib.request.Request(
        DOWNLOAD_URL, headers={"User-Agent": "dsa-transparency-data/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        blob = resp.read()
    zf = zipfile.ZipFile(io.BytesIO(blob))
    names = [n for n in zf.namelist()
             if n.endswith(".csv") and not n.startswith("__MACOSX")]
    if len(names) != 1:
        raise SystemExit(f"expected exactly one CSV in the ZIP, found {names}")
    csv_data = zf.read(names[0])
    with open(os.path.join(raw_dir, RAW_CSV), "wb") as f:
        f.write(csv_data)
    print(f"downloaded {RAW_CSV} ({len(csv_data)} bytes) from {DOWNLOAD_URL}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raw", default=RAW_DIR, help="Dir of the archived CSV")
    ap.add_argument("--out", default=OUT_JSON, help="Output dataset JSON path")
    ap.add_argument("--download", action="store_true",
                    help="Refresh raw/ from the archived export ZIP first")
    args = ap.parse_args()

    if args.download:
        _download(args.raw)
    data = build(args.raw)
    out_dir = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    rows = data["rows"]
    print(f"wrote {args.out}: {len(rows)} disruptions, "
          f"{len({r[0] for r in rows})} countries, "
          f"{len({r[2] for r in rows})} products "
          f"(coverage {data['coverage']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
