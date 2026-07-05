# EU — Terrorist Content Online (TCO) implementation reports

The **Terrorist Content Online Regulation** ([(EU) 2021/784](https://eur-lex.europa.eu/eli/reg/2021/784/oj/eng),
"TCOR") requires hosting service providers to remove terrorist content within
one hour of a competent authority's removal order and to publish annual
transparency reports. The **European Commission** publishes an annual **report
on the implementation of the Regulation**, each with a companion **staff working
document** setting out the detailed evidence (removal orders issued, cross-border
cooperation, specific measures, safeguards).

Those Commission documents — on EUR-Lex — are the retrievable, authoritative
**narrative** record of how the TCO regime is working. The platform-level TCO
transparency reports (Meta, X, …) are published only behind JavaScript
transparency centres and aren't machine-retrievable, so this corpus is the
**EU-institution layer**: the Commission reports + their staff working documents.

`build_eu_tco.py` pulls the prose of those PDFs so it can be full-text searched
alongside the other report narratives.

## Layout

| Path | What |
|------|------|
| `raw/*.pdf` | The EUR-Lex source PDFs, archived verbatim. |
| `build_eu_tco.py` | Pure-stdlib + pdfplumber extractor → `eu-tco-narratives.json`. `--download` refreshes raw/ from EUR-Lex. |
| `eu-tco-narratives.json` | The dataset the API is seeded from (vendored into `transparency-report-api/data/`). |

## Reproduce

```bash
python3 build_eu_tco.py              # rebuild from raw/
python3 build_eu_tco.py --download   # refresh raw/ from EUR-Lex first
```

Deterministic from `raw/` (rows sorted; no wall-clock).

## Schema (tidy long — one row per page of prose)

`[company, platform, period, page, heading, text]`

- **company** — the issuing body (`European Commission`).
- **platform** — the document kind (`Report` / `Staff Working Document`).
- **period** — the reporting year (`2024` / `2025`).
- **page** — 1-based page number in the source PDF.
- **heading** — the document's short title + its COM/SWD reference.
- **text** — the page's extracted text, whitespace-collapsed.

The API seeds this into the SQLite **FTS5** `report_narratives` table with
`source='eu-tco'`, behind `GET /api/narratives`. Current set: the 2024 + 2025
Commission implementation reports and the 2024 staff working document (52 pages);
add the next round to `DOCS` in `build_eu_tco.py` when the Commission publishes it.
