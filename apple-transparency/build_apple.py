#!/usr/bin/env python3
"""Build the interned apple-transparency.json from Apple's downloadable CSVs.

Apple publishes its Transparency Report as a zip of per-request-type CSVs
(https://www.apple.com/legal/transparency/). Each row is (period, country) +
a request-type-specific set of measures. We normalise the heterogeneous columns
onto a single canonical measure vocabulary and emit a compact interned dataset:

  {
    "source": "...", "coverage": "2025 H1",  # latest period (deterministic stamp)
    "periods":  ["2013 H1", ...],            # chronological
    "countries":["Australia", ...],
    "request_types": ["device", "account", ...],
    "rows":     [[period_id, country_id, request_type_id, <measures...>], ...],
    "ns_rows":  [[period_id, country_id, ns_type, req_low, req_high, acc_low, acc_high], ...]
  }

The two national-security CSVs (US national security, UK IPA) report banded
ranges like "0 - 249" rather than integers, so they go to a separate ns_rows
list with parsed low/high bounds.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import urllib.request
import zipfile

SOURCE_URL = "https://www.apple.com/legal/transparency/"
ZIP_URL = "https://www.apple.com/legal/zip/transparency/Apple_Transparency_Report.zip"
HERE = os.path.dirname(os.path.abspath(__file__))
RAW_ZIP = os.path.join(HERE, "raw", "Apple_Transparency_Report.zip")
OUT_JSON = os.path.join(HERE, "apple-transparency.json")

# Canonical measure columns of the apple_requests fact table, in order.
MEASURES = [
    "requests_received", "items_specified", "requests_data_provided",
    "pct_data_provided", "requests_challenged_rejected", "requests_no_data",
    "content_provided", "noncontent_provided", "accounts_preserved",
    "accounts_restricted", "accounts_deleted", "requests_app_removed",
    "apps_removed", "appeals_received", "appeals_granted", "apps_reinstated",
]

# Per-CSV: request_type slug + {source column header -> canonical measure}.
# Headers are matched case-insensitively after collapsing internal whitespace.
FILES = {
    "device_requests.csv": ("device", {
        "device requests received": "requests_received",
        "devices specified in requests": "items_specified",
        "requests where data provided": "requests_data_provided",
        "percentage of requests where data provided": "pct_data_provided",
    }),
    "account_requests.csv": ("account", {
        "account requests received": "requests_received",
        "accounts specified in requests": "items_specified",
        "requests challenged in part or rejected in full": "requests_challenged_rejected",
        "requests where only non-content data provided": "noncontent_provided",
        "requests where content provided": "content_provided",
        "percentage of requests where data provided": "pct_data_provided",
    }),
    "account_preservation_requests.csv": ("account_preservation", {
        "account preservation requests received": "requests_received",
        "accounts specified in requests": "items_specified",
        "accounts where data preserved": "accounts_preserved",
    }),
    "account_restriction_deletion_requests.csv": ("account_restriction_deletion", {
        "account restriction/ account deletion requests received": "requests_received",
        "accounts specified in the requests": "items_specified",
        "requests rejected/challenged where no action taken": "requests_challenged_rejected",
        "requests where account restricted": "accounts_restricted",
        "requests where account deleted": "accounts_deleted",
    }),
    "financial_identifier_requests.csv": ("financial_identifier", {
        "financial identifier requests received": "requests_received",
        "financial identifiers specified in requests": "items_specified",
        "requests where data provided": "requests_data_provided",
        "percentage of requests where data provided": "pct_data_provided",
    }),
    "push_token_requests.csv": ("push_token", {
        "push token requests received": "requests_received",
        "push tokens specified in requests": "items_specified",
        "requests where data provided": "requests_data_provided",
        "percentage of requests where data provided": "pct_data_provided",
    }),
    "emergency_requests.csv": ("emergency", {
        "emergency requests received": "requests_received",
        "requests rejected/challenged and no data provided": "requests_challenged_rejected",
        "requests where no data provided": "requests_no_data",
        "requests where data provided": "requests_data_provided",
        "percentage of requests where data provided": "pct_data_provided",
    }),
    "digital_content_provider_requests.csv": ("digital_content_provider", {
        "digital content provider requests received": "requests_received",
        "requests objected to in part or rejected in full": "requests_challenged_rejected",
        "requests where data provided": "requests_data_provided",
        "percentage of requests where data provided": "pct_data_provided",
    }),
    "app_takedown_legal_violation_requests.csv": ("app_takedown_legal_violation", {
        "legal violation takedown requests received": "requests_received",
        "apps specified in requests": "items_specified",
        "requests objected to in part or rejected in full": "requests_challenged_rejected",
        "requests where app removed": "requests_app_removed",
        "apps removed": "apps_removed",
        "appeals received": "appeals_received",
        "appeals granted": "appeals_granted",
        "apps reinstated": "apps_reinstated",
    }),
    "app_takedown_platform_policy_violation_requests.csv": ("app_takedown_platform_policy", {
        "platform policy violation takedown requests received": "requests_received",
        "apps specified in requests": "items_specified",
        "requests objected to in part or rejected in full": "requests_challenged_rejected",
        "requests where app removed": "requests_app_removed",
        "apps removed": "apps_removed",
        "appeals received": "appeals_received",
        "appeals granted": "appeals_granted",
        "apps reinstated": "apps_reinstated",
    }),
}
NS_FILES = {
    "us_national_security_requests.csv": "National Security Request Type",
    "uk_data_access_agreement_ipa_warrant_requests.csv": "IPA Warrant Request Type",
}


def _norm(h: str) -> str:
    return re.sub(r"\s+", " ", h.strip().lower())


def _num(v):
    """Integer count, or None for blanks / '-' sentinels / non-numeric."""
    s = (v or "").strip().replace(",", "")
    if not s or s in ("-", "—", "N/A", "n/a"):
        return None
    return int(s) if s.isdigit() else None


def _pct(v):
    """Percentage like '59%' -> 59.0; blank/'-' -> None."""
    s = (v or "").strip().rstrip("%")
    if not s or s in ("-", "—"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _period_of(row: dict) -> str:
    # Most files use 'TR Period'; account_preservation uses 'TR Date'.
    return (row.get("TR Period") or row.get("TR Date") or "").strip()


def _period_key(p: str):
    # "2013 H1" -> (2013, 1) for chronological sort.
    m = re.match(r"(\d{4})\s*H([12])", p)
    return (int(m.group(1)), int(m.group(2))) if m else (9999, 9)


def _parse_range(v):
    """'0 - 249' -> (0, 249); '5000+' -> (5000, None); plain int -> (n, n)."""
    s = (v or "").strip().replace(",", "")
    if not s or s in ("-", "—"):
        return (None, None)
    if s.isdigit():
        return (int(s), int(s))
    m = re.match(r"(\d+)\s*[-–]\s*(\d+)", s)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    m = re.match(r"(\d+)\s*\+", s)
    if m:
        return (int(m.group(1)), None)
    return (None, None)


def load_zip(zip_path: str) -> dict:
    """Read every per-type CSV out of Apple's report zip → {basename: [dict rows]}."""
    tables: dict[str, list[dict]] = {}
    with zipfile.ZipFile(zip_path) as z:
        for info in z.namelist():
            base = os.path.basename(info)
            if (not base.lower().endswith(".csv") or info.startswith("__MACOSX")
                    or base.startswith("._")):
                continue
            with z.open(info) as f:
                text = io.TextIOWrapper(f, encoding="utf-8-sig", newline="")
                tables[base] = list(csv.DictReader(text))
    return tables


def build(tables: dict, source_url: str = SOURCE_URL) -> dict:
    periods: dict[str, int] = {}
    countries: dict[str, int] = {}
    rtypes: dict[str, int] = {}

    def intern(d, key):
        if key not in d:
            d[key] = len(d)
        return d[key]

    rows = []
    for fname, (slug, colmap) in FILES.items():
        recs = tables.get(fname)
        if recs is None:
            raise SystemExit(f"missing expected CSV in zip: {fname}")
        headers = list(recs[0].keys()) if recs else []
        norm_to_canon = {h: colmap[_norm(h)] for h in headers if _norm(h) in colmap}
        missing = set(colmap.values()) - set(norm_to_canon.values())
        if missing:
            raise SystemExit(f"{fname}: unmapped canonical measures {missing}; headers were {headers}")
        for r in recs:
            country = (r.get("Country/Region") or "").strip()
            period = _period_of(r)
            if not country or not period:
                continue
            vals = {m: None for m in MEASURES}
            for src, canon in norm_to_canon.items():
                vals[canon] = _pct(r[src]) if canon == "pct_data_provided" else _num(r[src])
            rows.append([intern(periods, period), intern(countries, country),
                         intern(rtypes, slug)] + [vals[m] for m in MEASURES])

    ns_rows = []
    for fname, type_col in NS_FILES.items():
        for r in tables.get(fname, []):
            country = (r.get("Country/Region") or "").strip()
            period = _period_of(r)
            if not country or not period:
                continue
            req_lo, req_hi = _parse_range(r.get("Requests Received"))
            acc_lo, acc_hi = _parse_range(r.get("Users/Accounts"))
            ns_rows.append([intern(periods, period), intern(countries, country),
                            (r.get(type_col) or "").strip(),
                            req_lo, req_hi, acc_lo, acc_hi])

    # Re-key periods chronologically (ids must be the chronological ordinal).
    order = sorted(periods, key=_period_key)
    remap = {periods[p]: i for i, p in enumerate(order)}
    for row in rows:
        row[0] = remap[row[0]]
    for row in ns_rows:
        row[0] = remap[row[0]]
    periods = {p: i for i, p in enumerate(order)}

    inv = lambda d: [k for k, _ in sorted(d.items(), key=lambda kv: kv[1])]
    return {
        "source": source_url,
        # `coverage` = latest period in the data (deterministic; no wall-clock, so
        # re-running on the same archive is byte-identical for the CI sync check).
        "coverage": order[-1] if order else "",
        "measures": MEASURES,
        "periods": inv(periods),
        "countries": inv(countries),
        "request_types": inv(rtypes),
        "rows": rows,
        "ns_rows": ns_rows,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--zip", default=RAW_ZIP, help="Path to the archived Apple report zip")
    ap.add_argument("--out", default=OUT_JSON, help="Output dataset JSON path")
    ap.add_argument("--download", action="store_true",
                    help="Fetch a fresh zip from Apple into --zip before building")
    args = ap.parse_args()
    if args.download:
        os.makedirs(os.path.dirname(args.zip), exist_ok=True)
        req = urllib.request.Request(ZIP_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as resp, open(args.zip, "wb") as f:
            f.write(resp.read())
        print(f"downloaded {os.path.getsize(args.zip)} bytes -> {args.zip}")
    data = build(load_zip(args.zip))
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {args.out}: {len(data['rows'])} request rows, {len(data['ns_rows'])} "
          f"national-security rows, {len(data['periods'])} periods, "
          f"{len(data['countries'])} countries (coverage {data['coverage']})")


if __name__ == "__main__":
    main()
