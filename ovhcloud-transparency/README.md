# OVHcloud — EU DSA transparency report (hosting intermediary)

**OVHcloud** (OVH Groupe SAS, Roubaix, France) is Europe's largest cloud /
hosting provider — ~450,000 servers across 43 data centres, 1.6 million
customers in 140+ countries. Under the EU **Digital Services Act** it is an
**intermediary / hosting** service, and it publishes an annual transparency
report as a **narrative PDF** (not the Article 15/24 harmonised-template
workbook). This dataset covers the report period **17 February – 31 December
2024** (published April 2025).

Because OVHcloud is an infrastructure host — it cannot see or selectively remove
the content its customers store — its report has **no content-moderation
removals**. Instead it discloses two things the DSA requires of a hosting
intermediary: the **authority orders** it received per member state, and the
**notices** of allegedly illegal content submitted through its Article 16 abuse
form, broken down by category. Signalements about a customer's own data are
forwarded to that customer; OVHcloud itself acts only on infrastructure-level
abuse (phishing, malware, etc.).

## Sections & metrics

| `section` | `category` | metrics |
|-----------|-----------|---------|
| `member_state_orders` | `germany`, `belgium`, `spain`, `france`, `poland` | `orders_received` (count), `median_implementation_hours` (hours) |
| `illegal_content_notices` | `ip_infringement`, `csam`, `violent_or_shocking`, `personal_data`, `phishing`, `other` | `notices_received` (count), `median_action_seconds` (seconds), `automated_share_pct` (percent) |
| `notice_totals` | `all` | `total_notices_received`, `dsa_scope_notices`, `out_of_scope_notices` (counts) |

The report's "median time to notify the issuing authority of receipt" column is
`NA` for every country, so it is not emitted. `personal_data` notices have `NA`
for action time / automation and are excluded from the DSA-scope total (see
below).

## What's built

`build_ovhcloud.py --download` fetches the raw PDF from `corporate.ovhcloud.com`
into the shared `../pdf-reports/ovhcloud/` archive; `build()` then parses that
archived PDF **offline** (deterministic, via `pdfplumber`).

Output `ovhcloud-transparency.json`, tidy-long
(`publisher, period, section, category, metric, unit, value`).

```bash
python build_ovhcloud.py --download   # re-fetch the PDF → pdf-reports/ovhcloud/, then build
python build_ovhcloud.py              # rebuild offline from the archived PDF
```

### Parsing notes

- **Tables via `pdfplumber`.** The two figure tables (member-state orders;
  notices by category) are extracted with `page.extract_tables()`; the
  report-wide totals come from a narrative regex. French category / country
  labels are mapped to canonical English slugs by keyword.
- **Source number formatting is inconsistent.** France's order count is printed
  `3 339` (thin-space thousands separator) but Belgium's is `2932` (no
  separator); the parser strips all non-digits, so both read correctly (3339,
  2932). Belgium's figure is reproduced exactly as published.
- **Two reconciliations guard the extraction (the build raises on mismatch):**
  1. the six per-category `notices_received` (928,407) **minus** the
     `personal_data` row (4,642 — data-protection reports are not DSA "illegal
     content") equals the stated **DSA-scope total 923,765**; and
  2. `dsa_scope_notices` (923,765) + `out_of_scope_notices` (2,372,924) equals
     `total_notices_received` (3,296,689).
- **Rates must not be summed.** `median_action_seconds` and
  `automated_share_pct` are per-category rates; `notice_totals` already holds the
  report-wide totals, so summing category counts on top of them double-counts.

Source: OVHcloud DSA transparency report,
`corporate.ovhcloud.com/sites/default/files/2025-04/rapport_de_transparence_dsa_ovhcloud_2025.pdf`
(archived at [`../pdf-reports/ovhcloud/`](../pdf-reports/ovhcloud)), period
2024-02-17 … 2024-12-31.
