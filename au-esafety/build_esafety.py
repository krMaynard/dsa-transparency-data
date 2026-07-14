#!/usr/bin/env python3
"""Build the Australia eSafety BOSE — AI companion apps findings dataset (tidy-long).

Source: the eSafety Commissioner's **findings report** on the non-periodic
**Basic Online Safety Expectations (BOSE)** transparency notices given on
16 October 2025 to four AI companion service providers (Character.AI, Nomi, Chai,
Chub AI). Findings published March 2026; child-survey figures revised July 2026.

    https://www.esafety.gov.au/industry/basic-online-safety-expectations/ai-services/findings-october-2025

Output: ``au-esafety-ai-companion.json`` — ``{source, coverage, columns, rows}``
with columns ``provider, period, section, category, metric, unit, value``.

STATUS — SCAFFOLD. ``www.esafety.gov.au`` is WAF-blocked from datacenter IPs, so
the source has not been fetched yet (see ``raw/FETCH.md`` and the repo's
``BROWSER-FETCH-RUNBOOK.md``). This module therefore encodes the *design* — the
providers, the source URLs, the intended tidy-long schema — but does **not**
contain any figures. ``main()`` reads ``raw/`` and exits loudly if the report is
absent; it will never emit a fabricated dataset. The per-provider compliance
cells and survey percentages must be transcribed from the fetched report (with a
source comment per value, as ``singapore-online-safety/build_singapore.py`` does
for chart-only tables) before this produces rows.
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
NOTICE_PERIOD = "2025-10"          # notices given 16 Oct 2025 (response window)
SURVEY_PERIOD = "2026"             # eSafety child survey reported alongside

COLUMNS = ["provider", "period", "section", "category", "metric", "unit", "value"]

# Intended BOSE-expectation checks assessed per provider in the ``compliance``
# section — encode each as its own ``metric`` (unit='bool', value 0/1) when the
# report states a clear Yes/No. Names are the intended keys; confirm against the
# report's own headings before ingesting.
COMPLIANCE_METRICS = [
    "robust_age_verification",       # age assurance beyond app-store rating / self-declaration
    "self_harm_crisis_referral",     # refers users to mental-health/crisis support on self-harm
    "explicit_content_protections",  # guardrails against explicit/adult material for minors
    "reporting_mechanism",           # accessible reporting/complaint tools for the relevant harms
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
    """Extract tidy-long rows from the fetched report in ``raw/``.

    TODO (retry-from-residential-box): implement against the real report saved by
    ``raw/FETCH.md``. Expected to yield rows for:
      * section='survey'   (provider='All'): used_ai_companion / used_ai_companion_or_assistant
                            (unit='percent'), estimated_children (unit='count').
      * section='compliance' (per provider, per COMPLIANCE_METRICS): unit='bool', value 0/1.
      * section='provider_action' (per provider): post-notice remediation flags.
    Transcribe chart/image-only values with a source comment, like
    singapore-online-safety/build_singapore.py. Never fabricate.
    """
    raise NotImplementedError(
        "parse_findings() is a scaffold — implement it against the fetched "
        "report once raw/ is populated (see raw/FETCH.md)."
    )


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
