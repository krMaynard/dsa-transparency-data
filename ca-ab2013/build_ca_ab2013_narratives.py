#!/usr/bin/env python3
"""Extract the narrative prose of Google's California AB 2013 AI-training summary.

California **AB 2013** (the Generative Artificial Intelligence: Training Data
Transparency Act, in force 1 Jan 2026) requires a developer of a generative AI
system or service made available to Californians to post, on its website, a
high-level summary of the datasets used to train it. Google publishes one
consolidated "AI Training Data Transparency Summary" covering its generative-AI
products (Gemini Apps, Search, YouTube, Ads, …).

This is **prose, not numbers**, so — like the NY ToS / CA AB 587 / DSA Table-11 /
Japan corpora — it rides in the API's full-text `report_narratives` search index
rather than a structured table. This extractor reads the archived PDF under
``raw/`` and splits the single-page summary into a few searchable sections, each
verified with a fail-loud anchor (the build raises if the wording drifts).

Output ``ca-ab2013-narratives.json`` in the shared page-based narrative shape:
  company, platform, period, page, heading, text

Deterministic; pure PyMuPDF (``fitz``), no network.
"""
from __future__ import annotations

import argparse
import json
import os

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
PDF = os.path.join(RAW, "google-ai-training-data-transparency-summary.pdf")
OUT_JSON = os.path.join(HERE, "ca-ab2013-narratives.json")

COLUMNS = ["company", "platform", "period", "page", "heading", "text"]
COMPANY = "Google"
PERIOD = "2026"  # AB 2013 in force 1 Jan 2026; this summary is dated 2026-06

# Each section is (heading, start_anchor, end_anchor). The prose is sliced between
# the anchors (end exclusive); the last section runs to the end of the document.
_SECTIONS = [
    ("Overview",
     "The following reflects Google",
     "The training datasets are characterized"),
    ("Data sources",
     "The training datasets are characterized",
     "The models are trained on a large corpus"),
    ("Training-data size",
     "The models are trained on a large corpus",
     "The cleaning and preprocessing"),
    ("Data cleaning and preprocessing",
     "The cleaning and preprocessing",
     None),
]


def build(pdf_path: str) -> dict:
    with fitz.open(pdf_path) as doc:
        flat = " ".join(" ".join(p.get_text() for p in doc).split())
    rows: list[list] = []
    for heading, start, end in _SECTIONS:
        i = flat.find(start)
        if i < 0:
            raise SystemExit(f"{os.path.basename(pdf_path)}: section {heading!r} "
                             f"start anchor not found — summary wording changed?")
        j = flat.find(end, i + len(start)) if end else len(flat)
        if j < 0:
            raise SystemExit(f"{os.path.basename(pdf_path)}: section {heading!r} "
                             f"end anchor not found — summary wording changed?")
        text = flat[i:j].strip()
        if len(text) < 60:  # not searchable prose — a sign the slice went wrong
            raise SystemExit(f"{os.path.basename(pdf_path)}: section {heading!r} "
                             f"extracted only {len(text)} chars")
        rows.append([COMPANY, "", PERIOD, 2, heading, text])
    return {
        "source": "California AB 2013 (Generative AI: Training Data Transparency "
                  "Act) — Google's AI Training Data Transparency Summary",
        "coverage": PERIOD,
        "columns": COLUMNS,
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pdf", default=PDF)
    ap.add_argument("--out", default=OUT_JSON)
    args = ap.parse_args()
    data = build(args.pdf)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    print(f"wrote {args.out}: {len(data['rows'])} narrative sections")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
