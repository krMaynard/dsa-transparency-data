# Meta — Community Standards Enforcement Report (CSER)

Meta's flagship **voluntary** transparency report: how much violating content it
actioned on **Facebook** and **Instagram** across ~16 policy areas, **quarterly
since 2017 Q4**. Unlike the EU-DSA or Türkiye Law 5651 reports, the CSER isn't
filed under any single law — Meta publishes it of its own accord (now under the
"Integrity Reports" umbrella).

## Pipeline

| Script | What |
|--------|------|
| `build_cser.py` | Parses the archived `raw/cser.csv` into `meta-cser.json`. `--download` refreshes the CSV from Meta's GraphQL feed first. |

## Source

The CSER has **no static CSV/ZIP download** — its charts are drawn client-side
from a same-origin **GraphQL** feed. One persisted query,
`TransparencyReportCSERRootCSVQuery`, returns the **entire dataset as a single
CSV** (`app,policy_area,metric,period,value`) — every chart's series at once, no
per-chart enumeration. `--download` replays it deterministically with two
requests and **no login**:

1. GET a CSER page with browser headers; scrape the `lsd` token from the HTML.
2. POST the persisted query to `/api/graphql/` with that token; the response's
   `data.csv.content` field is the CSV.

The persisted-query `doc_id` **rotates** when Meta redeploys the site. If a
refresh returns no CSV, re-derive it by grepping the page's JS bundles for the
`TransparencyReportCSERRootCSVQuery` operation id (see `_DOC_ID` in the script).
The archived `raw/cser.csv` keeps the **build** fully deterministic regardless.

## Coverage

- **Apps:** Facebook, Instagram
- **Quarters:** 2017 Q4 → 2025 Q4 (33)
- **Policy areas (16):** Adult Nudity & Sexual Activity, Bullying & Harassment,
  Child Endangerment (Nudity/Physical Abuse; Sexual Exploitation), Child Nudity
  & Sexual Exploitation, **Cross-Policy Data** (an across-policy aggregate),
  Dangerous Organizations (Organized Hate; Terrorism), Fake Accounts, Hateful
  Conduct, Restricted Goods & Services (Drugs; Firearms), Spam, Suicide/Self-
  Injury/Eating Disorders, Violence and Incitement, Violent and Graphic Content.
- **Metrics (14):** Prevalence + Lowerbound/Upperbound Prevalence + UBP,
  Content Actioned, Content Removed, Content Appealed, Content Restored
  with/without appeal, Proactive rate, Enforcement Precision Lower/Upper Bound,
  False Positive Lower/Upper Bound.

## Output schema

Tidy-long, one row per measured value:

`[app, policy_area, metric, period, unit, value]`

- **app** — `Facebook` / `Instagram`.
- **policy_area** — the violation type (kept verbatim). `Cross-Policy Data` is an
  aggregate across policies — **not** a peer of the individual areas.
- **metric** — one of the 14 above.
- **period** — reporting quarter, `YYYY Qn`.
- **unit** — `count` or `percent` (derived per row: any `%` value — including the
  lone "approximately N%" Prevalence estimate — is a percent; everything else a
  count).
- **value** — a number.

### Caveats

- **Never sum across metrics or units.** Prevalence / Proactive rate /
  Enforcement Precision / False-Positive bounds / UBP are **percentages** (never
  SUM); Content Actioned ≠ Content Removed ≠ Appealed ≠ Restored are distinct
  counts. Pin a `metric` before aggregating.
- **`Cross-Policy Data` double-counts.** It's Meta's across-policy aggregate, so
  summing `value` over all `policy_area`s adds it on top of its own components —
  filter it out (or pin a single policy area) before aggregating.
- **Bounds are ranges.** `Lowerbound`/`Upperbound Prevalence` (and the precision
  / false-positive lower/upper bounds) are the two ends of an estimate, not
  additive quantities.
- **Sparse metrics.** Content Removed, Enforcement Precision, False Positive and
  UBP appear for only a few policy × quarter cells; blanks are genuine `N/A`
  (metric not reported), dropped at build time.
- The parser **fails loud** on any value it can't classify as a count, a percent,
  or `N/A`, so a format shift can't slip through as a silent drop.

## Reproduce

```bash
python3 build_cser.py --download   # refresh raw/cser.csv from Meta's GraphQL feed
python3 build_cser.py              # rebuild meta-cser.json from raw/cser.csv
```

Deterministic from `raw/cser.csv` (rows sorted; no wall-clock).

The API seeds `meta-cser.json` into the queryable `cser_metrics` table (behind
`POST /api/explore` / `/api/query`) and the `/cser` dataset page.
