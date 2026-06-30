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

**Not included.** Google/YouTube (JS-rendered SPA; CSV only via a client-side
button), Snap (numbers JS-loaded), and Telegram (account-gated in-app bot) aren't
fetchable headless — same wall that blocks TikTok. WhatsApp is a planned
fast-follow (its fbcdn PDF links are signed/expiring, so they need a live index
scrape rather than a templated URL). Moj/ShareChat redesigned their report layout
in mid-2022 (and later moved Moj's pages to a JS shell), so v1 covers the
consistent 2021–early-2022 static layout.

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

- **platform** — `Facebook` / `Instagram` / `Twitter` / `Moj` / `ShareChat`, plus
  `Meta` for the report-level GAC orders (which cover both surfaces).
- **period** — `YYYY-MM` of the covered month.
- **section** — `content_actioned_proactive`, `grievances_received`,
  `grievances_tools_provided`, `grievances`, `accounts_actioned`, `gac_orders`,
  `complaints`, `account_bans`, `law_enforcement`.
- **category** — policy area / complaint category / ban duration (empty where the
  section has no breakdown).
- **metric** — the specific measure within the section (e.g. `content_actioned`,
  `proactive_rate`, `reports`, `grievances_received`, `urls_actioned`,
  `accounts_suspended`, `orders_received`/`orders_complied`, `ugc_ban`,
  `requests_received`).
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
ShareChat **2021-07 → 2022-04** (6 months). Expanding coverage is a follow-up.
