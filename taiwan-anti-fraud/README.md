# Taiwan — Anti-Fraud Act (詐欺犯罪危害防制條例) transparency data

Taiwan's **Fraud Crime Hazard Prevention Act** ("打詐專法", in force July 2024)
created two transparency streams:

## 1. Government enforcement data (built — the current dataset)

The National Police Agency's Criminal Investigation Bureau publishes the
registry of **fraud websites whose DNS resolution was suspended under
Article 42** of the Act, on Taiwan's open-data portal:
[data.gov.tw dataset 176455](https://data.gov.tw/dataset/176455) — one row per
blocked domain: ROC month (民國年月), domain (網域), site category (網站性質,
16 labels such as 金融保險/電子商務/釣魚網站), legal basis (法律依據 = the Act),
requesting unit (聲請單位). The extractor aggregates it to blocked-site counts
per **month × category**; the domain-level registry itself is archived
verbatim in `raw/`.

**Rolling window caveat:** the upstream feed covers roughly the most recent
half-year and older months rotate out. `--download` therefore **unions** the
fresh feed with the archived rows, so history accumulates in `raw/` across
refreshes instead of being lost.

## 2. Platform transparency reports (pending — schema-ready)

MODA's designated online-ad platforms — Google LLC (Google/YouTube), Meta
(Facebook/Instagram), LY Corp (LINE), TikTok — must each publish an annual
**詐欺防制計畫透明度報告** (fraud-ads removed by type, suspended accounts,
Taiwan MAU; format rule effective 2024-11-30). Press coverage confirms the
first round exists (e.g. Google's covering Jul 2024–Jun 2025: 236 government
requests, 3,564 URLs removed = 227 law-violating + 3,337 policy-violating),
but the artifacts are not currently reachable from this pipeline: they are not
search-indexed, LINE's corporate site is bot-walled, and TikTok's/Google's
pages are JS-rendered. The tidy-long schema is **publisher-keyed** so each
platform's report drops in as a new source once its URL is curated.

## Layout

| Path | What |
|------|------|
| `raw/dns-blocked-sites.csv` | Archived Art. 42 DNS-suspension registry (domain-level, verbatim + unioned across refreshes). |
| `build_taiwan.py` | Pure-stdlib extractor → `taiwan-anti-fraud.json`. `--download` refreshes (union) from data.gov.tw. |
| `taiwan-anti-fraud.json` | The dataset the API is seeded from (vendored into `transparency-report-api/data/`). |

## Reproduce

```bash
python3 build_taiwan.py              # rebuild from raw/
python3 build_taiwan.py --download   # refresh raw/ from data.gov.tw first (union)
```

Deterministic from `raw/` (rows sorted; `coverage` = latest month; no
wall-clock) — CI re-derives it and fails on drift.

## Schema (tidy long)

`[publisher, period, section, category, metric, unit, value]`

- **publisher** — `NPA-165` (the 165 anti-fraud hotline / CIB) for the
  government stream; platform names (`Google`, `Meta`, `LINE`, `TikTok`) later.
- **period** — Gregorian month `YYYY-MM` (converted from the ROC 民國 year).
- **section** — `dns_blocked_sites` (per-publisher sections later).
- **category** — the registry's 網站性質 site-category label (kept in Chinese —
  the official taxonomy; e.g. 金融保險, 電子商務, 釣魚網站).
- **metric / unit / value** — `sites_blocked` / `count` / the number of
  domains DNS-blocked that month in that category.

The aggregate reconciles exactly with the raw registry (sum of `value` =
number of archived registry rows). Current coverage: **2025-12 → 2026-05**
(6 months, 16 categories, 58,334 blocked domains).
