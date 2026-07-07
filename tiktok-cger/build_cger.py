#!/usr/bin/env python3
"""Build tiktok-cger.json from TikTok's Community Guidelines Enforcement Report.

The **Community Guidelines Enforcement Report (CGER)** is TikTok's *voluntary*
content-moderation transparency report (distinct from its law-mandated DSA
report and its government/legal-request disclosures) — how much violating
content it removed, how proactively, and how fast, **quarterly since 2020 Q3**.
It's the TikTok analogue of Meta's Community Standards Enforcement Report.

## Source

TikTok publishes the CGER as a **downloadable ZIP** (a raw tidy-long CSV plus a
README, dashboard templates and a narratives PDF), but only via its bot-gated
transparency SPA. The report page server-renders a ``__remixContext`` blob whose
CDN URLs point straight at the per-quarter ZIP, so ``_download`` fetches it
deterministically with no browser:

1. GET the CGER report page with browser headers.
2. Regex the ``…/<PERIOD>_CGER_English.zip`` URL out of the page HTML (the latest
   quarter's ZIP contains the **full** back-history).
3. GET that ZIP (its eden-CDN path contains a literal ``[``, so no URL globbing).

The CDN folder token rotates each publication, so the URL is *discovered* from
the page rather than hardcoded — the same discover-then-fetch move as the CSER
GraphQL feed. The archived ``raw/cger.zip`` keeps the *build* deterministic.

## Output

The raw CSV is flat tidy-long (`Metric, Period type, Period, Policy type, Issue,
Task type, Task, Location, Market, Result`). We vendor the **Global cut**
(``Location='All'``) — every metric × policy × issue × task breakdown at the
global level, ~3k rows — and drop the per-country/per-language rows (156 markets
× everything ≈ 30× larger); pass ``--include-markets`` to keep them. One row per
measured value:

  period, metric, policy_type, issue, task_type, task, unit, value

``period`` is normalised (`Jul-Sep 2020` → `2020 Q3`). ``unit`` is ``count`` or
``rate`` (a **fraction of 1** — TikTok reports rates like ``0.944`` = 94.4%),
derived per metric (a metric naming a rate/share/percentage is a rate). Rows
where TikTok suppressed the value for privacy (fewer than 1,000 users) are blank
in the source and dropped. Rows sorted; no wall-clock. Pure stdlib.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_ZIP = os.path.join(HERE, "raw", "cger.zip")
OUT_JSON = os.path.join(HERE, "tiktok-cger.json")

SOURCE = "https://www.tiktok.com/transparency/en/community-guidelines-enforcement/"
_PAGE = "https://www.tiktok.com/safety/en/transparency/community-guidelines-enforcement"
COLUMNS = ["period", "metric", "policy_type", "issue",
           "task_type", "task", "unit", "value"]
# CSV columns as filed (the header carries a UTF-8 BOM on the first field).
_RAW_COLS = ["Metric", "Period type", "Period", "Policy type", "Issue",
             "Task type", "Task", "Location", "Market", "Result"]
_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

_QUARTER = {"jan-mar": "Q1", "apr-jun": "Q2", "jul-sep": "Q3", "oct-dec": "Q4"}


def _period(p: str) -> str:
    """`Jul-Sep 2020` -> `2020 Q3` (sortable)."""
    m = re.fullmatch(r"([A-Za-z]{3}-[A-Za-z]{3})\s+(\d{4})", p.strip())
    if not m or m.group(1).lower() not in _QUARTER:
        raise ValueError(f"unexpected CGER period {p!r}")
    return f"{m.group(2)} {_QUARTER[m.group(1).lower()]}"


def _unit(metric: str) -> str:
    """A metric naming a rate / share / percentage is a fraction of 1; else a
    raw count. (Consistent per metric in the source.)"""
    return "rate" if re.search(r"rate|share|percentage", metric, re.I) else "count"


def _read_csv(raw_zip: str) -> tuple[list[str], list[list[str]]]:
    with zipfile.ZipFile(raw_zip) as z:
        names = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(names) != 1:
            raise ValueError(f"expected exactly one CSV in {raw_zip}, got {names}")
        text = z.read(names[0]).decode("utf-8-sig")
    rows = list(csv.reader(io.StringIO(text)))
    header = [h.lstrip("﻿") for h in rows[0]]
    if header != _RAW_COLS:
        raise ValueError(f"unexpected CGER CSV header {header}")
    return header, [r for r in rows[1:] if r]


def build(raw_zip: str, include_markets: bool = False) -> dict:
    header, body = _read_csv(raw_zip)
    ix = {h: i for i, h in enumerate(header)}
    rows: list[list] = []
    for r in body:
        result = r[ix["Result"]].strip()
        if not result:  # suppressed for privacy (< 1,000 users)
            continue
        if not include_markets and r[ix["Location"]] != "All":
            continue
        metric = r[ix["Metric"]].strip()
        try:
            value = float(result.replace(",", ""))
        except ValueError:
            raise ValueError(f"unparseable CGER Result {result!r}")
        row = [_period(r[ix["Period"]]), metric, r[ix["Policy type"]].strip(),
               r[ix["Issue"]].strip(), r[ix["Task type"]].strip(),
               r[ix["Task"]].strip(), _unit(metric), value]
        if include_markets:
            row = row[:2] + [r[ix["Market"]].strip()] + row[2:]
        rows.append(row)
    rows.sort(key=lambda x: tuple(x[:-2]))  # all dims (excl. unit+value); market-aware
    periods = sorted({x[0] for x in rows})
    cols = COLUMNS[:2] + (["market"] if include_markets else []) + COLUMNS[2:]
    return {
        "source": SOURCE,
        "coverage": (f"{periods[0]}..{periods[-1]}" if len(periods) > 1
                     else periods[0] if periods else ""),
        "scope": "with-markets" if include_markets else "global",
        "columns": cols,
        "rows": rows,
    }


def _download(raw_zip: str) -> None:
    """Discover the latest CGER ZIP URL from the report page and fetch it."""
    import urllib.request

    def _get(url: str, headers: dict) -> bytes:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=180) as resp:
            return resp.read()

    html = _get(_PAGE, {
        "User-Agent": _UA,
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.9",
        "sec-fetch-dest": "document", "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none", "upgrade-insecure-requests": "1",
    }).decode("utf-8", "replace")
    urls = re.findall(r"https?://[^\s\"'\\<>]+?CGER[^\s\"'\\<>]*?\.zip", html, re.I)
    if not urls:
        raise RuntimeError("could not find a CGER .zip URL in the report page")
    # Pick the latest by the YYYYQn token in the path.
    def _key(u: str) -> str:
        m = re.search(r"(\d{4})Q([1-4])", u)
        return f"{m.group(1)}{m.group(2)}" if m else ""
    latest = max(urls, key=_key)
    blob = _get(latest, {"User-Agent": _UA})
    os.makedirs(os.path.dirname(raw_zip), exist_ok=True)
    with open(raw_zip, "wb") as f:
        f.write(blob)
    print(f"downloaded {latest} -> {raw_zip} ({len(blob)} bytes)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raw", default=RAW_ZIP, help="Archived CGER ZIP path")
    ap.add_argument("--out", default=OUT_JSON, help="Output dataset JSON path")
    ap.add_argument("--include-markets", action="store_true",
                    help="Keep the per-country/per-language rows (much larger)")
    ap.add_argument("--download", action="store_true",
                    help="Refresh the raw ZIP from TikTok's report page first")
    args = ap.parse_args()

    if args.download:
        _download(args.raw)

    data = build(args.raw, include_markets=args.include_markets)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    rows = data["rows"]
    print(f"wrote {args.out}: {len(rows)} values ({data['scope']}) across "
          f"{len({r[1] for r in rows})} metrics, "
          f"{len({r[0] for r in rows})} quarters (coverage {data['coverage']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
