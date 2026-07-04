#!/usr/bin/env python3
"""Build linkedin-transparency.json from LinkedIn's Government Requests Report.

LinkedIn's Government Requests Report page is **server-rendered HTML** — every
half-year's figures live in plain ``<table>`` markup on one page:

  https://about.linkedin.com/transparency/government-requests-report

Three quantitative sections are extracted (the raw page is archived verbatim
in raw/):

  * **Requests by country** (2016-H1 →): per country, requests for member
    data, accounts subject to those requests, the percentage of requests for
    which some data was provided, and the accounts for which data was provided.
  * **Breakdown of U.S. government requests** (2015-H1 →): a per-period
    key/value table — request/account counts, the share of requests LinkedIn
    provided data for, the split of legal process types (as **percentages of
    requests**, not counts), and the US national-security figures, reportable
    only in **banded ranges** (e.g. ``0-499``). LinkedIn published no US
    breakdown tables for 2022.
  * **Government requests for content removal** (2018-H1 →): per country,
    removal requests, requests where action was taken, and the percentage.

All feed one **tidy-long** table — one row per measured value:

  dataset, period, country, metric, unit, value_low, value_high

``dataset`` ∈ member_data_requests / us_breakdown / content_removal_requests.
``unit`` is ``count`` or ``percent`` (never SUM a percent). Exact figures have
``value_low == value_high``; the national-security bands have
``value_low != value_high`` (non-additive). Aggregate ``Total`` rows in the
source tables are **skipped** (derivable by SUM; keeping them would
double-count).

Deterministic: builds purely from the archived raw/ page (rows sorted); no
wall-clock. ``--download`` refreshes raw/ from the live page. Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request

PAGE_URL = "https://about.linkedin.com/transparency/government-requests-report"
HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, "raw")
RAW_PAGE = os.path.join(RAW_DIR, "government-requests-report.html")
OUT_JSON = os.path.join(HERE, "linkedin-transparency.json")

COLUMNS = ["dataset", "period", "country", "metric", "unit", "value_low", "value_high"]

# Column layout of the per-country member-data tables (after the country cell).
MEMBER_METRICS = [("requests", "count"), ("accounts_subject", "count"),
                  ("pct_disclosed", "percent"), ("accounts_disclosed", "count")]

# Column layout of the per-country content-removal tables.
REMOVAL_METRICS = [("requests", "count"), ("action_taken", "count"),
                   ("pct_action_taken", "percent")]

# Row labels of the US-breakdown key/value tables (footnote markers stripped).
# The legal-process rows are percentages of requests, not counts.
US_LABELS = {
    "Requests": ("requests", "count"),
    "Accounts subject to requests": ("accounts_subject", "count"),
    "Requests for which LinkedIn provided some data": ("pct_disclosed", "percent"),
    "Subpoenas": ("pct_subpoenas", "percent"),
    "Search warrants": ("pct_search_warrants", "percent"),
    "Court orders": ("pct_court_orders", "percent"),
    "Other": ("pct_other", "percent"),
    "National security letters received": ("nsl_received", "count"),
    "National security letters (accounts subject to request)": ("nsl_accounts", "count"),
    "National security requests received": ("ns_requests", "count"),
    "National security requests (accounts subject to request)": ("ns_accounts", "count"),
    "FISA requests": ("fisa_requests", "count"),
}


def download() -> None:
    os.makedirs(RAW_DIR, exist_ok=True)
    req = urllib.request.Request(PAGE_URL, headers={"User-Agent": "dsa-transparency-data/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        blob = resp.read()
    with open(RAW_PAGE, "wb") as f:
        f.write(blob)
    print(f"downloaded {PAGE_URL} ({len(blob)} bytes)")


def _text(fragment: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>|&nbsp;|&amp;", " ", fragment)).strip()


def _period(heading: str) -> str | None:
    """'2025: July-December' -> '2025-H2'; '2016: January-June' -> '2016-H1'."""
    m = re.match(r"(\d{4}):\s*(January-June|July-December)", heading)
    if not m:
        return None
    return f"{m.group(1)}-{'H1' if m.group(2).startswith('January') else 'H2'}"


def _value(cell: str) -> tuple[int, int, bool]:
    """'2,292' -> (2292, 2292, False); '80%' -> (80, 80, True); '0-499' -> (0, 499, False)."""
    s = cell.strip().replace(",", "")
    pct = s.endswith("%")
    s = s.rstrip("%").strip()
    m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", s)
    if m:
        return int(m.group(1)), int(m.group(2)), pct
    return int(s), int(s), pct


Row = tuple[str, str, str, str, str, int, int]


def _country_table(table_rows: list[list[str]], dataset: str, period: str,
                   metrics: list[tuple[str, str]]) -> list[Row]:
    out: list[Row] = []
    for cells in table_rows:
        cells = [c for c in cells if c != ""]  # some tables carry blank spacer columns
        if len(cells) < len(metrics) + 1 or cells[0].startswith("Total"):
            continue
        country = cells[0]
        for (metric, unit), cell in zip(metrics, cells[1:1 + len(metrics)]):
            lo, hi, is_pct = _value(cell)
            unit_final = "percent" if is_pct else unit
            out.append((dataset, period, country, metric, unit_final, lo, hi))
    return out


def _us_table(table_rows: list[list[str]], period: str) -> list[Row]:
    out: list[Row] = []
    for cells in table_rows:
        cells = [c for c in cells if c != ""]
        if len(cells) < 2:
            continue
        label = re.sub(r"\s*\[\d+\]$", "", cells[0]).strip()
        if label not in US_LABELS:
            raise ValueError(f"us_breakdown {period}: unknown row label {cells[0]!r}")
        metric, unit = US_LABELS[label]
        lo, hi, is_pct = _value(cells[1])
        out.append(("us_breakdown", period, "United States", metric,
                    "percent" if is_pct else unit, lo, hi))
    return out


def build() -> list[Row]:
    html = open(RAW_PAGE, encoding="utf-8", errors="replace").read()

    # Walk headings and tables in document order; an h2 selects the section, an
    # h4 the reporting period, and each table binds to the current (h2, h4).
    events = re.finditer(r"<h([1-6])[^>]*>(.*?)</h\1>|<table.*?</table>", html, re.S)
    section = period = None
    rows: list[Row] = []
    for m in events:
        if not m.group(0).startswith("<table"):
            heading = _text(m.group(2))
            if m.group(1) == "2":
                section = heading
            p = _period(heading)
            if p:
                period = p
            continue
        if section is None or period is None:
            continue
        table_rows = [
            [_text(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S)]
            for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", m.group(0), re.S)
        ]
        if section.startswith("Requests by country") or section.startswith(
                "Global government requests for data"):
            rows.extend(_country_table(table_rows[1:], "member_data_requests",
                                       period, MEMBER_METRICS))
        elif section.startswith("Breakdown of U.S. government requests"):
            rows.extend(_us_table(table_rows, period))
        elif section.startswith("Global government requests for content removal"):
            rows.extend(_country_table(table_rows[1:], "content_removal_requests",
                                       period, REMOVAL_METRICS))

    if not rows:
        raise ValueError("no rows extracted — page markup changed?")
    rows.sort()
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--download", action="store_true",
                    help="refresh raw/ from the live page before building")
    args = ap.parse_args()

    if args.download:
        download()

    rows = build()
    pds = sorted({r[1] for r in rows})
    datasets = sorted({r[0] for r in rows})
    out = {
        "source": PAGE_URL,
        "coverage": f"{pds[0]}..{pds[-1]}",
        "columns": COLUMNS,
        "rows": [list(r) for r in rows],
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    print(f"wrote {OUT_JSON}: {len(rows)} rows, {len(pds)} periods "
          f"({pds[0]}..{pds[-1]}), datasets: {', '.join(datasets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
