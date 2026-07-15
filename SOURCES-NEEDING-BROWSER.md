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

## B. JavaScript / help-center DSA pages — need a browser to reach the actual report

These catalogue entries are marked **`confidence=uncertain`**: we found the
platform's DSA landing page, but the actual figures/report file are behind
JS-rendered help-center widgets, SPA routing, or a "download" control our
static fetch can't follow. A browser should confirm the real report artifact
(XLSX/CSV/PDF or the on-page numbers) and record the direct link.
Full list: `dsa_reports.csv` (rows where `confidence=uncertain`).

- **Chess.com** (Chess.com, LLC) — https://www.chess.com/article/view/digital-services-act-compliance
- **Civitai** (Civitai, Inc.) — https://civitai.com/articles/10372/civitai-2024-transparency-report
- **Conforama** (Conforama France SA) — https://www.conforama.fr/digital-service-act
- **DocMorris** (DocMorris N.V.) — https://www.docmorris.de/digital-services-act
- **Fastly** (Fastly, Inc.) — https://www.fastly.com/dmca-dsa
- **Fiverr** (Fiverr International Ltd.) — https://help.fiverr.com/hc/en-us/articles/22578911624977-DSA-overview
- **Hetzner** (Hetzner Online GmbH) — https://www.hetzner.com/legal/digital-services-act/
- **Medium** (A Medium Corporation) — https://help.medium.com/hc/en-us/sections/21832701520791-Digital-Service-Act-DSA-Information
- **Quora** (Quora, Inc.) — https://help.quora.com/hc/en-us/sections/13296037150612-DSA-Transparency
- **Shein** (Roadget Business (Shein)) — https://euqs.shein.com/digital-service-act-a-1994.html
- **Vimeo** (Vimeo.com, Inc.) — https://vimeo.com/legal/transparency/dsa
- **Zepeto** (Naver Z Corporation) — https://support.zepeto.me/hc/en-us/articles/15675506191769-Digital-Services-Act

---

## C. Harmonised-template reports located but not yet pulled into the schema

These are **`harmonised_template=yes`** (i.e. the EU Art. 15/24 template — directly
loadable into the `t3`–`t11` star schema via `harmonised-reports/extract.py`),
but the report file sits behind a page our scraper didn't traverse (a downloads
hub, a JS gate, or a direct XLSX/CSV/ODS/PDF we haven't grabbed). Each is a
ready-to-ingest platform once the file is in hand — highest value.
Authoritative status: `harmonised-reports/sources.csv` (`status = hub-pending` are
landing pages whose file link needs a browser/EU egress to reach; `file-blocked`
is bot-walled). 16 of 54 template platforms are still un-extracted for this reason.

- **Akamai** (Akamai Technologies, Inc.) — PDF/XLSX; 2024, H1 & H2 2025 — https://www.akamai.com/legal/eu-digital-services-act
- **Apple Books** (Apple Distribution International) — HTML report (17 Feb – 31 Dec 2024); also a Feb 2026 XLSX template — https://www.apple.com/legal/dsa/transparency/eu/books/2502/
- **Apple Podcasts** (Apple Distribution International) — HTML report (17 Feb – 31 Dec 2024); also a Feb 2026 XLSX template — https://www.apple.com/legal/dsa/transparency/eu/podcasts/2502/
- **Epic Games Store** (Epic Games, Inc.) — XLSX + hub; Feb 2024 – Feb 2025 — https://safety.epicgames.com/transparency-reports/european-union
- **Faire** (Faire Wholesale, Inc.) — CSV; 2024 & 2025 — https://www.faire.com/support/articles/20960200105115
- **Flickr** (SmugMug, Inc.) — PDF + XLSX; 2024 & 2025 — https://www.flickr.com/help/legal
- **Glassdoor** (Glassdoor LLC) — XLSX; CY2024 — https://about-us.glassdoor.com/site-us/wp-content/uploads/sites/2/2025/10/2025_2025_Glassdoor-DSA-Transparency-Report-CY2024_x.xlsx
- **GMX** (1&1 Mail & Media GmbH) — ODS (Art. 15); 2024 & 2025 — https://freephone.gmx.net/transparenzbericht
- **heise forums** (Heise Medien GmbH & Co. KG) — CSV; annual (2024 & 2025) — https://www.heise.de/Transparenz-nach-dem-Digital-Services-Act-DSA-10639819.html
- **iCloud Storage** (Apple Distribution International) — HTML report (17 Feb – 31 Dec 2024); also a Feb 2026 XLSX template — https://www.apple.com/legal/dsa/transparency/eu/icloud/2502/
- **Jeuxvideo.com** (Webedia) — Harmonised template (CSV/XLSX/PDF); 2024 & 2025 — https://www.jeuxvideo.com/transparence.htm
- **Riot Games** (Riot Games Ltd.) — XLSX; 2024 & 2025 — https://support-leagueoflegends.riotgames.com/hc/en-us/articles/25972785684627
- **Upwork** (Upwork Global Inc.) — XLSX; 2024 & 2025 — https://www.upwork.com/blog/upworks-2025-transparency-report-our-ongoing-work-to-protect-yours
- **WordPress.com** (Automattic Inc.) — Web + CSV; Jul – Dec 2025 — https://transparency.automattic.com/wordpress-dot-com/digital-services-act/
- **x-kom** (x-kom sp. z o.o. (Poland)) — XLSX (harmonised template); 2024 — https://www.x-kom.pl/dsa
- **eToro** (eToro — social/copy-trading) — landing page JS-rendered — find the template file
- **Eventbrite** (Eventbrite, Inc.) — landing page JS-rendered — find the template file
- **OVHcloud** (OVH Groupe SAS) — landing page JS-rendered — find the template file

(The three above are in `sources.csv` as `hub-pending` but don't carry a resolved
URL in the API catalogue yet — a browser should locate each platform's DSA report
file and add it to `harmonised-reports/raw/` for `extract.py`.)

---

## D. Bulk PDF archival — accessible but not mirrored

**California AB 587 Terms-of-Service reports.** All **100** filings are
catalogued with a working `source_url` on `oag.ca.gov`, but the PDFs (~300 MB
total) were **not** mirrored in-repo, so `archived`/`sha256`/`bytes` are blank
and `extract_narrative.py` can't index them. A browser (or a patient fetcher)
should download each PDF, store it, and backfill those columns.
Platforms (21): ArtStation, BAND, Discord, GitHub, Goodreads, Hudl, LinkedIn, Meta, Microsoft, Nextdoor, Peloton, Pinterest, Reddit, Roblox, Sketchfab, Snap, Strava, TikTok, Vimeo, X, YouTube.
Full list with URLs: `ca-ab587/ca_ab587_reports.csv`.

---

## E. Known-hard targets — identified, still not retrievable

Specific reports we know exist and want, but that resisted extraction. Each note
comes from the dataset builder's own caveats.

- **Australia eSafety BOSE — `www.esafety.gov.au` is WAF-walled.** The eSafety
  Commissioner's **Basic Online Safety Expectations** transparency-notice findings
  are a new intended dataset (scaffolded in `au-esafety/`), but the whole
  `esafety.gov.au` origin **resets/hangs every datacenter-IP request** (HTTP/2
  stream reset; HTTP/1.1 hang; static `/sites/default/files/…` PDFs included;
  `web.archive.org` is also egress-blocked here) — a residential IP + real browser
  is the unlock. First target: the **AI companion apps** findings (non-periodic
  notices given 16 Oct 2025 to Character.AI, Nomi, Chai, Chub AI; report published
  Mar 2026, survey figures revised Jul 2026):
    - Findings report — https://www.esafety.gov.au/industry/basic-online-safety-expectations/ai-services/findings-october-2025
    - AI-services hub — https://www.esafety.gov.au/industry/basic-online-safety-expectations/ai-services
    - Media release — https://www.esafety.gov.au/newsroom/media-releases/esafety-report-shows-ai-companions-are-putting-children-at-risk
  Save the rendered page (+ any PDF) into `au-esafety/raw/` per
  `au-esafety/raw/FETCH.md`, then run `au-esafety/build_esafety.py` and wire it
  into the API like the Singapore online-safety dataset. Further BOSE slices to
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
- **EU AI Act training-data summaries — checkbox PDFs + non-template signatories.**
  Google's training-data size bands are **checkbox selections not in the PDF text
  layer**, so they were transcribed from the *rendered* form (a browser renders
  the ticked boxes reliably) — the same trick would be needed for any other
  provider that publishes the AI-Office template as a checkbox PDF. Current
  coverage is Google + Meta + Microsoft + OpenAI + Swiss AI + SpeakLeash + Hugging
  Face (9 model entries). Note: several Code-of-Practice signatories — **Anthropic
  (incl. Fable 5), Mistral, xAI** — have **not** published the standardised
  template at all; they disclose training content only as free-form prose (model
  cards) or rely on the 2 Aug 2027 transitional deadline, so there's nothing
  template-shaped to fetch yet — worth a periodic re-check, not a scrape target
  today. Would extend `ai_training_metrics`.
- **EU Terrorist Content Online Regulation (TCOR) — more Art. 7 / Art. 8 sources.**
  Coverage is a deliberate starting set (Commission COM(2024) 64 per-Member-State
  orders; Spotify + Meta Art. 7 reports; Ireland's Coimisiún na Meán). Specific
  Art. 7 platforms still to add: **X, TikTok, Google, Microsoft, LinkedIn** (…);
  plus other Member States' Art. 8 authority reports. All exist as archived PDFs
  to transcribe. Would extend `tco_metrics`.

---

## F. The long tail — catalogued locations not yet archived

Beyond the curated items above, **128 of 259** rows in the
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
  RTV Euro AGD, Otodom, Gratka, Modivo/eobuwie, Answear, Slevomat, Datart; ss.lv,
  Osta.ee, Skelbiu.lt, Aruodas.lt, Njuškalo (HR), Bolha (SI), OLX.bg, Bazar.bg,
  Car.gr, Spitogatos, Publi24, Kainos.lt, Varle.lt, Senukai.

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
