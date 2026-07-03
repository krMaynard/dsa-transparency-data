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

Coverage (2025 Q3): the eight reports that carry machine-readable enforcement
data — Discord, Reddit, LinkedIn, Naver (generic table melt) and Strava, Snap,
Roblox (bespoke text-layout parsers). The rest are narrative-only (X, TikTok,
Meta, Vimeo — ToS text + policy descriptions, no enforcement counts); those are
skipped and listed below.

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
}
GENERIC = ["discord-inc", "linkedin-corporation", "naver-corporation",
           "reddit-inc"]


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


# Strava lays each enforcement table out as a label line followed by exactly six
# numeric lines (PyMuPDF can't reconstruct the grid). The report has six tables;
# five carry data (the impressions one is a prose "we don't track this" note).
# Longest heading first so "…Resulting in…"/"…by User Sharing Data" match before
# the bare "Actioned Items of Content" prefix. Each table's first data row is its
# TOTAL row, so everything between the heading and the literal "TOTAL" line is
# column-header word-wrap and gets skipped.
_STRAVA_SHARED_COLS = ["flagged_by_users", "flagged_by_employees",
                       "flagged_by_technology", "actioned_by_employees",
                       "actioned_by_technology"]
_STRAVA_SECTIONS = [
    # (heading prefix, section key, column names for the 6 numeric cells)
    ("Actioned Items of Content Resulting in User or Group of User Action",
     "actioned_user_action", ["actions_against_users"] + _STRAVA_SHARED_COLS),
    ("Actioned Items of Content by User Sharing Data",
     "actioned_shared", ["times_shared"] + _STRAVA_SHARED_COLS),
    ("Actioned Items by Impression Data",
     "impressions", None),                       # no data: Strava doesn't track it
    ("Actioned Items of Content",
     "actioned", ["actioned_total"] + _STRAVA_SHARED_COLS),
    ("Flagged Items of Content",
     "flagged", ["flagged_total"] + _STRAVA_SHARED_COLS),
    ("User Appeals of Strava Actions",
     "appeals", ["appeals", "reversed_content_restored",
                 "reversed_content_not_restored", "upheld_changed_enforcement",
                 "upheld_no_change", "no_action"]),
]


def parse_strava(slug, path):
    out = []
    lines = []
    with fitz.open(path) as doc:
        for page in doc:
            for ln in page.get_text().splitlines():
                t = ln.replace("​", "").replace("\xad", "").strip()
                if t:
                    lines.append((page.number + 1, t))

    section, cols = None, None
    in_header = False         # between a table heading and its TOTAL row
    label_parts = []
    nums = []
    for pageno, t in lines:
        matched = False
        for name, key, section_cols in _STRAVA_SECTIONS:
            if t.startswith(name):
                section, cols = key, section_cols
                in_header = True
                label_parts, nums = [], []
                matched = True
                break
        if matched or section is None or cols is None:
            continue
        if in_header:
            # Skip the column-header word-wrap; the first data row is TOTAL.
            if t.strip(" .").upper() == "TOTAL":
                in_header = False
                label_parts = ["TOTAL"]
            continue
        v, unit = _num(t)
        if unit == "count" and isinstance(v, int):   # rows are integer counts
            nums.append((pageno, int(v)))
            if len(nums) == 6:                       # a complete data row
                label = " ".join(label_parts).strip(" .")
                if label and not _is_numeric_artifact(label):
                    for col, (pg, val) in zip(cols, nums):
                        out.append(dict(company=slug, period=PERIOD, page=pg,
                                        table_label=section, row_label=label,
                                        column=col, value=val, unit="count",
                                        raw=str(val)))
                label_parts, nums = [], []
        else:
            if nums:                                 # text after a partial row → reset
                label_parts, nums = [], []
            # skip stray footer/header fragments
            if not t.lower().startswith("number of") and len(t) < 70:
                label_parts.append(t)
    return out


# Snap's enforcement table (its "policy" pages are screenshots, but the data
# table itself is real text): 4 categories × 2 detection manners × 13 metrics.
# Each data row is a category label (possibly wrapped over several lines), a
# manner pair ("Human"/"Report" or "Proactive"/"Detection"), then 13 numeric
# tokens — 9 counts and 4 trailing Violative-View-Rate percentages.
_SNAP_CATEGORIES = ("Hate Speech", "Terrorism & Violent Extremism",
                    "False Information", "Harassment")
_SNAP_COLS = ["flagged_total", "content_enforced_human",
              "content_enforced_automated", "accounts_enforced_human",
              "accounts_enforced_automated", "lock_appeals_human",
              "lock_appeals_automated", "reinstated_human",
              "reinstated_automated", "vvr_human_pct", "vvr_automated_pct",
              "unique_viewer_rate_human_pct", "unique_viewer_rate_automated_pct"]
_SNAP_MANNERS = {("Human", "Report"): "human_report",
                 ("Proactive", "Detection"): "proactive_detection"}


def parse_snap(slug, path):
    out = []
    with fitz.open(path) as doc:
        page = next((p for p in doc if "Violative View Rate" in p.get_text()), None)
        if page is None:
            return out
        pageno = page.number + 1
        lines = [ln.replace("​", "").strip()
                 for ln in page.get_text().splitlines() if ln.strip()]

    category = manner = None
    pending = []      # candidate category-label lines since the last data row
    nums = []
    prev = ""
    for t in lines:
        toks = t.split()
        vals = [_num(tok) for tok in toks]
        if toks and all(u is not None for _, u in vals):
            # an all-numeric line ("3,184,734 756,736" carries two cells)
            nums.extend(vals)
            if len(nums) >= len(_SNAP_COLS):
                if len(nums) > len(_SNAP_COLS) or category is None or manner is None:
                    raise SystemExit(f"snap: malformed data row near {t!r}")
                for col, (v, unit) in zip(_SNAP_COLS, nums):
                    out.append(dict(company=slug, period=PERIOD, page=pageno,
                                    table_label=manner, row_label=category,
                                    column=col, value=v, unit=unit, raw=str(v)))
                nums = []
            prev = ""
            continue
        manner_key = _SNAP_MANNERS.get((prev, t))
        if manner_key:
            manner = manner_key
            rest = pending[:-1]                  # drop the buffered "Human"/"Proactive"
            if rest:                             # else: same category, next manner
                joined = " ".join(rest)
                category = next((c for c in _SNAP_CATEGORIES
                                 if joined.endswith(c)), None)
                if category is None:
                    raise SystemExit(
                        f"snap: unrecognized category before {t!r}: {joined[-80:]!r}")
            pending = []
            nums = []
        elif re.match(r"^\(\d+\)", t):           # numbered footnotes — table done
            break
        elif len(t) < 60:
            pending.append(t)
        prev = t
    return out


# Roblox lays out simple label/value column lists (the generic melt only caught
# a handful of bordered totals). A table starts at a run of known ALL-CAPS
# header lines: leading dimension columns, then 1–2 value columns; each data
# row is a label line followed by one numeric line per value column. In the
# CATEGORY × MEDIA TYPE tables a label followed by another label is a group
# header ("Account", "Content") that prefixes the rows under it.
_ROBLOX_DIM_HEADERS = {"VIOLATION CATEGORY", "IDENTIFICATION SOURCE",
                       "TYPE OF ACTION", "MEDIA TYPE", "CATEGORY"}
_ROBLOX_VALUE_HEADERS = {"TOTAL FLAGGED", "TOTAL ACTIONS", "CONTENT REMOVED",
                         "ACTIONS WITH USER CONSEQUENCES", "APPROVED APPEALS",
                         "TOTAL APPEALS"}


def parse_roblox(slug, path):
    out = []
    lines = []
    with fitz.open(path) as doc:
        for page in doc:
            for ln in page.get_text().splitlines():
                t = ln.replace("​", "").replace("‌", "").strip()
                if t:
                    lines.append((page.number + 1, t))

    seen_tables = {}
    i = 0
    while i < len(lines):
        pg, t = lines[i]
        if t not in _ROBLOX_DIM_HEADERS:
            i += 1
            continue
        # collect the full header run: dims, then value columns (a value header
        # may word-wrap across two lines, e.g. "ACTIONS WITH USER"/"CONSEQUENCES")
        dims, vals = [t], []
        j = i + 1
        while j < len(lines) and lines[j][1] in _ROBLOX_DIM_HEADERS:
            dims.append(lines[j][1]); j += 1
        while j < len(lines):
            if lines[j][1] in _ROBLOX_VALUE_HEADERS:
                vals.append(lines[j][1]); j += 1
            elif (j + 1 < len(lines)
                  and lines[j][1] + " " + lines[j + 1][1] in _ROBLOX_VALUE_HEADERS):
                vals.append(lines[j][1] + " " + lines[j + 1][1]); j += 2
            else:
                break
        if not vals:
            i += 1
            continue
        key = "|".join(dims + vals)
        seen_tables[key] = seen_tables.get(key, 0) + 1
        table = " × ".join(d.title() for d in dims) + " → " + \
                " / ".join(v.title() for v in vals)
        if seen_tables[key] > 1:                 # 1.2 and 2.2 repeat verbatim
            table += f" (#{seen_tables[key]})"
        # walk rows: label [group?] + len(vals) numeric lines
        group = ""
        while j < len(lines):
            rpg, label = lines[j]
            lv, lu = _num(label)
            if lv is not None:                   # numeric where a label belongs
                break
            if re.match(r"^\d+(\.\d+)?[:.]\s", label):
                break                            # a section heading ends the table
            nxt = lines[j + 1][1] if j + 1 < len(lines) else ""
            nv, _u = _num(nxt)
            if nv is None:
                # two labels in a row → the first is a group header
                if len(dims) >= 2 and label in ("Account", "Content"):
                    group = label
                    j += 1
                    continue
                break                            # prose after the table → done
            row_vals = []
            k = j + 1
            while k < len(lines) and len(row_vals) < len(vals):
                v, u = _num(lines[k][1])
                if v is None or u != "count":
                    break
                row_vals.append(v); k += 1
            if len(row_vals) != len(vals):
                break
            row_label = f"{group} / {label}" if group and "total" not in label else label
            for col, v in zip(vals, row_vals):
                out.append(dict(company=slug, period=PERIOD, page=rpg,
                                table_label=table, row_label=row_label,
                                column=col.title(), value=v, unit="count",
                                raw=str(v)))
            j = k
        i = j
    return out


def main():
    rows = []
    for slug in GENERIC:
        p = os.path.join(PDF_DIR, f"2025-q3-{slug}.pdf")
        if os.path.isfile(p):
            rows += melt_generic(slug, p)
    for slug, parser in (("strava-inc", parse_strava), ("snap-inc", parse_snap),
                         ("roblox-corporation", parse_roblox)):
        p = os.path.join(PDF_DIR, f"2025-q3-{slug}.pdf")
        if os.path.isfile(p):
            rows += parser(slug, p)

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
