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
| `download_zendesk.py` | Downloads the template file for Zendesk-hosted hubs whose landing page is JS-rendered, via the help-center attachments JSON API (no browser needed). |

## The 11 sections (fixed template order)

1. `report_identification` · 2. `categories_names` · 3. `member_states_orders` ·
4. `notices` (Art. 16) · 5. `own_initiative_illegal` · 6. `own_initiative_TC` ·
7. `appeals_and_recidivism` · 8. `automated_means` · 9. `human_resources` ·
10. `AMAR` (avg monthly active recipients — VLOP/VLOSE only) · 11. `qualitative`.

Sheet names are sometimes localised (German for Web.de, French for Veepee), but
the section *order* is fixed, so the extractor maps by the section number in each
sheet/file name. This is the same table structure as the aggregated VLOP dataset
(`t3`–`t11`).

**Format variants (`SHEET_MAP` in `extract.py`).** A few platforms file the same
template *content* under sheet names that don't carry a usable section number, so
position/number parsing would misplace them. For those, `extract.py` maps each
sheet to its canonical section by a name substring instead:

- **LINE** condenses the template into five unnumbered sheets
  (`report_identification`, `member_states_orders`, `notices`, `own_initiative`,
  `statements`) → sections 1, 3, 4, 5, 11. Its `own_initiative` sheet carries the
  illegal-content category × restriction-type grid with no surface column, so it
  maps to section 5 (not the ToS section 6); `statements` is the free-text
  indicator/value table → section 11.
- **Discord** omits own-initiative-on-illegal (5), human resources (9) and AMAR
  (10), then *renumbers* what remains 5–8 — so its "5. Own Initiative TC" is really
  section 6, "6. Appeals" is 7, "7. Automated Means" is 8 and "8. Qualitative" is
  11. Mapping by name keeps the renumbering from landing rows in the wrong table.

Reports that aren't the harmonised template at all (heise, WordPress.com) are
left as `format-variant` and archived rather than mapped, since forcing them into
1–11 would invent structure the source doesn't have.

## Status (54 template platforms — see `sources.csv`)

- **41 platforms extracted** (49 report files — AboutYou ships two consecutive periods; Miniclip ships eight games) — the 8 direct-file platforms, 19 found by crawling the
  landing pages (`discover_hubs.py`), Carrefour + Dailymotion (provided
  directly), 6 pulled from Zendesk help-center hubs via the article/attachments
  JSON API (`download_zendesk.py`), and Discord + LINE via `SHEET_MAP` (see below): AboutYou, Alibaba Cloud, Bumble, Carrefour, Ceneo, Cloudflare,
  Dailymotion, Depop, Discord, DuckDuckGo, Expedia, Grindr, HomeToGo, Hostelworld, Hostinger,
  Hotels.com, IMDb, Konami, Lilo, LINE, LinkedIn, ManoMano, Match Group (Tinder),
  Nexon, Miniclip (8 games), Niantic (Pokémon GO), Nintendo eShop, Pinterest, Qwant, Roblox, Shopify, Skroutz, Square Enix, Veepee,
  Vestiaire Collective, Vinted, Vrbo, Web.de, Whatnot, Wikipedia, Yahoo. For
  multi-brand providers (Match Group, Niantic, Yahoo, DuckDuckGo, Expedia family)
  we keep one representative/flagship file per catalogue platform. (Carrefour
  Marketplace, Dailymotion, Depop, Nexon, Nintendo eShop, Square Enix and Alibaba Cloud were catalogued as linked/HTML/PDF reports
  until their standardized XLSX files surfaced — all corrected to
  `harmonised_template = yes`.)
- **2 format-variant** — WordPress.com (a different report: DMCA / government /
  IRU requests, not the Annex I template) and heise (a short free-form Art. 15
  CSV summary with German free-text categories). Genuinely different report
  types — archived but not forced into the canonical 11-section shape, because
  mapping them would invent structure the source doesn't have.
- **1 file-blocked** — Glassdoor's `.xlsx` returns a 403 bot-wall.
- **16 hub-pending** — two sub-groups:
  - *Bot-walled* (Cloudflare/Akamai `403` to a headless fetch — need a real
    browser session and/or EU egress): Akamai, Epic Games, Faire, Jeuxvideo,
    Just Eat Takeaway, Upwork, x-kom.
  - *Non-template formats* (the page loads but publishes the report as HTML or
    PDF, not the Annex I workbook, so there is nothing to extract into 1–11):
    Apple Books / Podcasts / iCloud (rendered HTML), eToro (split section PDFs),
    Eventbrite & OVHcloud (narrative PDF), Flickr (no report file), GMX & Riot
    Games (JS/custom). The PDF reports are archived under
    [`../pdf-reports/`](../pdf-reports/). Candidates for reclassification to
    `format-variant`.

IMDb and Skroutz ship only sections 1–8 + 11 (no AMAR / human-resources); the
extractor maps by the section number in each sheet/file name, so the omitted
sections stay empty rather than shifting the others.

## Reproduce

```bash
pip install openpyxl xlrd          # .xlsx and legacy .xls readers
python3 download_hubs.py           # curated landing-page files -> raw/
python3 download_zendesk.py        # Zendesk help-center attachments -> raw/
python3 extract.py                 # writes extracted/, manifest.json, summary.csv
```

Files were fetched with a browser User-Agent over HTTPS. All sources are public
transparency reports linked from the catalogue; nothing here is behind a login.
