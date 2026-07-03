#!/usr/bin/env python3
"""Build taiwan-anti-fraud.json from data published under Taiwan's Anti-Fraud Act.

Taiwan's 詐欺犯罪危害防制條例 (Fraud Crime Hazard Prevention Act, "打詐專法",
in force July 2024) created two transparency streams:

1. **Government enforcement data.** The National Police Agency's Criminal
   Investigation Bureau publishes — on Taiwan's open-data portal
   (data.gov.tw dataset 176455) — the registry of **fraud websites whose DNS
   resolution was suspended under Article 42** of the Act: one row per blocked
   domain, with the ROC-calendar month, a site-category label (網站性質), the
   legal basis, and the requesting unit. The extractor aggregates that registry
   to a tidy-long table of blocked-site counts per month × category. The raw
   registry (the domain-level CSV) is archived verbatim in raw/.

2. **Platform transparency reports.** The designated online-ad platforms
   (Google/YouTube, Meta Facebook/Instagram, LINE, TikTok — MODA's list under
   Art. 27) must publish an annual 詐欺防制計畫透明度報告 (fraud-ads removed by
   type, suspended accounts, Taiwan MAU). Press coverage confirms the first
   round exists (e.g. Google: Jul 2024–Jun 2025, 236 government requests,
   3,564 URLs removed), but the report artifacts are not yet reachable from
   this pipeline (not search-indexed; LINE's site is bot-walled; TikTok's and
   Google's are JS-rendered). The schema below is publisher-keyed so those
   reports slot in as additional SOURCES entries once their URLs are curated.

Tidy-long output — one row per measured value:

  publisher, period, section, category, metric, unit, value

`publisher` is `NPA-165` for the government stream (platform names later);
`period` is the Gregorian month (`YYYY-MM`, converted from the ROC 民國 year);
`unit` is `count`. Never sum across sections once platform data lands.

**Rolling window caveat:** the upstream registry is a live feed covering
roughly the most recent half-year; older months drop out upstream. The
archived raw/ CSV freezes the window captured at vendoring time, and
`--download` refreshes it (union with the existing archive so months that
have rotated out upstream are preserved).
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
OUT_JSON = os.path.join(HERE, "taiwan-anti-fraud.json")

COLUMNS = ["publisher", "period", "section", "category", "metric", "unit", "value"]

RAW_CSV = "dns-blocked-sites.csv"
# data.gov.tw dataset 176455 — the stable per-resource download endpoint.
DNS_URL = ("https://opdadm.moi.gov.tw/api/v1/no-auth/resource/api/dataset/"
           "29E8E643-88ED-4952-B21E-BD42A3B7108C/resource/"
           "BBA077D2-2AB6-4011-9D61-E2585110AC62/download")
EXPECTED_HEADER = ["民國年月", "網域", "網站性質", "法律依據", "聲請單位"]


def _period(roc_ym: str) -> str:
    """ROC-calendar 民國年月 ('11412') -> Gregorian 'YYYY-MM' ('2025-12')."""
    s = (roc_ym or "").strip()
    if not re.fullmatch(r"\d{4,5}", s):
        raise SystemExit(f"unrecognised 民國年月: {roc_ym!r}")
    year, month = int(s[:-2]) + 1911, int(s[-2:])
    if not 1 <= month <= 12:
        raise SystemExit(f"unrecognised 民國年月: {roc_ym!r}")
    return f"{year:04d}-{month:02d}"


def _read_registry(path: str) -> list[dict[str, str]]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != EXPECTED_HEADER:
            raise SystemExit(f"{path}: unexpected header {reader.fieldnames}; "
                             f"expected {EXPECTED_HEADER}")
        return [r for r in reader if (r.get("網域") or "").strip()]


def build(raw_dir: str) -> dict:
    path = os.path.join(raw_dir, RAW_CSV)
    if not os.path.isfile(path):
        raise SystemExit(f"missing expected raw file: {path}")
    registry = _read_registry(path)
    counts: dict[tuple[str, str], int] = {}
    for r in registry:
        period = _period(r["民國年月"])
        category = re.sub(r"\s+", " ", r["網站性質"]).strip() or "不詳"
        counts[(period, category)] = counts.get((period, category), 0) + 1
    rows = [["NPA-165", period, "dns_blocked_sites", category,
             "sites_blocked", "count", n]
            for (period, category), n in counts.items()]
    rows.sort(key=lambda x: (x[0], x[1], x[2], x[3], x[4], x[5]))
    if not rows:
        raise SystemExit("parsed zero rows (format drift?)")
    return {
        "source": "https://data.gov.tw/dataset/176455",
        "coverage": max(r[1] for r in rows),
        "columns": COLUMNS,
        "rows": rows,
    }


def _download(raw_dir: str) -> None:
    """Refresh the registry, **unioning** with the archived rows: the upstream
    feed is a rolling window, so months that have rotated out are kept."""
    os.makedirs(raw_dir, exist_ok=True)
    path = os.path.join(raw_dir, RAW_CSV)
    old: list[dict[str, str]] = _read_registry(path) if os.path.isfile(path) else []
    req = urllib.request.Request(DNS_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = resp.read().decode("utf-8-sig")
    reader = csv.DictReader(body.splitlines())
    if reader.fieldnames != EXPECTED_HEADER:
        raise SystemExit(f"download: unexpected header {reader.fieldnames}")
    new = [r for r in reader if (r.get("網域") or "").strip()]
    seen = set()
    merged: list[dict[str, str]] = []
    for r in new + old:  # fresh rows win; dedupe on the full row
        key = tuple(r[c] for c in EXPECTED_HEADER)
        if key not in seen:
            seen.add(key)
            merged.append(r)
    merged.sort(key=lambda r: tuple(r[c] for c in EXPECTED_HEADER))
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=EXPECTED_HEADER)
        writer.writeheader()
        writer.writerows(merged)
    print(f"downloaded registry: {len(new)} live rows, {len(merged)} after "
          f"union with archive -> {path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", default=RAW_DIR, help="Dir of the archived registry CSV")
    ap.add_argument("--out", default=OUT_JSON, help="Output dataset JSON path")
    ap.add_argument("--download", action="store_true",
                    help="Refresh raw/ from data.gov.tw (union with the archive)")
    args = ap.parse_args()
    if args.download:
        _download(args.raw)
    data = build(args.raw)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {args.out}: {len(data['rows'])} rows, "
          f"{len({r[1] for r in data['rows']})} periods, "
          f"{len({r[3] for r in data['rows']})} categories "
          f"(coverage {data['coverage']})")


if __name__ == "__main__":
    main()
