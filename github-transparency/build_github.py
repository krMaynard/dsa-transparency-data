#!/usr/bin/env python3
"""Build the tidy github-transparency.json from GitHub's open transparency CSVs.

GitHub publishes its Transparency Report data as a set of small, heterogeneous
CSVs (github/transparency, CC-BY-4.0): government takedowns, requests to disclose
user information, DMCA, automated detection, appeals/reinstatements, and EU-DSA
MAU. Rather than one typed table per file, we normalise them all onto a single
**tidy long** fact table — one row per measured value:

  [year, period, dataset, government, iso2, category, metric, count_low, count_high]

- `period` is the sub-year label when a file carries one ("Jul-Dec", a month
  number), else "".
- `government`/`iso2` are set for country-keyed files, else "".
- `category` is the in-row breakdown (request type, abuse type, …), else "".
- `metric` names the count column when a file has several (received/disclosed,
  repos/pages/accounts affected), else "count".
- National-security and EU-DSA-MAU values are banded ranges (e.g. "0-249"), so
  every value is stored as count_low/count_high (low == high for exact counts).

Pure stdlib; deterministic from the archived raw/ CSVs (rows sorted), so CI can
re-derive and diff. `--download` refreshes raw/ from github/transparency first.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import urllib.request

SOURCE_URL = "https://github.com/github/transparency"
RAW_BASE = "https://raw.githubusercontent.com/github/transparency/main/data"
HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, "raw")
OUT_JSON = os.path.join(HERE, "github-transparency.json")

# Upstream paths (under data/) for --download, keyed by local raw/ filename.
DOWNLOAD = {
    "government_takedowns_received.csv": "government_takedowns/government_takedowns_received.csv",
    "government_takedowns_processed.csv": "government_takedowns/government_takedowns_processed.csv",
    "requests_received_and_disclosed.csv": "requests_to_disclose_user_information/requests_received_and_disclosed.csv",
    "requests_accounts_affected.csv": "requests_to_disclose_user_information/requests_accounts_affected.csv",
    "cross_border_data_requests.csv": "requests_to_disclose_user_information/cross_border_data_requests.csv",
    "national_security_letters_and_orders.csv": "requests_to_disclose_user_information/national_security_letters_and_orders.csv",
    "dmca_takedowns_summary.csv": "dmca/dmca_takedowns_summary.csv",
    "circumvention_claims.csv": "dmca/circumvention_claims.csv",
    "cseai_and_tvec_reported.csv": "automated_detection/cseai_and_tvec_reported.csv",
    "abuse_related_violations.csv": "appeals_and_other_reinstatements/abuse_related_violations.csv",
    "trade_controls_compliance.csv": "appeals_and_other_reinstatements/trade_controls_compliance.csv",
    "eu_dsa_mau.csv": "eu_dsa/eu_dsa_mau.csv",
}

# Per-CSV mapping onto the tidy schema. `metrics` = [(source_col, metric_label)];
# OR `metric_col`+`value_col` when the metric name itself comes from a column.
# `ranged` flags files whose count cells are banded ranges (e.g. "0-249").
CONFIG = {
    "government_takedowns_received.csv": dict(
        dataset="government_takedowns_received", gov="government", iso2="government_iso2_code",
        category=None, period=None, ranged=False, metrics=[("count_received", "received")]),
    "government_takedowns_processed.csv": dict(
        dataset="government_takedowns_processed", gov="government", iso2="government_iso2_code",
        category="type", period=None, ranged=False,
        metrics=[("count_processed", "processed"), ("count_repos_affected", "repos_affected"),
                 ("count_pages_affected", "pages_affected"), ("count_accounts_affected", "accounts_affected")]),
    "requests_received_and_disclosed.csv": dict(
        dataset="user_info_requests", gov=None, iso2=None, category="type", period=None, ranged=False,
        metrics=[("count_requests_received", "received"), ("count_disclosed", "disclosed")]),
    "requests_accounts_affected.csv": dict(
        dataset="user_info_accounts_affected", gov=None, iso2=None, category=None, period=None,
        ranged=False, metrics=[("count_accounts_affected", "accounts_affected")]),
    "cross_border_data_requests.csv": dict(
        dataset="cross_border_data_requests", gov="government", iso2="government_iso2_code",
        category=None, period=None, ranged=False, metrics=[("count", "requests")]),
    "national_security_letters_and_orders.csv": dict(
        dataset="national_security", gov=None, iso2=None, category="type", period="month_range",
        ranged=True, metrics=[("count", "count")]),
    "dmca_takedowns_summary.csv": dict(
        dataset="dmca_takedowns", gov=None, iso2=None, category="type", period=None, ranged=False,
        metrics=[("count", "count")]),
    "circumvention_claims.csv": dict(
        dataset="dmca_circumvention_claims", gov=None, iso2=None, category=None, period=None,
        ranged=False, metrics=[("count", "count")]),
    "cseai_and_tvec_reported.csv": dict(
        dataset="automated_detection", gov=None, iso2=None, category="abuse_type", period=None,
        ranged=False, metric_col="detection_type", value_col="count"),
    "abuse_related_violations.csv": dict(
        dataset="appeals_abuse_related", gov=None, iso2=None, category="type", period=None,
        ranged=False, metrics=[("count", "count")]),
    "trade_controls_compliance.csv": dict(
        dataset="appeals_trade_controls", gov="government", iso2="government_iso2_code",
        category="type", period=None, ranged=False, metrics=[("count", "count")]),
    "eu_dsa_mau.csv": dict(
        dataset="eu_dsa_mau", gov=None, iso2=None, category=None, period="month", ranged=True,
        metrics=[("average_mau", "average_mau")]),
}


def _clean(v) -> str:
    return (v or "").strip()


def _parse_range(v):
    """'0-249' / '0 - 249' -> (0, 249); plain int -> (n, n); blank -> (None, None)."""
    s = _clean(v).replace(",", "")
    if not s or s in ("-", "—", "N/A", "n/a"):
        return (None, None)
    if s.lstrip("-").isdigit():
        return (int(s), int(s))
    m = re.match(r"(\d+)\s*[-–]\s*(\d+)$", s)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    return (None, None)


def build(raw_dir: str, source_url: str = SOURCE_URL) -> dict:
    rows = []
    years = []
    for fname, cfg in CONFIG.items():
        path = os.path.join(raw_dir, fname)
        if not os.path.isfile(path):
            raise SystemExit(f"missing expected CSV: {path}")
        with open(path, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                year = _clean(r.get("year"))
                if not year.isdigit():
                    continue
                year = int(year)
                years.append(year)
                period = _clean(r.get(cfg["period"])) if cfg["period"] else ""
                gov = _clean(r.get(cfg["gov"])) if cfg["gov"] else ""
                iso2 = _clean(r.get(cfg["iso2"])) if cfg["iso2"] else ""
                category = _clean(r.get(cfg["category"])) if cfg["category"] else ""
                if "metric_col" in cfg:
                    pairs = [(_clean(r.get(cfg["metric_col"])), cfg["value_col"])]
                else:
                    pairs = [(label, col) for col, label in cfg["metrics"]]
                for metric, col in pairs:
                    lo, hi = _parse_range(r.get(col))
                    if lo is None and hi is None:
                        continue  # blank cell — no value to record
                    rows.append([year, period, cfg["dataset"], gov, iso2, category, metric, lo, hi])
    # Deterministic order (stable JSON for the CI diff), independent of file/row order.
    rows.sort(key=lambda x: (x[2], x[0], x[1], x[3], x[5], x[6]))
    return {
        "source": source_url,
        "coverage": max(years) if years else None,
        "columns": ["year", "period", "dataset", "government", "iso2", "category",
                    "metric", "count_low", "count_high"],
        "rows": rows,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", default=RAW_DIR, help="Dir of archived GitHub transparency CSVs")
    ap.add_argument("--out", default=OUT_JSON, help="Output dataset JSON path")
    ap.add_argument("--download", action="store_true",
                    help="Refresh raw/ from github/transparency before building")
    args = ap.parse_args()
    if args.download:
        os.makedirs(args.raw, exist_ok=True)
        for fname, rel in DOWNLOAD.items():
            req = urllib.request.Request(f"{RAW_BASE}/{rel}", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp, \
                    open(os.path.join(args.raw, fname), "wb") as f:
                f.write(resp.read())
        print(f"downloaded {len(DOWNLOAD)} CSVs -> {args.raw}")
    data = build(args.raw)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        f.write("\n")
    datasets = sorted({r[2] for r in data["rows"]})
    print(f"wrote {args.out}: {len(data['rows'])} rows across {len(datasets)} datasets "
          f"(coverage {data['coverage']})")


if __name__ == "__main__":
    main()
