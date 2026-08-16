# Sources we mapped but couldn't fetch (browser needed)

This is a hand-off backlog for a **browser-capable agent** (e.g. Codex). Every
item here is a transparency-reporting source we *located* while building the
[transparency dashboard](https://github.com/krmaynard/transparency-report-api),
but could **not** pull with the plain-HTTP scrapers in this repo — because the
page is login-gated, JavaScript-rendered, hidden behind an interactive
form/checkbox PDF, or simply not yet fetched in bulk.

For each item: the **why it's blocked**, the **URL(s)**, and **what to extract**.
Canonical full lists live in this repo's CSVs (paths noted per section) — this
file is the curated, prioritized view.

> How to use: work top-to-bottom. Categories A–C are the highest value (they
> feed existing dashboard tables); D is bulk archival; E is known-hard targets;
> F is the long tail.

---

## A. Login-gated filings — need an authenticated browser session

**New York Social Media ToS reports** (Stop Hiding Hate Act). 18 filings are
served from the NY AG webform host (`ag.ny.gov/system/files/webform/...`) that
returns a login/redirect wall to non-browser clients, so our scraper catalogued
them with a `source_url` only (`access=auth-required`). A browser session should
open each URL and save the PDF into `ny-tos-reports/pdfs/` (the dir
`extract_narrative.py` reads, per its `PDF_DIR`), named to match the catalogue's
`filename` column, then flip the row's `access` to `public` so the indexer
picks it up.
Full list: `ny_tos_reports.csv` (rows where `access=auth-required`).

- **Agile Sports Technologies Inc (Hudl)** — 2025 Q3 — https://ag.ny.gov/system/files/webform/social_media_terms_of_service_re/95920/2025-q3-agile-sports-technologies-inc-policy.pdf
- **Alphabet Inc (YouTube)** — 2025 Q3 — https://ag.ny.gov/system/files/webform/social_media_terms_of_service_re/98065/2025-q3-alphabet-inc-policy.pdf
- **Nextdoor Inc** — 2025 Q3 — https://ag.ny.gov/system/files/webform/social_media_terms_of_service_re/96455/2025-q3-nextdoor-inc-policy.pdf
- **Agile Sports Technologies Inc (Hudl)** — 2025 Q4 — https://ag.ny.gov/system/files/webform/social_media_terms_of_service_re/106111/2025-q4-agile-sports-technologies-inc-policy.pdf
- **Amazon.com Inc (GoodReads Inc)** — 2025 Q4 — https://ag.ny.gov/system/files/webform/social_media_terms_of_service_re/106529/2025-q4-amazon.com-inc-policy.pdf
- **Amazon.com Inc (Twitch Interactive Inc)** — 2025 Q4 — https://ag.ny.gov/system/files/webform/social_media_terms_of_service_re/112056/2025-q4-amazon.com-inc-policy.pdf
- **Discord Inc** — 2025 Q4 — https://ag.ny.gov/system/files/webform/social_media_terms_of_service_re/106231/2025-q4-discord-inc-policy.pdf
- **Kick Streaming Pty Ltd** — 2025 Q4 — https://ag.ny.gov/system/files/webform/social_media_terms_of_service_re/106550/2025-q4-kick-streaming-pty-ltd-policy.pdf
- **LinkedIn Corporation** — 2025 Q4 — https://ag.ny.gov/system/files/webform/social_media_terms_of_service_re/106176/2025-q4-linkedin-corporation-policy.pdf
- **Naver Corporation (Other)** — 2025 Q4 — https://ag.ny.gov/system/files/webform/social_media_terms_of_service_re/123272/2025-q4-naver-corporation-policy.pdf
- **Nextdoor Inc** — 2025 Q4 — https://ag.ny.gov/system/files/webform/social_media_terms_of_service_re/106543/2025-q4-nextdoor-inc-policy.pdf
- **Reddit Inc** — 2025 Q4 — https://ag.ny.gov/system/files/webform/social_media_terms_of_service_re/106514/2025-q4-reddit-inc-policy.pdf
- **Roblox Corporation** — 2025 Q4 — https://ag.ny.gov/system/files/webform/social_media_terms_of_service_re/106537/2025-q4-roblox-corporation-policy.pdf
- **Snap Inc** — 2025 Q4 — https://ag.ny.gov/system/files/webform/social_media_terms_of_service_re/105139/2025-q4-snap-inc-policy.pdf
- **Strava Inc** — 2025 Q4 — https://ag.ny.gov/system/files/webform/social_media_terms_of_service_re/106538/2025-q4-strava-inc-policy.pdf
- **TikTok Inc** — 2025 Q4 — https://ag.ny.gov/system/files/webform/social_media_terms_of_service_re/106547/2025-q4-tiktok-inc-policy.pdf
- **Vimeo.com Inc** — 2025 Q4 — https://ag.ny.gov/system/files/webform/social_media_terms_of_service_re/105508/2025-q4-vimeo.com-inc-policy.pdf
- **X Corp** — 2025 Q4 — https://ag.ny.gov/system/files/webform/social_media_terms_of_service_re/106235/2025-q4-x-corp-policy.pdf

---

## B. JavaScript / help-center DSA pages — audited in Chrome

The browser audit resolved eleven of the twelve uncertain entries:

- **Vimeo** exposed 2024 and 2025 harmonised XLSX workbooks. Both are archived
  and extracted into the canonical 1–11 schema.
- **SHEIN** exposed H1 and H2 2025 XLSX workbooks. H1 is archived and the
  corrected 30 July 2026 H2 version replaces the earlier VLOP source workbook.
- **Chess.com** is an Art. 24(2) monthly-active-recipient disclosure only.
- **Civitai** is a general 2024 company/community report, not a DSA report.
- **Fastly**, **Hetzner**, **Medium**, and **Quora** publish DSA information,
  contact, notice, or orders pages, but no Art. 15 transparency report was found.
- **Zepeto** publishes an Art. 24(2) AMAR disclosure only, with a latest period
  ending in 2023.
- **DocMorris** now returns a 404 at its catalogued DSA URL.
- **Conforama** now exposes a 2025 Article 15 PDF from its rendered DSA page;
  the report is archived under `pdf-reports/conforama/`.

One page remains unresolved:

- **Fiverr:** the help-centre overview renders and Fiverr's own search result
  confirms a 2024 DSA transparency report, but the actual report hub at
  https://www.fiverr.com/legal-portal/community/dsa triggers a PerimeterX human
  verification challenge before exposing the download.

---

## C. Harmonised-template browser backlog — completed

The browser sweep resolved every source previously listed here. Canonical Annex
I workbooks for Akamai, Flickr, Glassdoor, Jeuxvideo.com, Riot Games, Upwork,
Vimeo, and x-kom are extracted into the 1–11 schema. Vimeo contributes two
reporting periods. GMX is covered by the combined GMX and WEB.DE workbook
already stored as `webde`.

The browser confirmed that the remaining publishers expose other formats rather
than a complete machine-readable workbook: Apple Books, Apple Podcasts, and
iCloud use rendered HTML; Epic Games Store, eToro, Eventbrite, and OVHcloud use
PDFs; Faire publishes concatenated CSV tables with an incomplete category table;
and heise forums and WordPress.com use custom CSV bundles. Those artifacts are
archived and linked from `REPORT_LOCATIONS.md`, but are not forced into the
canonical 1–11 schema. `harmonised-reports/sources.csv` is the authoritative
status list and now has no `hub-pending` or `file-blocked` rows for this batch.

---

## D. Bulk PDF archival: completed

**California AB 587 Terms-of-Service reports.** All **100** filings are
catalogued with a working `source_url` on `oag.ca.gov`. The complete PDF set is
now mirrored under `ca-ab587/pdfs/`; `archived`, `sha256`, and `bytes` are
populated for every row, and the 4,963-page narrative index is reproducible
from the archive.
Platforms (21): ArtStation, BAND, Discord, GitHub, Goodreads, Hudl, LinkedIn, Meta, Microsoft, Nextdoor, Peloton, Pinterest, Reddit, Roblox, Sketchfab, Snap, Strava, TikTok, Vimeo, X, YouTube.
Full list with URLs: `ca-ab587/ca_ab587_reports.csv`.

---

## E. Known-hard targets — identified, still not retrievable

Specific reports we know exist and want, but that resisted extraction. Each note
comes from the dataset builder's own caveats.

- **Australia eSafety BOSE, completed in Chrome.** The eSafety
  Commissioner's **Basic Online Safety Expectations** transparency-notice findings
  are now captured in `au-esafety/`. The `esafety.gov.au` origin still resets or
  hangs plain datacenter-IP requests, while Chrome renders the findings page in
  full. The capture covers the **AI companion apps** findings (non-periodic
  notices given 16 Oct 2025 to Character.AI, Nomi, Chai, Chub AI; report published
  Mar 2026, survey figures revised Jul 2026):
    - Findings report — https://www.esafety.gov.au/industry/basic-online-safety-expectations/ai-services/findings-october-2025
    - AI-services hub — https://www.esafety.gov.au/industry/basic-online-safety-expectations/ai-services
    - Media release — https://www.esafety.gov.au/newsroom/media-releases/esafety-report-shows-ai-companions-are-putting-children-at-risk
  The rendered findings page, hub and media release are now archived in
  `au-esafety/raw/`, and `au-esafety/build_esafety.py` emits 22 audited numeric
  rows. The API already exposes the same facts in its combined BOSE dataset.
  Further BOSE slices to
  scout next: the CSEA messaging periodic-notice snapshots (Apple/Discord/Google/
  Meta/Microsoft/Skype/Snap/WhatsApp) and the Social Media Minimum Age compliance
  updates.
- **India IT Rules 2021 — publishers blocked by JS / anti-bot.** The monthly
  compliance reports are ingested for Meta, Twitter/X, Moj, ShareChat, Roblox,
  Google and Pinterest, but several significant intermediaries can't be fetched
  headless (per `india-it-rules/README.md`). Each is a browser target that would
  extend `india_metrics`:
    - **TikTok** — India monthly page is JS-rendered (the wall behind several of these).
    - **Snap** — India monthly compliance page loads its numbers via JS.
    - **Reddit** and **Quora** — publish India pages but sit behind a Cloudflare challenge.
    - **Josh (VerSe)** — renders its grievance data client-side.
    - **WhatsApp** — a planned fast-follow: its report PDFs are signed/expiring
      `fbcdn` links, so they need a live index scrape rather than a templated URL.
    - **Telegram** — account-gated in-app bot, no published report page (may be a dead end).
  New publishers are curated in `india-it-rules/build_india.py`'s `SOURCES`.
- **Taiwan Anti-Fraud Act — Meta's statutory report.** The Art. 32/33 fraud-prevention
  透明度報告 for the designated platforms is retrievable for Google / LINE / TikTok
  but **Meta's is not** (the figures aren't in a fetchable page/PDF we could find).
  Target: Meta's Taiwan anti-fraud statutory report. Would extend `taiwan_metrics`.
- **Türkiye Law No. 5651 — TikTok & YouTube.** Meta (Facebook/Instagram) and X
  publish standalone Türkiye 5651 transparency PDFs (already ingested); **TikTok
  and YouTube publish no retrievable standalone 5651 report** — their Turkish
  figures appear only inside their global transparency tools. A browser could
  confirm whether a standalone TR report exists or extract the TR slice from the
  global tool. Would extend `turkey_metrics`.
- **Japan 情プラ法 (IDPA) Art. 28 — TikTok & X.** LY Corp, Google (YouTube) and Meta
  file quantitative Art. 28 implementation statistics (ingested); **TikTok and X
  so far publish only the qualitative Art. 21 criteria**, no numbers. Re-check
  their Japan transparency pages for a quantitative Art. 28 filing. Would extend
  `japan_metrics`.
- **EU AI Act training-data summaries — remaining major providers.** Current
  coverage is 15 summary entries across 11 providers, including filled templates
  newly recovered for EuroLLM and the Polish Ministry of Digital Affairs' PLLuM
  base/instruct/chat families. xAI, Bria, OpenAI and Meta are already archived,
  so they are no longer browser targets. Periodically re-check **Anthropic,
  Mistral, Cohere, Aleph Alpha, Stability, NVIDIA, IBM, Amazon, Alibaba/Qwen and
  DeepSeek** for provider-hosted Article 53(1)(d) templates. **Domyn Small v1.0**
  is a specific publication-gap target: its official model card and technical
  report both claim a companion Article 53(1)(d) artefact, but a Chrome audit on
  8 August 2026 found no link and no summary in the rendered model-repository
  file tree. Re-check Domyn's model repository and official research site for a
  newly attached or corrected link. The AI Office says
  the template is mandatory for new GPAI models and enforcement began 2 August
  2026; pre-2-August-2025 models have until 2 August 2027. Checkbox PDFs may need
  rendered visual verification. Would extend `ai_training_metrics`.
- **EU Terrorist Content Online Regulation (TCOR) — more Art. 7 / Art. 8 sources.**
  Coverage is a deliberate starting set (Commission COM(2024) 64 per-Member-State
  orders; Spotify + Meta Art. 7 reports; Ireland's Coimisiún na Meán). Specific
  Art. 7 platforms still to add: **X, TikTok, Google, Microsoft, LinkedIn** (…);
  plus other Member States' Art. 8 authority reports. All exist as archived PDFs
  to transcribe. Would extend `tco_metrics`.

---

## F. The long tail — catalogued locations not yet archived

Beyond the curated items above, **111 of 259** rows across **104 platforms** in the
report-locations catalogue have a known `url` but **no `archived` mirror** — we
know *where* each platform publishes, but haven't captured the report itself.
Most are ordinary pages a browser can save; a batch pass over these would let
`link_archives.py` fill in the `archived` column.
Full list: `dsa_reports.csv` (rows where `archived` is empty). Prioritize
`harmonised_template=yes` (Section C) and `confidence=uncertain` (Section B) first.

---

## G. Other report *types* — bot-walled clusters & not-yet-scouted regimes

Beyond the individual datasets above, two frontiers where a browser earns its keep.

### G1. Bot-walled platform clusters (report may exist — a browser should confirm & fetch)

`REPORT_LOCATIONS.md` → **"Searched, not found / out of scope"** records the full
scouting sweep. Most entries there are genuine dead ends (no report published, or
the platform is out of DSA scope) — **not** worth a browser. But two clusters were
marked *"no own report found **/ heavily bot-blocked**"*, meaning our headless
scraper hit an anti-bot wall before it could even confirm whether a report exists.
A browser (correct UA, EU egress, JS) should re-check each and grab any DSA report:

- **Chinese e-commerce & gaming** (Shein-style fast-fashion + marketplaces + game
  publishers): Miravia, Taobao/Tmall, 1688, Vova, Geekbuying, Zaful, Rosegal,
  PatPat, Cider, Cupshe, Floryday; Douyin, Xiaohongshu/RED, Bilibili, Kwai/Kuaishou,
  QQ/QZone, Trip.com; HoYoverse (Genshin), NetEase Games, Lilith, Moonton, Century
  Games; Vivo, Lenovo, Anker, TCL, Huawei Cloud.
- **CEE / Baltic / Balkan classifieds & retail** (many bot-blocked): Media Expert,
  RTV Euro AGD, Gratka, Modivo/eobuwie, Answear, Slevomat, Datart; ss.lv,
  Osta.ee, Skelbiu.lt, Aruodas.lt, Njuškalo (HR), Bolha (SI), Bazar.bg,
  Car.gr, Spitogatos, Publi24, Kainos.lt, Varle.lt, Senukai.

  Chrome audit, 8 August 2026: **Otodom** and **OLX Bulgaria** were recoverable
  from JavaScript-rendered Salesforce help centres. Both expose 2024 and 2025
  PDFs; all four are archived under `pdf-reports/otodom/` and
  `pdf-reports/olx-bg/`. Focused checks found no report for Miravia, Gratka,
  Slevomat, ss.lv, Osta.ee or Njuškalo. The remaining names above stay queued.

(Everything else in that section — Russian/sanctioned, Swiss/Norway/UK out-of-EEA,
India-only real-money gaming, "Art. 11 contact only" — is out of scope; skip it.)

### G2. Report-type regimes we've built as a *starting set* (scout for more filers)

These datasets each cover one or two sources of a broader regime; a browser scout
could find and fetch additional filers. Not blocked so much as **not yet mapped**:

- **Regional content-moderation laws** (`regional_metrics`) — only **Texas HB 20**
  (§120.053) and **Austria KoPl-G** (§4) are built. Other sub-national / national
  content-moderation transparency statutes with platform filings exist (e.g. other
  US-state laws; more EU member-state transitional laws) — each new statute is a
  scout-then-extract task.
- **Korea Network Act** (`korea_network_act_metrics`) — only **Google** (Search +
  YouTube) is ingested; other Korean OSPs file annual illegal-sexual-content reports
  under Art. 64-5 / Art. 22-5. Scout for their reports.
- **California AB 2013** AI-training summaries (narratives) — only **Google**'s is
  captured; other generative-AI providers must post AB 2013 summaries too (in force
  Jan 2026). Scout oag.ca.gov / provider sites.

_(Out of scope for a **browser** doc but noted for completeness: the DSA-TDB
Statements-of-Reasons dataset could go deeper — the Commission also publishes an
"advanced" aggregation and per-platform cuts, and the raw SoRs — and TikTok's CGER
has a per-market cut in its source ZIP we didn't vendor. None of these need a
browser, just more builder runs.)_

---

_Generated from the catalogue snapshots in `krmaynard/transparency-report-api`
(`data/report-locations.csv`, `data/ny-tos-reports.csv`, `data/ca-ab587-reports.csv`),
which mirror this repo's `dsa_reports.csv`, `ny_tos_reports.csv`, and
`ca-ab587/ca_ab587_reports.csv`._
