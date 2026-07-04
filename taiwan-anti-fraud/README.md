# Taiwan — Anti-Fraud Act (詐欺犯罪危害防制條例) transparency data

Taiwan's **Fraud Crime Hazard Prevention Act** ("打詐專法", in force July 2024)
created two transparency streams:

## 1. Government enforcement data

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

## 2. Platform statutory transparency reports (2025 round — built)

MODA's designated online-ad platforms — Google LLC (Google/YouTube), Meta
(Facebook/Instagram), LY Corp (LINE), TikTok — must each publish an annual
**詐欺防制計畫透明度報告** under Art. 30 ¶2(2) of the Act (fraud-ad
notifications received and content/accounts actioned under Arts. 32–33;
format rule effective 2024-11-30). Three of the four first-round (2025)
reports are extracted here, from artifacts archived verbatim in `raw/`:

| Publisher | Coverage | Artifact | Source |
|---|---|---|---|
| **Google** | 2024-07-01..2025-06-30 | `raw/google-fraud-prevention-report-2025.pdf` | [Transparency Report downloads (report-27)](https://transparencyreport.google.com/report-downloads?lu=report-27) → [PDF](https://storage.googleapis.com/transparencyreport/report-downloads/pdf-report-ll_2024-7-1_2025-6-30_zh_TW_v1.pdf) |
| **TikTok** | 2025-01-01..2025-09-30 | `raw/tiktok-fraud-prevention-report-2025.pdf` | [TikTok transparency: Taiwan fraud prevention](https://www.tiktok.com/safety/en/transparency/taiwan-fraud-prevention) → [PDF](https://sf16-va.tiktokcdn.com/obj/eden-va2/zayvwlY_fjulyhwzuhy%5B/ljhwZthlaukjlkulzlp/misc/tw-fraud-prevention-report-2025.pdf) |
| **LINE** | 2024-08-02..2025-09-30 | `raw/line-fraud-prevention-report-2025.html` | [LY Corp disclosure page](https://tw-af-disclosure.landpress.line.me/2025-AF-Transparency) |

**Meta (Facebook/Instagram) is absent, not skipped:** its report exists on
[transparency.meta.com](https://transparency.meta.com/reports/regulatory-transparency-reports/)
("Taiwan Fraud Prevention Transparency Report") but the PDF sits behind
expiring `fbcdn.net` CDN tokens, the live page errors for this pipeline, and
the only Wayback capture of the asset is a 403. It slots in as a fourth
parser once a retrievable artifact is curated.

Each parser anchors on the report's own table labels / sentences and **crashes
on drift**; Google's figures are cross-checked internally (removed = legal +
policy; named = removed + not-actioned). Statutory statistics land in section
`afa_transparency_report`; the voluntary proactive-enforcement figures TikTok
discloses alongside land in `platform_enforcement`.

## Layout

| Path | What |
|------|------|
| `raw/dns-blocked-sites.csv` | Archived Art. 42 DNS-suspension registry (domain-level, verbatim + unioned across refreshes). |
| `raw/{google,tiktok}-fraud-prevention-report-2025.pdf`, `raw/line-fraud-prevention-report-2025.html` | The 2025 statutory platform reports, archived verbatim. |
| `build_taiwan.py` | Extractor → `taiwan-anti-fraud.json` (stdlib + `pdfplumber` for the platform PDFs). `--download` refreshes the NPA registry (union) from data.gov.tw. |
| `taiwan-anti-fraud.json` | The dataset the API is seeded from (vendored into `transparency-report-api/data/`). |

## Reproduce

```bash
python3 build_taiwan.py              # rebuild from raw/
python3 build_taiwan.py --download   # refresh the NPA registry from data.gov.tw first (union)
```

Deterministic from `raw/` (rows sorted; `coverage` = latest NPA month; no
wall-clock) — CI re-derives it and fails on drift.

## Schema (tidy long)

`[publisher, period, section, category, metric, unit, value]`

- **publisher** — `NPA-165` (the 165 anti-fraud hotline / CIB) for the
  government stream; the platform name (`Google`, `LINE`, `TikTok`, later
  `Meta`) for the statutory reports.
- **period** — Gregorian month `YYYY-MM` for the NPA stream (converted from
  the ROC 民國 year); the report's stated coverage window `YYYY-MM..YYYY-MM`
  for platform rows (windows differ per publisher, and LINE's securities-law
  metric has its own longer window).
- **section** — `dns_blocked_sites` (NPA), `afa_transparency_report`
  (platform statistics filed under Arts. 32/33), `platform_enforcement`
  (voluntary proactive figures TikTok discloses alongside).
- **category** — the registry's 網站性質 site-category label for NPA rows
  (kept in Chinese — the official taxonomy; e.g. 金融保險, 電子商務,
  釣魚網站); empty for platform rows.
- **metric / unit / value** — `sites_blocked` for NPA rows; per-report metric
  names for platform rows (`government_requests`, `urls_removed`,
  `art33_accounts_suspended`, …), all `count`, exact integers as filed.

Pin a `section` **and a `metric`** before aggregating: requests ≠ URLs ≠
accounts; `urls_removed_legal`/`urls_removed_policy` are the parts of
`urls_removed`; and LINE's `art33_accounts_suspended_cib_project` is a subset
of its `art33_accounts_suspended`. The NPA aggregate reconciles exactly with
the raw registry (sum of `value` = number of archived registry rows). Current
NPA coverage: **2025-12 → 2026-05** (6 months, 16 categories, 58,334 blocked
domains).
