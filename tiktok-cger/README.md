# TikTok — Community Guidelines Enforcement Report (CGER)

TikTok's **voluntary** content-moderation transparency report: how much
violating content it removed, how proactively, and how fast, **quarterly since
2020 Q3**. It's the TikTok analogue of Meta's Community Standards Enforcement
Report, and is distinct from TikTok's law-mandated **DSA** report and its
**government/legal-request** disclosures (both carried separately in this repo).

## Pipeline

| Script | What |
|--------|------|
| `build_cger.py` | Parses the archived `raw/cger.zip` into `tiktok-cger.json`. `--download` refreshes the ZIP from TikTok's report page first. `--include-markets` keeps the per-country rows. |

## Source

TikTok publishes the CGER as a **downloadable ZIP** (a raw tidy-long CSV + a
README, dashboard templates and a narratives PDF), reachable only via its
bot-gated transparency SPA. The report page server-renders a `__remixContext`
blob whose CDN URLs point straight at the per-quarter ZIP, so `--download`
fetches it deterministically **with no browser**:

1. GET the CGER report page with browser headers.
2. Regex the `…/<PERIOD>_CGER_English.zip` URL out of the HTML — the latest
   quarter's ZIP carries the **full** back-history.
3. GET that ZIP (its eden-CDN path contains a literal `[`, so no URL globbing).

The CDN folder token **rotates each publication**, so the URL is *discovered*
from the page each time rather than hardcoded. The archived `raw/cger.zip` keeps
the build fully deterministic.

## Coverage

- **Quarters:** 2020 Q3 → 2026 Q1 (23), quarterly.
- **25 metrics:** Total videos removed, Proactive removal rate, Removal rate
  before any views, Removal rate within 24 hours, Videos restored, Category
  share, Percentage of user reports actioned, Accounts removed, Fake
  accounts/followers/likes removed & prevented, Comments removed, LIVE
  suspensions/restores/demonetizations, Video/Comment removal rates, etc.
- **Policy breakdown:** `policy_type` (`All` / `Policy` / `Sub-policy` / `Ban
  reason…`) × `issue` (128 community-guideline values, kept verbatim).
- **Moderation breakdown:** `task_type` × `task` (`Automation` / `Human
  moderation` / `AI Moderation`; view-band buckets `0 views` … `>1,000,000
  views`; turnaround buckets `Less than 2 hours` …).

## Output schema

Tidy-long, one row per measured value:

`[period, metric, policy_type, issue, task_type, task, unit, value]`

- **period** — reporting quarter, `YYYY Qn`.
- **metric** — one of the 25 (kept verbatim).
- **policy_type / issue** — community-guideline breakdown; `All` for the
  top-level figure.
- **task_type / task** — moderation-system / view-band / turnaround breakdown;
  `All` for the top-level figure. (TikTok's export labels the moderation-system
  grouping `task_type` verbatim — a source quirk, kept as filed.)
- **unit** — `count` or `rate` (a **fraction of 1** — TikTok reports rates like
  `0.944` = 94.4%), derived per metric.
- **value** — a number.

### Scope

The vendored `tiktok-cger.json` is the **Global cut** (`Location='All'` in the
source) — ~3.1k rows covering every metric × policy × task breakdown at the
global level. The source also carries a per-country / per-language geography
breakdown (156 markets, ~30× larger); `build_cger.py --include-markets` keeps it
(adding a `market` column), but it's excluded from the vendored snapshot to keep
it lean.

### Caveats

- **Never sum across metrics or units.** Rates (proactive removal, removal-speed,
  category share, percentages) are fractions of 1 — never SUM. Counts of videos ≠
  accounts ≠ comments. Pin a `metric` before aggregating.
- **Don't sum a breakdown with its `All`.** `policy_type`/`issue` and
  `task_type`/`task` each carry an `All` total alongside the breakdown rows;
  summing both double-counts. Pin the grain (`All` vs a breakdown) before
  aggregating.
- **Policy taxonomy changed.** The `Policy`/`Sub-policy` breakdown is only
  populated from Q4 2025 on (TikTok recategorised); earlier quarters carry the
  `All`/`Ban reason` grains.
- **Privacy suppression.** Values representing fewer than 1,000 users are blank
  in the source and dropped at build time.

## Reproduce

```bash
python3 build_cger.py --download   # refresh raw/cger.zip from TikTok's report page
python3 build_cger.py              # rebuild tiktok-cger.json (global cut) from raw/
```

Deterministic from `raw/cger.zip` (rows sorted; no wall-clock).

The API seeds `tiktok-cger.json` into the queryable `tiktok_cger_metrics` table
(behind `POST /api/explore` / `/api/query`) and the `/tiktok-cger` dataset page.
