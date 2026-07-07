# India IT Rules 2021 — monthly compliance reports

India's [Information Technology (Intermediary Guidelines and Digital Media Ethics
Code) Rules, 2021](https://www.meity.gov.in/) require "significant social media
intermediaries" (>5M registered users) to publish a **monthly compliance report**
under Rule 4(1)(d)/(e): content actioned proactively (by policy area, with a
proactive-detection rate), user grievances received and actioned (by category),
accounts actioned, Grievance Appellate Committee (GAC) orders, and
law-enforcement / takedown actions. Each intermediary files in its own layout, so
this extractor has a small per-publisher adapter, all feeding one **tidy-long**
table — one row per measured value. This is net-new vs. the EU DSA data.

## Covered publishers (v1)

| Publisher | Source | Format | Notes |
|-----------|--------|--------|-------|
| **Facebook, Instagram** | `transparency.meta.com/sr/india-monthly-report-<pubdate>` | PDF | One Meta PDF carries both surfaces (Tables 1–7). GAC table appears from 2023 (when the committee began operating). |
| **Twitter / X** | `transparency.twitter.com/.../India-ITR-<Mon>-<YYYY>.pdf` | PDF | Grievances by issue type + accounts suspended. Reporting window is an offset 26th→25th period; `period` is labelled by the window's **end month**. |
| **Moj, ShareChat** | `help.mojapp.in` / `help.sharechat.com/transparency-report/<month-year>/` | static HTML | Law-enforcement requests, total complaints, and the UGC/profile/comment **ban matrix** by duration. |
| **Roblox** | `cms-media.roblox.com/assets/<slug>.pdf` (linked from `about.roblox.com/pdf/…`) | PDF | Grievance reports received + enforcement actions by policy category (Table 1) and a single **global** proactive-moderation total (Table 2 — worldwide, not India-only). First filed March 2025. A `-` cell (nil) reads as `0`; later months use a literal `0`. Asset slugs vary month-to-month (some add an `india-`/`-1` token, one is an opaque CDN key), so each is curated in `SOURCES`. **Feb 2026** brought a redesigned layout — a `Reporting Period:`/year-month cover header instead of the in-body "covers the period" line, a two-page grievance table (header repeated per page), and a **revised category taxonomy** (e.g. `Child Endangerment`, `Sexual Content`, `Terrorism or Violent Extremism` replacing the 2025 set) — so a cross-period category query spans two vocabularies; the adapter handles all three period phrasings. |
| **Google / YouTube** | `storage.googleapis.com/transparencyreport/report-downloads/india-intermediary-guidelines_<Y>-<M>-1_<Y>-<M>-<last>_en_v1.pdf` (landing: `transparencyreport.google.com`) | PDF | The interactive landing page is a JS SPA, but the underlying monthly report is a **static, text-embedded PDF** on a public GCS bucket — the largest India IT-Rules source, **April 2021 →**, covering all of Google's SSMI surfaces (YouTube, Play, Search, Blogger…). Two figures per month, each split by complaint **reason** (Copyright / Trademark / Defamation / Other Legal / Counterfeit / Circumvention / Court Order / Impersonation / Graphic Sexual Content): complaints received (`complaints_received`) and removal actions on those complaints (`removal_actions`). The layout was redesigned c. 2025 (percentage lines → `Category Count` tables); reasons are matched by label, so both eras parse. |
| **Pinterest** | `policy.pinterest.com/en/india-transparency-report` | HTML (JSON) | A **single page** carrying every month, with the numbers embedded in the Next.js `__NEXT_DATA__` payload (not JS-loaded). Two sections per month — grievance **`reports`** and proactive **`voluntary_actions`** — each a policy × object-type (Pins / Boards / Accounts / Comments) table; a cell may carry two actions (`… _deactivated` and `… _limited_distribution`). Covers June 2024 →. |

**Not included.** Snap (its India monthly page loads the numbers via JS) and
Telegram (account-gated in-app bot, no published report) aren't fetchable
headless — same wall that blocks TikTok. Reddit and Quora publish India pages but
sit behind a Cloudflare challenge; Josh (VerSe) renders its grievance data
client-side. WhatsApp is a planned fast-follow (its fbcdn PDF links are
signed/expiring, so they need a live index scrape rather than a templated URL).
LinkedIn files no India-specific monthly file (only global semi-annual reports);
Koo (the first Indian SSMI to publish) shut down in 2024 and its Drive-hosted
report PDFs are now unreliable to retrieve. Moj/ShareChat redesigned their report
layout in mid-2022 (and later moved Moj's pages to a JS shell), so the Moj/ShareChat
coverage is the consistent 2021–early-2022 static layout.

## Layout

| Path | What |
|------|------|
| `raw/<publisher>-<period>.{pdf,html}` | The archived source reports, verbatim from each publisher. |
| `build_india.py` | Per-publisher extractor → `india-it-rules.json`. Needs `pdfplumber` for the PDF adapters; HTML adapters are pure stdlib. `--download` refreshes `raw/` from the curated URLs. |
| `india-it-rules.json` | The dataset the API is seeded from (vendored into `transparency-report-api/data/`). |

## Reproduce

```bash
python3 build_india.py              # rebuild india-it-rules.json from raw/
python3 build_india.py --download   # refresh raw/ from the curated URLs first
```

Deterministic from the archived `raw/` files (rows sorted; `coverage` = latest
period; no wall-clock), so re-running is byte-identical — CI re-derives it and
fails on drift.

## Schema (tidy long)

`[platform, period, section, category, metric, unit, value]`

- **platform** — `Facebook` / `Instagram` / `Twitter` / `Moj` / `ShareChat` /
  `Roblox` / `Google` / `Pinterest`, plus `Meta` for the report-level GAC orders
  (which cover both surfaces).
- **period** — `YYYY-MM` of the covered month.
- **section** — `content_actioned_proactive`, `grievances_received`,
  `grievances_tools_provided`, `grievances`, `accounts_actioned`, `gac_orders`,
  `complaints`, `account_bans`, `law_enforcement`; Google adds
  `complaints_received` / `removal_actions` and `gac_appeals` (the half-yearly
  Rule 3A(7) report of user appeals the Grievance Appellate Committee closed, by
  Google service × outcome); Pinterest adds `reports` / `voluntary_actions`.
- **category** — policy area / complaint reason / ban duration (empty where the
  section has no breakdown).
- **metric** — the specific measure within the section (e.g. `content_actioned`,
  `proactive_rate`, `reports`, `grievances_received`, `enforcement_actions`,
  `urls_actioned`, `accounts_suspended`, `orders_received`/`orders_complied`,
  `ugc_ban`, `requests_received`, Google's `complaints`/`removal_actions` and its
  GAC `appeals_closed`/`appeals_rejected`/`appeals_allowed`/`appeals_not_admitted`,
  Pinterest's `pins_deactivated`/`pins_limited_distribution`/… per object type).
- **unit** — `count` (exact integer), `approx_count` (Meta's abbreviated
  `2.3M`/`448.6K` proactive figures — the company's own rounded best-estimates,
  not exact), or `percent` (proactive-detection rates).

**Don't sum across `unit`s**, and pin a `section` before aggregating — metrics
aren't comparable across sections (same discipline as the Snap/GitHub tables).
Reported "Total" rows are dropped (the breakdown sums to them) to keep a `SUM`
clean. Meta category labels are de-fragmented across months (pdfplumber preserves
word spacing in some PDFs and concatenates it in others; the build rewrites each
to the most-readable variant).

## Periods

Curated in `build_india.py`'s `SOURCES`. Add new reports there as publishers
file them. Current coverage: Meta **2022-07 → 2023-09** (8 months), Twitter
**2021-06 → 2022-10** (11 months), Moj **2021-06 → 2022-04** (5 months),
ShareChat **2021-07 → 2022-04** (6 months), Roblox **2025-03 → 2026-05**
(15 months), Google **2021-04 → 2026-05** (62 months), Pinterest
**2024-06 → 2026-05** (24 months). For Google, extend the end bound in
`_google_months()` as new PDFs publish (~1-month lag); Pinterest re-vendors
every month from the single page. Expanding coverage is a follow-up.
