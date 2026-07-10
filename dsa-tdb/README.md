# DSA Transparency Database — Statements of Reasons (aggregated)

Every content-moderation decision an in-scope platform takes under the EU Digital
Services Act is filed to the [**DSA Transparency Database**](https://transparency.dsa.ec.europa.eu/)
as an individual **Statement of Reasons** (SoR). The raw database is enormous
(billions of SoRs, ~4 TB of daily dumps), so this builder does **not** vendor it
raw. It uses the European Commission's own toolbox,
[**dsa-tdb**](https://code.europa.eu/dsa/transparency-database/dsa-tdb), to fetch
the pre-made **global "simple" monthly aggregates**, then **re-aggregates** them
into a compact tidy-long snapshot (`dsa-tdb.json`).

## Build

```bash
pip install dsa-tdb --index-url https://code.europa.eu/api/v4/projects/943/packages/pypi/simple
pip install pandas

# one-shot (downloads the aggregates, then builds)
python build_dsa_tdb.py --from 2023-09-01 --to 2026-05-01

# or reuse an already-downloaded aggregates dir
dsa-tdb-cli download-aggs -o /tmp/aggs --format csv --agg-version simple -i 2023-09-01 -f 2026-05-01
python build_dsa_tdb.py --aggs-dir /tmp/aggs
```

## Output — `dsa-tdb.json`

Tidy-long, one row per measured value: `section, platform, period, category, metric, unit, value`.

| section | dimension (`category`) | select |
|---|---|---|
| `totals` | `All` | — |
| `by_category` | the 14 DSA statement categories | single |
| `by_decision_ground` | Illegal content / Incompatible with terms | single |
| `by_automated_detection` | Yes / No | single |
| `by_automated_decision` | Fully / Partially / Not automated | single |
| `by_source_type` | Article 16 notice / Trusted flagger / Own-initiative / Other | single |
| `by_decision_visibility` | Content removed / Access disabled / Demoted / … | **multi** |

`metric` is always `statements`, `unit` always `count`, `value` the SoR count.
`period` is the SoR's `created_at` month (`YYYY-MM`).

### Caveats
- The **single-select** cuts each partition the platform-month total, so a cut's
  categories sum back to `totals` — never sum a cut *together with* `totals`.
- `by_decision_visibility` is **multi-select** (one SoR can carry several
  restriction types), so its rows do **not** sum to the total.
- Kept to the **top 60 platforms** by volume (≈99.97% of all SoRs); the long tail
  of one-off filers is dropped. Volumes are dominated by a few marketplaces
  (Google Shopping product delistings), so cross-platform sums are heavily skewed
  — pin a `section` and usually a `platform` before aggregating.

The snapshot is vendored into the API repo as `data/dsa-tdb.json`.
