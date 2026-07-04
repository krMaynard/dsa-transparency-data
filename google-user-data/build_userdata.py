#!/usr/bin/env python3
"""Build google-user-data.json from Google's user-data-requests bulk export.

Google's Transparency Report publishes government **requests for user
information** as a bulk CSV zip (the same "DOWNLOAD REPORT DATA" flow as the
government content-removals dataset already ingested):

  https://storage.googleapis.com/transparencyreport/google-user-data-requests.zip

The zip carries several files, all archived verbatim in raw/:

  * google-global-user-data-requests.csv — period × country × legal process →
    requests, accounts, percentage disclosed. H2-2009 onward. The legal-process
    dimension evolves: 2009-H2..2012-H1 report an ``All`` aggregate only;
    2012-H2..2014-H1 report ``All`` **alongside** the per-process split (so a
    naive SUM over those periods double-counts — pin ``legal_process``);
    2014-H2 onward is split-only.
  * google-global-user-data-dlr-requests.csv — requests identifiable as issued
    through diplomatic procedures (e.g. MLAT), by country of origin ×
    assisting country.
  * google-enterprise-data-requests.csv — Enterprise Cloud (GCP / Google
    Workspace) customer requests, by country × product × legal process.
  * google-enterprise-data-dlr-requests.csv — the diplomatic slice of the
    enterprise requests.
  * google-usnationalsecurity-fisa-content-requests.csv /
    -fisa-non-content-requests.csv / -nsl-requests.csv — US national-security
    demands (FISA content / FISA non-content / National Security Letters),
    reportable only in **banded ranges** (e.g. 0–499 requests), per period.
  * google-usnationalsecurity-nsl-requests-released.csv — a per-letter log of
    NSLs released from nondisclosure (issue date × release date). Archived but
    **not** folded into the tidy table (it's a document log, not a time series).

All feed one **tidy-long** table — one row per measured value:

  dataset, period, country, iso2, product, legal_process, assisting_country,
  metric, unit, value_low, value_high

``dataset`` ∈ global / global_diplomatic / enterprise / enterprise_diplomatic /
us_fisa_content / us_fisa_non_content / us_nsl. ``unit`` is ``count`` or
``percent`` (percentage of requests where some data was disclosed — never SUM
it). Exact figures have ``value_low == value_high``; the US national-security
bands have ``value_low != value_high`` (non-additive). ``period`` is the
half-year the reporting window ends in (``2009-H2`` = period ending
2009-12-31). Percentages are 0 before 2010-H2 because Google did not report a
disclosure rate then — a "not reported" sentinel in the source file, kept as
filed.

Deterministic: builds purely from the archived raw/ CSVs (rows sorted); no
wall-clock. ``--download`` refreshes raw/ from the live zip. Pure stdlib.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import urllib.request
import zipfile

ZIP_URL = "https://storage.googleapis.com/transparencyreport/google-user-data-requests.zip"
HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, "raw")
OUT_JSON = os.path.join(HERE, "google-user-data.json")

COLUMNS = [
    "dataset", "period", "country", "iso2", "product", "legal_process",
    "assisting_country", "metric", "unit", "value_low", "value_high",
]

RAW_FILES = [
    "google-global-user-data-requests.csv",
    "google-global-user-data-dlr-requests.csv",
    "google-enterprise-data-requests.csv",
    "google-enterprise-data-dlr-requests.csv",
    "google-usnationalsecurity-fisa-content-requests.csv",
    "google-usnationalsecurity-fisa-non-content-requests.csv",
    "google-usnationalsecurity-nsl-requests.csv",
    "google-usnationalsecurity-nsl-requests-released.csv",
    "README.txt",
]


def _period(date_str: str) -> str:
    """'2009-12-31' -> '2009-H2'; '2010-06-30' -> '2010-H1'."""
    year, month, _ = date_str.split("-")
    half = "H1" if int(month) <= 6 else "H2"
    return f"{year}-{half}"


def _num(cell: str) -> int:
    cell = cell.strip().replace(",", "")
    if cell == "":
        raise ValueError("blank numeric cell")
    return int(cell)


def _blank(cell: str) -> bool:
    """A blank numeric cell means "not reported / not applicable" (e.g. no
    disclosure percentage for preservation requests, or the China
    local-subsidiary rows with no counts) — the row is skipped, never zeroed."""
    return cell.strip() == ""


def _read(name: str) -> list[dict[str, str]]:
    path = os.path.join(RAW_DIR, name)
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def download() -> None:
    os.makedirs(RAW_DIR, exist_ok=True)
    req = urllib.request.Request(ZIP_URL, headers={"User-Agent": "dsa-transparency-data/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        blob = resp.read()
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for info in z.infolist():
            base = os.path.basename(info.filename)
            if base in RAW_FILES:
                with open(os.path.join(RAW_DIR, base), "wb") as f:
                    f.write(z.read(info))
    print(f"downloaded {ZIP_URL} -> raw/ ({len(blob)} bytes)")


Row = tuple[str, str, str, str, str, str, str, str, str, int, int]


def _exact(dataset: str, period: str, country: str, iso2: str, product: str,
           process: str, assisting: str, metric: str, unit: str, value: int) -> Row:
    return (dataset, period, country, iso2, product, process, assisting,
            metric, unit, value, value)


def build() -> list[Row]:
    rows: list[Row] = []

    for r in _read("google-global-user-data-requests.csv"):
        period = _period(r["Period Ending"])
        country, iso2 = r["Country/Region"], r["CLDR Territory Code"]
        process = r["Legal Process"]
        for metric, unit, col in [("requests", "count", "User Data Requests"),
                                  ("accounts", "count", "Accounts"),
                                  ("pct_disclosed", "percent", "Percentage disclosed")]:
            if not _blank(r[col]):
                rows.append(_exact("global", period, country, iso2, "", process, "",
                                   metric, unit, _num(r[col])))

    for r in _read("google-global-user-data-dlr-requests.csv"):
        rows.append(_exact("global_diplomatic", _period(r["Period Ending"]),
                           r["Country/Region of Origin"], r["CLDR Territory Code"],
                           "", "", r["Assisting Country"],
                           "requests", "count", _num(r["User Data Diplomatic Legal requests"])))

    for r in _read("google-enterprise-data-requests.csv"):
        period = _period(r["Period Ending"])
        country, iso2 = r["Country/Region"], r["CLDR Territory Code"]
        product, process = r["Product"], r["Legal Process"]
        for metric, unit, col in [("requests", "count", "Enterprise Cloud customer requests"),
                                  ("customers", "count", "Enterprise Cloud customers"),
                                  ("pct_disclosed", "percent", "Percentage disclosed")]:
            if not _blank(r[col]):
                rows.append(_exact("enterprise", period, country, iso2, product, process, "",
                                   metric, unit, _num(r[col])))

    for r in _read("google-enterprise-data-dlr-requests.csv"):
        rows.append(_exact("enterprise_diplomatic", _period(r["Period Ending"]),
                           r["Country/Region of Origin"], "", r["Product"], "",
                           r["Assisting Country"],
                           "requests", "count", _num(r["Enterprise Diplomatic Legal requests"])))

    for name, dataset in [
        ("google-usnationalsecurity-fisa-content-requests.csv", "us_fisa_content"),
        ("google-usnationalsecurity-fisa-non-content-requests.csv", "us_fisa_non_content"),
        ("google-usnationalsecurity-nsl-requests.csv", "us_nsl"),
    ]:
        for r in _read(name):
            period = _period(r["Reporting period ending date"])
            for metric, lo_col, hi_col in [
                ("requests", "Number of requests (range MIN)", "Number of requests (range MAX)"),
                ("accounts", "Number of accounts (range MIN)", "Number of accounts (range MAX)"),
            ]:
                rows.append((dataset, period, "United States", "US", "", "", "",
                             metric, "count", _num(r[lo_col]), _num(r[hi_col])))

    rows.sort()
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--download", action="store_true",
                    help="refresh raw/ from the live bulk zip before building")
    args = ap.parse_args()

    if args.download:
        download()

    rows = build()
    periods = sorted({r[1] for r in rows})
    datasets = sorted({r[0] for r in rows})
    out = {
        "source": ZIP_URL,
        "coverage": f"{periods[0]}..{periods[-1]}",
        "columns": COLUMNS,
        "rows": [list(r) for r in rows],
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    print(f"wrote {OUT_JSON}: {len(rows)} rows, {len(periods)} periods "
          f"({periods[0]}..{periods[-1]}), datasets: {', '.join(datasets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
