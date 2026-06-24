# Harmonised-template DSA transparency reports

Downloaded + extracted transparency reports from non-VLOP platforms that publish
in the **EU harmonised machine-readable template** (Implementing Regulation (EU)
2024/2835) — the fixed **11-section workbook** (tables 1–11 of the DSA reporting
template). These are the catalogue entries with `harmonised_template = yes` in
[`../REPORT_LOCATIONS.md`](../REPORT_LOCATIONS.md) / [`../dsa_reports.csv`](../dsa_reports.csv).

## Layout

| Path | What |
|------|------|
| `raw/` | The original files exactly as downloaded (`.xlsx`, legacy `.xls`, or `.zip` of per-section CSVs). |
| `extracted/<platform>/NN_<section>.csv` | One CSV per template section, normalised to the canonical English section order (1–11), regardless of the source format or sheet language. |
| `manifest.json` | Per-platform record: source file, format, provider, reporting period, EU AMAR total, sections found, per-section data-row counts. |
| `summary.csv` | Flat cross-platform headline table (provider · period · AMAR · row totals). |
| `sources.csv` | Status of **every** `harmonised_template = yes` platform: `extracted`, `format-variant`, `file-blocked`, or `hub-pending`. |
| `extract.py` | The extractor — re-run after adding files to `raw/`. |
| `discover_hubs.py` | Crawls the `hub-pending` landing pages for direct template-file links (writes `hub_candidates.json`). |
| `download_hubs.py` | Downloads the curated latest file per hub-discovered platform into `raw/`. |

## The 11 sections (fixed template order)

1. `report_identification` · 2. `categories_names` · 3. `member_states_orders` ·
4. `notices` (Art. 16) · 5. `own_initiative_illegal` · 6. `own_initiative_TC` ·
7. `appeals_and_recidivism` · 8. `automated_means` · 9. `human_resources` ·
10. `AMAR` (avg monthly active recipients — VLOP/VLOSE only) · 11. `qualitative`.

Sheet names are sometimes localised (German for Web.de, French for Veepee), but
the section *order* is fixed, so the extractor maps by position. This is the same
table structure as the aggregated VLOP dataset (`t3`–`t11`).

## Status (53 template platforms — see `sources.csv`)

- **28 extracted** — the 8 direct-file platforms, 19 found by crawling the
  landing pages (`discover_hubs.py`), and Dailymotion (provided directly):
  AboutYou, Ceneo, Cloudflare, Dailymotion, DuckDuckGo, Expedia, HomeToGo,
  Hostelworld, Hostinger, Hotels.com, IMDb, Konami, Lilo, LinkedIn, ManoMano,
  Match Group (Tinder), Niantic (Pokémon GO), Pinterest, Qwant, Roblox, Shopify,
  Skroutz, Veepee, Vinted, Vrbo, Web.de, Wikipedia, Yahoo. For multi-brand
  providers (Match Group, Niantic, Yahoo, DuckDuckGo, Expedia family) we keep one
  representative/flagship file per catalogue platform. (Dailymotion was catalogued
  as an HTML/narrative report until its standardized XLSX surfaced, so it had been
  marked `harmonised_template = no`; the catalogue is now corrected to `yes`.)
- **4 format-variant** — Discord (renumbers the sections), LINE (a 5-sheet
  variant), WordPress.com (a different report: DMCA / government / IRU requests,
  not the Annex I template), heise (a single combined CSV). Downloaded but not
  forced into the canonical 11-section shape.
- **1 file-blocked** — Glassdoor's `.xlsx` returns a 403 bot-wall.
- **20 hub-pending** — landing pages with no static file link (JS-rendered or
  the file sits behind a click), or that 403 a headless fetch. Need a real
  browser session and/or EU egress.

IMDb and Skroutz ship only sections 1–8 + 11 (no AMAR / human-resources); the
extractor maps by the section number in each sheet/file name, so the omitted
sections stay empty rather than shifting the others.

## Reproduce

```bash
pip install openpyxl xlrd          # .xlsx and legacy .xls readers
# (re-)download into raw/ as needed, then:
python3 extract.py                 # writes extracted/, manifest.json, summary.csv
```

Files were fetched with a browser User-Agent over HTTPS. All sources are public
transparency reports linked from the catalogue; nothing here is behind a login.
