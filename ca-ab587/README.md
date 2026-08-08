# California — AB 587 Terms-of-Service reports

California's **AB 587** (Bus. & Prof. Code §§ 22675-22681) requires social-media
companies with over $100M in revenue to file a **semiannual Terms-of-Service
Report** with the California Attorney General. Each report describes, in prose,
how the company's terms of service define and enforce categories of content —
**hate speech, extremism, disinformation, harassment and foreign political
interference** — how automated content moderation works, and data on
terms-of-service violations. The AG publishes every filing in a public
repository:

<https://oag.ca.gov/ab587/submissions>

This is the **California analogue of New York's Stop-Hiding-Hate-Act ToS
reports** (`../ny-tos-reports/`) — the same content categories, a US-state
Attorney-General filing repository, archived PDFs — so it's built the same way:
a flat catalogue + a mirror of the PDFs + a narrative full-text extraction.

## Pipeline

| Script | What |
|--------|------|
| `build_ab587.py` | Parses the archived listing (`raw/submissions.html`) into `ca_ab587_reports.csv`; `--download` refreshes the listing and mirrors every report PDF into `pdfs/` (with sha256 + size). |
| `extract_narrative.py` | Pulls the prose of the `pdfs/` PDFs into `ca-ab587-narratives.json` (one row per page), matched to the catalogue by filename. |
| `extract_quant.py` | Conservatively extracts auditable statutory-category statistics from 12 early filings into `ca_ab587_normalized.csv`; see `QUANTITATIVE.md`. |

## Layout

| Path | What |
|------|------|
| `raw/submissions.html` | The AG repository listing page, archived verbatim. |
| `pdfs/*.pdf` | The mirrored report PDFs. |
| `ca_ab587_reports.csv` | The catalogue (one row per filing). |
| `ca-ab587-narratives.json` | The narrative full text, for search. |
| `ca_ab587_normalized.csv` | Best-effort normalized enforcement cells from early filings. |

## Reproduce

```bash
python3 build_ab587.py --download   # refresh listing + mirror all PDFs
python3 build_ab587.py              # rebuild the catalogue from raw/ + pdfs/
python3 extract_narrative.py        # rebuild the narratives from pdfs/
python3 extract_quant.py            # rebuild normalized statistics (PyMuPDF)
```

Deterministic from `raw/submissions.html` + `pdfs/` (rows sorted; no wall-clock).

## Catalogue schema

`[company, platform, period, period_original, access, source_url, filename, archived, sha256, bytes]`

- **company** — the filer, verbatim from the repository.
- **platform** — a normalised brand for grouping (Discord / TikTok / X / …).
- **period** — the reporting half-year, normalised (`2025 H2`); the partial first
  filings stay `2023 Q3` / `2023 Q4`. **period_original** keeps the AG's label.
- **access** — `public` (the AG mirrors every filing).
- **source_url** — the PDF on oag.ca.gov; **archived** — the GitHub mirror;
  **sha256 / bytes** — of the mirrored PDF.

The API seeds the catalogue into the read-only `ca_ab587_reports` table (behind
`GET /api/ca-ab587-reports` + the `/ca-ab587` page) and the narratives into the
FTS5 `report_narratives` table with `source='ca-ab587'`.

Coverage: 21 platforms, 2023 Q3 → 2025 H2 (100 filings). Periods are normalised
verbatim from the AG's "Submission Period" column, so a filing the AG labelled
`Q3/Q4 2026` surfaces as `2026 H2` (kept as filed, not corrected). Add newer
filings by re-running `build_ab587.py --download`.
