#!/usr/bin/env python3
"""Build the EU Terrorist Content Online Regulation (TCO) transparency dataset.

Regulation (EU) 2021/784 ("TCOR") creates two annual transparency-reporting
duties:

- **Art. 7** — every hosting service provider that took action against terrorist
  content in a calendar year publishes a transparency report (items removed,
  removal orders received & actioned, complaints, reinstatements, reviews),
  before 1 March of the following year.
- **Art. 8** — every Member State's competent authority publishes an annual
  report on its activity (removal orders issued, Art. 5(4) exposure decisions,
  reviews, penalties). The European Commission additionally reports on the
  Regulation's implementation, aggregating the per-Member-State removal-order
  counts.

The reported figures are **sparse and scattered** across heterogeneous prose
PDFs (each platform's transparency centre, each authority's own site, EUR-Lex),
so — like ``japan-info-platform/build_japan_narratives.py`` — this builder
**transcribes** the figures from the archived source reports and **verifies**
each source with fail-loud anchor checks (a distinctive phrase / number that must
still appear in that report's text), rather than fragile prose parsing. If a
vendored PDF drifts, the build raises.

Two streams (``role``), emitted tidy-long:

- ``authority`` — the Art. 8 / Commission side. Per-Member-State
  ``removal_orders_issued`` (the comparable country data, **Romania included**)
  from the Commission's implementation report, plus an example national Art. 8
  report (Ireland's Coimisiún na Meán).
- ``platform`` — the Art. 7 side. Each publisher's enforcement figures, by the
  report's own sub-service breakdown where given (Spotify) or whole-service
  (Meta Facebook).

Output ``tco-regulation.json`` columns:
  publisher, role, period, section, category, metric, unit, value

Coverage is a starting set — more platforms (X, TikTok, Google, Microsoft, …)
and more national Art. 8 authorities slot in as their reports are archived.

Deterministic: reads only the archived ``raw/*.pdf`` + the curated SOURCES below;
no network, no wall-clock. Pure stdlib + PyMuPDF.
"""
from __future__ import annotations

import argparse
import json
import os
import re

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT_JSON = os.path.join(HERE, "tco-regulation.json")

COLUMNS = ["publisher", "role", "period", "section", "category", "metric", "unit", "value"]

# Each source: the archived PDF it's transcribed from, fail-loud `checks`
# (whitespace-insensitive substrings that must still appear in that PDF), and its
# `rows` — [section, category, metric, unit, value] tuples. `publisher`, `role`
# and `period` are shared across a source's rows.
SOURCES: list[dict] = [
    {
        # European Commission report on the implementation of the TCOR,
        # COM(2024) 64 final (14 Feb 2024). Aggregates the per-Member-State
        # removal-order counts issued 7 Jun 2022 (entry into application) to
        # 31 Dec 2023.
        "pdf": "ec-com-2024-64-implementation.pdf",
        "publisher": "European Commission",
        "role": "authority",
        "period": "2022-06..2023-12",
        "checks": ["twenty-three Member States", "at least 349 removal orders",
                   "Spain, Romania, France, Germany, Czechia and Austria",
                   "Sixty-two removal orders", "ANCOM", "sent two removal orders"],
        "rows": [
            # Per-Member-State removal orders issued (six MS issued orders).
            ["removal_orders_issued", "Germany", "removal_orders_issued", "count", 249],
            ["removal_orders_issued", "Spain", "removal_orders_issued", "count", 62],
            ["removal_orders_issued", "France", "removal_orders_issued", "count", 26],
            ["removal_orders_issued", "Austria", "removal_orders_issued", "count", 8],
            ["removal_orders_issued", "Romania", "removal_orders_issued", "count", 2],
            ["removal_orders_issued", "Czechia", "removal_orders_issued", "count", 2],
            # EU-level summary figures.
            ["removal_orders_issued", "EU", "total_removal_orders_issued", "count", 349],
            ["removal_orders_issued", "EU", "member_states_issuing_orders", "count", 6],
            ["removal_orders_issued", "EU", "member_states_with_designated_authority", "count", 23],
        ],
    },
    {
        # Ireland — Coimisiún na Meán, TCOR Article 8 transparency report 2024.
        # An Coimisiún is Ireland's Art. 12(1)(c)/(d) authority (oversight of
        # HSP specific measures + penalties), so it reports Art. 5(4) exposure
        # decisions rather than removal orders.
        "pdf": "ireland-cnam-art8-2024.pdf",
        "publisher": "Coimisiún na Meán (Ireland)",
        "role": "authority",
        "period": "2024",
        "checks": ["three HSPs were exposed to terrorist content",
                   "No penalties were imposed pursuant to Article 18",
                   "Meta Platforms Ireland Limited", "TikTok", "Twitter International"],
        "rows": [
            ["authority_activity", "Ireland", "art5_4_exposure_decisions", "count", 3],
            ["authority_activity", "Ireland", "review_proceedings", "count", 0],
            ["authority_activity", "Ireland", "penalties_imposed", "count", 0],
        ],
    },
    {
        # Spotify — EU TCO Art. 7 transparency report 2024 (published 26 Feb 2025).
        # Reports its enforcement per sub-service. "content_removed_via_orders" is
        # content removed after being reported in removal orders from EU national
        # competent authorities; "content_removed_proactive" is terrorism/violent-
        # extremism content removed under Spotify's own Platform Rules.
        "pdf": "spotify-art7-2024.pdf",
        "publisher": "Spotify",
        "role": "platform",
        "period": "2024",
        "checks": ["Findaway Voices", "removal orders from EU national competent authorities",
                   "449", "175"],
        "rows": [
            ["platform_enforcement", "Spotify", "content_removed_proactive", "count", 449],
            ["platform_enforcement", "Spotify", "content_removed_via_orders", "count", 2],
            ["platform_enforcement", "Spotify", "appeals_received", "count", 1],
            ["platform_enforcement", "Spotify", "review_proceedings", "count", 0],
            ["platform_enforcement", "Spotify", "decisions_reversed", "count", 0],
            ["platform_enforcement", "Spotify for Creators", "content_removed_proactive", "count", 175],
            ["platform_enforcement", "Spotify for Creators", "content_removed_via_orders", "count", 25],
            ["platform_enforcement", "Spotify for Creators", "appeals_received", "count", 6],
            ["platform_enforcement", "Spotify for Creators", "review_proceedings", "count", 0],
            ["platform_enforcement", "Spotify for Creators", "decisions_reversed", "count", 0],
            ["platform_enforcement", "Spotify for Artists", "content_removed_proactive", "count", 39],
            ["platform_enforcement", "Spotify for Artists", "content_removed_via_orders", "count", 8],
            ["platform_enforcement", "Spotify for Artists", "appeals_received", "count", 0],
            ["platform_enforcement", "Spotify for Artists", "review_proceedings", "count", 0],
            ["platform_enforcement", "Spotify for Artists", "decisions_reversed", "count", 0],
            ["platform_enforcement", "Findaway Voices", "content_removed_proactive", "count", 0],
            ["platform_enforcement", "Findaway Voices", "content_removed_via_orders", "count", 0],
            ["platform_enforcement", "Findaway Voices", "appeals_received", "count", 0],
            ["platform_enforcement", "Findaway Voices", "review_proceedings", "count", 0],
            ["platform_enforcement", "Findaway Voices", "decisions_reversed", "count", 0],
        ],
    },
    {
        # Meta — EU TCO Art. 7 transparency report for Facebook, 2023 (published
        # 29 Feb 2024). Received 143 order requests via its dedicated channel, of
        # which 15 were valid Competent-Authority orders and 10 led to removal /
        # access restriction. Its proactive figure (6.1M) covers a broader policy
        # set (Dangerous Organizations & Individuals, Violence & Incitement,
        # Coordinating Harm) than Spotify's terrorism-only scope and overlaps
        # Meta's Community Standards Enforcement Report — hence `approx_count`
        # (Meta rounds to millions/thousands). No Art. 10 complaints or reviews.
        "pdf": "meta-facebook-art7-2023.pdf",
        "publisher": "Meta",
        "role": "platform",
        "period": "2023",
        "checks": ["we received 143 requests through the dedicated channel",
                   "only 15 of them were in fact valid orders",
                   "10 of them led to content removal", "6.1 million pieces of content",
                   "857.2 thousand appeals", "restored 156 thousand",
                   "No complaints were handled by Meta in accordance with Article 10"],
        "rows": [
            ["platform_enforcement", "Facebook", "removal_order_requests_received", "count", 143],
            ["platform_enforcement", "Facebook", "removal_orders_valid", "count", 15],
            ["platform_enforcement", "Facebook", "content_removed_via_orders", "count", 10],
            ["platform_enforcement", "Facebook", "content_removed_proactive", "approx_count", 6100000],
            ["platform_enforcement", "Facebook", "appeals_received", "approx_count", 857200],
            ["platform_enforcement", "Facebook", "content_reinstated", "approx_count", 156000],
            ["platform_enforcement", "Facebook", "complaints_art10", "count", 0],
            ["platform_enforcement", "Facebook", "review_proceedings", "count", 0],
        ],
    },
]


def _pdf_text(path: str) -> str:
    # Join pages with a newline so a word at a page boundary can't glue onto the
    # first word of the next page (which would break an anchor check).
    with fitz.open(path) as doc:
        return "\n".join(page.get_text() for page in doc)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s)


def build(raw_dir: str) -> dict:
    rows: list[list] = []
    for src in SOURCES:
        path = os.path.join(raw_dir, src["pdf"])
        if not os.path.isfile(path):
            raise FileNotFoundError(f"archived source missing: {path}")
        text = _norm(_pdf_text(path))
        for chk in src["checks"]:
            if _norm(chk) not in text:
                raise ValueError(
                    f"{src['pdf']}: anchor {chk!r} not found — has the report changed?")
        for section, category, metric, unit, value in src["rows"]:
            rows.append([src["publisher"], src["role"], src["period"],
                         section, category, metric, unit, value])
    rows.sort(key=lambda r: (r[1], r[0], r[2], r[3], r[4], r[5]))
    years = sorted({y for r in rows for y in re.findall(r"\d{4}", r[2])})
    coverage = (years[0] if len(years) == 1 else f"{years[0]}..{years[-1]}") if years else ""
    return {
        "source": "EU Regulation 2021/784 (Terrorist Content Online Regulation)",
        "coverage": coverage,
        "columns": COLUMNS,
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raw", default=RAW, help="Dir of the archived source reports")
    ap.add_argument("--out", default=OUT_JSON, help="Output dataset JSON path")
    args = ap.parse_args()

    data = build(args.raw)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    pubs = sorted({r[0] for r in data["rows"]})
    print(f"wrote {args.out}: {len(data['rows'])} rows across {len(pubs)} publishers "
          f"({', '.join(pubs)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
