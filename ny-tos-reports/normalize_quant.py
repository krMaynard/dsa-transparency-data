#!/usr/bin/env python3
"""Normalize the extracted NY ToS enforcement statistics to the Stop Hiding
Hate Act's five content categories.

Reads the committed ``ny_tos_quant.csv`` (produced by ``extract_quant.py``) and
writes ``ny_tos_normalized.csv`` — the subset of cells whose row label is a
*content category* in the filing company's own taxonomy, tagged with the SHHA
category it corresponds to. Methodology, the full mapping rationale, and the
caveats live in ``NORMALIZATION.md`` — read that before comparing anything
across companies.

Design rules (see NORMALIZATION.md §Methodology):

* **Only the category dimension is normalized.** Metrics (what was counted:
  flagged / actioned / warned / removed / appealed …) keep each company's own
  ``metric``/``submetric`` labels and are *not* comparable across companies.
* **Curated, exhaustive, fail-loud mapping.** Every distinct (company,
  row_label) in the extraction must have an explicit disposition below —
  ``map`` (→ a SHHA category), ``total`` (cross-category total row),
  ``dimension`` (a format/channel/method breakdown, not a category), or
  ``out_of_scope`` (a real category outside the SHHA five). An unknown label
  raises, so a re-extraction can never silently mis-normalize.
* **Conservative.** A label maps only when it squarely covers a SHHA category;
  broader/adjacent categories stay ``out_of_scope`` rather than being forced.

Stdlib-only; deterministic from the committed CSV.

Re-run:  ``python3 normalize_quant.py``
"""
import csv
import os
import re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "ny_tos_quant.csv")
DST = os.path.join(HERE, "ny_tos_normalized.csv")

# The five categories of NY GBS §1100(2) (Stop Hiding Hate Act).
SHHA = {
    "A": "hate_speech_or_racism",
    "B": "extremism_or_radicalization",
    "C": "disinformation_or_misinformation",
    "D": "harassment",
    "E": "foreign_political_interference",
}

# Strava appends a content-format suffix to its category labels
# ("Hateful Content - Photo"); split it off so the base category maps once.
_STRAVA_FORMATS = ("Activity", "Club", "Comment", "Other", "Photo", "Post",
                   "Profile", "Segment", "Video")
_STRAVA_SUFFIX = re.compile(r"\s*-\s*(" + "|".join(_STRAVA_FORMATS) + r")$")

# Disposition of every distinct row label per company. Values:
#   ("map", "A".."E")  — the label squarely corresponds to that SHHA category
#   ("total",)         — cross-category total row (excluded: would double count)
#   ("dimension",)     — a breakdown by format/channel/detection method, not a
#                        content category (excluded)
#   ("out_of_scope",)  — a genuine category in the company's taxonomy that is
#                        not one of the SHHA five (excluded, listed in the doc)
DISPOSITIONS = {
    "discord-inc": {
        # Discord reports directly in the statute's own categories (its tables
        # also carry an "(E) Foreign Political Interference" row, but every
        # value is "N/A" so no numeric cell reaches the extraction).
        "(A) Hate speech or racism": ("map", "A"),
        "(B) Extremism or radicalization": ("map", "B"),
        "(C) Disinformation or misinformation": ("map", "C"),
        "(D) Harassment": ("map", "D"),
        "Total (global data)": ("total",),
    },
    "reddit-inc": {
        "Hateful content": ("map", "A"),
        # Reddit's narrowest extremism-adjacent category; terrorism is the core
        # of "extremism or radicalization" though not its full breadth.
        "Terrorism": ("map", "B"),
        "Harassment": ("map", "D"),
    },
    "linkedin-corporation": {
        "Hateful and derogatory": ("map", "A"),
        # LinkedIn's standard industry category for terrorist/violent-extremist
        # organizations and their supporters.
        "Dangerous organizations or individuals": ("map", "B"),
        # Broader than mis/disinformation (includes scams & inauthentic
        # content) — documented as an over-inclusive mapping.
        "False and misleading": ("map", "C"),
        "Harassment": ("map", "D"),
        # Content-format / detection-method / channel breakdowns:
        "Comment": ("dimension",), "Post": ("dimension",),
        "Post with images": ("dimension",), "Post with video": ("dimension",),
        "Text only": ("dimension",), "Job post": ("dimension",),
        "Other / miscellaneous": ("dimension",),
        "Other (e.g. Pages, Groups, Events)": ("dimension",),
        "By LinkedIn content moderators": ("dimension",),
        "By LinkedIn systems": ("dimension",),
        "LinkedIn automated system": ("dimension",),
        "LinkedIn manual investigation": ("dimension",),
        "Member report": ("dimension",),
    },
    "naver-corporation": {
        "Hate Speech": ("map", "A"),
        "Self-Harm": ("out_of_scope",),
        "Impersonation": ("out_of_scope",),
        "TOTAL": ("total",), "Total": ("total",),
        # Service/channel and detection-method breakdowns:
        "BAND": ("dimension",), "CHAT": ("dimension",),
        "CONTENTS": ("dimension",), "USER": ("dimension",),
        "USER REPORT": ("dimension",), "User report": ("dimension",),
        "Moderator Review": ("dimension",),
        "Machine Detection": ("dimension",),
        "MACHINE DETECTION": ("dimension",),
    },
    "roblox-corporation": {
        # Roblox's appendix explicitly equates its Community Standards to the
        # statute's categories ("Extremism or Radicalization" ⇔ "Terrorism and
        # Violent Extremism", etc.), so these mappings are the company's own.
        "Discrimination, Slurs, and Hate Speech": ("map", "A"),
        "Terrorism and Violent Extremism": ("map", "B"),
        "Threats, Bullying, and Harassment": ("map", "D"),
        "Threats, Bullying & Harassment": ("map", "D"),   # spelling varies
        "Grand total": ("total",), "Content total": ("total",),
        "Account total": ("total",),
        # Media-type / channel / detection-method / action-type breakdowns:
        **{lab: ("dimension",) for lab in (
            "Account", "Account / Account", "Account / Chat", "Account / Voice",
            "Ads", "Audio", "Avatar Item", "Community", "Image", "Model",
            "Place", "Unclassified", "User Profile", "Video",
            "Content / Ads", "Content / Audio", "Content / Avatar",
            "Content / Avatar Item", "Content / Community", "Content / Image",
            "Content / Model", "Content / Place", "Content / Text",
            "Content / Unclassified", "Content / User Profile",
            "Content / Video",
            "Abuse Report", "Machine Detection", "Moderator Review",
            "Automated", "Manual",
        )},
    },
    "snap-inc": {
        # Snap's single enforcement table uses near-statute category names.
        "Hate Speech": ("map", "A"),
        "Terrorism & Violent Extremism": ("map", "B"),
        "False Information": ("map", "C"),
        "Harassment": ("map", "D"),
    },
    "strava-inc": {
        "Hateful Content": ("map", "A"),
        "False or misleading information": ("map", "C"),
        "Harassment": ("map", "D"),
        # Violence/graphic content is not one of the SHHA five; Strava itself
        # says its policies address the statute's categories only "in whole or
        # in part".
        "Dangerous, violent, or graphic content": ("out_of_scope",),
        "TOTAL": ("total",),
    },
}

OUT_COLS = ["company", "period", "shha_category", "original_label",
            "content_format", "grain", "metric", "submetric",
            "value", "unit", "page"]


def main():
    with open(SRC, encoding="utf-8") as f:
        cells = list(csv.DictReader(f))

    out = []
    tally = Counter()
    coverage = {}          # company -> set of SHHA letters with data
    unknown = set()
    for c in cells:
        co, label = c["company"], c["row_label"]
        fmt = ""
        if co == "strava-inc":
            m = _STRAVA_SUFFIX.search(label)
            if m:
                fmt, label = m.group(1), _STRAVA_SUFFIX.sub("", label)
        disp = DISPOSITIONS.get(co, {}).get(label)
        if disp is None:
            unknown.add((co, label))
            continue
        tally[(co, disp[0])] += 1
        if disp[0] != "map":
            continue
        letter = disp[1]
        coverage.setdefault(co, set()).add(letter)
        out.append({
            "company": co, "period": c["period"],
            "shha_category": SHHA[letter],
            "original_label": c["row_label"],
            "content_format": fmt,
            # Strava's un-suffixed rows are that category's total; suffixed
            # rows are its per-format breakdown (summing both double counts).
            "grain": "breakdown" if fmt else "category_total",
            "metric": c["table_label"], "submetric": c["column"],
            "value": c["value"], "unit": c["unit"], "page": c["page"],
        })

    if unknown:
        listing = "\n".join(f"  {co}: {lab!r}" for co, lab in sorted(unknown))
        raise SystemExit(
            f"Labels without a disposition (add them to DISPOSITIONS):\n{listing}")

    out.sort(key=lambda r: (r["company"], r["shha_category"],
                            r["original_label"], r["metric"], r["submetric"],
                            r["content_format"]))
    with open(DST, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OUT_COLS)
        w.writeheader()
        w.writerows(out)

    print(f"{len(out)} normalized cells → {os.path.basename(DST)}\n")
    print("Disposition of extracted cells per company:")
    for co in sorted(DISPOSITIONS):
        parts = [f"{kind}={tally[(co, kind)]}"
                 for kind in ("map", "total", "dimension", "out_of_scope")
                 if tally[(co, kind)]]
        print(f"  {co:26} {', '.join(parts) or '(none)'}")
    print("\nSHHA category coverage (categories with numeric data):")
    for co in sorted(DISPOSITIONS):
        got = coverage.get(co, set())
        line = " ".join(f"{L}:{'Y' if L in got else '-'}" for L in "ABCDE")
        print(f"  {co:26} {line}")


if __name__ == "__main__":
    main()
