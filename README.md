# DSA Transparency Data

Archive of EU [Digital Services Act](https://eur-lex.europa.eu/eli/reg/2022/2065/oj) transparency reports for 33 services covering **H2 2025 (1 July – 31 December 2025)**, published February 2026. This covers every designated VLOP/VLOSE that reported for the period, plus lower-tier online platforms operated by VLOP parents (the non-VLOP Apple and Wikimedia services). Stripchat, designated in December 2023, was [de-designated in May 2025](https://digital-strategy.ec.europa.eu/en/policies/list-designated-vlops-and-vloses) and is therefore not included.

Each report follows the DSA Implementing Regulation [(EU) 2025/40](https://eur-lex.europa.eu/eli/reg_impl/2025/40/oj) template (tables 1–11). Files are stored in their original publisher format (CSV bundle, `.xlsx`, or `.xls`).

## Layout

```
.
├── aliexpress/         (CSVs)
├── amazon/             (CSVs)
├── apple/
│   ├── app-store.xlsx
│   ├── books.xlsx
│   ├── icloud-storage.xlsx
│   └── podcasts.xlsx
├── booking-com/        (CSVs)
├── google/
│   ├── maps/           (CSVs + source xlsx)
│   ├── multi-services/
│   ├── play/
│   ├── search/
│   ├── shopping/
│   └── youtube/
├── meta/
│   ├── facebook/       (CSVs)
│   └── instagram/      (CSVs)
├── microsoft/
│   ├── bing.xlsx
│   └── linkedin/       (CSVs)
├── pinterest/          (CSVs)
├── shein.xlsx
├── snapchat/           (CSVs)
├── temu/               (CSVs)
├── tiktok/             (CSVs)
├── wikimedia/
│   ├── commons.xls
│   ├── wikidata.xls
│   ├── wikipedia.xls
│   ├── wikiversity.xls
│   ├── wikivoyage.xls
│   └── wiktionary.xls
├── x/                  (CSVs)
├── zalando/            (CSVs)
│
│   # adult-content VLOPs (original publisher folder names)
├── PH_DSA_Transparency_Report_FH26_1776436263/          (Pornhub — CSVs)
├── XNXX+-+Transparency+report+-+July-December+2025/      (XNXX — CSVs)
└── XVideos+-+Transparency+report+-+July-December+2025/   (XVideos — CSVs)
```

CSV bundles contain the standard 11 tables:

| # | Table |
|---|---|
| 1 | Report identification |
| 2 | Categories of illegal content / ToS violations |
| 3 | Member State orders |
| 4 | Notices |
| 5 | Own-initiative actions on illegal content |
| 6 | Own-initiative actions on ToS violations |
| 7 | Appeals & recidivism |
| 8 | Automated means |
| 9 | Human resources |
| 10 | Average Monthly Active Recipients (AMAR) |
| 11 | Qualitative description |

## convert.py

`convert.py` flattens tables 3–11 from all 33 services into a single compact JSON file used by a separate dashboard project. It writes to `../krMaynard.github.io/data/vlop-dsa.json` by default — adjust `OUT_FILE` in the script if you want it elsewhere.

```
python3 convert.py
```

Requires `openpyxl` and `xlrd`.

**Surfaces.** Google reports tables 6 & 7 as several disjoint sub-reports per service (organic "Core", "Ads", and for Search a breakdown by action level — URL-, domain-, host-level, etc.). Those services are flagged `"surfaces": True` in `SERVICE_DEFS`; the converter emits one row per surface, tagged with a trailing surface index (`surfaces` lookup, index 0 = "All" = no breakdown). Every other service resolves to a single canonical file (the shortest filename, so e.g. Amazon's `_version2` variant is ignored deterministically).

### append_platforms.py

`append_platforms.py` incrementally appends any `SERVICE_DEFS` entries that are not yet present to an **existing** `vlop-dsa.json`, leaving the services already in the file untouched. It reuses `convert.py`'s table parsers. Use this when you want to add new services without regenerating (and potentially perturbing) the existing ones — the committed JSON predates this archive and a full `convert.py` rebuild does not reproduce it exactly for the Google services.

```
python3 append_platforms.py
```

### add_surfaces.py

`add_surfaces.py` retro-fits the surface dimension onto an **existing** `vlop-dsa.json`: it tags every t6/t7 row with a surface index and replaces each surfaced (Google) service's t6/t7 rows with the full set parsed from every sub-report, leaving tables 3–5, non-Google rows, and the existing index ordering untouched. Used to add surfaces without the full re-intern/reorder a clean `convert.py` rebuild would cause.

```
python3 add_surfaces.py
```

## Source

Reports are published by each VLOP on their own transparency page; aggregated index at the EU [DSA Transparency Database](https://transparency.dsa.ec.europa.eu/).

## Non-VLOP report locations

Beyond the VLOPs/VLOSEs archived here, the DSA (Art. 15 & 24) requires **every**
EU online platform above the small-enterprise threshold to publish a periodic
transparency report — scattered across each platform's own site, with no single
official index. [`REPORT_LOCATIONS.md`](REPORT_LOCATIONS.md) catalogues where
those reports live for **214 non-VLOP platforms** (232 report URLs; operating
company, report URL(s), format/period, a verified/likely/uncertain confidence
rating — 141 verified — and whether the report uses the EU harmonised
machine-readable template, which **54** of them do), grouped across 16
categories. It also lists the 25 designated VLOPs/VLOSEs for completeness, the
authoritative EU/aggregator index sources, and a categorised list of platforms
that were searched but had no findable report.

### Relational database

`build_reports_db.py` parses `REPORT_LOCATIONS.md` (the single source of truth)
into a normalised SQLite database and a flat CSV, both ordered alphabetically:

```
python3 build_reports_db.py     # writes dsa_reports.db + dsa_reports.csv
```

- **`dsa_reports.db`** — SQLite, schema in [`schema.sql`](schema.sql): `category`,
  `company`, and `platform` tables plus a `report_url` table (one platform can
  have several URLs, e.g. a hub page + a direct file). A `v_reports` view flattens
  the join alphabetically. Stdlib only — no dependencies.
- **`dsa_reports.csv`** — one row per report URL, git-friendly and diffable.

Each platform carries a **`harmonised_template`** dimension — whether its report
uses the EU machine-readable template (Reg. (EU) 2024/2835, Annex I): `yes` /
`no` / `partial` (latest report only / file unverified) / `unknown`. It is derived
from the recorded format, with a curated override table for the VLOPs (whose first
harmonised reports were due end of Feb 2026).

Re-run the script after editing `REPORT_LOCATIONS.md` to regenerate both. Example
query:

```sql
SELECT platform, company, url FROM v_reports WHERE confidence = 'verified';
```

### Extracted harmonised-template reports

For the catalogue entries that file the EU harmonised machine-readable template
(54 platforms), [`harmonised-reports/`](harmonised-reports/) downloads the actual
report files and normalises them into the canonical 11-section layout — one CSV
per section under `harmonised-reports/extracted/<platform>/`, plus a
`manifest.json` and `summary.csv`. `discover_hubs.py` crawls the landing pages
for direct file links; `extract.py` reads each source (`.xlsx` / legacy `.xls` /
`.zip`-of-CSVs), mapping sections by template position so localised DE/FR/EL/…
reports load identically.

**29 of 54 extracted** so far; the rest are bot-walled, geo-fenced, or
JS-rendered landing pages (tracked with per-platform status in
`harmonised-reports/sources.csv`). These extracted reports are loaded into the
companion [transparency-report-api](https://github.com/krMaynard/transparency-report-api)
so the non-VLOP platforms are queryable alongside the VLOP dataset.

