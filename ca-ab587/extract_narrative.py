#!/usr/bin/env python3
"""Extract the narrative text of the California AB 587 ToS reports.

California's AB 587 Terms-of-Service reports (see `build_ab587.py`) are prose
filings in which each platform describes, in its own words, how it defines and
enforces categories of content — hate speech, extremism, disinformation,
harassment and foreign political interference — plus how automated moderation
works and how it handles violations. `build_ab587.py` catalogues them; this
script pulls the **prose** so it can be full-text searched alongside the other
report narratives.

For each archived PDF in ``pdfs/`` the text of each page is emitted as one tidy
row, matched to the catalogue (`ca_ab587_reports.csv`) by filename so a narrative
row joins cleanly to its catalogue entry. Pages with almost no extractable text
(covers, image-only pages) are dropped.

Tidy-long output — one row per page of prose:

  company, platform, period, page, heading, text

Deterministic: builds purely from ``pdfs/`` + the catalogue (rows sorted); no
wall-clock. Pure stdlib + pdfplumber.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re

import pdfplumber

HERE = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(HERE, "pdfs")
CATALOGUE = os.path.join(HERE, "ca_ab587_reports.csv")
OUT_JSON = os.path.join(HERE, "ca-ab587-narratives.json")

SOURCE = "https://oag.ca.gov/ab587/submissions"
COLUMNS = ["company", "platform", "period", "page", "heading", "text"]

MIN_CHARS = 40
_WS = re.compile(r"\s+")


def _catalogue() -> dict[str, dict]:
    """filename -> catalogue row."""
    with open(CATALOGUE, newline="", encoding="utf-8-sig") as f:
        return {r["filename"]: r for r in csv.DictReader(f) if r.get("filename")}


def _heading(text: str) -> str:
    line = text.strip().splitlines()[0].strip() if text.strip() else ""
    if not line or len(line) > 70 or line.endswith((".", ",", ";", ":")):
        return ""
    return line if (line.isupper() or line.istitle()) else ""


def _page_rows(path: str, meta: dict) -> list[list]:
    rows: list[list] = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            raw = page.extract_text() or ""
            if len(_WS.sub("", raw)) < MIN_CHARS:
                continue
            rows.append([meta["company"], meta.get("platform", ""),
                         meta["period"], i, _heading(raw), _WS.sub(" ", raw).strip()])
    return rows


def build(pdf_dir: str) -> dict:
    catalogue = _catalogue()
    rows: list[list] = []
    for fname in sorted(os.listdir(pdf_dir)) if os.path.isdir(pdf_dir) else []:
        if not fname.endswith(".pdf"):
            continue
        meta = catalogue.get(fname)
        if meta is None:
            print(f"  (skipping {fname}: not in the catalogue)")
            continue
        try:
            rows.extend(_page_rows(os.path.join(pdf_dir, fname), meta))
        except Exception as e:  # a corrupt/incomplete PDF shouldn't kill the whole run
            print(f"  (error processing {fname}: {e})")
    rows.sort(key=lambda r: (r[1] or r[0], r[2], r[0], r[3]))
    periods = sorted({r[2] for r in rows})
    return {
        "source": SOURCE,
        "coverage": (f"{periods[0]}..{periods[-1]}" if len(periods) > 1
                     else periods[0] if periods else ""),
        "columns": COLUMNS,
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pdfs", default=PDF_DIR, help="Dir of the archived PDFs")
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
          f"{len({r[1] or r[0] for r in rows})} platforms "
          f"(coverage {data['coverage']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
