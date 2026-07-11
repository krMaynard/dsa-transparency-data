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
open each URL, save the PDF, and drop it in `ny-tos-reports/archive/` so
`extract_narrative.py` can index it.
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
Full list: `dsa_reports.csv` (rows with `harmonised_template=yes` and no `archived` link).

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
- **EU AI Act training-data summaries — checkbox PDFs + more providers.** Google's
  training-data size bands are **checkbox selections not in the PDF text layer**,
  so they were transcribed from the *rendered* form (a browser renders the ticked
  boxes reliably). Current coverage is Google + Meta + Microsoft + OpenAI; other
  GPAI providers (e.g. Anthropic, Mistral, xAI, Amazon) publish the AI-Office
  template and could be added. Would extend `ai_training_metrics`.
- **EU Terrorist Content Online Regulation (TCOR) — more Art. 7 / Art. 8 sources.**
  Coverage is a deliberate starting set (Commission COM(2024) 64 per-Member-State
  orders; Spotify + Meta Art. 7 reports; Ireland's Coimisiún na Meán). More hosting
  providers' Art. 7 reports and other Member States' Art. 8 authority reports exist
  as archived PDFs to transcribe. Would extend `tco_metrics`.

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

_Generated from the catalogue snapshots in `krmaynard/transparency-report-api`
(`data/report-locations.csv`, `data/ny-tos-reports.csv`, `data/ca-ab587-reports.csv`),
which mirror this repo's `dsa_reports.csv`, `ny_tos_reports.csv`, and
`ca-ab587/ca_ab587_reports.csv`._
