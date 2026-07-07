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
YouTube jointly** (there is no per-service split in the figures). This directory
ingests Google's **2025** report — its sixth publication — archived in
`raw/google-korea-network-act-2025.pdf`.

## What's built

`build_korea_network_act.py` transcribes the single quantitative table (§II,
p. 14 — the monthly Jan–Dec breakdown) into the tidy-long
`korea-network-act.json`, whose `columns` are
`publisher, period, section, category, metric, unit, value`:

- **`period`** — monthly, `2025-01` … `2025-12`. The report's annual "Total"
  column is used only to **validate** (each row's twelve months must sum to it),
  never stored, so summing over `period` is a legitimate annual total.
- **`section`** / **`category`** / **`metric`**:
  - `requests_received` — removal requests by complainant type
    (`Victims etc. (User Requests)` 21,859 + `Agency and Org (Gov Requests)`
    93,421 = **115,280**); `metric='requests'`.
  - `request_reasons` — the same 115,280 requests by reason
    (`Illegal Photos and Videos` / `Fake Images and Videos` /
    `Child or Youth Sexual Abuse Content`); `metric='requests'`.
  - `processed_result` — the same 115,280 by outcome (`Removed Voluntarily by
    the Company` 92,334; four `Not Removed - …` reasons totalling 22,946; two
    all-zero `KCSC Assessment - …` rows); `metric='urls'`.
  - `removal_reasons` — the 92,334 removed URLs by reason; `metric='urls_removed'`.

Every breakdown is cross-checked against the report's stated totals — both the
per-row annual total **and** the section grand total — and the build **raises**
on any mismatch, so a mistranscription can't slip through.

### Caveats

- **Sections are cross-cuts of the same requests, not additive.**
  `requests_received`, `request_reasons` and `processed_result` are three cuts
  of the same 115,280 requests; `removal_reasons` cuts the 92,334 removed. Pin a
  `section` (and `metric`) before aggregating — never sum across sections.
- **Categories partition their section.** The report's "Total" rows are dropped
  (they're derivable), so within a section the categories are disjoint and sum
  to the section total — summing over `category` within one section is a
  legitimate grand total.
- **Search + YouTube are reported jointly** — the figures aren't split by
  product.
- Only Google publishes a machine-retrievable report in this format so far;
  additional publishers/years slot in as they become available (the report is
  Google's sixth annual publication — prior years are addable).

## Refresh

```bash
python build_korea_network_act.py   # re-validates + writes korea-network-act.json
```

Source: Google's South Korea Network Act & Telecommunications Business Act
Transparency Report, <https://transparencyreport.google.com/report-downloads>.
