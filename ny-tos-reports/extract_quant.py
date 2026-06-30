#!/usr/bin/env python3
"""Best-effort extraction of the *quantitative* data in the NY Social Media ToS
reports (Stop Hiding Hate Act, GBS §1102).

Unlike the EU DSA filings, these reports follow no shared template — most are
narrative policy/ToS documents, and only some include enforcement-statistics
tables, each in the company's own layout. This script pulls the numeric tables
out of the publicly-archived PDFs (``pdfs/``) into one tidy CSV/JSON:

    company, period, page, table_label, row_label, column, value, unit, raw

`unit` is ``count`` or ``percent``. One output row per numeric cell, so the
table shape is preserved as (row_label × column) without forcing a cross-company
schema (the companies' taxonomies genuinely differ). ``table_label`` is the
table's corner/header cell (e.g. Discord's "Accounts Disabled") so the metric
isn't lost for 2-column tables where it sits in the header rather than a column.

Coverage (2025 Q3): the six reports that carry machine-readable enforcement
tables — Discord, Reddit, LinkedIn, Naver, Roblox (generic table melt) and
Strava (bespoke 6-column layout). The rest are narrative-only (X, TikTok, Meta,
Vimeo — ToS text + policy descriptions, no enforcement counts) or image-based
(Snap — would need OCR); those are skipped and listed below.

Re-run:  ``python3 extract_quant.py``  (reads ./pdfs, writes ny_tos_quant.csv/.json)
"""
import csv
import json
import os
import re

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(HERE, "pdfs")
PERIOD = "2025 Q3"

# Reports with no extractable enforcement statistics, with the reason — recorded
# so the coverage gap is explicit rather than silent.
NARRATIVE_ONLY = {
    "x-corp": "narrative ToS + policy text; no enforcement-count tables",
    "tiktok-inc": "narrative policy; only scattered prose figures",
    "meta-platforms-inc-facebook-instagram-threads": "ToS text; no per-category counts",
    "vimeo-com-inc": "narrative policy definitions; no enforcement counts",
    "snap-inc": "image-based PDF; numbers are in graphics (needs OCR)",
}
GENERIC = ["discord-inc", "linkedin-corporation", "naver-corporation",
           "reddit-inc", "roblox-corporation"]


def _num(s):
    """(value, unit) for a numeric cell, else (None, None)."""
    if s is None:
        return None, None
    t = s.strip().replace("​", "").replace(",", "")
    m = re.fullmatch(r"([+-]?\d+(?:\.\d+)?)\s*%", t)
    if m:
        return float(m.group(1)), "percent"
    if re.fullmatch(r"[+-]?\d+(?:\.\d+)?", t):
        v = float(t)
        return (int(v) if v.is_integer() else v), "count"
    return None, None


def _clean(s):
    return (s or "").replace("​", "").replace("\n", " ").strip()


def _is_numeric_artifact(s):
    """True when a cell contains no letters in any script — i.e. it's bare
    numbers/punctuation (a value that melted into a label or header slot), so it
    should be dropped. Real labels/headers carry letters, so this keeps valid
    labels that merely *contain* a number (years, "Section 1102", "2025 3Q",
    "S895B", Korean/CJK labels) instead of dropping them."""
    s = (s or "").replace("​", "").strip()
    return bool(s) and re.search(r"[^\W\d_]", s, re.UNICODE) is None


def melt_generic(slug, path):
    """Melt every numeric table: (table_label, row_label, column) -> value.

    `table_label` is the corner/header cell (ex[0][0]) — for 2-column "metric"
    tables that's the metric name itself (Discord), so it isn't lost.
    """
    out = []
    with fitz.open(path) as doc:
        for pi, page in enumerate(doc):
            for tbl in page.find_tables().tables:
                ex = tbl.extract()
                if len(ex) < 2:
                    continue
                header = [_clean(c) for c in ex[0]]
                table_label = header[0] if header and not _is_numeric_artifact(header[0]) else ""
                for row in ex[1:]:
                    cells = [_clean(c) for c in row]
                    if not cells:
                        continue
                    label = cells[0]
                    if not label or _is_numeric_artifact(label):
                        continue
                    for ci in range(1, len(cells)):
                        v, unit = _num(cells[ci])
                        if v is None:
                            continue
                        col = header[ci] if ci < len(header) else ""
                        if _is_numeric_artifact(col):
                            col = ""  # header cell got polluted by a melted value
                        out.append(dict(company=slug, period=PERIOD, page=pi + 1,
                                        table_label=table_label, row_label=label,
                                        column=col, value=v, unit=unit, raw=cells[ci]))
    return out


# Strava lays its six enforcement tables out as a label line followed by exactly
# six numeric lines (PyMuPDF can't reconstruct the grid). Each table's six
# columns are the same shape; capture them positionally.
_STRAVA_SECTIONS = {
    "Flagged Items of Content": "flagged",
    "Actioned Items of Content.": "actioned",
    "Actioned Items of Content Resulting in User or Group of User Action":
        "actioned_user_action",
}
_STRAVA_COLS = ["total", "flagged_by_users", "flagged_by_employees",
                "flagged_by_technology", "actioned_by_employees",
                "actioned_by_technology"]


def parse_strava(slug, path):
    out = []
    lines = []
    with fitz.open(path) as doc:
        for page in doc:
            for ln in page.get_text().splitlines():
                t = ln.replace("​", "").replace("\xad", "").strip()
                if t:
                    lines.append((page.number + 1, t))

    section = None
    label_parts = []
    nums = []
    for pageno, t in lines:
        for name, key in _STRAVA_SECTIONS.items():
            if t.startswith(name):
                section = key
                label_parts, nums = [], []
                break
        if section is None:
            continue
        v, unit = _num(t)
        if unit == "count":
            nums.append((pageno, int(v)))
            if len(nums) == 6:                       # a complete data row
                label = " ".join(label_parts).strip(" .")
                if label and not _is_numeric_artifact(label):
                    for col, (pg, val) in zip(_STRAVA_COLS, nums):
                        out.append(dict(company=slug, period=PERIOD, page=pg,
                                        table_label=section, row_label=label,
                                        column=col, value=val, unit="count",
                                        raw=str(val)))
                label_parts, nums = [], []
        else:
            if nums:                                 # text after a partial row → reset
                label_parts, nums = [], []
            # skip the verbose column-header sentences
            if not t.lower().startswith("number of") and len(t) < 70:
                label_parts.append(t)
    return out


def main():
    rows = []
    for slug in GENERIC:
        p = os.path.join(PDF_DIR, f"2025-q3-{slug}.pdf")
        if os.path.isfile(p):
            rows += melt_generic(slug, p)
    sp = os.path.join(PDF_DIR, "2025-q3-strava-inc.pdf")
    if os.path.isfile(sp):
        rows += parse_strava("strava-inc", sp)

    rows.sort(key=lambda r: (r["company"], r["page"], r["table_label"], r["row_label"], r["column"]))
    cols = ["company", "period", "page", "table_label", "row_label", "column", "value", "unit", "raw"]
    with open(os.path.join(HERE, "ny_tos_quant.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(HERE, "ny_tos_quant.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
        f.write("\n")

    import collections
    by = collections.Counter(r["company"] for r in rows)
    print(f"{len(rows)} quantitative cells across {len(by)} reports:")
    for c, n in by.most_common():
        print(f"  {c:48} {n}")
    print("\nNarrative-only / image-based (no extractable stats):")
    for c, why in NARRATIVE_ONLY.items():
        print(f"  {c:48} {why}")


if __name__ == "__main__":
    main()
