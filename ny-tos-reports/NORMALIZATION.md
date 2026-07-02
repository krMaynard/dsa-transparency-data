# Normalizing the NY ToS enforcement statistics to the Stop Hiding Hate Act categories

**Artifacts:** [`normalize_quant.py`](normalize_quant.py) → [`ny_tos_normalized.csv`](ny_tos_normalized.csv)
(968 cells, derived from the 1,272-cell [`ny_tos_quant.csv`](ny_tos_quant.csv) extraction).

New York's Stop Hiding Hate Act (GBS §1100(2)) defines five content categories
that covered social-media companies must report on:

| Key | Category |
|-----|----------|
| A | Hate speech or racism |
| B | Extremism or radicalization |
| C | Disinformation or misinformation |
| D | Harassment |
| E | Foreign political interference |

In practice **only Discord reports directly in these categories**. Every other
company reports in its own policy taxonomy, in its own table layouts, with its
own metrics. This document describes how — and how far — that data can be
normalized onto the statute's categories, and why the result must be read with
care.

## Methodology

1. **Source.** The input is `ny_tos_quant.csv` — the best-effort extraction of
   every numeric table cell from the 11 publicly-archived 2025 Q3 PDFs (see the
   [README](README.md#quantitative-data-extract_quantpy)). Six reports carry
   machine-readable tables (Discord, Reddit, LinkedIn, Naver, Roblox, Strava);
   the other five have no extractable statistics.
2. **Only the category dimension is normalized.** Each company's *metrics*
   (what was counted: flagged / actioned / warned / disabled / removed /
   appealed / viewed…) are kept verbatim in `metric` (the source table) and
   `submetric` (the source column). No attempt is made to equate, say,
   Discord's "Accounts Disabled" with Strava's "actioned items" — they measure
   different things at different grains.
3. **Curated, exhaustive, fail-loud mapping.** Every distinct
   `(company, row_label)` pair in the extraction has an explicit *disposition*
   in `normalize_quant.py`:
   - `map` → the label squarely corresponds to one SHHA category (kept, tagged);
   - `total` → a cross-category total row (excluded — keeping it alongside its
     parts would double count);
   - `dimension` → a breakdown by content format, channel, or detection method,
     not a content category (excluded);
   - `out_of_scope` → a genuine category in the company's taxonomy that is not
     one of the SHHA five (excluded, listed below).
   A label with no disposition makes the script exit with an error, so a future
   re-extraction can never silently mis-normalize new labels.
4. **Conservative mapping.** A label is mapped only when it squarely covers a
   SHHA category. Adjacent-but-different categories (e.g. Strava's "Dangerous,
   violent, or graphic content") are excluded rather than forced. Where a
   mapped label is broader or narrower than the statute's category, that
   judgment is documented below.
5. **Grain.** Strava reports each category as a base row (its total) plus
   per-format rows ("Hateful Content - Photo"). The base rows get
   `grain=category_total`, the suffixed rows `grain=breakdown` with the format
   in `content_format`. **Summing both grains double counts.**
6. **Determinism.** `normalize_quant.py` is stdlib-only and fully deterministic
   from the committed `ny_tos_quant.csv`; re-running it reproduces
   `ny_tos_normalized.csv` byte for byte.

## The mapping, per company

Judgment calls are flagged ⚠ — read them before citing cross-company numbers.

### Discord (36 mapped cells)
Reports directly in the statute's categories — mapped 1:1, no judgment needed.
Its tables include an "(E) Foreign Political Interference" row, but every value
is "N/A", so no numeric cell exists to normalize. "Total (global data)" rows
are excluded as totals.

### Reddit (24 mapped cells)
| Reddit label | → | Note |
|---|---|---|
| Hateful content | A | |
| Terrorism | B | ⚠ narrower than "extremism or radicalization" — terrorism is its core but not its full breadth |
| Harassment | D | |

### LinkedIn (36 mapped cells)
| LinkedIn label | → | Note |
|---|---|---|
| Hateful and derogatory | A | ⚠ slightly broader ("derogatory" content need not be hate speech) |
| Dangerous organizations or individuals | B | ⚠ the standard industry category for terrorist/violent-extremist organizations; can include non-extremist dangerous actors |
| False and misleading | C | ⚠ broader — includes scams and inauthentic content beyond mis/disinformation |
| Harassment | D | |

Format rows (Comment, Post, Text only, Job post…) and detection-method rows
(By LinkedIn systems, Member report…) are excluded as `dimension`. LinkedIn's
flagged-items table (its "A." table, PDF p. 7) lost its header in extraction,
so those cells carry an empty `metric`/`submetric` — they are the per-category
*number of flagged items*.

### Naver (2 mapped cells)
Only "Hate Speech" (→ A) is a SHHA category. "Self-Harm" and "Impersonation"
are real categories but out of scope; service/channel (BAND, CHAT…) and
detection-method rows are dimensions. Naver's numbers cover its **Global BAND
service only** (per its report), not all Naver products.

### Roblox (0 mapped cells)
Only total-grain rows ("Grand total", "Content total") survived extraction —
Roblox's per-category tables did not melt into label × value pairs the generic
extractor could keep. ⚠ **Roblox contributes nothing to the normalized file**
even though its PDF does contain per-category data; recovering it would need a
bespoke parser.

### Strava (870 mapped cells)
| Strava label | → | Note |
|---|---|---|
| Hateful Content | A | |
| False or misleading information | C | |
| Harassment | D | |
| Dangerous, violent, or graphic content | — | out of scope (violence/graphic content is not a SHHA category) |

Strava itself notes its policies address the statute's categories only
"in whole or in part". TOTAL rows are excluded as totals.

## Coverage matrix

Categories with at least one numeric datum in the normalized file:

| Company | A hate | B extremism | C disinfo | D harassment | E foreign interference |
|---|:-:|:-:|:-:|:-:|:-:|
| Discord | ✓ | ✓ | ✓ | ✓ | reported "N/A" |
| Reddit | ✓ | ✓ ⚠ | — | ✓ | — |
| LinkedIn | ✓ | ✓ ⚠ | ✓ ⚠ | ✓ | — |
| Naver | ✓ | — | — | — | — |
| Roblox | — | — | — | — | — |
| Strava | ✓ | — | ✓ | ✓ | — |

**No company reports numeric data on foreign political interference.**

## Caveats — read before comparing anything

1. **Metrics are not comparable across companies.** The normalization aligns
   *categories only*. "Accounts disabled" (Discord), "items actioned" (Strava),
   "posts removed" (Reddit) and "flagged items" (LinkedIn) are different events
   counted at different stages of different pipelines. Never sum or rank across
   companies; compare only within one company's own metric.
2. **Geographic scope differs and is mostly not New York.** Discord's tables
   are explicitly "global data"; Strava's and LinkedIn's appear platform-wide;
   Naver's cover one service (BAND). The statute is a NY law, but the filings
   largely report global enforcement volumes.
3. **Category boundaries are editorial.** The ⚠-flagged mappings (Terrorism →
   extremism; Dangerous organizations → extremism; False and misleading →
   disinformation; Hateful and derogatory → hate speech) are defensible but
   inexact — some are narrower than the statute's category (undercounting),
   some broader (overcounting). The `original_label` column always preserves
   what the company actually reported.
4. **Coverage is a floor, not a ceiling.** A missing cell means *no extractable
   number*, not *no enforcement*: 5 of 11 public reports are narrative-only or
   image-based (X, TikTok, Meta, Vimeo, Snap), Roblox's tables didn't survive
   extraction, and 18 of the 29 catalogued filings (including **all of
   2025 Q4**) are login-gated at the AG's site and not archived at all.
5. **One quarter only.** Everything here is 2025 Q3. No trend can be drawn yet.
6. **Grain discipline.** For Strava, use either `grain=category_total` or
   `grain=breakdown`, never both in one sum. Reddit's `percent` cells
   (`unit=percent`) are shares, not counts.
7. **Upstream extraction is best-effort.** PDF table detection is imperfect;
   the extraction was spot-checked against the source PDFs but not exhaustively
   audited. The `page` column lets any cell be verified against the archived
   PDF in [`pdfs/`](pdfs/).

## Regenerating

```bash
python3 extract_quant.py      # pdfs/ → ny_tos_quant.csv/.json  (needs pymupdf)
python3 normalize_quant.py    # ny_tos_quant.csv → ny_tos_normalized.csv  (stdlib)
```
