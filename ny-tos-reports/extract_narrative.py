#!/usr/bin/env python3
"""Extract the narrative text of the NY Terms-of-Service reports.

New York's Social Media Terms-of-Service reports (Stop Hiding Hate Act) are
**narrative policy filings** — prose PDFs in which each company describes, in its
own words, how it defines and enforces hate speech, extremism, disinformation,
harassment and foreign political interference. The catalogue
(`ny_tos_reports.csv`) records where each lives and `normalize_quant.py` pulls
out the *numbers*; this script pulls out the **prose** so it can be full-text
searched.

For each **publicly archived** PDF in ``pdfs/``, the text of each page is
extracted and emitted as one tidy row. The page is the unit — a stable, citable
anchor back into the archived PDF — and pages with almost no extractable text
(covers, image-only pages) are dropped.

Tidy-long output — one row per page of prose:

  company, platform, period, page, heading, text

- **company / platform / period** — taken from the catalogue (matched by
  filename) so a narrative row joins cleanly to its ``ny_tos_reports`` entry.
- **page** — 1-based page number in the archived PDF.
- **heading** — a best-effort section heading for the page (the page's first
  line when it reads like a heading — short, no trailing period), else ``""``.
- **text** — the page's extracted text, whitespace-collapsed.

Deterministic: builds purely from the archived ``pdfs/`` + the catalogue (rows
sorted); no wall-clock. Pure stdlib + pdfplumber.
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re

import pdfplumber

HERE = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(HERE, "pdfs")
CATALOGUE = os.path.join(os.path.dirname(HERE), "ny_tos_reports.csv")
OUT_JSON = os.path.join(HERE, "ny_tos_narratives.json")

SOURCE = "https://ag.ny.gov/resources/organizations/stop-hiding-hate"
COLUMNS = ["company", "platform", "period", "page", "heading", "text"]

# A page with fewer than this many non-space characters is a cover / image page.
MIN_CHARS = 40
_WS = re.compile(r"\s+")


def _catalogue() -> dict[str, dict]:
    """filename -> catalogue row (public filings only)."""
    with open(CATALOGUE, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    out = {}
    for r in rows:
        if r.get("access") == "public" and r.get("filename"):
            out[r["filename"]] = r
    return out


def _heading(text: str) -> str:
    """Best-effort section heading = the page's first line when it reads like a
    heading (short, not a sentence). Conservative: returns "" when unsure."""
    line = text.strip().splitlines()[0].strip() if text.strip() else ""
    if not line or len(line) > 70:
        return ""
    if line.endswith((".", ",", ";", ":")):
        return ""
    # A heading is title/upper case or has few lowercase-started words.
    if line.isupper() or line.istitle():
        return line
    return ""


def _page_rows(path: str, meta: dict) -> list[list]:
    rows: list[list] = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            raw = page.extract_text() or ""
            if len(raw.replace(" ", "").replace("\n", "")) < MIN_CHARS:
                continue
            heading = _heading(raw)
            text = _WS.sub(" ", raw).strip()
            rows.append([meta["company"], meta.get("platform", ""),
                         meta["period"], i, heading, text])
    return rows


def build(pdf_dir: str) -> dict:
    catalogue = _catalogue()
    rows: list[list] = []
    for path in sorted(glob.glob(os.path.join(pdf_dir, "*.pdf"))):
        fname = os.path.basename(path)
        meta = catalogue.get(fname)
        if meta is None:
            # A PDF in pdfs/ that the catalogue doesn't mark public — skip loudly
            # rather than guess its company/period.
            print(f"  (skipping {fname}: no public catalogue entry)")
            continue
        rows.extend(_page_rows(path, meta))
    rows.sort(key=lambda r: (r[0], r[2], r[3]))
    periods = sorted({r[2] for r in rows})
    return {
        "source": SOURCE,
        "coverage": f"{periods[0]}..{periods[-1]}" if periods else "",
        "columns": COLUMNS,
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pdfs", default=PDF_DIR, help="Dir of the archived NY ToS PDFs")
    ap.add_argument("--out", default=OUT_JSON, help="Output dataset JSON path")
    args = ap.parse_args()

    data = build(args.pdfs)
    out_dir = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    rows = data["rows"]
    print(f"wrote {args.out}: {len(rows)} pages of prose, "
          f"{len({r[0] for r in rows})} companies "
          f"(coverage {data['coverage']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
