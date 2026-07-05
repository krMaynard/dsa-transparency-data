# TikTok — Government & Legal Requests reports

TikTok's transparency centre publishes three **government / legal request**
reports as machine-readable CSVs (the "Legal, Information & Government Requests"
/ LIGR download bucket). This is a stream distinct from the content-moderation
figures the DSA pipeline already covers:

<https://www.tiktok.com/transparency/en/government-removals-report>

Each current-period CSV is **cumulative** — one file carries every reporting
half-year since 2019 — so a single download per stream yields the full history.

## Streams

| Dataset | Aspect | Grain | What |
|---|---|---|---|
| `government_removals` | `GRFCR` | country × half-year | Government content-removal requests: requests / content / accounts received, content & accounts actioned (community-guideline vs local-law grounds), removal rate. |
| `information_requests` | `LRFUI` | country × half-year | Government requests for user information: legal / emergency / preservation requests, the accounts they specify, and the share of legal / emergency requests where some data was disclosed. |
| `ip_removals` | `Copyright` | global × half-year | Intellectual-property (copyright & trademark) removal requests: request and removal counts plus success / appeal rates. |

Coverage: **2019-H1 → 2025-H2** (`government_removals` / `information_requests`,
158 markets incl. the global `All` aggregate); `ip_removals` is global-only,
2021-H2 onward.

## Layout

| Path | What |
|------|------|
| `raw/government-removal-requests.csv`, `raw/information-requests.csv`, `raw/intellectual-property-requests.csv` | The cumulative CLIGR CSVs, archived verbatim. |
| `build_tiktok.py` | Pure-stdlib extractor → `tiktok-transparency.json`. `--download` refreshes raw/ from the current-period CSVs. |
| `tiktok-transparency.json` | The dataset the API is seeded from (vendored into `transparency-report-api/data/`). |

## Reproduce

```bash
python3 build_tiktok.py              # rebuild from raw/
python3 build_tiktok.py --download   # refresh raw/ from TikTok's CDN first
```

Deterministic from `raw/` (rows sorted; `coverage` from the periods; no
wall-clock) — CI re-derives it and fails on drift. Each source metric label
maps to a stable `metric` key via an explicit registry, so an unrecognised
label **crashes the build** (fail-loud) rather than being silently dropped;
count values are asserted integral.

## Schema (tidy long)

`[dataset, period, country, metric, unit, value]`

- **dataset** — `government_removals` / `information_requests` / `ip_removals`.
- **period** — half-year `YYYY-H1` / `YYYY-H2`.
- **country** — the market name, or `All` for the **global aggregate row that
  sits alongside** the per-country rows. A SUM over both double-counts — pin
  `country` (or filter out `All`) before aggregating.
- **metric** — the stable snake_case key (e.g. `total_requests_received`,
  `legal_requests`, `pct_legal_disclosed`).
- **unit** — `count` (exact integer) or `percent` (a rate / percentage reported
  as a **fraction of 1**, e.g. `0.875`; never SUM a percent).
- **value** — the reported figure (`REAL`; integers for counts).

Pin a `dataset` and a `metric` before aggregating — requests ≠ content ≠
accounts, the counts split several ways (community-guideline vs local-law;
legal vs emergency vs preservation), and the rate/percentage rows are
non-additive.
