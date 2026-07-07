# Korea Network Act — illegal-sexual-content transparency report

South Korea's amended **Network Act** (Act on Promotion of Information and
Communications Network Utilization and Information Protection — **Art. 64-5**)
and **Telecommunications Business Act** (**Art. 22-5**), from the two bills that
passed on 20 May 2020, require online service providers (OSPs) to implement
technical and managerial measures against the circulation of *illegal sexual
content* and to publish an **annual transparency report** on them. "Illegal
sexual content" here spans illegally-filmed content (몰카), deepfake / "fake"
images and videos, and child/youth sexual-abuse material (CSAM).

**Google** publishes one report per calendar year, covering **Search and
YouTube jointly** (no per-service split). This directory ingests **all six
reports published so far — 2020 → 2025** — archived in
`raw/google-korea-network-act-YYYY.pdf`.

## What's built

`build_korea_network_act.py` writes the tidy-long `korea-network-act.json`,
whose `columns` are `publisher, period, section, category, metric, unit, value`.
The reports come in two shapes:

### 2024 & 2025 — full monthly table (§II)

`period` is monthly (`YYYY-01` … `YYYY-12`). Four `section`s:

- `requests_received` — removal requests by complainant type
  (`Victims etc. (User Requests)` + `Agency and Org (Gov Requests)`),
  `metric='requests'`.
- `request_reasons` — the same requests by reason (`Illegal Photos and Videos` /
  `Fake Images and Videos` / `Child or Youth Sexual Abuse Content`),
  `metric='requests'`.
- `processed_result` — the same requests by outcome (`Removed Voluntarily by the
  Company`; four `Not Removed - …` reasons; two `KCSC Assessment - …` rows),
  `metric='urls'`.
- `removal_reasons` — the removed URLs by reason, `metric='urls_removed'`.

The report's per-section "Total" rows are **dropped** (derivable), so within a
section the categories partition it. 2025's monthly values were transcribed;
2024's were extracted from the PDF's §II table and **re-validated** here (each
row's twelve months are cross-checked against its printed annual total, and each
section's categories against its grand total — the build raises on any mismatch).

### 2020–2023 — prose-only headline figures

These reports give only the year's aggregate URL counts (2020 covers just
**10–31 Dec 2020**, the law's implementation date — 8 government requests / 61
URLs). They go into an **`annual_summary`** section (`period` = the year `YYYY`,
`category='All'`) with `metric` `urls_received` / `urls_removed`.

`annual_summary` is **also** emitted for 2024/2025 (rolled up from their tables)
so it holds one comparable **2020 → 2025** series:

| Year | URLs received | URLs removed |
|---|--:|--:|
| 2020 (partial) | 61 | 42 |
| 2021 | 31,281 | 18,294 |
| 2022 | 47,162 | 38,908 |
| 2023 | 90,616 | 81,593 |
| 2024 | 158,052 | 142,211 |
| 2025 | 115,280 | 92,334 |

### Caveats

- **Sections are cross-cuts, not additive.** The four monthly sections are cuts
  of the same requests; `annual_summary` is a rollup of them. Pin a `section`
  (and `metric`) before aggregating — never sum across sections, and don't sum
  `annual_summary` together with the monthly sections.
- **Mixed `period` granularity.** Monthly sections use `YYYY-MM`;
  `annual_summary` uses `YYYY`. Summing over `period` within a monthly section
  gives that year's annual total.
- **Search + YouTube are reported jointly** — figures aren't split by product.
- **2024's own totals don't perfectly reconcile** — requests-received 158,052 vs
  processed 158,044 (a 8-URL discrepancy in Google's report), preserved rather
  than "fixed".
- Only Google publishes a machine-retrievable report in this format so far;
  other designated OSPs' reports slot in as they become available.

## Refresh

```bash
python build_korea_network_act.py   # re-validates + writes korea-network-act.json
```

Source: Google's South Korea Network Act & Telecommunications Business Act
Transparency Reports, <https://transparencyreport.google.com/report-downloads>.
