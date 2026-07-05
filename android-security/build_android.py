#!/usr/bin/env python3
"""Build android-security.json from Google's Android ecosystem security report.

Google's Transparency Report publishes **Android ecosystem security** figures —
the rate of **Potentially Harmful Applications (PHA)** on devices and in Google
Play — at:

  https://transparencyreport.google.com/android-security/overview

The export (``google-android-security.zip``) is five CSVs, each a different
cut of the same PHA-rate measure:

  - ``percentage-of-devices-with-pha.csv``              (12-mo rolling, by market type)
  - ``percentage-of-devices-with-pha-by-android-version.csv`` (quarterly, by OS version)
  - ``percentage-of-pha-installs.csv``                  (12-mo rolling, by install source)
  - ``percentage-of-pha-installs-by-top-countries.csv`` (12-mo rolling, by country)
  - ``percentage-of-pha-installs-by-categories.csv``    (quarterly, by PHA category)

This isn't a government-request stream like the rest of the pipeline — it's a
security-telemetry dataset — but it's the same tidy-long shape, so it slots in
as one queryable table.

Tidy-long output — one row per measured value:

  section, period, category, metric, unit, value

- **section** — which cut (``devices_with_pha`` / ``devices_by_version`` /
  ``installs`` / ``installs_by_country`` / ``installs_by_category``).
- **period** — the reporting date as ``YYYY-MM-DD``: the *12-month rolling end
  date* for the rolling cuts, the *quarter end date* for the quarterly cuts (its
  quarter start is derivable; kept as the end date so every section shares one
  sortable column).
- **category** — the row dimension kept verbatim: a market type
  (``All Devices`` / ``Enterprise devices``), an Android version (``KitKat`` …
  ``15``), an install source (``Google Play``), a country ISO-2 code, or a PHA
  category (``Backdoor``, ``Riskware``, …).
- **metric** — ``pha_rate`` for every cut; the by-categories cut *also* carries
  ``category_share`` (each PHA category's share of PHA installs that quarter).
- **unit** — ``rate`` (a **fraction of 1**, Google's PHA rate — never SUM) or
  ``percent`` (the by-categories ``category_share``, which sums to ~100 across
  categories per quarter).
- **value** — the reported figure (``REAL``).

Deterministic: builds purely from the archived raw/ CSVs (rows sorted); no
wall-clock. ``--download`` refreshes raw/ from the current export ZIP. Pure
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
OUT_JSON = os.path.join(HERE, "android-security.json")

OVERVIEW_URL = "https://transparencyreport.google.com/android-security/overview"
DOWNLOAD_URL = "https://storage.googleapis.com/transparencyreport/google-android-security.zip"

COLUMNS = ["section", "period", "category", "metric", "unit", "value"]

# Each raw CSV -> (section slug, expected header, a row-parser producing
# [category, period, [(metric, unit, value), ...]] tuples). Parsers validate the
# header (fail loud on drift) and normalise every cut into the shared shape.
#
# The PHA rate is a fraction of 1 (unit "rate"); the by-categories "Percentage"
# column is a share of PHA installs across categories (unit "percent").


def _rate(v: str) -> float:
    return float(v)


def _sections():
    return {
        "percentage-of-devices-with-pha.csv": (
            "devices_with_pha",
            ["12-month Rolling End Date", "Market Type", "PHA Rate"],
            lambda r: (r["Market Type"], r["12-month Rolling End Date"],
                       [("pha_rate", "rate", _rate(r["PHA Rate"]))]),
        ),
        "percentage-of-devices-with-pha-by-android-version.csv": (
            "devices_by_version",
            ["Start Date", "End Date", "Android API Version", "PHA Rate"],
            lambda r: (r["Android API Version"], r["End Date"],
                       [("pha_rate", "rate", _rate(r["PHA Rate"]))]),
        ),
        "percentage-of-pha-installs.csv": (
            "installs",
            ["12-month Rolling End Date", "Source", "PHA Rate"],
            lambda r: (r["Source"], r["12-month Rolling End Date"],
                       [("pha_rate", "rate", _rate(r["PHA Rate"]))]),
        ),
        "percentage-of-pha-installs-by-top-countries.csv": (
            "installs_by_country",
            ["12-month Rolling End Date", "Region", "PHA Rate"],
            lambda r: (r["Region"], r["12-month Rolling End Date"],
                       [("pha_rate", "rate", _rate(r["PHA Rate"]))]),
        ),
        "percentage-of-pha-installs-by-categories.csv": (
            "installs_by_category",
            ["Start Date", "End Date", "Category", "Source", "PHA Rate", "Percentage"],
            lambda r: (r["Category"], r["End Date"],
                       [("pha_rate", "rate", _rate(r["PHA Rate"])),
                        ("category_share", "percent", _rate(r["Percentage"]))]),
        ),
    }


def _parse_csv(fname: str, section: str, header: list[str], parse, text: str) -> list[list]:
    reader = csv.reader(io.StringIO(text))
    got = next(reader)
    if got != header:
        raise SystemExit(f"unexpected header in {fname}:\n  got:      {got}\n"
                         f"  expected: {header}")
    idx = {c: i for i, c in enumerate(header)}
    out: list[list] = []
    for lineno, rec in enumerate(reader, start=2):
        if not any(cell.strip() for cell in rec):
            continue
        if len(rec) != len(header):
            raise SystemExit(f"{fname}:{lineno}: expected {len(header)} columns, "
                             f"got {len(rec)}")
        row = {c: rec[idx[c]].strip() for c in header}
        try:
            category, period, measures = parse(row)
        except ValueError as e:
            raise SystemExit(f"{fname}:{lineno}: bad numeric value ({e})")
        for metric, unit, value in measures:
            out.append([section, period, category, metric, unit, value])
    return out


def build(raw_dir: str) -> dict:
    rows: list[list] = []
    for fname, (section, header, parse) in _sections().items():
        path = os.path.join(raw_dir, fname)
        if not os.path.isfile(path):
            raise SystemExit(f"missing expected raw file: {path}")
        with open(path, encoding="utf-8-sig") as f:
            rows.extend(_parse_csv(fname, section, header, parse, f.read()))
    rows.sort(key=lambda r: (r[0], r[3], r[2], r[1]))
    periods = sorted({r[1] for r in rows})
    return {
        "source": OVERVIEW_URL,
        "coverage": f"{periods[0]}..{periods[-1]}",
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
    wanted = set(_sections())
    found = set()
    for name in zf.namelist():
        base = name.split("/")[-1]
        if base in wanted:
            data = zf.read(name)
            with open(os.path.join(raw_dir, base), "wb") as f:
                f.write(data)
            found.add(base)
            print(f"downloaded {base} ({len(data)} bytes)")
    missing = wanted - found
    if missing:
        raise SystemExit(f"export ZIP is missing expected CSVs: {sorted(missing)}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raw", default=RAW_DIR, help="Dir of the archived CSVs")
    ap.add_argument("--out", default=OUT_JSON, help="Output dataset JSON path")
    ap.add_argument("--download", action="store_true",
                    help="Refresh raw/ from the current export ZIP first")
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
    print(f"wrote {args.out}: {len(rows)} rows, "
          f"{len({r[0] for r in rows})} sections, "
          f"{len({r[1] for r in rows})} periods "
          f"(coverage {data['coverage']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
