#!/usr/bin/env python3
"""Build the Korea Network Act (illegal-sexual-content) transparency dataset.

South Korea's amended **Network Act** (Act on Promotion of Information and
Communications Network Utilization and Information Protection, Art. 64-5) and
**Telecommunications Business Act** (Art. 22-5), in force since 2020, require
online service providers to publish an **annual transparency report** on the
technical/managerial measures they take to prevent the circulation of *illegal
sexual content* (illegally-filmed content, deepfake/"fake" images and videos,
and child/youth sexual-abuse material).

**Google** publishes one such report per calendar year covering **Search and
YouTube jointly**. This builder transcribes the single quantitative table (the
monthly Jan–Dec breakdown, §II of the report) from Google's 2025 report
(archived in ``raw/google-korea-network-act-2025.pdf``) into a tidy-long
``korea-network-act.json`` — ``{source, publisher, coverage, columns, rows}``
with columns ``publisher, period, section, category, metric, unit, value``.

Design choices:
 * **Monthly only.** ``period`` is ``2025-01`` … ``2025-12``; the report's
   annual "Total" column is used only to *validate* (each row's twelve months
   must sum to it), never stored — so summing over ``period`` is a legitimate
   annual total, not a total-plus-parts double count.
 * **Disjoint categories per section.** Within a ``section`` the categories
   partition that section's requests/URLs (they sum to the reported section
   total, checked below), so summing over ``category`` within one section is a
   legitimate grand total. The report's "Total" rows are therefore dropped.
 * **Sections are cross-cuts, not additive.** ``requests_received`` (by
   complainant), ``request_reasons`` (by reason) and ``processed_result`` (by
   outcome) are three cuts of the SAME 115,280 requests; ``removal_reasons`` is
   a cut of the 92,334 removed. Pin a ``section`` (and ``metric``) before
   aggregating — never sum across sections.

Every breakdown is cross-checked against the report's stated totals (both the
per-row annual total and the section grand total); the build raises on any
mismatch, so a mistranscription can't slip through.
"""
from __future__ import annotations

import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "korea-network-act.json")

PUBLISHER = "Google"
YEAR = 2025
SOURCE = ("https://storage.googleapis.com/transparencyreport/report-downloads/"
          "south-korea-network-act_2025-1-1_2025-12-31_en_v1.pdf")

PERIODS = [f"{YEAR}-{m:02d}" for m in range(1, 13)]

# section, metric, unit, {category: [Jan … Dec]}. Transcribed from §II (p. 14)
# of the report — the monthly table. Each list is the twelve Jan–Dec values;
# the annual total and the section grand total are validated below.
TABLE = [
    # Requests received, by complainant type (partition of all requests).
    ("requests_received", "requests", "count", {
        "Victims etc. (User Requests)":
            [1549, 1268, 1343, 2201, 1255, 1129, 1310, 1373, 3535, 2094, 2369, 2433],
        "Agency and Org (Gov Requests)":
            [2377, 2971, 2902, 4482, 5908, 8061, 8269, 6751, 15720, 12310, 14059, 9611],
    }),
    # Requests received, by reason (partition of all requests).
    ("request_reasons", "requests", "count", {
        "Illegal Photos and Videos":
            [3849, 4137, 4181, 6632, 7120, 9108, 9513, 7992, 18795, 14084, 16359, 11933],
        "Fake Images and Videos":
            [74, 101, 43, 38, 42, 46, 15, 43, 138, 61, 22, 27],
        "Child or Youth Sexual Abuse Content":
            [3, 1, 21, 13, 1, 36, 51, 89, 322, 259, 47, 84],
    }),
    # Processed result, by outcome (partition of all requests).
    ("processed_result", "urls", "count", {
        "Removed Voluntarily by the Company":
            [3089, 3727, 3358, 5343, 6066, 7119, 7801, 6604, 15671, 11390, 12825, 9341],
        "Not Removed - Not Enough Information":
            [197, 128, 381, 171, 182, 979, 536, 205, 620, 860, 476, 593],
        "Not Removed - Content Already Removed":
            [102, 78, 94, 214, 198, 96, 119, 99, 418, 311, 234, 247],
        "Not Removed - Content Not Found":
            [441, 242, 325, 718, 658, 856, 1012, 932, 2045, 1459, 2623, 1530],
        "Not Removed - Other":
            [97, 64, 87, 237, 59, 140, 111, 284, 501, 384, 270, 333],
        "KCSC Assessment - Removed after the Assessment":
            [0] * 12,
        "KCSC Assessment - N/A (False Positive, Dismissals etc.)":
            [0] * 12,
    }),
    # Reasons for removal, by reason (partition of the removed URLs).
    ("removal_reasons", "urls_removed", "count", {
        "Illegal Photos and Videos":
            [3032, 3638, 3331, 5314, 6031, 7073, 7801, 6565, 15542, 11377, 12802, 9324],
        "Fake Images and Videos":
            [57, 89, 26, 29, 35, 31, 0, 37, 127, 12, 19, 15],
        "Child or Youth Sexual Abuse Content":
            [0, 0, 1, 0, 0, 15, 0, 2, 2, 1, 4, 2],
    }),
]

# The report's stated annual totals, used to fail loudly on mistranscription.
# Per-row: the "Total" column on p. 14. Per-section: the grand total the report
# prints for that block.
EXPECT_ROW_TOTALS = {
    ("requests_received", "Victims etc. (User Requests)"): 21859,
    ("requests_received", "Agency and Org (Gov Requests)"): 93421,
    ("request_reasons", "Illegal Photos and Videos"): 113703,
    ("request_reasons", "Fake Images and Videos"): 650,
    ("request_reasons", "Child or Youth Sexual Abuse Content"): 927,
    ("processed_result", "Removed Voluntarily by the Company"): 92334,
    ("processed_result", "Not Removed - Not Enough Information"): 5328,
    ("processed_result", "Not Removed - Content Already Removed"): 2210,
    ("processed_result", "Not Removed - Content Not Found"): 12841,
    ("processed_result", "Not Removed - Other"): 2567,
    ("processed_result", "KCSC Assessment - Removed after the Assessment"): 0,
    ("processed_result", "KCSC Assessment - N/A (False Positive, Dismissals etc.)"): 0,
    ("removal_reasons", "Illegal Photos and Videos"): 91830,
    ("removal_reasons", "Fake Images and Videos"): 477,
    ("removal_reasons", "Child or Youth Sexual Abuse Content"): 27,
}
EXPECT_SECTION_TOTALS = {
    "requests_received": 115280,
    "request_reasons": 115280,
    "processed_result": 115280,
    "removal_reasons": 92334,
}


def build_rows():
    rows = []
    for section, metric, unit, cats in TABLE:
        section_sum = 0
        for cat, months in cats.items():
            if len(months) != 12:
                raise ValueError(f"{section}/{cat}: expected 12 months, got {len(months)}")
            row_total = sum(months)
            expected = EXPECT_ROW_TOTALS[(section, cat)]
            if row_total != expected:
                raise ValueError(f"{section}/{cat}: months sum to {row_total:,} "
                                 f"!= stated annual total {expected:,}")
            section_sum += row_total
            for period, val in zip(PERIODS, months, strict=True):
                rows.append((PUBLISHER, period, section, cat, metric, unit, val))
        if section_sum != EXPECT_SECTION_TOTALS[section]:
            raise ValueError(f"{section}: categories sum to {section_sum:,} "
                             f"!= stated section total {EXPECT_SECTION_TOTALS[section]:,}")
    return rows


def main():
    rows = build_rows()
    data = {
        "source": SOURCE,
        "publisher": PUBLISHER,
        "coverage": f"{YEAR}-01..{YEAR}-12",
        "columns": ["publisher", "period", "section", "category", "metric", "unit", "value"],
        "rows": rows,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    print(f"wrote {OUT}: {len(rows)} rows")
    print("rows per section:", dict(Counter(r[2] for r in rows)))


if __name__ == "__main__":
    main()
