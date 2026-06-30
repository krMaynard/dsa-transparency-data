# GitHub Transparency Report

GitHub publishes its [Transparency Report](https://github.com/github/transparency)
data as open CSVs (CC-BY-4.0): government takedowns (received + processed),
requests to disclose user information (subpoenas / court orders / cross-border /
national-security letters & orders), DMCA takedowns + circumvention claims,
automated detection (CSEAI / TVEC), appeals & reinstatements, and EU-DSA monthly
active users. GitHub is not a designated VLOP, so this is net-new vs. the DSA data.

## Layout

| Path | What |
|------|------|
| `raw/*.csv` | The canonical top-level CSVs, copied verbatim from `github/transparency` (`data/**`). The finer `by_calendar_year_half/` and `by_month/` variants upstream are intentionally **not** vendored — they're alternate resolutions of the same series. |
| `build_github.py` | Stdlib extractor; normalises the heterogeneous CSVs onto one **tidy long** table and emits `github-transparency.json`. |
| `github-transparency.json` | The dataset the API is seeded from (vendored into `transparency-report-api/data/`). |

## Reproduce

```bash
python3 build_github.py              # rebuild github-transparency.json from raw/
python3 build_github.py --download   # refresh raw/ from github/transparency first
```

Deterministic from the archived CSVs (rows are sorted; `coverage` is the latest
year in the data, not wall-clock), so re-running is byte-identical — CI re-derives
it and fails on drift.

## Schema (tidy long)

One row per measured value:

`[year, period, dataset, government, iso2, category, metric, count_low, count_high]`

- **`period`** — sub-year label where a file has one (`Jul-Dec`, a month number), else `""`.
- **`government`/`iso2`** — set for country-keyed files (government takedowns, cross-border, trade controls), else `""`.
- **`category`** — the in-row breakdown (request type, abuse type, takedown type, …), else `""`.
- **`metric`** — the count column when a file reports several (`received`/`disclosed`,
  `repos_affected`/`pages_affected`/`accounts_affected`), else `count`.
- **`count_low`/`count_high`** — the value; `low == high` for exact counts. National-security
  letters/orders and EU-DSA MAU are published as **banded ranges** (e.g. `0-249`,
  `10000000-11000000`), so they populate distinct low/high bounds.
