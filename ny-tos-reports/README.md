# New York Social Media Terms-of-Service Reports

Archive + catalogue of the **terms-of-service reports** that social-media
companies file with the **New York State Attorney General** under the
**Stop Hiding Hate Act** ([S895B](https://www.nysenate.gov/legislation/bills/2025/S895) /
A6789B).

The law requires social-media platforms with over **$100 million** in annual
revenue and New York users to file **twice-yearly** reports describing their
terms of service and how they define, moderate, and report on hateful conduct,
racism, extremism, disinformation, harassment, and foreign political
interference. The AG publishes each filing as a narrative **policy PDF**:

> https://ag.ny.gov/resources/organizations/social-media-tos-reporting/reports

These are **qualitative policy documents**, not the EU DSA Annex-I
machine-readable workbooks, so they aren't extracted into the 1–11 template like
the rest of this repo — we mirror the original PDFs (as
[`download_pdfs.py`](../download_pdfs.py) does for PDF-format DSA reports) and
build a flat catalogue.

## Contents

| Path | What |
|------|------|
| [`../ny_tos_reports.csv`](../ny_tos_reports.csv) | Catalogue — one row per filing (all **29**) |
| [`../ny_tos_reports.json`](../ny_tos_reports.json) | Same catalogue, JSON |
| `pdfs/` | The archived PDFs (`<period>-<company>[-<platform>].pdf`) |

Catalogue columns: `company`, `platform` (the child platform/brand, when the
filing names one), `period` (`2025 Q3` / `2025 Q4`), `upload_date`, `access`,
`source_url`, `filename`, `archived`, `sha256`, `bytes`.

## Access note — 18 of 29 filings are login-gated at the source

The AG serves the **older filings** from a public directory
(`/sites/default/files/social-media-policy-report/…`) but serves **newer
filings** from a private Drupal *webform* directory
(`/system/files/webform/…`) that **302-redirects anonymous requests to a login
page**. Those files are publicly *listed* on the index but cannot be downloaded
without an account — almost certainly a misconfiguration on the AG's side
(webform file uploads default to private in Drupal).

So the catalogue records **all 29** filings, but only the **11 publicly
downloadable** ones are mirrored here as PDFs:

| `access` | Count | Meaning |
|----------|-------|---------|
| `public` | 11 | Mirrored under `pdfs/`; `archived`/`sha256`/`bytes` populated |
| `auth-required` | 18 | Login-gated at source; catalogued with `source_url` only |

If the AG later exposes the gated files publicly, re-running the scraper will
pick them up automatically.

## Companies (29 filings)

Naver, Amazon (Twitch, GoodReads), Kick, TikTok, Nextdoor, Strava, Roblox,
Reddit, X Corp, Discord, LinkedIn, Agile Sports (Hudl), Vimeo, Snap, Alphabet
(YouTube), and Meta (Facebook, Instagram, Threads) — across **2025 Q3** and
**2025 Q4**.

## Regenerating

```bash
python3 scrape_ny_tos.py     # network required
```

Walks every page of the AG index, downloads each publicly-served PDF (verifying
the `%PDF` magic), and rewrites the catalogue. Like the other `download_*` /
`scrape_*` scripts it hits the live web and is **not** run by CI.

## Quantitative data (`extract_quant.py`)

These filings follow **no shared template** — most are narrative policy / ToS
documents, and only some embed enforcement-statistics tables, each in the
company's own layout. `extract_quant.py` pulls the numeric tables out of the
archived PDFs into a tidy long CSV/JSON — one row per numeric cell, so each
table's shape is preserved as `table_label × row_label × column` without forcing
a (non-existent) cross-company schema:

```bash
pip install pymupdf
python3 extract_quant.py     # reads pdfs/, writes ny_tos_quant.csv / .json
```

Columns: `company`, `period`, `page`, `table_label`, `row_label`, `column`,
`value`, `unit` (`count` / `percent`), `raw`.

**Coverage (2025 Q3, 1,482 cells from 7 of the 11 archived reports):**

| Report | Cells | Notes |
|--------|------:|-------|
| Strava | 1,104 | category × content-format rows across its 5 data tables (flagged / actioned / actions-against-users / times-shared / appeals), 6 columns each — bespoke parser |
| Roblox | 126 | per-category + media-type / detection-source / action-type tables (flagged / actioned / user consequences / removed / appeals) — bespoke parser |
| Snap | 104 | 4 near-statute categories × Human-Report/Proactive-Detection × 13 measures (incl. Violative View Rates) — bespoke parser; its *policy* pages are screenshots but the data table is real text |
| LinkedIn | 49 | by category (Hateful & derogatory / Dangerous orgs / False & misleading / Harassment) |
| Discord | 38 | by the **Stop Hiding Hate Act categories** (hate speech/racism, extremism, disinformation, harassment, foreign interference) × action |
| Naver | 37 | by category + flagging method |
| Reddit | 24 | by violation type, with automation/user-report split + appeals |

The other four carry **no extractable enforcement statistics**: X, TikTok, Meta,
and Vimeo are narrative ToS / policy text (no count tables). The script lists
these explicitly rather than silently dropping them.

Best-effort and **not run by CI** (needs `pymupdf`; PDF table detection is
imperfect — cells whose label/header carries a stray 3+ digit run are dropped as
melt artifacts). Spot-checked against the source PDFs (e.g. Strava
*Harassment – Profile* = 6,665/6,522/0/143/12/0; Discord *Accounts Disabled*
hate-speech = 279).

## Normalized to the Stop Hiding Hate Act categories (`normalize_quant.py`)

Only Discord reports in the statute's own five categories; everyone else uses
their own taxonomy. `normalize_quant.py` maps each company's *category* labels
onto the SHHA five via a curated, exhaustive, fail-loud disposition table and
writes [`ny_tos_normalized.csv`](ny_tos_normalized.csv) (1,090 cells;
stdlib-only, deterministic from `ny_tos_quant.csv`). Metrics are **not**
normalized — they stay in each company's own terms and are not comparable
across companies.

**Read [`NORMALIZATION.md`](NORMALIZATION.md) before using this file** — it
documents the full methodology, every mapping judgment (e.g. Reddit
*Terrorism* → extremism ⚠; Roblox's mappings come from its own appendix
cross-references), the coverage matrix, and the caveats (global-not-NY scope,
one quarter only, no company reports foreign political interference numbers).

```bash
python3 normalize_quant.py   # ny_tos_quant.csv → ny_tos_normalized.csv
```

## Narrative full text (`extract_narrative.py`)

The filings are **narrative policy documents** — prose, not just tables. While
`extract_quant.py` pulls out the numbers, `extract_narrative.py` pulls out the
**prose** so it can be full-text searched: for each publicly archived PDF in
`pdfs/` it emits one tidy row per page —
`[company, platform, period, page, heading, text]` — into
[`ny_tos_narratives.json`](ny_tos_narratives.json) (488 pages across the 11
public filings; deterministic from `pdfs/` + the catalogue). The API seeds this
into a SQLite **FTS5** table behind `GET /api/narratives`, so a reader can
search the actual language platforms use to describe their hate-speech,
extremism, disinformation, harassment and foreign-political-interference
policies, and jump to the page in the archived PDF.

```bash
python3 extract_narrative.py   # pdfs/*.pdf → ny_tos_narratives.json
```
