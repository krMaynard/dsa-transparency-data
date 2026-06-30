# New York Social Media Terms-of-Service Reports

Archive + catalogue of the **terms-of-service reports** that social-media
companies file with the **New York State Attorney General** under the
**Stop Hiding Hate Act** ([S895B](https://www.nysenate.gov/legislation/bills/2025/S895) /
A6789B).

The law requires social-media platforms with over **$100 million** in annual
revenue and New York users to file **twice-yearly** reports describing their
terms of service and how they define, moderate, and report on hateful conduct,
racism, extremism, disinformation, harassment, and foreign political
interference. The AG publishes each filing as a narrative **policy PDF**:

> https://ag.ny.gov/resources/organizations/social-media-tos-reporting/reports

These are **qualitative policy documents**, not the EU DSA Annex-I
machine-readable workbooks, so they aren't extracted into the 1–11 template like
the rest of this repo — we mirror the original PDFs (as
[`download_pdfs.py`](../download_pdfs.py) does for PDF-format DSA reports) and
build a flat catalogue.

## Contents

| Path | What |
|------|------|
| [`../ny_tos_reports.csv`](../ny_tos_reports.csv) | Catalogue — one row per filing (all **29**) |
| [`../ny_tos_reports.json`](../ny_tos_reports.json) | Same catalogue, JSON |
| `pdfs/` | The archived PDFs (`<period>-<company>[-<platform>].pdf`) |

Catalogue columns: `company`, `platform` (the child platform/brand, when the
filing names one), `period` (`2025 Q3` / `2025 Q4`), `upload_date`, `access`,
`source_url`, `filename`, `archived`, `sha256`, `bytes`.

## Access note — 18 of 29 filings are login-gated at the source

The AG serves the **older filings** from a public directory
(`/sites/default/files/social-media-policy-report/…`) but serves **newer
filings** from a private Drupal *webform* directory
(`/system/files/webform/…`) that **302-redirects anonymous requests to a login
page**. Those files are publicly *listed* on the index but cannot be downloaded
without an account — almost certainly a misconfiguration on the AG's side
(webform file uploads default to private in Drupal).

So the catalogue records **all 29** filings, but only the **11 publicly
downloadable** ones are mirrored here as PDFs:

| `access` | Count | Meaning |
|----------|-------|---------|
| `public` | 11 | Mirrored under `pdfs/`; `archived`/`sha256`/`bytes` populated |
| `auth-required` | 18 | Login-gated at source; catalogued with `source_url` only |

If the AG later exposes the gated files publicly, re-running the scraper will
pick them up automatically.

## Companies (29 filings)

Naver, Amazon (Twitch, GoodReads), Kick, TikTok, Nextdoor, Strava, Roblox,
Reddit, X Corp, Discord, LinkedIn, Agile Sports (Hudl), Vimeo, Snap, Alphabet
(YouTube), and Meta (Facebook, Instagram, Threads) — across **2025 Q3** and
**2025 Q4**.

## Regenerating

```bash
python3 scrape_ny_tos.py     # network required
```

Walks every page of the AG index, downloads each publicly-served PDF (verifying
the `%PDF` magic), and rewrites the catalogue. Like the other `download_*` /
`scrape_*` scripts it hits the live web and is **not** run by CI.
