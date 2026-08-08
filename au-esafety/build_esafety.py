#!/usr/bin/env python3
"""Build the Australia eSafety BOSE — AI companion apps findings dataset (tidy-long).

Source: the eSafety Commissioner's **findings report** on the non-periodic
**Basic Online Safety Expectations (BOSE)** transparency notices given on
16 October 2025 to four AI companion service providers (Character.AI, Nomi, Chai,
Chub AI). Findings published March 2026; child-survey figures revised July 2026.

    https://www.esafety.gov.au/industry/basic-online-safety-expectations/ai-services/findings-october-2025

Output: ``au-esafety-ai-companion.json`` — ``{source, coverage, columns, rows}``
with columns ``provider, period, section, category, metric, unit, value``.

The rendered findings page, AI-services hub and media release are archived in
``raw/``. The figures below are transcribed from the findings page's chart text
versions and surrounding prose. ``main()`` still exits loudly when that archive
is absent so the output cannot silently outlive its source evidence.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT = os.path.join(HERE, "au-esafety-ai-companion.json")

FINDINGS_URL = (
    "https://www.esafety.gov.au/industry/basic-online-safety-expectations/"
    "ai-services/findings-october-2025"
)

# The four AI companion providers noticed on 16 October 2025 (display -> entity).
PROVIDERS = {
    "Character.AI": "Character Technologies, Inc.",
    "Nomi": "Glimpse.AI, Inc.",
    "Chai": "Chai Research Corp.",
    "Chub AI": "Chub.AI, Inc.",
}

# Coverage windows.
NOTICE_PERIOD = "2025-07-01..2025-09-30"
SURVEY_PERIOD = "2026"

COLUMNS = ["provider", "period", "section", "category", "metric", "unit", "value"]

# Figure 1: confirmed global user reports that breached provider Terms of
# Service. An absent provider/category combination is not converted to zero:
# the page sometimes says the category was not in the provider's Terms.
USER_REPORTS = {
    "Character.AI": {"pornography": 3_164, "csea": 1_527, "self_harm": 642},
    "Chai": {"pornography": 504, "csea": 8, "self_harm": 28},
    "Chub AI": {"csea": 47},
    "Nomi": {"pornography": 0, "csea": 2, "self_harm": 2},
}

# Figure 2, as at 30 September 2025. Chai's 6.5 is an FTE-style figure made up
# of engineers and moderators; Nomi reported seven total staff but none
# dedicated to trust and safety.
TRUST_SAFETY_STAFF = {
    "Character.AI": 37,
    "Chai": 6.5,
    "Chub AI": 0,
    "Nomi": 0,
}

# eSafety's demographically representative survey of 1,950 Australian children
# aged 10–17. Chai's ever-used figure was revised from 1% to 2% and the recent
# AI-companion figure from 3% to 4% in July 2026 after weighting adjustments.
SURVEY = [
    ("AI companion or assistant", "ever_used", 79),
    ("AI companion", "ever_used", 8),
    ("AI companion or assistant", "used_past_4_weeks", 66),
    ("AI companion", "used_past_4_weeks", 4),
    ("Character.AI", "ever_used", 5),
    ("Chai", "ever_used", 2),
    ("Chub AI", "ever_used", 0.4),
    ("Nomi", "ever_used", 0.3),
]


def _raw_files() -> list[str]:
    if not os.path.isdir(RAW):
        return []
    # Only real files count as fetched sources — a browser's "Webpage, Complete"
    # save drops an asset directory (e.g. findings_files/) beside the HTML, which
    # must not be mistaken for a raw report.
    return [
        f
        for f in os.listdir(RAW)
        if os.path.isfile(os.path.join(RAW, f)) and not f.startswith(".") and f != "FETCH.md"
    ]


def parse_findings(raw_dir: str) -> list[list]:
    """Return the audited numeric facts transcribed from the archived page."""
    findings = os.path.join(raw_dir, "findings-october-2025.html")
    if not os.path.isfile(findings):
        raise FileNotFoundError(f"missing rendered findings archive: {findings}")

    rows: list[list] = []
    for provider, harms in USER_REPORTS.items():
        for harm, value in harms.items():
            rows.append([
                provider, NOTICE_PERIOD, "reports", harm,
                "user_reports", "count", value,
            ])
    for provider, value in TRUST_SAFETY_STAFF.items():
        rows.append([
            provider, NOTICE_PERIOD, "staff", "trust_and_safety",
            "staff_responsible", "count", value,
        ])
    for provider, metric, value in SURVEY:
        rows.append([
            provider, SURVEY_PERIOD, "survey", "children_10_17",
            metric, "percent", value,
        ])

    for row in rows:
        assert len(row) == len(COLUMNS), row
        assert isinstance(row[-1], (int, float)) and not isinstance(row[-1], bool), row
    return rows


def main() -> None:
    if not _raw_files():
        sys.exit(
            "au-esafety: no source in raw/ — eSafety is WAF-blocked from this "
            "environment. Fetch the report from a residential browser first "
            "(see au-esafety/raw/FETCH.md). Refusing to emit a fabricated dataset."
        )

    rows = parse_findings(RAW)
    data = {
        "source": FINDINGS_URL,
        "coverage": NOTICE_PERIOD,
        "columns": COLUMNS,
        "rows": rows,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {OUT}: {len(rows)} rows")


if __name__ == "__main__":
    main()
