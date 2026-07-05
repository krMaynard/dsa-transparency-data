# Discord — Transparency Reports

Discord publishes a **Transparency Report** each reporting period — quarterly
through 2023, half-yearly from 2024 — as a **ZIP containing one CSV** (plus a
narrative PDF) on its CDN, linked from
<https://discord.com/safety-transparency-reports>.

Each CSV is a stack of **labelled sub-tables**: a one-cell *section* header
(e.g. `Accounts Disabled`, `Appeals`, `US Gov Info Requests`), then a
column-header row (whose first cell names the row dimension — Policy Category /
Country / Request Type / Month — and whose remaining cells name the measures),
then the data rows, then a `Total` row. The report spans:

- **Trust & Safety enforcement** — accounts, servers and server-members actioned
  by policy category (Child Safety, Harassment, Hateful Conduct, …); accounts
  disabled; servers removed; appeals (with grant rates); user reports; NCMEC
  media reports.
- **Government / legal requests** — US legal process (court orders, subpoenas,
  search warrants, …), international government information requests (by
  country), and preservation & emergency requests (by country) — a stream not
  otherwise in this pipeline.

## Extraction

`build_discord.py` walks that structure **generically** — it doesn't hard-code
the section or measure list, so new policy categories / sections / measures in
later reports flow through as new rows rather than crashing. Each section and
measure label is normalised to a stable snake_case `metric`/`section` key; the
row dimension's value is kept verbatim as `category`; `Total` rows are dropped
(derivable by SUM, and keeping them would double-count).

**Section labels evolve across eras** (Discord's own renaming), e.g. the
US-legal-process section is `legal` (2022), then
`united_states_government_information_requests` (2023), then `us_gov_info_requests`
(2024); the enforcement section is `warns` (2022–2023) then
`accounts_and_servers_warnings_and_temporary_interventions` (2024). The keys are
kept as filed rather than force-merged — pin a `section` (and `period` era)
before aggregating.

> The separate `Discord-DSA_Transparency_Report.zip` (EU DSA report) is
> **excluded** — it overlaps this project's DSA harmonised-report pipeline.

## Layout

| Path | What |
|------|------|
| `raw/<period>.csv` | The per-period report CSV, extracted from its ZIP and archived verbatim (`YYYY-Qn` / `YYYY-Hn`). |
| `build_discord.py` | Pure-stdlib extractor → `discord-transparency.json`. `--download` refreshes raw/ from the current report ZIPs. |
| `discord-transparency.json` | The dataset the API is seeded from (vendored into `transparency-report-api/data/`). |

## Reproduce

```bash
python3 build_discord.py              # rebuild from raw/
python3 build_discord.py --download   # refresh raw/ from Discord's CDN first
```

Deterministic from `raw/` (rows sorted; `coverage` from the periods; no
wall-clock) — CI re-derives it and fails on drift.

## Schema (tidy long)

`[period, section, category, metric, unit, value]`

- **period** — the report's own grain: `YYYY-Qn` (2022–2023) or `YYYY-Hn`
  (2024+).
- **section** — the sub-table, snake_case (`accounts_disabled`, `appeals`,
  `us_gov_info_requests`, `international_government_information_requests`, …).
- **category** — the row-dimension value kept verbatim (a policy category like
  `Child Safety`, a country like `Germany`, a request type like `Subpoenas`, or
  a month).
- **metric** — the measure column, snake_case (`individual_accounts`,
  `servers`, `appeals`, `pct_of_appeals_granted`, `requests`,
  `information_produced`, …).
- **unit** — `count` or `percent` (an appeal/report rate, carried as the
  reported percentage number, e.g. `10.45` — never SUM a percent).
- **value** — the reported figure (`REAL`; integers for counts).

Pin a `section` **and a `metric`** before aggregating — the sections mix
enforcement counts, request counts and rates, and the section labels change
across eras. Coverage: **2022-Q1 → 2024-H1** (8 periods).
