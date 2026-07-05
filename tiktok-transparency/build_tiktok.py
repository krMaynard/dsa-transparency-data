#!/usr/bin/env python3
"""Build tiktok-transparency.json from TikTok's government & legal request reports.

TikTok's transparency centre publishes three **government / legal request**
reports as machine-readable CSVs on its "Legal, Information & Government
Requests" (LIGR) download bucket — a stream that is entirely distinct from the
content-moderation figures already covered by the DSA pipeline:

  https://www.tiktok.com/transparency/en/government-removals-report

Each current-period CSV is **cumulative**, carrying every reporting half-year
since 2019 in one tidy-long file, so a single download per stream yields the
whole history. Three streams are extracted (the raw CSVs archived in raw/):

  * **government_removals** — Government content-removal requests
    (aspect ``GRFCR``): per country × half-year, requests / content / accounts
    received, the content & accounts actioned (split by community-guideline vs
    local-law grounds) and the removal rate.
  * **information_requests** — Government requests for user information
    (aspect ``LRFUI``): per country × half-year, legal / emergency /
    preservation requests, the accounts they specify, and the share of legal /
    emergency requests where some data was disclosed.
  * **ip_removals** — Intellectual-property (copyright & trademark) removal
    requests (aspect ``Copyright``): **global only** — request and removal
    counts plus success/appeal rates.

All feed one **tidy-long** table — one row per measured value:

  dataset, period, country, metric, unit, value

``dataset`` ∈ government_removals / information_requests / ip_removals.
``period`` is the half-year ``YYYY-H1`` / ``YYYY-H2``. ``country`` is the market
name, or ``All`` for the global aggregate row that sits **alongside** the
per-country rows (a SUM over both double-counts — pin ``country`` first, or
filter it out). ``unit`` is ``count`` (exact integer) or ``percent`` (a rate /
percentage reported as a fraction of 1 — never SUM a percent). Each source
metric label maps to a stable snake_case ``metric`` key via an explicit
registry, so an unrecognised label crashes the build (fail-loud) rather than
being silently dropped.

Deterministic: builds purely from the archived raw/ CSVs (rows sorted); no
wall-clock. ``--download`` refreshes raw/ from the current-period CSVs. Pure
stdlib.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, "raw")
OUT_JSON = os.path.join(HERE, "tiktok-transparency.json")

REPORT_URL = "https://www.tiktok.com/transparency/en/government-removals-report"

COLUMNS = ["dataset", "period", "country", "metric", "unit", "value"]

# The current-period cumulative CSVs (rotate per release; refresh with
# --download when TikTok publishes a new half-year). raw filename -> CDN URL.
_CDN = ("https://sf16-va.tiktokcdn.com/obj/eden-va2/zayvwlY_fjulyhwzuhy%5B/"
        "ljhwZthlaukjlkulzlp/2025H2_CLIGR/data_downloads")
SOURCES = {
    "government-removal-requests.csv":
        f"{_CDN}/CLIGR_2025H2_GovernmentRemovalsRequests.csv",
    "information-requests.csv":
        f"{_CDN}/CLIGR_2025H2_InformationRequests.csv",
    "intellectual-property-requests.csv":
        f"{_CDN}/CLIGR_2025H2_IntellectualPropertyRights.csv",
}

# metric_name (as filed) -> (snake_case key, unit). Unknown labels crash the
# build. Every "…rate" / "Percentage of…" metric is a fraction of 1 -> percent.
_GOV_METRICS = {
    "Total requests received": ("total_requests_received", "count"),
    "Total Government Requests": ("total_government_requests", "count"),
    "Total content received": ("content_specified", "count"),
    "Total accounts received": ("accounts_specified", "count"),
    "Content actioned due to community guidelines violations":
        ("content_actioned_community_guidelines", "count"),
    "Content actioned due to (local) law violations":
        ("content_actioned_local_law", "count"),
    "Content not actioned": ("content_not_actioned", "count"),
    "Accounts actioned due to community guidelines violations":
        ("accounts_actioned_community_guidelines", "count"),
    "Accounts actioned due to (local) law violations":
        ("accounts_actioned_local_law", "count"),
    "Accounts not actioned": ("accounts_not_actioned", "count"),
    "Removal rate": ("removal_rate", "percent"),
}
_INFO_METRICS = {
    "Total requests": ("total_requests", "count"),
    "Total legal requests": ("total_legal_requests", "count"),
    "Legal requests": ("legal_requests", "count"),
    "Legal request accounts specified": ("legal_accounts_specified", "count"),
    "Total emergency requests": ("total_emergency_requests", "count"),
    "Emergency requests": ("emergency_requests", "count"),
    "Emergency request accounts specified": ("emergency_accounts_specified", "count"),
    "Total preservation requests": ("total_preservation_requests", "count"),
    "Preservation requests": ("preservation_requests", "count"),
    "Preservation request accounts specified": ("preservation_accounts_specified", "count"),
    "Percentage of legal requests where some data was disclosed":
        ("pct_legal_disclosed", "percent"),
    "Percentage of emergency requests where some data was disclosed":
        ("pct_emergency_disclosed", "percent"),
}
_IP_METRICS = {
    "Total IP Requests": ("total_ip_requests", "count"),
    "Total requests": ("total_requests", "count"),
    "Requests resulting in removal": ("requests_resulting_in_removal", "count"),
    "Percentage of successful requests": ("pct_successful", "percent"),
    "Total copyright removal requests": ("total_copyright_requests", "count"),
    "Copyright requests resulting in removal": ("copyright_requests_removed", "count"),
    "Percentage of copyright requests resulting in removal":
        ("pct_copyright_removed", "percent"),
    "Total trademark removal requests": ("total_trademark_requests", "count"),
    "Trademark requests resulting in removal": ("trademark_requests_removed", "count"),
    "Total trademark removal requests which involve counterfeits":
        ("trademark_requests_counterfeit", "count"),
    "Percentage of trademark requests resulting in removal":
        ("pct_trademark_removed", "percent"),
    "Number of actions taken against accounts": ("account_actions", "count"),
    "Invalid requests": ("invalid_requests", "count"),
    "Appeal success rate": ("appeal_success_rate", "percent"),
}

# raw filename -> (dataset name, aspect code as filed, metric registry).
_STREAMS = {
    "government-removal-requests.csv": ("government_removals", "GRFCR", _GOV_METRICS),
    "information-requests.csv": ("information_requests", "LRFUI", _INFO_METRICS),
    "intellectual-property-requests.csv": ("ip_removals", "Copyright", _IP_METRICS),
}

_EXPECTED_HEADER = ["replication_info", "entity", "aspect", "metric_name",
                    "period", "period_value", "policy", "policy_value", "task",
                    "task_value", "location", "location_value", "result",
                    "base", "date"]

Row = tuple[str, str, str, str, str, float]


def _period(period_value: str) -> str:
    """'Jan-Jun 2019' -> '2019-H1'; 'Jul-Dec 2019' -> '2019-H2'."""
    m = re.fullmatch(r"(Jan-Jun|Jul-Dec)\s+(\d{4})", period_value.strip())
    if not m:
        raise SystemExit(f"unrecognised period_value: {period_value!r}")
    return f"{m.group(2)}-{'H1' if m.group(1) == 'Jan-Jun' else 'H2'}"


def _value(raw: str, unit: str) -> float:
    v = float(raw)
    if unit == "count":
        if v != int(v):
            raise SystemExit(f"non-integral count value: {raw!r}")
        return int(v)
    return v


def _read_stream(path: str, dataset: str, aspect: str,
                 metrics: dict[str, tuple[str, str]]) -> list[Row]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != _EXPECTED_HEADER:
            raise SystemExit(f"{path}: unexpected header {reader.fieldnames}")
        out: list[Row] = []
        for r in reader:
            if r["aspect"] != aspect:
                raise SystemExit(f"{path}: unexpected aspect {r['aspect']!r}")
            label = (r["metric_name"] or "").strip()
            if label not in metrics:
                raise SystemExit(f"{dataset}: unknown metric label {label!r}")
            key, unit = metrics[label]
            country = (r["location_value"] or "").strip() or "All"
            out.append((dataset, _period(r["period_value"]), country, key, unit,
                        _value(r["result"], unit)))
    if not out:
        raise SystemExit(f"{path}: parsed zero rows (format drift?)")
    return out


def build(raw_dir: str) -> dict:
    rows: list[Row] = []
    for fname, (dataset, aspect, metrics) in _STREAMS.items():
        path = os.path.join(raw_dir, fname)
        if not os.path.isfile(path):
            raise SystemExit(f"missing expected raw file: {path}")
        rows.extend(_read_stream(path, dataset, aspect, metrics))
    rows.sort()
    periods = sorted({r[1] for r in rows})
    return {
        "source": REPORT_URL,
        "coverage": f"{periods[0]}..{periods[-1]}",
        "columns": COLUMNS,
        "rows": [list(r) for r in rows],
    }


def _download(raw_dir: str) -> None:
    os.makedirs(raw_dir, exist_ok=True)
    for fname, url in SOURCES.items():
        req = urllib.request.Request(url, headers={"User-Agent": "dsa-transparency-data/1.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            blob = resp.read()
        with open(os.path.join(raw_dir, fname), "wb") as f:
            f.write(blob)
        print(f"downloaded {fname} ({len(blob)} bytes)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raw", default=RAW_DIR, help="Dir of the archived CSVs")
    ap.add_argument("--out", default=OUT_JSON, help="Output dataset JSON path")
    ap.add_argument("--download", action="store_true",
                    help="Refresh raw/ from the current-period CSVs first")
    args = ap.parse_args()

    if args.download:
        _download(args.raw)
    data = build(args.raw)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    rows = data["rows"]
    print(f"wrote {args.out}: {len(rows)} rows, "
          f"{len({r[1] for r in rows})} periods, "
          f"{len({r[2] for r in rows})} countries, "
          f"datasets: {', '.join(sorted({r[0] for r in rows}))} "
          f"(coverage {data['coverage']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
