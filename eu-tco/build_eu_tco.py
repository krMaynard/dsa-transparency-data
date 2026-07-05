#!/usr/bin/env python3
"""Build eu-tco-narratives.json from the EU Terrorist Content Online reports.

The **Terrorist Content Online Regulation** ((EU) 2021/784, "TCOR") obliges
hosting service providers to remove terrorist content within one hour of a
removal order and to publish annual transparency reports. The European
Commission, in turn, publishes an annual **report on the implementation of the
Regulation** to the Parliament and Council, each accompanied by a **staff
working document** with the detailed evidence. Those Commission documents are
the retrievable, authoritative narrative record of how the TCO regime is
working — published on EUR-Lex as PDFs.

This extractor pulls the **prose** of those documents so it can be full-text
searched alongside the other report narratives (the same shape as the NY ToS
narratives). Platform-level TCO transparency reports (Meta, X, …) are published
only behind JavaScript transparency centres and aren't machine-retrievable, so
this corpus is the EU-institution layer: the Commission reports + their staff
working documents.

Tidy-long output — one row per page of prose:

  company, platform, period, page, heading, text

- **company** — the issuing body (``European Commission``).
- **platform** — the document kind (``Report`` / ``Staff Working Document``).
- **period** — the reporting year (``2024`` / ``2025``).
- **page** — 1-based page number in the source PDF.
- **heading** — the document's short title + its CELEX/COM reference, so a
  result names the exact document it came from.
- **text** — the page's extracted text, whitespace-collapsed.

Deterministic: builds purely from the archived ``raw/`` PDFs (rows sorted); no
wall-clock. ``--download`` refreshes raw/ from EUR-Lex. Pure stdlib + pdfplumber.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request

import pdfplumber

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, "raw")
OUT_JSON = os.path.join(HERE, "eu-tco-narratives.json")

SOURCE = "https://eur-lex.europa.eu/"
COLUMNS = ["company", "platform", "period", "page", "heading", "text"]

# A page with fewer than this many non-space characters is a cover / blank page.
MIN_CHARS = 60
_WS = re.compile(r"\s+")

# The EU-institution TCO document set on EUR-Lex. Each is a Commission report
# (`Report`) or its companion staff working document (`Staff Working Document`),
# keyed by CELEX number → (raw filename, period, kind, short heading). Curate a
# new entry when the Commission publishes the next annual round.
DOCS = {
    "52024DC0064": ("com-2024-64.pdf", "2024", "Report",
                    "TCO Regulation implementation report — COM(2024) 64 final"),
    "52024SC0036": ("swd-2024-36.pdf", "2024", "Staff Working Document",
                    "TCO Regulation implementation — SWD(2024) 36 final"),
    "52025DC0064": ("com-2025-64.pdf", "2025", "Report",
                    "TCO Regulation implementation report — COM(2025) 64 final"),
    # The 2025 staff working document isn't on EUR-Lex yet; add it when published.
}

_EURLEX = "https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:{}"


def _page_rows(path: str, period: str, kind: str, heading: str) -> list[list]:
    rows: list[list] = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            raw = page.extract_text() or ""
            if len(_WS.sub("", raw)) < MIN_CHARS:  # count non-whitespace chars
                continue
            text = _WS.sub(" ", raw).strip()
            rows.append(["European Commission", kind, period, i, heading, text])
    return rows


def build(raw_dir: str) -> dict:
    rows: list[list] = []
    for celex, (fname, period, kind, heading) in DOCS.items():
        path = os.path.join(raw_dir, fname)
        if not os.path.isfile(path):
            raise SystemExit(f"missing expected raw file: {path} "
                             f"(run with --download to fetch it)")
        rows.extend(_page_rows(path, period, kind, heading))
    # Sort deterministically: period, then document heading, then page.
    rows.sort(key=lambda r: (r[2], r[4], r[3]))
    periods = sorted({r[2] for r in rows})
    return {
        "source": SOURCE,
        "coverage": (f"{periods[0]}..{periods[-1]}" if len(periods) > 1
                     else periods[0] if periods else ""),
        "columns": COLUMNS,
        "rows": rows,
    }


def _download(raw_dir: str) -> None:
    os.makedirs(raw_dir, exist_ok=True)
    for celex, (fname, *_rest) in DOCS.items():
        url = _EURLEX.format(celex)
        req = urllib.request.Request(
            url, headers={"User-Agent": "dsa-transparency-data/1.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            ctype = resp.headers.get("Content-Type", "")
            blob = resp.read()
        if "pdf" not in ctype.lower():
            raise SystemExit(f"{celex}: expected a PDF, got Content-Type {ctype!r}")
        with open(os.path.join(raw_dir, fname), "wb") as f:
            f.write(blob)
        print(f"downloaded {fname} ({len(blob)} bytes) from {url}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raw", default=RAW_DIR, help="Dir of the archived PDFs")
    ap.add_argument("--out", default=OUT_JSON, help="Output dataset JSON path")
    ap.add_argument("--download", action="store_true",
                    help="Refresh raw/ from EUR-Lex first")
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
    print(f"wrote {args.out}: {len(rows)} pages of prose, "
          f"{len({r[4] for r in rows})} documents "
          f"(coverage {data['coverage']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
