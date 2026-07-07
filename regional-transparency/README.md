# Regional content-moderation transparency-law reports

Two sub-national / national statutes require platforms to publish periodic
content-moderation transparency reports. Google files both for **YouTube** on
its public transparency-report bucket, and this dataset extracts them into one
tidy-long table (`jurisdiction, platform, period, section, category, metric,
unit, value`).

## Jurisdictions

### Texas HB 20 — Business & Commerce Code §120.053

YouTube's half-yearly report (2024-H2 →). Full-layout reports (2024-H2, 2025-H1)
carry:

- **`monetization`** — `demonetizations` (videos demonetized for monetization-
  policy violations).
- **`age_restrictions`** — `age_restrictions_applied`.
- **`enforcement`** — `videos_removed` / `appeals` / `reinstatements` (global
  Community-Guidelines figures for the period).
- **`coordinated_influence`** — `channels` / `actions` terminated for coordinated
  influence operations (from the TAG Bulletin).
- **`human_flags`** — human flags received by flagger type (`User` / `Organization`
  / `Government`), metric `flags`.
- **`removals_by_detection`** — videos removed by source of first detection
  (`Automated` + the three human flagger types).
- **`removals_by_reason`** — videos removed by Community-Guidelines category (ten
  reasons). YouTube renamed one from 2025-H1 ("Spam, Misleading and Scams" →
  "Spam, Deceptive Practices, and Scams"); each period's label is kept verbatim.
- **`removals_by_country`** — videos removed by country of upload (top table).

From **2025-H2** YouTube reduced the report — the enforcement figures now point
to the global Community Guidelines Enforcement report, so only `monetization`
and `age_restrictions` are filed.

The build **cross-checks** each full report: `removals_by_reason` and
`removals_by_detection` must each sum exactly back to `videos_removed` (they
partition the same total), or it raises.

### Austria KoPl-G — Kommunikationsplattformen-Gesetz §4

YouTube's biannual report (2021-H2 →) on complaints about allegedly-illegal
**textual** content (comments) under the KoPl-G. Section **`complaints`**:
`reported_items` / `removed_items`. The figures are **sparse** — YouTube's own
report notes the KoPl-G webform "is de facto not used" (single-digit counts).

## Method

`build_regional.py` parses every figure from the archived PDFs under `raw/` with
fail-loud anchor checks (the build raises if a report drifts). Deterministic;
pure `PyMuPDF`, no network.

```bash
python build_regional.py     # re-reads raw/ → regional-transparency.json
```

Sources: `storage.googleapis.com/transparencyreport/report-downloads/` (slug
`ee` = Texas §120.053, slug `21` = Austria KoPl-G).
