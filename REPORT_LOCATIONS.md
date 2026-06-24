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

The relational build (`build_reports_db.py` → `dsa_reports.db`/`.csv`) adds a
**`harmonised_template`** dimension per platform — whether the report uses the EU
machine-readable template (Reg. (EU) 2024/2835, Annex I): `yes`/`no`/`partial`/
`unknown`, derived from the format column with curated VLOP overrides. See the
repo README.

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
| Yubo | Twelve App SAS | [Transparency report](https://www.yubo.live/safety/transparency-report) | Bi-annual T&S report (DSA-aligned) | likely |
| Quora | Quora, Inc. | [DSA Transparency section](https://help.quora.com/hc/en-us/sections/13296037150612-DSA-Transparency) | HTML section; full Art. 15 stats unconfirmed | uncertain |
| heise forums | Heise Medien GmbH & Co. KG | [DSA transparency](https://www.heise.de/Transparenz-nach-dem-Digital-Services-Act-DSA-10639819.html) | CSV; annual (2024 & 2025) | verified |
| gutefrage | gutefrage.net GmbH | [Transparenzbericht](https://www.gutefrage.net/company/transparenzbericht) | Annual Art. 15 report | likely |
| eToro (social/copy-trading) | eToro (Europe) Ltd | [DSA transparency report](https://www.etoro.com/customer-service/regulation-license/dsa-transparency-report/) | PDF set (Art. 15/24 template) | verified |

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
| Skroutz | Skroutz S.A. (Greece) | [DSA hub](https://www.skroutz.gr/digital-services-act) | PDF + Excel/ZIP; 2024 & 2025 | verified |
| Ceneo | Ceneo.pl sp. z o.o. (Poland) | [DSA hub](https://info.ceneo.pl/dsa) | XLSX Annex I (EN + PL); 2024 & 2025 | verified |
| Discogs | Discogs (Zink Media, Inc.) | [Statement](https://support.discogs.com/hc/en-us/articles/12730436158349-EU-Digital-Services-Act-Statement) | HTML; 17 Feb 2024 – 16 Feb 2025 | likely |
| Reverb | Reverb.com LLC | [DSA page](https://help.reverb.com/hc/en-us/articles/14017920631571-EU-Digital-Services-Act) | HTML; semi-annual | likely |
| Depop | Depop Ltd | [DSA page](https://depophelp.zendesk.com/hc/en-gb/articles/13057572688273-EU-Digital-Services-Act) | HTML; 2025 | likely |
| Fruugo | Fruugo.com Ltd | [Compliance statement](https://www.fruugo.ie/help/detail/dsa-compliance-statement) | HTML; Jun – Dec 2025 | likely |
| Vivino | Vivino ApS | [Content moderation policy](https://www.vivino.com/legal/content-moderation-policy) | HTML; semi-annual (Art. 24) | likely |
| DocMorris | DocMorris N.V. | [DSA page](https://www.docmorris.de/digital-services-act) | HTML DSA page; contents unverified | uncertain |
| Trendyol | DSM Grup / Trendyol Group | [2025 PDF](https://9be604a381897de8.mncdn.com/tymp/prod/documents/policy/TY_DSA_Report_2025.pdf) ([2024 PDF](https://cdn.dsmcdn.com/mobile/international/legal/transparency_report_2024.pdf)) | PDF; 2024 & 2025 | verified |
| home24 | home24 SE | [Impressum](https://www.home24.de/home24-impressum/) | Transparenzbericht; 2025/2026 | likely |
| Conforama | Conforama France SA | [DSA page](https://www.conforama.fr/digital-service-act) | HTML DSA page; AMAR + notice | uncertain |
| Whatnot | Whatnot Inc. | [EU DSA](https://help.whatnot.com/hc/en-us/articles/23619888476557-Whatnot-The-EU-Digital-Services-Act) | PDF + XLSX; 2025 & 2026 | verified |
| Tradera | Tradera Sweden AB | [Support](https://www.tradera.com/support) | Annual report (referenced in T&C) | likely |

## Classifieds, real estate & auto

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Kleinanzeigen | Kleinanzeigen GmbH | [Hub](https://themen.kleinanzeigen.de/transparenzbericht/) | HTML hub + PDFs; semi-annual | likely |
| OLX | OLX B.V. (Prosus) | [Report](https://www.olx.pl/d/dsa-transparency-report/) | HTML; semi-annual | likely |
| AutoScout24 | AutoScout24 SE | [PDF](https://assets.ctfassets.net/uaddx06iwzdz/4oZBiZrkfhU88u1wa3zUGk/bb5b98026b8146453087306641ed9dec/AutoScout24Transparenzbericht2024.pdf) | PDF (Art. 15/24); Jul – Dec 2024 | verified |
| Idealista | Idealista S.A.U. | [DSA info](https://www.idealista.com/ayuda/articulos/informacion-de-idealista-en-cumplimiento-del-reglamento-de-servicios-digitales/) | HTML; Art. 15/24 | likely |

## Travel, mobility, accommodation & events

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Airbnb | Airbnb Ireland UC | [PDF](https://assets.airbnb.com/help/Airbnb_Ireland_UC_Transparency_Report_2025Feb14.pdf) | PDF; CY2024 | verified |
| Expedia | Expedia, Inc. | [Hub](https://legal.expediagroup.com/regulatory-and-compliance/digital-services-act) | PDF + XLSX; 2024 & 2025 | verified |
| Hotels.com | Hotels.com, L.P. | [Hub](https://legal.expediagroup.com/regulatory-and-compliance/digital-services-act) | PDF + XLSX; 2024 & 2025 | verified |
| Vrbo | EG Vacation Rentals Ireland Ltd. | [Hub](https://legal.expediagroup.com/regulatory-and-compliance/digital-services-act) | PDF + XLSX; 2024 & 2025 | verified |
| Trivago | trivago N.V. | [DSA info](https://company.trivago.com/dsa-information/) ([PDF](https://company.trivago.com/wp-content/uploads/2025/03/trivago-DSA-Transparency-Report.pdf)) | PDF; Feb 2025 | verified |
| Tripadvisor | Tripadvisor LLC | [Report](https://www.tripadvisor.com/TransparencyReport2025) | HTML; 2025 | likely |
| Viator | Viator, Inc. | [PDF](https://assetlibrary.viator.com/m/523fc4a4d818e6fd/original/Viator_Inc_Digital_Services_Act_Transparency_Report_CY_2024.pdf) | PDF; CY2024 | verified |
| Hostelworld | Hostelworld | [Security & privacy](https://www.hostelworld.com/legal/security-privacy/) | XLSX; 12 mo to 31 Dec 2025 | verified |
| Eventbrite | Eventbrite Operations (IE) Ltd. | [PDF](https://www.eventbrite.com/blog/wp-content/uploads/2026/03/Eventbrite-2025-Transparency-Report.pdf) | PDF (EC template); 2024 & 2025 | verified |
| BlaBlaCar | Comuto SA | [PDF](https://blog.blablacar.fr/wp-content/uploads/2025/02/2024-dsa-transparency-report-blablacar.pdf) | PDF; 2024 | verified |
| Kayak | KAYAK Software Corp. (Booking Holdings) | [Hub](https://www.kayak.ie/c/digital-services-act/) | PDF; 2026 | verified |
| Uber Eats | Uber B.V. | [Legal page](https://www.uber.com/legal/en/document/?name=digital-services-act---uber-eats-transparency-report) | Legal page + Drive docs; 2024 & 2025 | verified |
| Bolt | Bolt Technology OÜ | [Legal page](https://bolt.eu/en/legal/digital-services-act/) | Legal page; 17 Feb 2024 – 17 Feb 2025 | likely |
| GetYourGuide | GetYourGuide GmbH / AG | [DSA page](https://www.getyourguide.com/c/dsa/) | HTML; 2024 (Art. 15/24/42) | likely |
| Skyscanner | Skyscanner Ltd | [DSA hub](https://www.skyscanner.net/media/digital-services-act) | DSA hub (JS-rendered) | likely |
| HomeToGo | HomeToGo SE | [DSA page](https://www.hometogo.de/dsa/) | XLSX; Art. 24(2) + removals | verified |
| Novasol | Awaze A/S | [Report](https://www.novasol.com/digital-services-act) | PDF; Feb 2026 (Awaze group) | verified |
| Belvilla | Awaze Group | [Report (Awaze group)](https://www.novasol.com/digital-services-act) | PDF; Feb 2026 | likely |
| Interhome | Interhome Group (HomeToGo) | [Legal info](https://www.interhome.group/en-ch/legal-information) | Annual; report referenced | likely |

## Food delivery & gig / freelance

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Just Eat Takeaway (Lieferando, Thuisbezorgd) | Just Eat Takeaway.com N.V. | [Governance docs](https://www.justeattakeaway.com/governance/governance-documents/) | ZIP (template); 17 Feb – 31 Dec 2025 | verified |
| Deliveroo | Deliveroo plc | [PDF](https://dpd-12774-s3.s3.eu-west-2.amazonaws.com/assets/7517/4559/3138/Deliveroo_DSA_Transparency_Report_April2025.pdf) | PDF; Apr 2025 | verified |
| Glovo | Glovoapp23 S.A. (Delivery Hero) | [Report](https://about.glovoapp.com/culture-and-values/transparency-report/) | PDF; 2025 | verified |
| Wolt | Wolt Enterprises Oy (DoorDash) | [PDF](https://assets.ctfassets.net/23u853certza/4UBct5Uy0IYtBe4xXSEclg/84a36c8226a026a23859abb166875db6/Wolt_DSA_Transparency_Report2025.pdf) | PDF; 17 Feb 2024 – 17 Feb 2025 | verified |
| Delivery Hero (foodora, …) | Delivery Hero SE | [DSA statement](https://www.deliveryhero.com/digital-services-act/) | HTML; content-moderation report + AMAR | likely |
| Malt | Malt Community SAS | [Transparency](https://www.malt.fr/c/transparency) | Web report; 2024 & 2025 | likely |
| Upwork | Upwork Global Inc. | [2025 report](https://www.upwork.com/blog/upworks-2025-transparency-report-our-ongoing-work-to-protect-yours) | XLSX; 2024 & 2025 | likely |
| Fiverr | Fiverr International Ltd. | [DSA overview](https://help.fiverr.com/hc/en-us/articles/22578911624977-DSA-overview) | HTML overview | uncertain |
| Fixly | Fixly sp. z o.o. (OLX / Adevinta) | [Legal info](https://pomoc.fixly.pl/hc/pl/categories/34663617565725-Informacje-Prawne) | Web/PDF moderation report | likely |

## App stores & gaming

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Roblox | Roblox Corporation | [Transparency](https://about.roblox.com/transparency) ([2025 PDF](https://about.roblox.com/pdf/eu-dsa-transparency-report-2025)) | PDF + XLSX/CSV; 2024 & 2025 | verified |
| Ubisoft Connect | Ubisoft Entertainment SA | [Report](https://www.ubisoft.com/legal/documents/transparencyreport/en-US) | PDF; CY2024 | verified |
| Nintendo eShop | Nintendo Co., Ltd. | [DSA page](https://www.nintendo.com/en-gb/Legal-information/Digital-Services-Act-2522334.html) | PDF; Feb 2025 | verified |
| Samsung Galaxy Store | Samsung Electronics | [Regulatory info](https://www.samsung.com/uk/support/regulatory-information/) | PDF; Aug 2025 – Jan 2026 | verified |
| Epic Games Store | Epic Games, Inc. | [Report](https://safety.epicgames.com/transparency-reports/european-union) | XLSX + hub; Feb 2024 – Feb 2025 | likely |
| Twitch | Twitch Interactive (Amazon) | [Report](https://safety.twitch.tv/s/article/Twitch-DSA-Transparency-Report-February-2025) | HTML; Feb 2025 | likely |
| Miniclip | Miniclip SA (Tencent) | [Report](https://www.miniclip.com/dsa-transparency-report) | Landing + ZIP; CY2025 | verified |
| GameDistribution | Azerion | [Report](https://static.gamedistribution.com/dsa-transparency-report.html) | HTML; CY2024 | verified |
| Niantic (Pokémon GO, …) | Niantic Inc. | [Report](https://nianticlabs.com/dsa-transparency) | Landing + Excel/PDF; CY2025 | verified |
| Chess.com | Chess.com, LLC | [DSA compliance](https://www.chess.com/article/view/digital-services-act-compliance) | HTML; Art. 24(2) MAU only | uncertain |

## Dating

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Match Group (Tinder, Hinge, OkCupid, Meetic, …) | Match Group | [Resources](https://www.matchgroup-safety.com/resources) | PDF + per-app Excel; 2024 & 2025 | verified |
| Bumble (Badoo, Fruitz) | Bumble Inc. | [Hub](https://support.bumble.com/hc/en-us/articles/28718583113757-Digital-Services-Act-Transparency-report) ([2025 PDF](https://bumbcdn.com/i/big/dsa/bumble/dsa-transparency-report-2025.pdf)) | PDF + Annex; 2025 | verified |
| Grindr | Grindr LLC | [Reports](https://help.grindr.com/hc/en-us/articles/38555862683795-Grindr-EU-Digital-Services-Act-Transparency-Reports) | PDF + Excel; annual | likely |
| Feeld | Feeld Ltd | [DSA report](https://feeld.co/ask-feeld/member-resources/dsa) | ZIP; 2025 full year | verified |
| Happn | happn SAS | [PDF](https://www.happn.com/customer-support/rapport_2ndTrimestre.pdf) | PDF; S2 2025 | verified |
| Lovoo | LOVOO GmbH | [PDF](https://www.lovoo.com/de/wp-content/uploads/sites/4/2026/01/LOVOO_Transparenzbericht_2024.pdf) | PDF (DE); 2024 | likely |

## Developer / software / hosting

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| GitHub | GitHub, Inc. (Microsoft) | [Transparency Center](https://transparencycenter.github.com/) ([2024 PDF](https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/final/en-us/microsoft-brand/documents/GitHub-DSA-Transparency-Report-Feb-Dec-2024.pdf)) | PDF; Feb – Dec 2024 | verified |
| Cloudflare | Cloudflare, Inc. | [Transparency](https://www.cloudflare.com/transparency/) | XLSX (template); H2 2025 | verified |
| WordPress.com | Automattic Inc. | [Report](https://transparency.automattic.com/wordpress-dot-com/digital-services-act/) | Web + CSV; Jul – Dec 2025 | verified |
| Hugging Face | Hugging Face SAS | [Content policy](https://huggingface.co/content-policy) ([2025 PDF](https://cdn-media.huggingface.co/landing/assets/DSA_HF_2025.pdf)) | PDF; 2025 | likely |

## Web hosting, registrars, site builders & infrastructure

(Intermediary/hosting services with Art. 15 reporting duties.)

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Shopify | Shopify Inc. | [Legal notices](https://www.shopify.com/legal/p2b/legal-notices) | Hub: PDF + XLSX; CY2024 & 2025 | verified |
| Wix | Wix.com Ltd. | [Report](https://support.wix.com/en/article/dsa-transparency-report-2024) | Web; CY2024 | verified |
| Squarespace | Squarespace, Inc. | [PDF](https://www.squarespace.com/s/Digital-Services-Act-Report-20250228.pdf) | PDF; 2024 | verified |
| GoDaddy | GoDaddy Inc. | [Disclosure](https://www.godaddy.com/legal/agreements/digital-services-act-disclosure) | Web; 2024 & 2025 | likely |
| OVHcloud | OVH Groupe SAS | [PDF](https://corporate.ovhcloud.com/sites/default/files/2025-04/rapport_de_transparence_dsa_ovhcloud_2025.pdf) | PDF + spreadsheet; 17 Feb – 31 Dec 2024 | verified |
| Hostinger | Hostinger International Ltd. | [Report](https://www.hostinger.com/legal/dsa-transparency-report) | PDF + XLSX; 2024 – 2025 | verified |
| Akamai | Akamai Technologies, Inc. | [DSA hub](https://www.akamai.com/legal/eu-digital-services-act) | PDF/XLSX; 2024, H1 & H2 2025 | verified |
| Vercel | Vercel Inc. | [Transparency](https://vercel.com/legal/transparency) | Web; 17 Feb – 15 Dec 2024 | verified |
| Gandi | Gandi SAS | [Report](https://www.gandi.net/en-US/digital-service-act-transparency-report) | Web + PDF; 2024 & 2025 | verified |
| Alibaba Cloud | Alibaba Cloud (Alibaba.com Singapore) | [DSA compliance](https://www.alibabacloud.com/help/en/legal/latest/eu-digital-services-act-dsa-compliance-information) | PDF; 17 Feb 2024 – 16 Feb 2025 (cloud service, not the Alibaba.com marketplace) | verified |
| Hetzner | Hetzner Online GmbH | [DSA page](https://www.hetzner.com/legal/digital-services-act/) | Contact/notice page only | uncertain |
| Fastly | Fastly, Inc. | [DMCA/DSA](https://www.fastly.com/dmca-dsa) | Compliance notice only | uncertain |

## Search engines (non-VLOSE)

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| DuckDuckGo | DuckDuckGo, Inc. | [Regulatory reporting](https://duckduckgo.com/duckduckgo-help-pages/r-legal/regulatory-reporting) | XLSX (template); CY2025 (+ 2024 PDF) | verified |
| Qwant | Qwant (France) | [Report](https://about.qwant.com/legal/rapport-de-transparence-qwant-2025/) | HTML + Excel + PDF; CY2025 | verified |
| Lilo | Lilo SAS (now Qwant) | [Report](https://lilo.org/rapport-transparence) | HTML + Excel; Sep – Dec 2025 | verified |

## Reviews & jobs

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Trustpilot | Trustpilot A/S | [PDF](https://cdn.trustpilot.net/businesssite/Trustpilot-DSA-Transparency-Report-May-2025.pdf) | PDF; 17 Feb 2024 – 16 Feb 2025 | verified |
| Yelp | Yelp Inc. | [Report](https://www.yelp-support.com/article/Yelp-DSA-Transparency-Report-2025?l=en_GB) | HTML; 2024 & 2025 | likely |
| Indeed | Indeed, Inc. | [Report](https://www.indeed.com/legal/digital-services-act-transparency-report) | HTML; 16 Feb – 31 Dec 2024 | likely |
| Glassdoor | Glassdoor LLC | [XLSX](https://about-us.glassdoor.com/site-us/wp-content/uploads/sites/2/2025/10/2025_2025_Glassdoor-DSA-Transparency-Report-CY2024_x.xlsx) | XLSX; CY2024 | likely |
| StepStone | The Stepstone Group GmbH | [Report](https://www.stepstone.de/e-recruiting/en/legal/report-dsa/) | Web transparency report | likely |

## Creator, publishing, education & community

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Patreon | Patreon, Inc. | [DSA page](https://support.patreon.com/hc/en-us/articles/23684794051597-EU-Digital-Services-Act) | HTML; Art. 24 data, Jul – Dec 2025 | likely |
| Medium | A Medium Corporation | [DSA Information section](https://help.medium.com/hc/en-us/sections/21832701520791-Digital-Service-Act-DSA-Information) | HTML; DSA info/orders | uncertain |
| Fandom (Wikia) | Fandom, Inc. | [DSA hub](https://www.fandom.com/digital-services-act) ([2024 supplement](https://www.fandom.com/fandom-transparency-report-2024-dsa-supplement)) | HTML; 1 Feb 2024 – 31 Jan 2025 | verified |
| Wattpad | Wattpad Corp. (Naver) | [Report](https://policies.wattpad.com/transparency-report/) | HTML; to 31 Dec 2025 | verified |
| Behance | Adobe Inc. | [EU DSA report](https://www.adobe.com/trust/transparency/reports/eu-dsa-report.html) | HTML; 17 Feb – 31 Dec 2024 | verified |
| Udemy | Udemy, Inc. | [DSA information](https://support.udemy.com/hc/en-us/articles/17923655139095-Digital-Services-Act-Information-European-Union-Users-Only) | HTML; CY2024 | verified |
| Scribd (Everand, SlideShare) | Scribd, B.V. | [DSA section](https://support.scribd.com/hc/en-us/sections/23708444653588-Publication-of-Information-for-the-European-Digital-Services-Act) | HTML; from late 2024 | verified |

## Adult content

(Pornhub, XNXX, XVideos are already in this repo. Stripchat was de-designated as a
VLOP in May 2025 but still publishes.)

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Stripchat | Technius Ltd. (Cyprus) | [Jun 2025](https://support.stripchat.com/hc/en-us/articles/36391881823249-DSA-TRANSPARENCY-REPORT-JUNE-2025) ([Feb 2026](https://support.stripchat.com/hc/en-us/articles/44195482301457), [Dec 2024](https://support.stripchat.com/hc/en-us/articles/31227854549137), [Jun 2024](https://support.stripchat.com/hc/en-us/articles/26200876452753)) | HTML; semi-annual | likely (listed on the EC overview page) |

## Designated VLOPs / VLOSEs

The 25 EU-designated Very Large Online Platforms / Search Engines (45 M+ EU users)
— the ones whose full reports are archived elsewhere in this repo — included here
for completeness. They report **semi-annually**; the first EU harmonised
machine-readable (Annex I) reports were due **end of February 2026** (covering
H2 2025), so reports up to Aug 2025 are narrative PDF/HTML. Aggregated index: the
EC [DSA transparency page](https://digital-strategy.ec.europa.eu/en/policies/dsa-brings-transparency).

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| AliExpress | Alibaba (AliExpress) | [Transparency center](https://www.aliexpress.com/p/transparencycenter/transparencyReport.html) | Hub; latest H2 2025 | likely |
| Amazon Store | Amazon EU S.à r.l. | [Report](https://trustworthyshopping.aboutamazon.com/eu-transparency-report-amazon-jul-dec-2025) | HTML; Jul – Dec 2025 | likely |
| Apple App Store | Apple Distribution International | [DSA hub](https://www.apple.com/legal/dsa/) | Hub + PDF | likely |
| Booking.com | Booking.com B.V. | [DSA hub](https://www.booking.com/content/dsa.en-gb.html) | Hub; HTML/PDF | likely |
| Facebook | Meta Platforms Ireland | [Meta regulatory reports](https://transparency.meta.com/reports/regulatory-transparency-reports/) | Hub; latest H2 2025 | likely |
| Instagram | Meta Platforms Ireland | [Meta regulatory reports](https://transparency.meta.com/reports/regulatory-transparency-reports/) | Hub; latest H2 2025 | likely |
| LinkedIn | LinkedIn Ireland | [Feb 2026 ZIP](https://content.linkedin.com/content/dam/help/tns/en/report/LinkedIn-February-2026-Digital-Services-Act-Transparency-Report.zip) | ZIP (harmonised template); Feb 2026 (H2 2025) | verified |
| Pinterest | Pinterest Europe | [Feb 2026 ZIP](https://cdn.sanity.io/files/26f0hyrt/pinpolicy_prod/2c552b2ce80a75c1f9e9741e83da8bdbb5028579.zip) | ZIP (harmonised template); Feb 2026 (H2 2025) | verified |
| Snapchat | Snap Group Ltd | [H2 2025 report](https://values.snap.com/privacy/transparency/european-union-h2-2025) | HTML; H2 2025 | likely |
| TikTok | TikTok Technology Ltd | [DSA hub](https://www.tiktok.com/transparency/en/dsa-transparency/) | Hub; latest H2 2025 | likely |
| X (Twitter) | Twitter International Unlimited Co. | [DSA report](https://transparency.x.com/en/reports/dsa-transparency-report) | Hub + PDF; latest Feb 2026 | likely |
| YouTube | Google Ireland | [Transparency report](https://transparencyreport.google.com/?hl=en) | Hub; PDF + CSV | likely |
| Google Play | Google Ireland | [Transparency report](https://transparencyreport.google.com/?hl=en) | Hub; PDF + CSV | likely |
| Google Maps | Google Ireland | [Transparency report](https://transparencyreport.google.com/?hl=en) | Hub; PDF + CSV | likely |
| Google Shopping | Google Ireland | [Transparency report](https://transparencyreport.google.com/?hl=en) | Hub; PDF + CSV | likely |
| Google Search (VLOSE) | Google Ireland | [Transparency report](https://transparencyreport.google.com/?hl=en) | Hub; PDF + CSV | likely |
| Bing (VLOSE) | Microsoft Ireland | [EU DSA report](https://www.microsoft.com/en-us/corporate-responsibility/eu-dsa-report-bing) | Latest Feb 2026; prior PDF | likely |
| Zalando | Zalando SE | [Transparency hub](https://corporate.zalando.com/en/investor-relations/corporate-governance/transparency-hub) | Hub; latest H2 2025 | likely |
| Shein | Roadget Business (Shein) | [DSA hub](https://euqs.shein.com/digital-service-act-a-1994.html) | Hub; latest H2 2025 | uncertain |
| Temu | Whaleco / Elementary Innovation | [Transparency center](https://www.temu.com/transparency-center-reports.html) | Hub; Feb 2026 + PDFs | likely |
| Wikipedia | Wikimedia Foundation | [Feb 2026 XLS](https://foundation.wikimedia.org/wiki/File:Wikipedia_-_DSA_transparency_report_2026-02-28.xls) | XLS (harmonised template); Feb 2026 (H2 2025) | verified |
| Pornhub | Aylo (Technius Ltd) | [DSA reports](https://help.pornhub.com/hc/en-us/sections/46212654665363-DSA-Transparency-Reports) | HTML; latest Feb 2026 | likely |
| XVideos | WebGroup Czech Republic | [Mandatory information](https://info.xvideos.net/legal/mandatory-information) | Mandatory-info page; prior PDF | likely |
| XNXX | WebGroup Czech Republic | [Mandatory information](https://info.xnxx.com/legal/mandatory-information) | Mandatory-info page; prior PDF | likely |

## Searched, not found / out of scope

No first-party Art. 15/24 content-moderation report could be located (some publish
only an Art. 24(2) recipient-count notice or a point-of-contact page; others are
out of the EU/EEA or below the small-enterprise threshold). Recorded so the
negative result is not re-searched:

- **Only an Art. 11/24(2) notice or contact page (no full report found):** Telegram,
  Wallapop, Kaufland, Stack Overflow, Dropbox, Atlassian/Bitbucket, Substack
  (placeholder "coming soon"), FreeNow, Bandcamp (trader-info only).
- **Registered as a DSA reporter in the EU database but own report page not located:**
  mobile.de, Willhaben, Fotocasa, Coches.net, Subito.
- **No findable report:** Allegro, Bol.com, Idealo, Catawiki, Milanuncios, InfoJobs,
  Omio, eDreams ODIGEO / Opodo, Agoda, Ticketmaster, See Tickets, Trainline,
  Flixbus, Hopper, Klook, Lastminute.com, TheFork,
  OpenTable, TaskRabbit, Freelancer.com, PeoplePerHour, Treatwell, Doctolib,
  ImmobilienScout24, Immowelt, SeLoger, Rightmove, Zoopla, Funda, Pap.fr,
  Logic-Immo, Otomoto, Standvirtual, Heycar, La Centrale, Hemnet, Daft.ie,
  Habitaclia, GitLab, npm, PyPI, Docker Hub, SourceForge, Replit, Notion, Steam,
  GOG, EA, itch.io, Microsoft Store, Amazon Appstore, Mastodon, VK, Deezer, Rumble,
  Odysee, Triller, Likee, Bigo Live, Tchibo, Bonprix, vidaXL, Conrad,
  CDON, eDarling/Parship, DeviantArt, Archive of Our Own, GoFundMe,
  Audible, Goodreads, Issuu, Flipboard, Kickstarter, Indiegogo, Ko-fi,
  Buy Me a Coffee, Coursera, Skillshare, Duolingo, Khan Academy, WeTransfer, Mega,
  pCloud, MediaFire, OpenSea, Rarible, Xing, Dribbble, 500px, Giphy, Storytel,
  OnlyFans (general report exists, no DSA-specific one confirmable on its own domain).
- **Search engines (only an Art. 24(2)/notice page or nothing found):** Brave Search
  (Art. 24(2) MAR only), Ecosia (MAR only), Startpage, Kagi, Mojeek, Seznam.cz, Yandex,
  You.com, Swisscows, Perplexity.
- **Hosting / site builders (no report found):** Webflow, IONOS, Namecheap, Strato,
  Jimdo, BigCommerce, Weebly, Bluehost, SiteGround, DreamHost.
- **Gaming / mod / casual-game / streaming (no report found):** Nexus Mods,
  CurseForge, Mod.io, Game Jolt, Newgrounds, Poki, CrazyGames, Kongregate,
  Armor Games, Trovo, DLive, Rooter, Lichess, Garena, Krafton, Supercell.
- **Stock media / creative / Q&A (no report found):** Shutterstock, Getty Images,
  iStock, Canva (government-requests report only), Unsplash, Pexels, Pixabay,
  Freepik, Mixcloud, Audiomack, BandLab, 9GAG, 4chan, Imgur, ResetEra, Brainly,
  Chegg, Quizlet, Course Hero, ResearchGate, Academia.edu.
- **Only an Art. 24(2) recipient notice / contact page (no full report):** Spartoo,
  Showroomprivé, Privalia, Redbubble, TeePublic, Strava, Jodel.
- **B2B / cross-border & national retail (no report found):** Alibaba.com marketplace
  (only Alibaba *Cloud* publishes one — see table), Made-in-China, DHgate, Banggood,
  Wish, LightInTheBox, Joom, Faire, Ankorstore, Metro Markets, Mercateo/Unite,
  Gmarket, La Redoute, Fnac/Darty, Empik.
- **Health / grocery & quick-commerce (no report found):** Shop Apotheke / Redcare,
  Zur Rose, Picnic, Ocado, Getir, Gorillas, Flink, Flaschenpost, Knuspr/Rohlik,
  Gousto, HelloFresh, Marley Spoon, Everli, Auchan, E.Leclerc, Albert Heijn, Jumbo,
  Mercadona.
- **Fitness / maps / audio / reading (no report found):** Komoot, AllTrails, Wikiloc,
  TomTom, Citymapper, Foursquare/Swarm, Acast, Podimo, Last.fm, Babelio, LibraryThing,
  The StoryGraph, Letterboxd, Untappd.
- **Print-on-demand / jobs / misc social (no report found):** Society6, Zazzle,
  Spreadshirt, Teespring/Spring, Displate, INPRNT, Welcome to the Jungle, Monster,
  Totaljobs, Jobindex, Gab, Truth Social, Minds, Parler, Wykop, Tellonym, Lemon8,
  Bluesky (flagged by the Commission for not publishing the Art. 24 user-number
  disclosure).
- **CEE / Nordic / Southern-Europe e-commerce (no report found):** Alza, Heureka,
  Aukro, Mall.cz, Morele.net, Vatera/Jófogás, Fashion Days,
  Pigu/HobbyHall/Kaup24, Tori.fi, Verkkokauppa, Elgiganten, Komplett, Power.no,
  Bazos, Sbazar, Pazaruvaj.
- **Forums / community / Q&A (no report found):** Disqus, Mumsnet, The Student Room,
  XDA/GSMArena, MyAnimeList, DEV.to, Hashnode, Product Hunt, Genius, ComputerBase,
  Hardwareluxx, Motor-talk, Hacker News, Discourse (per-community, not central).
- **Crypto / NFT / fintech (no report found, several likely out of DSA scope):**
  TradingView, StockTwits, Blur, Magic Eden, Revolut, Public.com, Coinbase
  (government-requests report only); pure exchanges not "online platforms" — Binance,
  Kraken, Crypto.com, Bitpanda, Bybit, OKX.
- **More travel / dating (no report found):** Holidu, Casamundo, Pierre & Vacances /
  Center Parcs, NockNock, Hily, Once, Lex, Her, Taimi, eHarmony, Jaumo, MeetMe, Twoo.
- **Auctions / collectibles / resale (no full report found):** Catawiki (DSA pages,
  no statistical report), BrickLink (Art. 24(2) notice only), StockX, GOAT, Chrono24,
  Rebelle, Sellpy, Momox/Medimops, Ubup, The Saleroom, Drouot, Beatport, Grailed,
  Heritage Auctions, Barnebys, Auctionet, Whisky Auctioneer.
- **Crowdfunding / edtech (no report found; many out of scope):** GoStudent,
  Domestika (notice/contact only); Ulule, KissKissBankBank, Startnext,
  Seedrs, Crowdcube, Companisto, Leetchi, FutureLearn, OpenClassrooms, edX,
  Babbel, Busuu, Preply, italki, Brilliant, MasterClass.
- **More regional marketplaces / local-services / ticketing (no report found):**
  Hepsiburada, Wayfair, Westwing, Maisons du Monde, BUT, Sarenza, JD/Ochama, Coupang,
  Vivense, Made.com, mydealz/Pepper, MyHammer, Helpling, ProntoPro, StarOfService,
  Werkspot, Cabify, Heetch, Gett, CTS Eventim, Viagogo, StubHub, TicketSwap, DICE,
  Fever, Bandsintown, Songkick.
- **Out of scope:** Swiss-only platforms (tutti.ch, ricardo.ch, anibis.ch — not
  EU/EEA); Finn.no (Norway has not transposed the DSA into the EEA agreement);
  Avito (not EU-operating).
