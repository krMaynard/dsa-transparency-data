#!/usr/bin/env python3
"""Build discord-transparency.json from Discord's Transparency Reports.

Discord publishes a Transparency Report every reporting period — quarterly
through 2023, half-yearly from 2024 — each as a **ZIP containing one CSV** (plus
a narrative PDF) on its CDN, linked from:

  https://discord.com/safety-transparency-reports

The CSV is a stack of **labelled sub-tables**: a one-cell *section* header
(e.g. ``Accounts Disabled``, ``US Gov Info Requests``,
``International Government Information Requests``), then a column-header row
(its first cell names the row dimension — Policy Category / Country / Request
Type / Month — and the rest name the measures), then the data rows, then a
``Total`` row. The report covers Trust & Safety enforcement (accounts, servers
and members actioned by policy category; appeals; user reports; NCMEC) **and**
government / legal requests (US legal process, international requests,
preservation and emergency requests — by country), a stream not otherwise in
this pipeline.

The extractor walks that structure generically — it doesn't hard-code the
section or measure list, so new policy categories / sections / measures in
later reports flow through as new rows rather than crashing. Each section and
measure label is normalised to a stable snake_case key; the row dimension's
value is kept verbatim as ``category``. ``Total`` rows are dropped (derivable
by SUM; keeping them would double-count).

Tidy-long output — one row per measured value:

  period, section, category, metric, unit, value

``period`` is the report's own grain — ``YYYY-Qn`` (2022-2023) or ``YYYY-Hn``
(2024+). ``unit`` is ``count`` or ``percent`` (an appeal/report percentage
carried as the reported percentage number, e.g. ``10.45`` — never SUM a
percent). The raw per-period CSVs are archived verbatim in raw/.

Deterministic: builds purely from the archived raw/ CSVs (rows sorted); no
wall-clock. ``--download`` refreshes raw/ from the current report ZIPs. Pure
stdlib.
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

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, "raw")
OUT_JSON = os.path.join(HERE, "discord-transparency.json")

REPORT_URL = "https://discord.com/safety-transparency-reports"

COLUMNS = ["period", "section", "category", "metric", "unit", "value"]

# period -> report ZIP on the CDN (curate a new entry each release; the general
# global report only — the separate Discord-DSA_Transparency_Report.zip overlaps
# this project's DSA pipeline and is intentionally excluded).
_CDN = "https://cdn.discordapp.com/assets/transparency-reports"
SOURCES = {
    "2022-Q1": f"{_CDN}/Discord-Transparency-Report-Q1-2022.zip",
    "2022-Q2": f"{_CDN}/Discord-Transparency-Report-Q2-2022.zip",
    "2022-Q3": f"{_CDN}/Discord-Transparency-Report-Q3-2022.zip",
    "2023-Q1": f"{_CDN}/Discord-Transparency-Report-Q1-2023.zip",
    "2023-Q2": f"{_CDN}/Discord-Transparency-Report-Q2-2023.zip",
    "2023-Q3": f"{_CDN}/Discord-Transparency-Report-Q3-2023.zip",
    "2023-Q4": f"{_CDN}/Discord-Transparency-Report-Q4-2023.zip",
    "2024-H1": f"{_CDN}/Discord-Transparency-Report-H1-2024.zip",
}

Row = tuple[str, str, str, str, str, float]


def _key(text: str) -> str:
    """Normalise a section / measure label to a stable snake_case key."""
    s = text.strip().lower().replace("%", "pct").replace("&", "and")
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def _num(cell: str) -> tuple[str, float] | None:
    """('1,586' -> ('count', 1586)); ('10.45%' -> ('percent', 10.45)); '--'/'' -> None."""
    v = cell.strip()
    if not v or v == "--":
        return None
    unit = "percent" if "%" in v else "count"
    try:
        return unit, float(v.replace(",", "").replace("%", "").strip())
    except ValueError:
        return None


def _parse_csv(text: str, period: str) -> list[Row]:
    """Walk the labelled sub-tables of one report CSV into tidy-long rows."""
    reader = csv.reader(io.StringIO(text))
    out: list[Row] = []
    section: str | None = None
    metrics: list[str] | None = None
    pending: str | None = None
    for raw in reader:
        cells = [c.strip() for c in raw]
        while cells and not cells[-1]:
            cells.pop()
        if not cells:
            continue
        filled = [c for c in cells if c]
        if len(filled) == 1 and cells[0]:
            # A one-cell row: a section header (or the title / a stray note).
            # Await its column-header row; a fresh one-cell row before that
            # simply replaces it (so the CSV title line is discarded).
            pending, metrics = cells[0], None
            continue
        if pending is not None and metrics is None:
            section, metrics, pending = pending, cells[1:], None  # column header
            continue
        if metrics is None:
            continue  # data before any section header — ignore
        category = cells[0]
        if re.fullmatch(r"total:?", category, re.IGNORECASE):
            continue  # aggregate row — derivable, would double-count
        for j, measure in enumerate(metrics):
            if not measure or j + 1 >= len(cells):
                continue
            parsed = _num(cells[j + 1])
            if parsed is None:
                continue
            unit, value = parsed
            out.append((period, section and _key(section), category,
                        _key(measure), unit, value))
    if not out:
        raise SystemExit(f"{period}: parsed zero rows (report format drift?)")
    return out


def build(raw_dir: str) -> dict:
    rows: list[Row] = []
    for period in SOURCES:
        path = os.path.join(raw_dir, f"{period}.csv")
        if not os.path.isfile(path):
            raise SystemExit(f"missing expected raw file: {path}")
        with open(path, encoding="utf-8-sig") as f:
            rows.extend(_parse_csv(f.read(), period))
    rows.sort()
    periods = sorted({r[0] for r in rows})
    return {
        "source": REPORT_URL,
        "coverage": f"{periods[0]}..{periods[-1]}",
        "columns": COLUMNS,
        "rows": [list(r) for r in rows],
    }


def _download(raw_dir: str) -> None:
    os.makedirs(raw_dir, exist_ok=True)
    for period, url in SOURCES.items():
        req = urllib.request.Request(url, headers={"User-Agent": "dsa-transparency-data/1.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            blob = resp.read()
        zf = zipfile.ZipFile(io.BytesIO(blob))
        names = [n for n in zf.namelist()
                 if n.endswith(".csv") and not n.startswith("__MACOSX")]
        if len(names) != 1:
            raise SystemExit(f"{period}: expected exactly one CSV in the ZIP, "
                             f"found {names}")
        with open(os.path.join(raw_dir, f"{period}.csv"), "wb") as f:
            f.write(zf.read(names[0]))
        print(f"downloaded {period}.csv ({len(zf.read(names[0]))} bytes)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raw", default=RAW_DIR, help="Dir of the archived CSVs")
    ap.add_argument("--out", default=OUT_JSON, help="Output dataset JSON path")
    ap.add_argument("--download", action="store_true",
                    help="Refresh raw/ from the current report ZIPs first")
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
          f"{len({r[0] for r in rows})} periods, "
          f"{len({r[1] for r in rows})} sections "
          f"(coverage {data['coverage']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
