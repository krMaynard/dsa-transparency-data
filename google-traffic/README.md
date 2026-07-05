# Google — Traffic & Disruptions catalogue

Google's Transparency Report tracked **disruptions to the availability of its
products** — government-ordered internet shutdowns, network blocks and outages
— at <https://transparencyreport.google.com/traffic/overview>. For each event
it recorded the affected country, the Google product, the approximate
start/end dates, and a **news-source citation** corroborating the disruption.

Google **froze** this dataset: the last recorded disruption is late 2021, so
this is a **historical catalogue (2009–2021)**, not a live feed. It survives as
a single CSV in Google's archived transparency-report export bucket
(`archived-google-traffic.zip`).

Unlike the metrics datasets in this pipeline this isn't a tidy-long table of
measured quantities but a **flat catalogue** (like the report-locations and NY
ToS catalogues): each row is one disruption event, with the citation that
documents it.

## Extraction

`build_traffic.py` reads the archived CSV, validates its header, and normalises
each row to the schema below — deriving `year` from `start_date` and carrying
Google's own deep link (`disruption_url`) back into the interactive chart. The
two rows Google published without a start date (only an end date, for the
2011 Syria/Myanmar unblockings) keep a null `start_date`/`year`.

## Layout

| Path | What |
|------|------|
| `raw/traffic-disruptions.csv` | The archived catalogue CSV, extracted from `archived-google-traffic.zip` and archived verbatim. |
| `build_traffic.py` | Pure-stdlib extractor → `google-traffic.json`. `--download` refreshes raw/ from the archived export ZIP. |
| `google-traffic.json` | The dataset the API is seeded from (vendored into `transparency-report-api/data/`). |

## Reproduce

```bash
python3 build_traffic.py              # rebuild from raw/
python3 build_traffic.py --download   # refresh raw/ from the archived export ZIP first
```

Deterministic from `raw/` (rows sorted; `coverage` from the years; no
wall-clock) — CI re-derives it and fails on drift.

## Schema (flat catalogue)

`[country, iso2, product, start_date, end_date, year, source, source_url, title, excerpt, disruption_url]`

- **country** — the affected country (Google's `Region` label).
- **iso2** — Google's CLDR territory code (e.g. `SD`, `BF`).
- **product** — the disrupted Google product (`Web Search`, `YouTube`,
  `Gmail`, `Blogger`, …).
- **start_date / end_date** — `YYYY-MM-DD`, Pacific time, may be approximated;
  `start_date` is null for the two end-date-only rows.
- **year** — derived from `start_date` (null when there's no start date).
- **source / source_url** — the news outlet + article corroborating the event.
- **title / excerpt** — the cited article's headline and snippet.
- **disruption_url** — Google's deep link into the interactive traffic chart.

Coverage: **2009 → 2021** (152 disruptions, 67 countries, 12 products).
