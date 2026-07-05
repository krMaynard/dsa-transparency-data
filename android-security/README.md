# Google — Android ecosystem security (PHA rates)

Google's Transparency Report publishes **Android ecosystem security** figures —
the rate of **Potentially Harmful Applications (PHA)** on devices and in Google
Play — at
<https://transparencyreport.google.com/android-security/overview>.

The export (`google-android-security.zip`) is **five CSVs**, each a different
cut of the same PHA-rate measure:

| Raw CSV | Section | Grain | Row dimension |
|---------|---------|-------|---------------|
| `percentage-of-devices-with-pha.csv` | `devices_with_pha` | 12-mo rolling (daily) | market type (`All Devices` / `Enterprise devices`) |
| `percentage-of-devices-with-pha-by-android-version.csv` | `devices_by_version` | quarterly | Android version (`KitKat` … `15`) |
| `percentage-of-pha-installs.csv` | `installs` | 12-mo rolling (daily) | install source (`Google Play`) |
| `percentage-of-pha-installs-by-top-countries.csv` | `installs_by_country` | 12-mo rolling (daily) | country (ISO-2) |
| `percentage-of-pha-installs-by-categories.csv` | `installs_by_category` | quarterly | PHA category (`Backdoor`, `Riskware`, …) |

This isn't a government-request stream like the rest of the pipeline — it's
security telemetry — but it's the same tidy-long shape, so it slots in as one
queryable table.

## Extraction

`build_android.py` reads the five CSVs, validates each header (fails loud on
drift), and normalises them into the shared tidy-long shape below. The
by-categories cut yields **two** measures per row (`pha_rate` and the
`category_share` percentage); every other cut yields one `pha_rate`.

## Layout

| Path | What |
|------|------|
| `raw/*.csv` | The five export CSVs, archived verbatim. |
| `build_android.py` | Pure-stdlib extractor → `android-security.json`. `--download` refreshes raw/ from the export ZIP. |
| `android-security.json` | The dataset the API is seeded from (vendored into `transparency-report-api/data/`). |

## Reproduce

```bash
python3 build_android.py              # rebuild from raw/
python3 build_android.py --download   # refresh raw/ from the export ZIP first
```

Deterministic from `raw/` (rows sorted; `coverage` from the periods; no
wall-clock) — CI re-derives it and fails on drift.

## Schema (tidy long)

`[section, period, category, metric, unit, value]`

- **section** — which cut (see the table above).
- **period** — the reporting date as `YYYY-MM-DD`: the 12-month **rolling end
  date** for the rolling cuts, the **quarter end date** for the quarterly cuts
  (kept as the end date so every section shares one sortable column).
- **category** — the row dimension kept verbatim (market type / Android version
  / install source / country ISO-2 / PHA category).
- **metric** — `pha_rate` for every cut; `installs_by_category` also carries
  `category_share`.
- **unit** — `rate` (a **fraction of 1** — Google's PHA rate; never SUM) or
  `percent` (the `category_share`, which sums to ~100 across categories per
  quarter).
- **value** — the reported figure (`REAL`).

Pin a `section` **and a `metric`** before aggregating — the rates aren't
comparable across cuts, and they're rates, not counts. Coverage: **2017-Q1 →
2024-Q4** (24,888 rows; 5 sections).
