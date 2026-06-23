# DSA transparency-report locations — non-VLOP online platforms

Under the EU [Digital Services Act](https://eur-lex.europa.eu/eli/reg/2022/2065/oj)
(Articles 15 & 24), **every** online platform offering services in the EU — not
just the designated Very Large Online Platforms / Search Engines (VLOPs/VLOSEs) —
must publish a periodic transparency report on its content moderation (micro and
small enterprises are exempt). Unlike the VLOPs, these reports are **not collected
in any single official index**: each platform publishes on its own site, in its
own format (PDF, HTML, XLSX/CSV — increasingly the harmonised
[Implementing Regulation (EU) 2024/2835](https://eur-lex.europa.eu/eli/reg_impl/2024/2835/oj)
template, mandatory from H2 2025).

This file catalogues where those reports live, to extend the VLOP/VLOSE dataset in
this repo. **The designated VLOPs/VLOSEs already archived here are not repeated** —
see the repo [`README.md`](README.md) for that list.

## How this was compiled

Located via web search and verified by fetching the page/file where possible.
Confidence levels:

- **verified** — the report page or file was fetched and confirmed to be a genuine
  DSA Art. 15/24 content-moderation report.
- **likely** — the URL was found in search results on the platform's own domain
  with strong DSA-specific signals (correct path/title/period), but the live page
  could not be fetched to confirm (most help-center pages on Zendesk/Salesforce
  return HTTP 403 to automated fetchers, and several sites are JS-rendered or
  geo/bot-gated).
- **uncertain** — a DSA page exists but it could not be confirmed as a full
  Art. 15/24 statistics report (e.g. only an Art. 24(2) recipient-count notice, a
  point-of-contact page, or a placeholder marked "coming soon").

No URLs were fabricated. Platforms for which no report could be located are listed
under "Searched, not found" so the negative result is recorded too.

## Authoritative index / aggregator sources

The best starting points for finding more report locations:

| Source | What it gives you |
|--------|-------------------|
| [EC — "How the DSA enhances transparency online"](https://digital-strategy.ec.europa.eu/en/policies/dsa-brings-transparency) | **Authoritative.** Direct per-VLOP/VLOSE links to each platform's periodic reports (incl. the adult platforms). |
| [EC — List of designated VLOPs and VLOSEs](https://digital-strategy.ec.europa.eu/en/policies/list-designated-vlops-and-vloses) | Canonical designation list — operating companies + designation/termination dates. |
| [EU DSA Transparency Database](https://transparency.dsa.ec.europa.eu/) | Individual "statements of reasons" (2.4 B+ records). NOT the periodic Art. 15 reports. |
| [Tech Policy Press — DSA report tracker](https://www.techpolicy.press/tracking-the-first-digital-services-act-transparency-reports/) | Third-party tracker of the first reports (mainly VLOPs). |
| [Tremau — DSA tracker](https://tremau.com/resources/dsa-database/) | Vendor tracker of designations + reporting guidance. |
| [DSA Observatory (Univ. of Amsterdam)](https://dsa-observatory.eu/) | Academic analysis + researcher-built trackers. |
| [Microsoft — DSA non-VLO report links](https://www.microsoft.com/en-us/digitalsafety/transparency-reports/jurisdictional-reports/dsa-non-vlo-tr-report-links) | Microsoft's own non-VLOP reports (incl. GitHub). |

## Social, messaging, community & video

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Discord | Discord Netherlands B.V. | [Hub](https://discord.com/safety-transparency) | ZIP (machine-readable template); 2024 & 2025 | verified |
| Reddit | Reddit, Inc. | [DSA info / Transparency Center](https://support.reddithelp.com/hc/en-us/articles/23595536875796-Digital-Services-Act-DSA-Information-for-EU-users) | PDF; semi-annual | likely |
| Viber | Rakuten Viber (Viber Media S.à r.l.) | [Report](https://www.viber.com/en/terms/eu-digital-services-act-dsa-transparency-report/) | HTML + tables; 18 Feb – 31 Dec 2025 | verified |
| Flickr | SmugMug, Inc. | [Legal / Transparency](https://www.flickr.com/help/legal) | PDF + XLSX; 2024 & 2025 | verified |
| Tumblr | Automattic Inc. | [Report](https://transparency.automattic.com/tumblr/digital-services-act/) | Web report + data; semi-annual | verified |
| Dailymotion | Dailymotion SA | [Report](https://legal.dailymotion.com/en/transparency/transparency-report-on-prohibited-content-policys-enforcement/) | HTML; annual | verified |
| Vimeo | Vimeo.com, Inc. | [DSA page](https://vimeo.com/legal/transparency/dsa) | HTML; Art. 24(2) recipient disclosure (<45 M), semi-annual | uncertain |
| Jeuxvideo.com | Webedia | [Report](https://www.jeuxvideo.com/transparence.htm) | Harmonised template (CSV/XLSX/PDF); 2024 & 2025 | likely |
| Threads | Meta Platforms Ireland Ltd. | [Meta regulatory reports](https://transparency.meta.com/reports/regulatory-transparency-reports/) | In Meta's non-VLOP DSA report; periodic | likely |
| Nextdoor | Nextdoor Holdings, Inc. | [Report](https://help.nextdoor.com/s/article/DSA-Transparency-Report) | HTML; periodic | likely |
| Kick | Kick Streaming Pty Ltd (Easygo) | [DSA guide](https://help.kick.com/en/articles/12066402-digital-services-act-dsa-information-guide) | HTML guide referencing the report | likely |
| Quora | Quora, Inc. | [DSA Transparency section](https://help.quora.com/hc/en-us/sections/13296037150612-DSA-Transparency) | HTML section; full Art. 15 stats unconfirmed | uncertain |

## Audio / music streaming

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Spotify | Spotify AB | [Hub](https://www.spotify.com/safetyandprivacy/transparency) ([2025 reports](https://www.spotify.com/safetyandprivacy/file/eu_2025_dsa_report_introduction_spotify)) | Report files; Art. 15; CY2025 | verified |
| SoundCloud | SoundCloud Ltd | [Hub](https://soundcloud.com/transparency-reports) ([2025 PDF](https://pages.soundcloud.com/en/transparency-reports/resources/SoundCloud_DSA_Report_2025_EN.pdf)) | PDF; 2025 | verified |

## E-commerce marketplaces & retail

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| eBay | eBay Inc. | [Hub](https://www.ebayinc.com/company/digital-services-act/) | PDF; 17 Feb – 31 Dec 2024 | likely |
| Etsy | Etsy, Inc. / Etsy Ireland UC | [Legal hub](https://www.etsy.com/legal/policy/eu-digital-services-act/1119915664620) | PDF; 2024 & 2025 | likely |
| Otto | Otto GmbH & Co KGaA | [Hub](https://www.otto.de/shoppages/digital_services_act_transparency_reports_dsa) | Hub + PDFs; 2024 & 2025 | verified |
| Vinted | Vinted UAB | [Safety hub](https://www.vinted.com/safety) ([2025 XLSX](https://marketplace-web-assets.vinted.com/assets/transparency-report/vinted-transparency-report-2025.xlsx)) | XLSX; 2024 & 2025 | verified |
| Vestiaire Collective | Vestiaire Collective SA | [Report](https://faq.vestiairecollective.com/hc/en-us/articles/34009544661393-EU-Digital-Services-Act) | PDF + Excel; 2025 | verified |
| Decathlon Marketplace | Decathlon SE | [Hub](https://www.decathlon.fr/lp/i/rapport-annuel-de-transparence) | Hub + PDF; 2024 & 2025 | verified |
| zooplus | zooplus SE | [Legal/DSA](https://www.zooplus.de/info/legal/DSA) ([PDF](https://corporate.zooplus.com/wp-content/uploads/2025/12/2025_DigitalServiceActTransparencyReporting_zooplus_signed.pdf)) | Signed PDF; Dec 2025 | verified |
| Veepee (vente-privee) | Veepee | [Report](https://aide.veepee.fr/article/1630-informations-reglementaires) ([2026 XLSX](https://www.veepee.fr/docs/dsa/2025/fr/french_transparency_report_2026.xlsx)) | XLSX; 2024 & 2025 | verified |
| AboutYou | ABOUT YOU SE & Co. KG | [Impressum](https://www.aboutyou.de/impressum) ([XLSX](https://www.aboutyou.de/assets/documents/Transparency_Report.csv.xlsx)) | XLSX (harmonised template); 2025/2026 | verified |
| Refurbed | refurbed GmbH | [Report](https://refurbed.com/dsa-transparency-report/) | HTML; 17 Feb 2024 – 16 Feb 2025 | verified |
| Back Market | Back Market SAS | [PDF](https://assets.ctfassets.net/mmeshd7gafk1/1rtDZVxgD6BhehY82JVTiX/2aacbe1237b2aa49b869c20b982795a2/Transparency_Report_04.2025.pdf) | PDF; Apr 2025 (semi-annual) | verified |
| Marktplaats | Marktplaats B.V. (Adevinta) | [PDF](https://statisch.marktplaats.nl/docs/Transparency_report_MP.pdf) | PDF; 17 Feb – 31 Dec 2024 | verified |
| ManoMano | Colibri SAS | [XLSX](https://cdn.manomano.com/legal/reports/DSA_Transparency_Report_2025.xlsx) | XLSX; 2025 | verified |
| Cdiscount | Cdiscount S.A. | [Hub](https://www.cdiscount.com/n-429993/pagesaurlfixe-arbo/rapport-de-transparence-dsa.html) | HTML hub | likely |
| Leboncoin | LBC France SAS (Adevinta) | [PDF](https://img.leboncoin.fr/api/v1/lbcpb2/documents/transparency_report-cover_page-FR_version.pdf?rule=cms_pdf) | PDF (FR) | likely |
| Rakuten France | Rakuten France SAS | [PDF](https://fr.shopping.rakuten.com/cdn/legal/DSA/Rapport_Transparence_1_v1/RAKUTEN_FRANCE_RAPPORT_TRANSPARENCE_2025.pdf) | PDF; 2025 | likely |
| Boulanger | Boulanger SA | [PDF](https://www.boulanger.com/content/dam/Boulanger/juridique/mentions-legales/rapporttransparence-dsa-2024.pdf) | PDF; CY2024 | likely |
| Carrefour Marketplace | Carrefour | [Legal notices](https://www.carrefour.fr/mentions-legales) | Linked report; FY2024 & FY2025 | likely |
| eMAG | Dante International S.A. | [Report](https://www.emag.ro/info/raport-transparenta-dsa) | HTML + downloads; biannual | likely |
| Notino | Notino s.r.o. | [Report](https://www.notino.com/dsa-transparency-report/) | HTML/PDF | likely |
| MediaMarkt / Saturn | MediaMarktSaturn | [Report](https://www.mediamarkt.de/de/shop/dsa-transparenzbericht.html) | HTML | likely |
| Galaxus / Digitec | Digitec Galaxus AG | [Report](https://www.galaxus.de/de/page/transparenzbericht-dsa-9020) | HTML (DE/AT) | likely |
| Douglas | Douglas GmbH | [Report](https://www.douglas.de/de/cp/dsa-transparenzbericht/dsa-transparenzbericht) | HTML | likely |
| Coolblue | Coolblue B.V. | [Report](https://www.coolblue.nl/transparantierapport) | HTML | likely |
| Discogs | Discogs (Zink Media, Inc.) | [Statement](https://support.discogs.com/hc/en-us/articles/12730436158349-EU-Digital-Services-Act-Statement) | HTML; 17 Feb 2024 – 16 Feb 2025 | likely |
| Reverb | Reverb.com LLC | [DSA page](https://help.reverb.com/hc/en-us/articles/14017920631571-EU-Digital-Services-Act) | HTML; semi-annual | likely |
| Depop | Depop Ltd | [DSA page](https://depophelp.zendesk.com/hc/en-gb/articles/13057572688273-EU-Digital-Services-Act) | HTML; 2025 | likely |
| Fruugo | Fruugo.com Ltd | [Compliance statement](https://www.fruugo.ie/help/detail/dsa-compliance-statement) | HTML; Jun – Dec 2025 | likely |
| Vivino | Vivino ApS | [Content moderation policy](https://www.vivino.com/legal/content-moderation-policy) | HTML; semi-annual (Art. 24) | likely |

## Classifieds

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Kleinanzeigen | Kleinanzeigen GmbH | [Hub](https://themen.kleinanzeigen.de/transparenzbericht/) | HTML hub + PDFs; semi-annual | likely |
| OLX | OLX B.V. (Prosus) | [Report](https://www.olx.pl/d/dsa-transparency-report/) | HTML; semi-annual | likely |

## Travel, mobility & accommodation

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| BlaBlaCar | Comuto SA | [PDF](https://blog.blablacar.fr/wp-content/uploads/2025/02/2024-dsa-transparency-report-blablacar.pdf) | PDF; 2024 | verified |
| Kayak | KAYAK Software Corp. (Booking Holdings) | [Hub](https://www.kayak.ie/c/digital-services-act/) | PDF; 2026 | verified |
| Uber Eats | Uber B.V. | [Legal page](https://www.uber.com/legal/en/document/?name=digital-services-act---uber-eats-transparency-report) | Legal page + Drive docs; 2024 & 2025 | verified |
| Bolt | Bolt Technology OÜ | [Legal page](https://bolt.eu/en/legal/digital-services-act/) | Legal page; 17 Feb 2024 – 17 Feb 2025 | likely |
| GetYourGuide | GetYourGuide GmbH / AG | [DSA page](https://www.getyourguide.com/c/dsa/) | HTML; 2024 (Art. 15/24/42) | likely |
| Skyscanner | Skyscanner Ltd | [DSA hub](https://www.skyscanner.net/media/digital-services-act) | DSA hub (JS-rendered) | likely |

## App stores & gaming

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Roblox | Roblox Corporation | [Transparency](https://about.roblox.com/transparency) ([2025 PDF](https://about.roblox.com/pdf/eu-dsa-transparency-report-2025)) | PDF + XLSX/CSV; 2024 & 2025 | verified |
| Ubisoft Connect | Ubisoft Entertainment SA | [Report](https://www.ubisoft.com/legal/documents/transparencyreport/en-US) | PDF; CY2024 | verified |
| Nintendo eShop | Nintendo Co., Ltd. | [DSA page](https://www.nintendo.com/en-gb/Legal-information/Digital-Services-Act-2522334.html) | PDF; Feb 2025 | verified |
| Samsung Galaxy Store | Samsung Electronics | [Regulatory info](https://www.samsung.com/uk/support/regulatory-information/) | PDF; Aug 2025 – Jan 2026 | verified |
| Epic Games Store | Epic Games, Inc. | [Report](https://safety.epicgames.com/transparency-reports/european-union) | XLSX + hub; Feb 2024 – Feb 2025 | likely |
| Twitch | Twitch Interactive (Amazon) | [Report](https://safety.twitch.tv/s/article/Twitch-DSA-Transparency-Report-February-2025) | HTML; Feb 2025 | likely |

## Dating

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Match Group (Tinder, Hinge, OkCupid, Meetic, …) | Match Group | [Resources](https://www.matchgroup-safety.com/resources) | PDF + per-app Excel; 2024 & 2025 | verified |
| Bumble (Badoo, Fruitz) | Bumble Inc. | [Hub](https://support.bumble.com/hc/en-us/articles/28718583113757-Digital-Services-Act-Transparency-report) ([2025 PDF](https://bumbcdn.com/i/big/dsa/bumble/dsa-transparency-report-2025.pdf)) | PDF + Annex; 2025 | verified |
| Grindr | Grindr LLC | [Reports](https://help.grindr.com/hc/en-us/articles/38555862683795-Grindr-EU-Digital-Services-Act-Transparency-Reports) | PDF + Excel; annual | likely |

## Developer / software / hosting

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| GitHub | GitHub, Inc. (Microsoft) | [Transparency Center](https://transparencycenter.github.com/) ([2024 PDF](https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/final/en-us/microsoft-brand/documents/GitHub-DSA-Transparency-Report-Feb-Dec-2024.pdf)) | PDF; Feb – Dec 2024 | verified |
| Cloudflare | Cloudflare, Inc. | [Transparency](https://www.cloudflare.com/transparency/) | XLSX (template); H2 2025 | verified |
| WordPress.com | Automattic Inc. | [Report](https://transparency.automattic.com/wordpress-dot-com/digital-services-act/) | Web + CSV; Jul – Dec 2025 | verified |
| Hugging Face | Hugging Face SAS | [Content policy](https://huggingface.co/content-policy) ([2025 PDF](https://cdn-media.huggingface.co/landing/assets/DSA_HF_2025.pdf)) | PDF; 2025 | likely |

## Reviews & jobs

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Trustpilot | Trustpilot A/S | [PDF](https://cdn.trustpilot.net/businesssite/Trustpilot-DSA-Transparency-Report-May-2025.pdf) | PDF; 17 Feb 2024 – 16 Feb 2025 | verified |
| Yelp | Yelp Inc. | [Report](https://www.yelp-support.com/article/Yelp-DSA-Transparency-Report-2025?l=en_GB) | HTML; 2024 & 2025 | likely |
| Indeed | Indeed, Inc. | [Report](https://www.indeed.com/legal/digital-services-act-transparency-report) | HTML; 16 Feb – 31 Dec 2024 | likely |
| Glassdoor | Glassdoor LLC | [XLSX](https://about-us.glassdoor.com/site-us/wp-content/uploads/sites/2/2025/10/2025_2025_Glassdoor-DSA-Transparency-Report-CY2024_x.xlsx) | XLSX; CY2024 | likely |

## Creator / publishing

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Patreon | Patreon, Inc. | [DSA page](https://support.patreon.com/hc/en-us/articles/23684794051597-EU-Digital-Services-Act) | HTML; Art. 24 data, Jul – Dec 2025 | likely |
| Medium | A Medium Corporation | [DSA Information section](https://help.medium.com/hc/en-us/sections/21832701520791-Digital-Service-Act-DSA-Information) | HTML; DSA info/orders | uncertain |

## Adult content

(Pornhub, XNXX, XVideos are already in this repo. Stripchat was de-designated as a
VLOP in May 2025 but still publishes.)

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Stripchat | Technius Ltd. (Cyprus) | [Jun 2025](https://support.stripchat.com/hc/en-us/articles/36391881823249-DSA-TRANSPARENCY-REPORT-JUNE-2025) ([Feb 2026](https://support.stripchat.com/hc/en-us/articles/44195482301457), [Dec 2024](https://support.stripchat.com/hc/en-us/articles/31227854549137), [Jun 2024](https://support.stripchat.com/hc/en-us/articles/26200876452753)) | HTML; semi-annual | likely (listed on the EC overview page) |

## Searched, not found / out of scope

No first-party Art. 15/24 content-moderation report could be located (some publish
only an Art. 24(2) recipient-count notice or a point-of-contact page; others are
out of the EU/EEA or below the small-enterprise threshold). Recorded so the
negative result is not re-searched:

- **Only an Art. 11/24(2) notice or contact page (no full report found):** Telegram,
  Wallapop, Kaufland, Stack Overflow, Dropbox, Atlassian/Bitbucket, Substack
  (placeholder "coming soon"), FreeNow.
- **No findable report:** Allegro, Bol.com, Idealo, Willhaben, Subito, Catawiki,
  Milanuncios, Mobile.de, Fotocasa, InfoJobs, Joom, Omio, eDreams ODIGEO,
  GitLab, npm, PyPI, Docker Hub, SourceForge, Replit, Notion, Steam, GOG, EA,
  itch.io, Microsoft Store, Amazon Appstore, Mastodon, VK, Deezer, Rumble,
  Odysee, Triller, Likee, Bigo Live, Home24, Tchibo, Bonprix, vidaXL, Conrad,
  Spartoo, CDON, eDarling/Parship, OnlyFans (general report exists, no DSA-specific
  one confirmable on its own domain).
- **Out of scope:** Swiss-only platforms (tutti.ch, ricardo.ch, anibis.ch — not
  EU/EEA); Finn.no (Norway has not transposed the DSA into the EEA agreement);
  Avito (not EU-operating).
