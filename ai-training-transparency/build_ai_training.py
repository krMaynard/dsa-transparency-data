#!/usr/bin/env python3
"""Build the EU AI Act training-data transparency dataset.

Article 53(1)(d) of the EU AI Act (Reg. (EU) 2024/1689) requires providers of
general-purpose AI models to publish a **public summary of the content used to
train the model**, on the AI Office's standardised template (in force 2 Aug
2025). The summary discloses, per modality (Text / Image / Audio / Video), a
**banded training-data size**, the data-acquisition cut-off, and yes/no flags for
each data-source category (publicly available, commercially licensed, private
third-party, personal data, synthetic).

This builds a **cross-provider, comparable** dataset from those summaries. There
is no single registry of the filled summaries — each provider self-publishes in
its own format — so this reads two source shapes archived in ``raw/``:

- **Markdown "data summary cards"** (Microsoft's convention on Hugging Face) —
  the template fields as ``**1.3.1.A Text training data size:** …`` lines, parsed
  directly.
- **PDF** (Google, on its transparency-report bucket) — the size bands are
  checkbox selections not present in the text layer, so Google's row values are
  **curated** from the rendered form and cross-checked with fail-loud anchors
  against the PDF's text (model name, market date, knowledge cut-off).

Output ``ai-training-transparency.json``, tidy-long:
  provider, model, released, section, field, value, size_rank

- **section** ``modality`` (field = Text/Image/Audio/Video/Other; value = the
  size band; ``size_rank`` = 1/2/3 for the three bands, 0 = "Not applicable",
  so the coarse sizes are numerically comparable across providers), ``general``
  (data_cutoff / ongoing_collection) or ``data_source`` (publicly_available /
  commercially_licensed / third_party_private / personal_data / synthetic;
  value = Yes/No/Not applicable/…).

Coverage is a starting, expandable set (Google + Microsoft). More providers slot
in as their summaries are archived — the markdown parser is generic.

Deterministic: reads only ``raw/`` + the curated GOOGLE block; no network. Pure
stdlib + PyMuPDF.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT_JSON = os.path.join(HERE, "ai-training-transparency.json")

COLUMNS = ["provider", "model", "released", "section", "field", "value", "size_rank"]

# The five modality rows and the data-source flags, in template order.
MODALITIES = ["Text", "Image", "Audio", "Video", "Other"]


def _band_rank(value: str) -> int | None:
    """Map a training-data-size band to a comparable rank: 0 = not applicable,
    1 = the smallest band ('less than …'), 3 = the largest ('more than …'),
    2 = the middle range. None if the value isn't a size band."""
    v = re.sub(r"\s+", " ", value).strip().lower()
    if not v:
        return None
    if "not applicable" in v or v in ("n/a", "na"):
        return 0
    if "less than" in v:
        return 1
    if "more than" in v:
        return 3
    # a "X to Y" range (tokens / images / hours)
    if " to " in v and any(u in v for u in ("token", "image", "hour")):
        return 2
    return None


# ── Microsoft-style markdown "data summary card" parser ─────────────────────
# Fields are `**<code> <label>:** <value>` lines. We key off the stable numeric
# codes so label wording drift doesn't matter.
_MD_FIELD = re.compile(r"\*\*([\d.]+[A-Z]?)\s+[^:*]+:\*\*\s*(.+?)\s*$", re.M)

_MD_MAP = {  # template code -> (section, field)
    "1.3.1.A": ("modality", "Text"),
    "1.3.1.C": ("modality", "Image"),
    "1.3.1.E": ("modality", "Audio"),
    "1.3.1.G": ("modality", "Video"),
    "1.3.1.I": ("modality", "Other"),
    "1.3.2": ("general", "data_cutoff"),
    "1.3.3": ("general", "ongoing_collection"),
    "2.1.1": ("data_source", "publicly_available"),
    "2.2.1.A": ("data_source", "commercially_licensed"),
    "2.2.2.A": ("data_source", "third_party_private"),
    "2.3.1": ("data_source", "personal_data"),
    "2.4.1": ("data_source", "synthetic"),
}


def _parse_markdown(path: str, provider: str) -> list[list]:
    text = open(path, encoding="utf-8").read()
    fields = {code: val for code, val in _MD_FIELD.findall(text)}
    model = fields.get("1.2.1", os.path.basename(path))
    released = fields.get("1.2.2", "")
    rows: list[list] = []
    for code, (section, field) in _MD_MAP.items():
        if code not in fields:
            continue
        val = fields[code]
        rank = _band_rank(val) if section == "modality" else None
        rows.append([provider, model, released, section, field, val, rank])
    if not any(r[3] == "modality" for r in rows):
        raise ValueError(f"{path}: no modality rows parsed — card format changed?")
    return rows


# ── Google (Gemini 3 Pro) — curated from the rendered form (checkbox bands are
# not in the PDF text layer), verified with fail-loud anchors on the text. ────
GOOGLE = {
    "pdf": "google-gemini3pro-eu-training-summary.pdf",
    "provider": "Google",
    "model": "Gemini 3 Pro family",
    "released": "November 2025",
    "checks": ["The Gemini 3 Pro family of models", "November 2025",
               "knowledge cut-off date for Gemini 3 Pro is 01 / 2025"],
    "rows": [  # (section, field, value)
        ("modality", "Text", "More than 10 trillion tokens"),
        ("modality", "Image", "More than 1 billion images"),
        ("modality", "Audio", "More than 1 million hours"),
        ("modality", "Video", "More than 1 million hours"),
        ("general", "data_cutoff", "01/2025"),
        ("data_source", "publicly_available", "Yes"),
        ("data_source", "commercially_licensed", "Yes"),
        ("data_source", "third_party_private", "Yes"),
    ],
}


def _squash(s: str) -> str:
    # Google's PDF sprinkles zero-width spaces (U+200B) between words, so strip
    # all whitespace *and* zero-width characters before the anchor comparison.
    return re.sub(r"[\s​‌‍﻿]+", "", s)


def _parse_google(raw_dir: str) -> list[list]:
    path = os.path.join(raw_dir, GOOGLE["pdf"])
    with fitz.open(path) as doc:
        text = _squash("\n".join(p.get_text() for p in doc))
    for chk in GOOGLE["checks"]:
        if _squash(chk) not in text:
            raise ValueError(f"{GOOGLE['pdf']}: anchor {chk!r} not found — changed?")
    rows = []
    for section, field, value in GOOGLE["rows"]:
        rank = _band_rank(value) if section == "modality" else None
        rows.append([GOOGLE["provider"], GOOGLE["model"], GOOGLE["released"],
                     section, field, value, rank])
    return rows


def build(raw_dir: str) -> dict:
    rows: list[list] = _parse_google(raw_dir)
    for path in sorted(glob.glob(os.path.join(raw_dir, "microsoft-*.md"))):
        rows += _parse_markdown(path, "Microsoft")
    rows.sort(key=lambda r: (r[0], r[1], r[3], r[4]))
    return {
        "source": "EU AI Act (Reg. 2024/1689) Art. 53(1)(d) — public summaries of training content",
        "columns": COLUMNS,
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raw", default=RAW)
    ap.add_argument("--out", default=OUT_JSON)
    args = ap.parse_args()
    data = build(args.raw)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    models = sorted({(r[0], r[1]) for r in data["rows"]})
    print(f"wrote {args.out}: {len(data['rows'])} rows across {len(models)} models "
          f"({', '.join(m[1] for m in models)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
