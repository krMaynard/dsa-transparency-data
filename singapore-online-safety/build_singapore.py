#!/usr/bin/env python3
"""Build the Singapore IMDA Online Safety dataset (tidy-long).

Source: the Online Safety Reports published under Singapore's **Code of Practice
for Online Safety** (issued by the Infocomm Media Development Authority, IMDA,
under the Broadcasting Act 1994 s.45). Six services are designated Designated
Social Media Services (DSMSs): Facebook, Instagram, TikTok, X, YouTube and
HardwareZone. Each files an annual online safety report; IMDA publishes its own
Online Safety Assessment Report (OSAR) benchmarking them.

Two streams are extracted, both archived verbatim under ``raw/``:

1. ``assessment`` — IMDA's OSAR cross-service benchmark tables (the normalised,
   comparable figures). From IMDA's "Mystery Shopper" tests: the *action rate*
   on legitimate user reports and the *average time to action*, per service, for
   both assessment rounds (OSAR 2024 and OSAR 2025). These live as charts in the
   OSAR PDFs, so the values are transcribed here from the published tables
   (OSAR 2025, "Areas where DSMSs have Improved", Tables 1 & 2) rather than
   text-scraped, and each is cited in ``README.md``.

2. ``platform_report`` — Singapore-specific figures each DSMS reports in its own
   annual report (period 1 Apr 2024 – 31 Mar 2025). These are heterogeneous per
   vendor, so metric names are kept per-service and are **not** comparable across
   services. Meta (Facebook/Instagram) and YouTube publish structured
   per-category tables (parsed from the PDF text layer here); TikTok and X give
   a handful of headline Singapore figures; HardwareZone reports essentially no
   Singapore statistics (IMDA flagged it for this).

Output: ``singapore-online-safety.json`` — ``{source, coverage, columns, rows}``
with columns ``service, period, section, category, metric, unit, value``.
"""
from __future__ import annotations

import json
import os
import re

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT = os.path.join(HERE, "singapore-online-safety.json")

LANDING = "https://www.imda.gov.sg/regulations-and-licensing-listing/content-standards-and-classification/standards-and-classification/internet/online-safety"

# Report coverage windows (YYYY-MM..YYYY-MM).
OSAR_2024 = "2023-08..2024-07"   # first OSAR: 1 Aug 2023 – 31 Jul 2024
PERIOD = "2024-04..2025-03"      # second cycle: 1 Apr 2024 – 31 Mar 2025

SERVICES = ["Facebook", "Instagram", "TikTok", "X", "YouTube", "HardwareZone"]


# ── Stream 1: IMDA OSAR benchmark tables (transcribed from the published charts) ──
# OSAR 2025, Table 1 (Action Rate on user reports, "Mystery Shopper" tests) and
# Table 2 (Average Time to Action), both giving the 2024 and 2025 rounds.
# service -> {round_period -> (action_rate_pct, time_to_action_days)}
OSAR = {
    "Facebook":     {OSAR_2024: (53, 9), PERIOD: (81, 4)},
    "Instagram":    {OSAR_2024: (2, 7),  PERIOD: (54, 4)},
    "TikTok":       {OSAR_2024: (39, 5), PERIOD: (25, 4)},
    "X":            {OSAR_2024: (54, 10), PERIOD: (74, 5)},
    "YouTube":      {OSAR_2024: (46, 5), PERIOD: (68, 4)},
    "HardwareZone": {OSAR_2024: (89, 3), PERIOD: (93, 2)},
}


def _text(name: str) -> str:
    with fitz.open(os.path.join(RAW, name)) as doc:
        return "\n".join(p.get_text() for p in doc)


# ── Stream 2a: Meta (Facebook / Instagram) per-category Singapore figures ──
# Each report gives, per Community Standards category: the volume of content
# "created in Singapore that we took action on", and the Singapore
# proactive-detection rate.
def parse_meta(name: str):
    """Yield (category, sg_content_actioned, sg_proactive_pct) per category.

    The count and the proactive rate for each category appear in separate
    sentences, so they are parsed with two passes and paired positionally. Both
    passes walk the document in the same per-category order; a length mismatch
    means the two passes fell out of step, so we fail loudly rather than align
    rates against the wrong categories.
    """
    txt = re.sub(r"\s+", " ", _text(name))
    # (category, count), in document order — a list, so repeated category labels
    # can't silently collapse.
    scale = {"thousand": 1000, "million": 1_000_000, None: 1}
    cats = []
    for m in re.finditer(
        # count may be "over 215.6 thousand", "about 4 million" or a bare "808".
        r"including (?:over |about )?([\d,.]+)(?: (thousand|million))? pieces of "
        r"content created in Singapore,? for violating (?:our )?Community "
        r"Standards on n? ?([A-Za-z()&,:/ -]+?)\s*\d",
        txt,
    ):
        val = float(m.group(1).replace(",", "")) * scale[m.group(2)]
        cats.append((_clean_cat(m.group(3)), int(round(val))))
    rates = re.findall(
        r"content created in Singapore, we proactively detected about ([\d.]+) ?percent",
        txt,
    )
    if len(rates) != len(cats):
        raise ValueError(
            f"{name}: parsed {len(cats)} category counts but {len(rates)} "
            f"proactive rates — the two passes are misaligned"
        )
    for (cat, count), pct in zip(cats, rates):
        yield cat, count, float(pct)


def _clean_cat(c: str) -> str:
    c = c.strip().rstrip(".").strip()
    # collapse the two "Dangerous Organisations and Individuals" sub-rows, which
    # the reports footnote as (Organized Hate) / (Terrorism)
    return c


# ── Stream 2b: YouTube per-reason Singapore tables ──
def parse_youtube():
    txt = _text("youtube-2025.pdf")

    def table(after: str):
        """Grab the `Reason\\n<name>\\n<number>` rows following a heading."""
        idx = txt.find(after)
        if idx < 0:
            return []
        chunk = txt[idx: idx + 900]
        rows = re.findall(r"([A-Za-z][A-Za-z ,/]+?)\s*\n\s*([\d,]+)", chunk)
        out = []
        for name, num in rows:
            name = name.strip()
            if name.lower() in ("reason", "number of flags received", "number of videos removed"):
                continue
            out.append((name, int(num.replace(",", ""))))
        return out

    flags = table("Table 1.1 End-user flags from Singapore IP address, by reason")
    removed = table("Table 1.2 Videos removed that were uploaded from a Singapore IP address, by reason")
    return flags, removed


# ── Stream 2c: TikTok & X headline Singapore figures (transcribed, cited in README) ──
TIKTOK = [
    ("", "videos_removed_sg", "count", 20493),
    ("", "videos_removed_proactively_sg", "count", 754231),
    ("", "reports_found_violative_sg", "count", 36602),
    ("under_13", "accounts_removed_sg", "count", 37610),
]
# X's report gives per-*policy* Singapore counts ("Accessible by"/"Originated
# from Singapore") that repeat across content categories and are footnoted as
# covering more than one category, so they can't be cleanly attributed or summed.
# Only X's single clearly-scoped Singapore figure is captured here; the rest is
# left as prose (see README).
X = [
    ("", "median_time_to_action_hours", "hours", 69),
]


def main():
    rows = []

    # Stream 1 — OSAR benchmark
    for svc in SERVICES:
        for period, (ar, tta) in OSAR[svc].items():
            rows.append([svc, period, "assessment", "", "action_rate", "percent", ar])
            rows.append([svc, period, "assessment", "", "time_to_action", "days", tta])

    # Stream 2a — Meta
    for svc, fname in (("Facebook", "facebook-2025.pdf"), ("Instagram", "instagram-2025.pdf")):
        for cat, count, pct in parse_meta(fname):
            rows.append([svc, PERIOD, "platform_report", cat, "content_actioned_sg", "count", count])
            if pct is not None:
                rows.append([svc, PERIOD, "platform_report", cat, "proactive_rate_sg", "percent", pct])

    # Stream 2b — YouTube
    flags, removed = parse_youtube()
    for cat, n in flags:
        rows.append(["YouTube", PERIOD, "platform_report", cat, "flags_received_sg", "count", n])
    for cat, n in removed:
        rows.append(["YouTube", PERIOD, "platform_report", cat, "videos_removed_sg", "count", n])

    # Stream 2c — TikTok & X
    for cat, metric, unit, val in TIKTOK:
        rows.append(["TikTok", PERIOD, "platform_report", cat, metric, unit, val])
    for cat, metric, unit, val in X:
        rows.append(["X", PERIOD, "platform_report", cat, metric, unit, val])

    data = {
        "source": LANDING,
        "coverage": PERIOD,
        "columns": ["service", "period", "section", "category", "metric", "unit", "value"],
        "rows": rows,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {OUT}: {len(rows)} rows")
    # quick summary
    from collections import Counter
    by_svc = Counter(r[0] for r in rows)
    print("rows per service:", dict(by_svc))


if __name__ == "__main__":
    main()
