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
| `sources.csv` | Status of **every** `harmonised_template = yes` platform: `extracted`, `file-blocked`, or `hub-pending`. |
| `extract.py` | The extractor — re-run after adding files to `raw/`. |

## The 11 sections (fixed template order)

1. `report_identification` · 2. `categories_names` · 3. `member_states_orders` ·
4. `notices` (Art. 16) · 5. `own_initiative_illegal` · 6. `own_initiative_TC` ·
7. `appeals_and_recidivism` · 8. `automated_means` · 9. `human_resources` ·
10. `AMAR` (avg monthly active recipients — VLOP/VLOSE only) · 11. `qualitative`.

Sheet names are sometimes localised (German for Web.de, French for Veepee), but
the section *order* is fixed, so the extractor maps by position. This is the same
table structure as the aggregated VLOP dataset (`t3`–`t11`).

## Status (52 template platforms)

- **8 extracted** — AboutYou, LinkedIn, ManoMano, Pinterest, Veepee, Vinted,
  Web.de, Wikipedia (their catalogue URL is a direct file link).
- **1 file-blocked** — Glassdoor's `.xlsx` URL returns a 403 bot-wall to this
  fetcher (Cloudflare). Needs a real browser session.
- **43 hub-pending** — the catalogue URL is a transparency *landing page*, not a
  direct file. Extracting these needs per-site navigation (and some are EU
  geo-fenced) to locate the actual template file. See `sources.csv`.

## Reproduce

```bash
pip install openpyxl xlrd          # .xlsx and legacy .xls readers
# (re-)download into raw/ as needed, then:
python3 extract.py                 # writes extracted/, manifest.json, summary.csv
```

Files were fetched with a browser User-Agent over HTTPS. All sources are public
transparency reports linked from the catalogue; nothing here is behind a login.
