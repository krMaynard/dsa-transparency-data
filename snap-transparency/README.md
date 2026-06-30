# Snap (Snapchat) Transparency Report

Snap publishes its [Transparency Report](https://values.snap.com/privacy/transparency)
data as a per-reporting-period CSV (linked from each
`values.snap.com/privacy/transparency-<period>` page, hosted on Contentful). The
CSV is already **tidy-long** — one row per measured value — covering Trust &
Safety enforcements, ads moderation, appeals, child-sexual-exploitation, DMCA /
trademark notices, governmental content & account removal requests, information
requests (incl. US national-security), bilateral data-access requests, and a
regional / country overview. Snap is not a designated VLOP, so this is net-new
vs. the DSA data.

## Layout

| Path | What |
|------|------|
| `raw/Snap_Transparency_Report_<period>.csv` | The per-period CSVs, verbatim from Snap's Contentful asset host. |
| `build_snap.py` | Stdlib extractor; passes the tidy CSVs through to `snap-transparency.json`. `--download` refreshes `raw/` from the curated per-period URLs. |
| `snap-transparency.json` | The dataset the API is seeded from (vendored into `transparency-report-api/data/`). |

## Reproduce

```bash
python3 build_snap.py              # rebuild snap-transparency.json from raw/
python3 build_snap.py --download   # refresh raw/ from the curated per-period URLs first
```

Deterministic from the archived CSVs (rows sorted; `coverage` = latest period),
so re-running is byte-identical — CI re-derives it and fails on drift.

## Schema (tidy long)

`[period, section, category, sub_category_1, sub_category_2, metric, value]` — the
same columns Snap ships. `value` is numeric (counts plus a few medians, e.g.
`median_turnaround_time_minutes`); the handful of blank / non-numeric cells are
dropped.

## Periods

Curated in `build_snap.py`'s `SOURCES` (period → Contentful CSV URL). Each
per-period `values.snap.com` page embeds its own CSV link; add new periods there
as Snap publishes them. Currently **2024-H1** and **2024-H2** (the periods on the
current tidy schema); older periods used a different layout.
