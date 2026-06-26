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
| [Microsoft — DSA non-VLO report links](https://www.microsoft.com/en-us/digitalsafety/transparency-reports/jurisdictional-reports/dsa-non-vlo-tr-report-links) | Authoritative company-published catalogue of ~20 Microsoft non-VLOP services' DSA reports (Azure, Edge, Outlook, OneDrive, Teams/Skype, Xbox, Start.gg, GroupMe, M365, Forms, Learn, Community, …), each a resolvable PDF. |

## Social, messaging, community & video

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Discord | Discord Netherlands B.V. | [Hub](https://discord.com/safety-transparency) · [archived data](harmonised-reports/extracted/discord) | ZIP (machine-readable template); 2024 & 2025 | verified |
| Messenger / Instagram Direct | Meta Platforms Ireland | [Meta non-VLOP reports](https://transparency.meta.com/reports/regulatory-transparency-reports/) | In Meta's non-VLOP DSA report; periodic | likely |
| LINE | LY Corporation | [Report](https://www.lycorp.co.jp/en/company/transparency/dsa-transparency/2025/) · [archived data](harmonised-reports/extracted/line) | Excel (Art. 15); CY2025 | verified |
| WeChat | Tencent International Service Europe B.V. | [2026 report](https://safety.wechat.com/en_US/enforcement/transparency/wechat-dsa-transparency-report-2026) ([prior](https://safety.wechat.com/en_US/enforcement/transparency/wechat-dsa-transparency-report-2025)) | HTML (Art. 15); 2024 & 2025 | verified |
| IMDb | IMDb.com, Inc. (Amazon) | [DSA info](https://help.imdb.com/article/imdb/general-information/digital-services-act-information/GDAKKSDKCPU25H86) · [archived data](harmonised-reports/extracted/imdb) | XLSX/CSV; 2024, H1 & H2 2025 | verified |
| Microsoft Teams / Skype | Microsoft | [PDF](https://go.microsoft.com/fwlink/?linkid=2304741) · [archived PDF](pdf-reports/microsoft-teams-skype) | PDF (Communications); Feb – Dec 2024 | verified |
| Microsoft Community | Microsoft | [PDF](https://go.microsoft.com/fwlink/?linkid=2305901) · [archived PDF](pdf-reports/microsoft-community) | PDF; Feb – Dec 2024 | verified |
| Microsoft Feedback Portal | Microsoft | [PDF](https://go.microsoft.com/fwlink/?linkid=2304743) · [archived PDF](pdf-reports/microsoft-feedback-portal) | PDF; Feb – Dec 2024 | verified |
| Reddit | Reddit, Inc. | [DSA info / Transparency Center](https://support.reddithelp.com/hc/en-us/articles/23595536875796-Digital-Services-Act-DSA-Information-for-EU-users) | PDF; semi-annual | likely |
| Viber | Rakuten Viber (Viber Media S.à r.l.) | [Report](https://www.viber.com/en/terms/eu-digital-services-act-dsa-transparency-report/) | HTML + tables; 18 Feb – 31 Dec 2025 | verified |
| Flickr | SmugMug, Inc. | [Legal / Transparency](https://www.flickr.com/help/legal) | PDF + XLSX; 2024 & 2025 | verified |
| Tumblr | Automattic Inc. | [Report](https://transparency.automattic.com/tumblr/digital-services-act/) | Web report + data; semi-annual | verified |
| Dailymotion | Dailymotion SA | [Report](https://legal.dailymotion.com/en/transparency/transparency-report-on-prohibited-content-policys-enforcement/) · [archived data](harmonised-reports/extracted/dailymotion) | XLSX (Annex I template) + HTML; annual | verified |
| Vimeo | Vimeo.com, Inc. | [DSA page](https://vimeo.com/legal/transparency/dsa) | HTML; Art. 24(2) recipient disclosure (<45 M), semi-annual | uncertain |
| Jeuxvideo.com | Webedia | [Report](https://www.jeuxvideo.com/transparence.htm) | Harmonised template (CSV/XLSX/PDF); 2024 & 2025 | likely |
| Threads | Meta Platforms Ireland Ltd. | [Meta regulatory reports](https://transparency.meta.com/reports/regulatory-transparency-reports/) | In Meta's non-VLOP DSA report; periodic | likely |
| Nextdoor | Nextdoor Holdings, Inc. | [Report](https://help.nextdoor.com/s/article/DSA-Transparency-Report) | HTML; periodic | likely |
| Kick | Kick Streaming Pty Ltd (Easygo) | [DSA guide](https://help.kick.com/en/articles/12066402-digital-services-act-dsa-information-guide) | HTML guide referencing the report | likely |
| Yubo | Twelve App SAS | [Transparency report](https://www.yubo.live/safety/transparency-report) | Bi-annual T&S report (DSA-aligned) | likely |
| Quora | Quora, Inc. | [DSA Transparency section](https://help.quora.com/hc/en-us/sections/13296037150612-DSA-Transparency) | HTML section; full Art. 15 stats unconfirmed | uncertain |
| Start.gg / GroupMe | Microsoft | [PDF](https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/final/en-us/microsoft-brand/documents/Social-Media-DSA-Transparency-Report-Feb-Dec-2024.pdf) · [archived PDF](pdf-reports/start-gg-groupme) | PDF; Feb – Dec 2024 | verified |
| heise forums | Heise Medien GmbH & Co. KG | [DSA transparency](https://www.heise.de/Transparenz-nach-dem-Digital-Services-Act-DSA-10639819.html) | CSV; annual (2024 & 2025) | verified |
| gutefrage | gutefrage.net GmbH | [Transparenzbericht](https://www.gutefrage.net/company/transparenzbericht) | Annual Art. 15 report | likely |
| eToro (social/copy-trading) | eToro (Europe) Ltd | [DSA transparency report](https://www.etoro.com/customer-service/regulation-license/dsa-transparency-report/) · [archived PDF](pdf-reports/etoro) | PDF set (Art. 15/24 template) | verified |

## Audio / music streaming

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Spotify | Spotify AB | [Hub](https://www.spotify.com/safetyandprivacy/transparency) ([2025 reports](https://www.spotify.com/safetyandprivacy/file/eu_2025_dsa_report_introduction_spotify)) | Report files; Art. 15; CY2025 | verified |
| SoundCloud | SoundCloud Ltd | [Transparency reports](https://soundcloud.com/transparency-reports) | PDF; 2025 | verified |
| Apple Podcasts | Apple Distribution International | [Report](https://www.apple.com/legal/dsa/transparency/eu/podcasts/2502/) | HTML report (17 Feb – 31 Dec 2024); also a Feb 2026 XLSX template | verified |

## E-commerce marketplaces & retail

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| eBay | eBay Inc. | [Hub](https://www.ebayinc.com/company/digital-services-act/) | PDF; 17 Feb – 31 Dec 2024 | likely |
| Etsy | Etsy, Inc. / Etsy Ireland UC | [Legal hub](https://www.etsy.com/legal/policy/eu-digital-services-act/1119915664620) | PDF; 2024 & 2025 | likely |
| Otto | Otto GmbH & Co KGaA | [Hub](https://www.otto.de/shoppages/digital_services_act_transparency_reports_dsa) | Hub + PDFs; 2024 & 2025 | verified |
| Vinted | Vinted UAB | [Safety hub](https://www.vinted.com/safety) ([2025 XLSX](https://marketplace-web-assets.vinted.com/assets/transparency-report/vinted-transparency-report-2025.xlsx)) · [archived data](harmonised-reports/extracted/vinted) | XLSX; 2024 & 2025 | verified |
| Vestiaire Collective | Vestiaire Collective SA | [Report](https://faq.vestiairecollective.com/hc/en-us/articles/34009544661393-EU-Digital-Services-Act) · [archived data](harmonised-reports/extracted/vestiaire) | PDF + Excel; 2025 | verified |
| Decathlon Marketplace | Decathlon SE | [Hub](https://www.decathlon.fr/lp/i/rapport-annuel-de-transparence) | Hub + PDF; 2024 & 2025 | verified |
| zooplus | zooplus SE | [Legal/DSA](https://www.zooplus.de/info/legal/DSA) ([PDF](https://corporate.zooplus.com/wp-content/uploads/2025/12/2025_DigitalServiceActTransparencyReporting_zooplus_signed.pdf)) · [archived PDF](pdf-reports/zooplus) | Signed PDF; Dec 2025 | verified |
| Veepee (vente-privee) | Veepee | [Report](https://aide.veepee.fr/article/1630-informations-reglementaires) ([2026 XLSX](https://www.veepee.fr/docs/dsa/2025/fr/french_transparency_report_2026.xlsx)) · [archived data](harmonised-reports/extracted/veepee) | XLSX; 2024 & 2025 | verified |
| AboutYou | ABOUT YOU SE & Co. KG | [Impressum](https://www.aboutyou.de/impressum) ([XLSX](https://www.aboutyou.de/assets/documents/Transparency_Report.csv.xlsx)) · [archived data](harmonised-reports/extracted/aboutyou) | XLSX (harmonised template); 2025/2026 | verified |
| Refurbed | refurbed GmbH | [Report](https://refurbed.com/dsa-transparency-report/) | HTML; 17 Feb 2024 – 16 Feb 2025 | verified |
| Back Market | Back Market SAS | [PDF](https://assets.ctfassets.net/mmeshd7gafk1/1rtDZVxgD6BhehY82JVTiX/2aacbe1237b2aa49b869c20b982795a2/Transparency_Report_04.2025.pdf) · [archived PDF](pdf-reports/back-market) | PDF; Apr 2025 (semi-annual) | verified |
| Marktplaats | Marktplaats B.V. (Adevinta) | [PDF](https://statisch.marktplaats.nl/docs/Transparency_report_MP.pdf) · [archived PDF](pdf-reports/marktplaats) | PDF; 17 Feb – 31 Dec 2024 | verified |
| ManoMano | Colibri SAS | [XLSX](https://cdn.manomano.com/legal/reports/DSA_Transparency_Report_2025.xlsx) · [archived data](harmonised-reports/extracted/manomano) | XLSX; 2025 | verified |
| Cdiscount | Cdiscount S.A. | [Hub](https://www.cdiscount.com/n-429993/pagesaurlfixe-arbo/rapport-de-transparence-dsa.html) | HTML hub | likely |
| Leboncoin | LBC France SAS (Adevinta) | [PDF](https://img.leboncoin.fr/api/v1/lbcpb2/documents/transparency_report-cover_page-FR_version.pdf?rule=cms_pdf) · [archived PDF](pdf-reports/leboncoin) | PDF (FR) | verified |
| Rakuten France | Rakuten France SAS | [PDF](https://fr.shopping.rakuten.com/cdn/legal/DSA/Rapport_Transparence_1_v1/RAKUTEN_FRANCE_RAPPORT_TRANSPARENCE_2025.pdf) | PDF; 2025 | likely |
| Boulanger | Boulanger SA | [PDF](https://www.boulanger.com/content/dam/Boulanger/juridique/mentions-legales/rapporttransparence-dsa-2024.pdf) | PDF; CY2024 | likely |
| Carrefour Marketplace | Carrefour | [Legal notices](https://www.carrefour.fr/mentions-legales) · [archived data](harmonised-reports/extracted/carrefour) | XLSX (Annex I template); FY2024 & FY2025 | likely |
| eMAG | Dante International S.A. | [Report](https://www.emag.ro/info/raport-transparenta-dsa) | HTML + downloads; biannual | likely |
| Notino | Notino s.r.o. | [Report](https://www.notino.com/dsa-transparency-report/) | HTML/PDF | likely |
| MediaMarkt / Saturn | MediaMarktSaturn | [Report](https://www.mediamarkt.de/de/shop/dsa-transparenzbericht.html) | HTML | likely |
| Galaxus / Digitec | Digitec Galaxus AG | [Report](https://www.galaxus.de/de/page/transparenzbericht-dsa-9020) | HTML (DE/AT) | likely |
| Douglas | Douglas GmbH | [Report](https://www.douglas.de/de/cp/dsa-transparenzbericht/dsa-transparenzbericht) | HTML | likely |
| Coolblue | Coolblue B.V. | [Report](https://www.coolblue.nl/transparantierapport) | HTML | likely |
| Skroutz | Skroutz S.A. (Greece) | [DSA hub](https://www.skroutz.gr/digital-services-act) · [archived data](harmonised-reports/extracted/skroutz) | PDF + Excel/ZIP; 2024 & 2025 | verified |
| Ceneo | Ceneo.pl sp. z o.o. (Poland) | [DSA hub](https://info.ceneo.pl/dsa) · [archived data](harmonised-reports/extracted/ceneo) | XLSX Annex I (EN + PL); 2024 & 2025 | verified |
| x-kom | x-kom sp. z o.o. (Poland) | [DSA hub](https://www.x-kom.pl/dsa) | XLSX (harmonised template); 2024 | verified |
| Discogs | Discogs (Zink Media, Inc.) | [Statement](https://support.discogs.com/hc/en-us/articles/12730436158349-EU-Digital-Services-Act-Statement) | HTML; 17 Feb 2024 – 16 Feb 2025 | likely |
| Reverb | Reverb.com LLC | [DSA page](https://help.reverb.com/hc/en-us/articles/14017920631571-EU-Digital-Services-Act) | HTML; semi-annual | likely |
| Depop | Depop Ltd | [DSA page](https://depophelp.zendesk.com/hc/en-gb/articles/13057572688273-EU-Digital-Services-Act) · [archived data](harmonised-reports/extracted/depop) | XLSX (harmonised template); 2025 | verified |
| Fruugo | Fruugo.com Ltd | [Compliance statement](https://www.fruugo.ie/help/detail/dsa-compliance-statement) | HTML; Jun – Dec 2025 | likely |
| Vivino | Vivino ApS | [Content moderation policy](https://www.vivino.com/legal/content-moderation-policy) | HTML; semi-annual (Art. 24) | likely |
| DocMorris | DocMorris N.V. | [DSA page](https://www.docmorris.de/digital-services-act) | HTML DSA page; contents unverified | uncertain |
| Trendyol | DSM Grup / Trendyol Group | [2025 PDF](https://9be604a381897de8.mncdn.com/tymp/prod/documents/policy/TY_DSA_Report_2025.pdf) ([2024 PDF](https://cdn.dsmcdn.com/mobile/international/legal/transparency_report_2024.pdf)) · [archived PDF](pdf-reports/trendyol) | PDF; 2024 & 2025 | verified |
| home24 | home24 SE | [Impressum](https://www.home24.de/home24-impressum/) | Transparenzbericht; 2025/2026 | likely |
| Conforama | Conforama France SA | [DSA page](https://www.conforama.fr/digital-service-act) | HTML DSA page; AMAR + notice | uncertain |
| Whatnot | Whatnot Inc. | [EU DSA](https://help.whatnot.com/hc/en-us/articles/23619888476557-Whatnot-The-EU-Digital-Services-Act) · [archived data](harmonised-reports/extracted/whatnot) · [archived PDF](pdf-reports/whatnot) | PDF + XLSX; 2025 & 2026 | verified |
| FinCompare | FinCompare GmbH | [PDF](https://fincompare.de/wp-content/uploads/2024/12/Transparenzbericht-nach-Art.-15-DSA-Berichtszeitraum_-Januar-2024-%E2%80%93-Dezember-2024.pdf) · [archived PDF](pdf-reports/fincompare) | PDF (Art. 15); Jan – Dec 2024 | verified |
| Tradera | Tradera Sweden AB | [Support](https://www.tradera.com/support) | Annual report (referenced in T&C) | likely |
| Mercari | Mercari, Inc. | [Transparency](https://about.mercari.com/en/safety/transparency/) · [archived PDF](pdf-reports/mercari) | PDF; half-yearly (DSA framing unconfirmed) | uncertain |
| Faire | Faire Wholesale, Inc. | [Report](https://www.faire.com/support/articles/20960200105115) | CSV; 2024 & 2025 | verified |
| CDON | CDON AB | [Transparensrapport](https://cdon.se/cdon/transparensrapport/) | HTML; CY2025 | verified |
| Fyndiq | Fyndiq AB | [Transparensrapport](https://fyndiq.se/fyndiq/transparensrapport/) | HTML; CY2025 | verified |
| idealo | idealo internet GmbH | [DSA legal page](https://www.idealo.de/legal/dsa) | HTML; CY2025 | likely |

## Classifieds, real estate & auto

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Kleinanzeigen | Kleinanzeigen GmbH | [Hub](https://themen.kleinanzeigen.de/transparenzbericht/) | HTML hub + PDFs; semi-annual | likely |
| OLX | OLX B.V. (Prosus) | [Report](https://www.olx.pl/d/dsa-transparency-report/) | HTML; semi-annual | likely |
| AutoScout24 | AutoScout24 SE | [PDF](https://assets.ctfassets.net/uaddx06iwzdz/4oZBiZrkfhU88u1wa3zUGk/bb5b98026b8146453087306641ed9dec/AutoScout24Transparenzbericht2024.pdf) · [archived PDF](pdf-reports/autoscout24) | PDF (Art. 15/24); Jul – Dec 2024 | verified |
| Idealista | Idealista S.A.U. | [DSA info](https://www.idealista.com/ayuda/articulos/informacion-de-idealista-en-cumplimiento-del-reglamento-de-servicios-digitales/) | HTML; Art. 15/24 | likely |
| Vivastreet | Vivastreet (legal entity unverified) | [Transparency report](https://www.vivastreet.com/s/transparency_report) | HTML (Art. 15/24/42); CY2025 | verified |

## Travel, mobility, accommodation & events

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Airbnb | Airbnb Ireland UC | [PDF](https://assets.airbnb.com/help/Airbnb_Ireland_UC_Transparency_Report_2025Feb14.pdf) · [archived PDF](pdf-reports/airbnb) | PDF; CY2024 | verified |
| Expedia | Expedia, Inc. | [Hub](https://legal.expediagroup.com/regulatory-and-compliance/digital-services-act) · [archived data](harmonised-reports/extracted/expedia) | PDF + XLSX; 2024 & 2025 | verified |
| Hotels.com | Hotels.com, L.P. | [Hub](https://legal.expediagroup.com/regulatory-and-compliance/digital-services-act) · [archived data](harmonised-reports/extracted/hotelscom) | PDF + XLSX; 2024 & 2025 | verified |
| Vrbo | EG Vacation Rentals Ireland Ltd. | [Hub](https://legal.expediagroup.com/regulatory-and-compliance/digital-services-act) · [archived data](harmonised-reports/extracted/vrbo) | PDF + XLSX; 2024 & 2025 | verified |
| Trivago | trivago N.V. | [DSA info](https://company.trivago.com/dsa-information/) ([PDF](https://company.trivago.com/wp-content/uploads/2025/03/trivago-DSA-Transparency-Report.pdf)) · [archived PDF](pdf-reports/trivago) | PDF; Feb 2025 | verified |
| Tripadvisor | Tripadvisor LLC | [Report](https://www.tripadvisor.com/TransparencyReport2025) | HTML; 2025 | likely |
| Viator | Viator, Inc. | [PDF](https://assetlibrary.viator.com/m/523fc4a4d818e6fd/original/Viator_Inc_Digital_Services_Act_Transparency_Report_CY_2024.pdf) · [archived PDF](pdf-reports/viator) | PDF; CY2024 | verified |
| Hostelworld | Hostelworld | [Security & privacy](https://www.hostelworld.com/legal/security-privacy/) · [archived data](harmonised-reports/extracted/hostelworld) | XLSX; 12 mo to 31 Dec 2025 | verified |
| Eventbrite | Eventbrite Operations (IE) Ltd. | [PDF](https://www.eventbrite.com/blog/wp-content/uploads/2026/03/Eventbrite-2025-Transparency-Report.pdf) · [archived PDF](pdf-reports/eventbrite) | PDF (EC template); 2024 & 2025 | verified |
| BlaBlaCar | Comuto SA | [PDF](https://blog.blablacar.fr/wp-content/uploads/2025/02/2024-dsa-transparency-report-blablacar.pdf) · [archived PDF](pdf-reports/blablacar) | PDF; 2024 | verified |
| Kayak | KAYAK Software Corp. (Booking Holdings) | [Hub](https://www.kayak.ie/c/digital-services-act/) · [archived PDF](pdf-reports/kayak) | PDF; 2026 | verified |
| Uber Eats | Uber B.V. | [Legal page](https://www.uber.com/legal/en/document/?name=digital-services-act---uber-eats-transparency-report) | Legal page + Drive docs; 2024 & 2025 | verified |
| Bolt | Bolt Technology OÜ | [Legal page](https://bolt.eu/en/legal/digital-services-act/) | Legal page; 17 Feb 2024 – 17 Feb 2025 | likely |
| GetYourGuide | GetYourGuide GmbH / AG | [DSA page](https://www.getyourguide.com/c/dsa/) | HTML; 2024 (Art. 15/24/42) | likely |
| Skyscanner | Skyscanner Ltd | [DSA hub](https://www.skyscanner.net/media/digital-services-act) | DSA hub (JS-rendered) | likely |
| HomeToGo | HomeToGo SE | [DSA page](https://www.hometogo.de/dsa/) · [archived data](harmonised-reports/extracted/hometogo) | XLSX; Art. 24(2) + removals | verified |
| Novasol | Awaze A/S | [Report](https://www.novasol.com/digital-services-act) | PDF; Feb 2026 (Awaze group) | verified |
| Belvilla | Awaze Group | [Report (Awaze group)](https://www.novasol.com/digital-services-act) | PDF; Feb 2026 | likely |
| Interhome | Interhome Group (HomeToGo) | [Legal info](https://www.interhome.group/en-ch/legal-information) | Annual; report referenced | likely |

## Food delivery & gig / freelance

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Just Eat Takeaway (Lieferando, Thuisbezorgd) | Just Eat Takeaway.com N.V. | [Governance docs](https://www.justeattakeaway.com/governance/governance-documents/) | ZIP (template); 17 Feb – 31 Dec 2025 | verified |
| Deliveroo | Deliveroo plc | [PDF](https://dpd-12774-s3.s3.eu-west-2.amazonaws.com/assets/7517/4559/3138/Deliveroo_DSA_Transparency_Report_April2025.pdf) · [archived PDF](pdf-reports/deliveroo) | PDF; Apr 2025 | verified |
| Glovo | Glovoapp23 S.A. (Delivery Hero) | [Report](https://about.glovoapp.com/culture-and-values/transparency-report/) · [archived PDF](pdf-reports/glovo) | PDF; 2025 | verified |
| Wolt | Wolt Enterprises Oy (DoorDash) | [PDF](https://assets.ctfassets.net/23u853certza/4UBct5Uy0IYtBe4xXSEclg/84a36c8226a026a23859abb166875db6/Wolt_DSA_Transparency_Report2025.pdf) · [archived PDF](pdf-reports/wolt) | PDF; 17 Feb 2024 – 17 Feb 2025 | verified |
| Delivery Hero (foodora, …) | Delivery Hero SE | [DSA statement](https://www.deliveryhero.com/digital-services-act/) | HTML; content-moderation report + AMAR | likely |
| Malt | Malt Community SAS | [Transparency](https://www.malt.fr/c/transparency) | Web report; 2024 & 2025 | likely |
| Upwork | Upwork Global Inc. | [2025 report](https://www.upwork.com/blog/upworks-2025-transparency-report-our-ongoing-work-to-protect-yours) | XLSX; 2024 & 2025 | likely |
| Fiverr | Fiverr International Ltd. | [DSA overview](https://help.fiverr.com/hc/en-us/articles/22578911624977-DSA-overview) | HTML overview | uncertain |
| Fixly | Fixly sp. z o.o. (OLX / Adevinta) | [Legal info](https://pomoc.fixly.pl/hc/pl/categories/34663617565725-Informacje-Prawne) | Web/PDF moderation report | likely |

## App stores & gaming

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Roblox | Roblox Corporation | [Transparency](https://about.roblox.com/transparency) ([2025 PDF](https://about.roblox.com/pdf/eu-dsa-transparency-report-2025)) · [archived data](harmonised-reports/extracted/roblox) | PDF + XLSX/CSV; 2024 & 2025 | verified |
| Ubisoft Connect | Ubisoft Entertainment SA | [Report](https://www.ubisoft.com/legal/documents/transparencyreport/en-US) | PDF; CY2024 | verified |
| Nintendo eShop | Nintendo Co., Ltd. | [DSA page](https://www.nintendo.com/en-gb/Legal-information/Digital-Services-Act-2522334.html) · [archived data](harmonised-reports/extracted/nintendo) | XLSX (harmonised template); Feb 2026 | verified |
| Samsung Galaxy Store | Samsung Electronics | [Regulatory info](https://www.samsung.com/uk/support/regulatory-information/) · [archived PDF](pdf-reports/samsung-galaxy-store) | PDF; Aug 2025 – Jan 2026 | verified |
| Epic Games Store | Epic Games, Inc. | [Report](https://safety.epicgames.com/transparency-reports/european-union) | XLSX + hub; Feb 2024 – Feb 2025 | likely |
| Twitch | Twitch Interactive (Amazon) | [Report](https://safety.twitch.tv/s/article/Twitch-DSA-Transparency-Report-February-2025) | HTML; Feb 2025 | likely |
| Xbox | Microsoft | [PDF](https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/final/en-us/microsoft-brand/documents/Xbox-platform-and-Xbox-Game-Studios-DSA-Transparency-Report-2024.pdf) · [archived PDF](pdf-reports/xbox) | PDF; 2024 | verified |
| Microsoft Store | Microsoft | [PDF](https://go.microsoft.com/fwlink/?linkid=2305704) · [archived PDF](pdf-reports/microsoft-store) | PDF; Feb – Dec 2024 | verified |
| Miniclip | Miniclip SA (Tencent) | [Report](https://www.miniclip.com/dsa-transparency-report) · [8 ball pool](harmonised-reports/extracted/miniclip-8-ball-pool) · [agar io](harmonised-reports/extracted/miniclip-agar-io) · [baseball clash](harmonised-reports/extracted/miniclip-baseball-clash) · [mini football](harmonised-reports/extracted/miniclip-mini-football) · [mini tennis](harmonised-reports/extracted/miniclip-mini-tennis) · [paint brawl](harmonised-reports/extracted/miniclip-paint-brawl) · [speed stars](harmonised-reports/extracted/miniclip-speed-stars) · [ultimate golf](harmonised-reports/extracted/miniclip-ultimate-golf) | ZIP (harmonised template, 8 games); CY2025 | verified |
| GameDistribution | Azerion | [Report](https://static.gamedistribution.com/dsa-transparency-report.html) | HTML; CY2024 | verified |
| Niantic (Pokémon GO, …) | Niantic Inc. | [Report](https://nianticlabs.com/dsa-transparency) · [archived data](harmonised-reports/extracted/niantic) | Landing + Excel/PDF; CY2025 | verified |
| Chess.com | Chess.com, LLC | [DSA compliance](https://www.chess.com/article/view/digital-services-act-compliance) | HTML; Art. 24(2) MAU only | uncertain |
| PlayStation Network | Sony Interactive Entertainment Network Europe | [DSA info](https://www.playstation.com/en-gb/legal/digital-service-act-information/) · [archived PDF](pdf-reports/playstation-network) | ZIP; 2024 & 2025 | verified |
| Riot Games | Riot Games Ltd. | [DSA report](https://support-leagueoflegends.riotgames.com/hc/en-us/articles/25972785684627) | XLSX; 2024 & 2025 | verified |
| Square Enix | Square Enix Ltd. | [Online safety](https://www.square-enix-games.com/en_GB/documents/online-safety) · [archived data](harmonised-reports/extracted/squareenix) | XLSX (harmonised template); 2025 | verified |
| Konami | Konami Digital Entertainment | [EU DSA hub](https://legal.konami.com/kde/eudsa/) · [archived data](harmonised-reports/extracted/konami) | XLSX/PDF; 2024 & 2025 | verified |
| Nexon | Nexon | [DSA page](https://playersupport.nexon.com/hc/en-us/articles/46401329736084-Digital-Services-Act) · [archived data](harmonised-reports/extracted/nexon) | XLSX (harmonised template); 2025 | verified |
| Level Infinite (PUBG Mobile, Honor of Kings, Arena Breakout, …) | Proxima Beta Europe B.V. (Tencent) | [Arena Breakout report](https://eulaforgames.com/rule/202502110002/ALL) ([PUBG](https://support.pubg.com/hc/en-us/articles/28819731069721-EU-Digital-Services-Act-information)) | In-page Art. 15 per game; 2024 | verified |
| Honor APPMarket | HONOR Device Co. | [DSA page](https://www.honor.com/uk/legal/dsa/) | HTML + annual reports; 2024 & 2025 | verified |
| OPPO Community / Theme Store | Guangdong OPPO / HEYTAP | [Online safety](https://www.oppo.com/en/onlinesafety/) · [archived PDF](pdf-reports/oppo-community-theme-store) | HTML + annual PDF; 2024 | verified |
| OnePlus Community | OnePlus Technology | [Online safety](https://www.oneplus.com/global/onlinesafety) · [archived PDF](pdf-reports/oneplus-community) | HTML + annual PDF; 2024 | verified |
| Xiaomi GetApps / Mi Community | Xiaomi | [DSA page](https://www.mi.com/global/support/policy/digital-service-act/) | HTML; Art. 15/24 + AMAR | likely |
| realme Community | realme | [DSA page](https://www.realme.com/global/legal/DigitalServicesAct) | HTML DSA page | likely |
| Huawei AppGallery | Aspiegel SE (Huawei) | [AMAR disclosure](https://consumer.huawei.com/eu/community/) | HTML; Art. 24(2) AMAR | likely |

## Dating

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Match Group (Tinder, Hinge, OkCupid, Meetic, …) | Match Group | [Resources](https://www.matchgroup-safety.com/resources) · [archived data](harmonised-reports/extracted/matchgroup) | PDF + per-app Excel; 2024 & 2025 | verified |
| Bumble (Badoo, Fruitz) | Bumble Inc. | [Hub](https://support.bumble.com/hc/en-us/articles/28718583113757-Digital-Services-Act-Transparency-report) ([2025 PDF](https://bumbcdn.com/i/big/dsa/bumble/dsa-transparency-report-2025.pdf)) · [archived data](harmonised-reports/extracted/bumble) · [archived PDF](pdf-reports/bumble-badoo-fruitz) | PDF + Annex; 2025 | verified |
| Grindr | Grindr LLC | [Reports](https://help.grindr.com/hc/en-us/articles/38555862683795-Grindr-EU-Digital-Services-Act-Transparency-Reports) · [archived data](harmonised-reports/extracted/grindr) | PDF + Excel; annual | likely |
| Feeld | Feeld Ltd | [DSA report](https://feeld.co/ask-feeld/member-resources/dsa) · [archived PDF](pdf-reports/feeld) | ZIP; 2025 full year | verified |
| Happn | happn SAS | [PDF](https://www.happn.com/customer-support/rapport_2ndTrimestre.pdf) · [archived PDF](pdf-reports/happn) | PDF; S2 2025 | verified |
| Lovoo | LOVOO GmbH | [PDF](https://www.lovoo.com/de/wp-content/uploads/sites/4/2026/01/LOVOO_Transparenzbericht_2024.pdf) · [archived PDF](pdf-reports/lovoo) | PDF (DE); 2024 | verified |

## Developer / software / hosting

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| GitHub | GitHub, Inc. (Microsoft) | [Transparency Center](https://transparencycenter.github.com/) ([2024 PDF](https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/final/en-us/microsoft-brand/documents/GitHub-DSA-Transparency-Report-Feb-Dec-2024.pdf)) · [archived PDF](pdf-reports/github) | PDF; Feb – Dec 2024 | verified |
| Cloudflare | Cloudflare, Inc. | [Transparency](https://www.cloudflare.com/transparency/) · [archived data](harmonised-reports/extracted/cloudflare) | XLSX (template); H2 2025 | verified |
| WordPress.com | Automattic Inc. | [Report](https://transparency.automattic.com/wordpress-dot-com/digital-services-act/) | Web + CSV; Jul – Dec 2025 | verified |
| Hugging Face | Hugging Face SAS | [Content policy](https://huggingface.co/content-policy) ([2025 PDF](https://cdn-media.huggingface.co/landing/assets/DSA_HF_2025.pdf)) · [archived PDF](pdf-reports/hugging-face) | PDF; 2025 | verified |

## Web hosting, registrars, site builders & infrastructure

(Intermediary/hosting services with Art. 15 reporting duties.)

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Shopify | Shopify Inc. | [Legal notices](https://www.shopify.com/legal/p2b/legal-notices) · [archived data](harmonised-reports/extracted/shopify) | Hub: PDF + XLSX; CY2024 & 2025 | verified |
| Wix | Wix.com Ltd. | [Report](https://support.wix.com/en/article/dsa-transparency-report-2024) | Web; CY2024 | verified |
| Squarespace | Squarespace, Inc. | [PDF](https://www.squarespace.com/s/Digital-Services-Act-Report-20250228.pdf) · [archived PDF](pdf-reports/squarespace) | PDF; 2024 | verified |
| GoDaddy | GoDaddy Inc. | [Disclosure](https://www.godaddy.com/legal/agreements/digital-services-act-disclosure) | Web; 2024 & 2025 | likely |
| OVHcloud | OVH Groupe SAS | [PDF](https://corporate.ovhcloud.com/sites/default/files/2025-04/rapport_de_transparence_dsa_ovhcloud_2025.pdf) · [archived PDF](pdf-reports/ovhcloud) | PDF + spreadsheet; 17 Feb – 31 Dec 2024 | verified |
| Hostinger | Hostinger International Ltd. | [Report](https://www.hostinger.com/legal/dsa-transparency-report) · [archived data](harmonised-reports/extracted/hostinger) | PDF + XLSX; 2024 – 2025 | verified |
| Akamai | Akamai Technologies, Inc. | [DSA hub](https://www.akamai.com/legal/eu-digital-services-act) | PDF/XLSX; 2024, H1 & H2 2025 | verified |
| Vercel | Vercel Inc. | [Transparency](https://vercel.com/legal/transparency) | Web; 17 Feb – 15 Dec 2024 | verified |
| Gandi | Gandi SAS | [Report](https://www.gandi.net/en-US/digital-service-act-transparency-report) | Web + PDF; 2024 & 2025 | verified |
| Alibaba Cloud | Alibaba Cloud (Alibaba.com Singapore) | [DSA compliance](https://www.alibabacloud.com/help/en/legal/latest/eu-digital-services-act-dsa-compliance-information) · [archived data](harmonised-reports/extracted/alibabacloud) | ZIP (harmonised template) + PDF; 2026 (cloud service, not the Alibaba.com marketplace) | verified |
| AWS | Amazon Web Services | [PDF](https://d1.awsstatic.com/legal/trust-and-safety-center/aws-eu-dsa-transparency-report.pdf) · [archived PDF](pdf-reports/aws) | PDF (Art. 15); covers AWS services | verified |
| Tencent Cloud | Tencent Cloud International | [DSA page](https://www.tencentcloud.com/document/product/301/59018) | HTML + PDF; 2024 & 2025 | verified |
| iCloud Storage | Apple Distribution International | [Report](https://www.apple.com/legal/dsa/transparency/eu/icloud/2502/) | HTML report (17 Feb – 31 Dec 2024); also a Feb 2026 XLSX template | verified |
| Microsoft Azure | Microsoft | [PDF](https://go.microsoft.com/fwlink/?linkid=2304935) · [archived PDF](pdf-reports/microsoft-azure) | PDF; Feb – Dec 2024 | verified |
| Microsoft OneDrive | Microsoft | [PDF](https://go.microsoft.com/fwlink/?linkid=2305905) · [archived PDF](pdf-reports/microsoft-onedrive) | PDF; Feb – Dec 2024 | verified |
| Microsoft Advertising | Microsoft | [PDF](https://go.microsoft.com/fwlink/?linkid=2305803) · [archived PDF](pdf-reports/microsoft-advertising) | PDF; Feb – Dec 2024 | verified |
| Microsoft Advertising (Xandr) | Microsoft / Xandr | [PDF](https://go.microsoft.com/fwlink/?linkid=2305804) · [archived PDF](pdf-reports/microsoft-advertising-xandr) | PDF; May – Dec 2024 | verified |
| Microsoft 365 Services | Microsoft | [PDF](https://go.microsoft.com/fwlink/?linkid=2305701) · [archived PDF](pdf-reports/microsoft-365-services) | PDF; Feb – Dec 2024 | verified |
| Microsoft 365 Copilot | Microsoft | [PDF](https://go.microsoft.com/fwlink/?linkid=2305802) · [archived PDF](pdf-reports/microsoft-365-copilot) | PDF; Feb – Dec 2024 | verified |
| Hetzner | Hetzner Online GmbH | [DSA page](https://www.hetzner.com/legal/digital-services-act/) | Contact/notice page only | uncertain |
| Fastly | Fastly, Inc. | [DMCA/DSA](https://www.fastly.com/dmca-dsa) | Compliance notice only | uncertain |

## Search engines (non-VLOSE)

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| DuckDuckGo | DuckDuckGo, Inc. | [Regulatory reporting](https://duckduckgo.com/duckduckgo-help-pages/r-legal/regulatory-reporting) · [archived data](harmonised-reports/extracted/duckduckgo) | XLSX (template); CY2025 (+ 2024 PDF) | verified |
| Qwant | Qwant (France) | [Report](https://about.qwant.com/legal/rapport-de-transparence-qwant-2025/) · [archived data](harmonised-reports/extracted/qwant) | HTML + Excel + PDF; CY2025 | verified |
| Lilo | Lilo SAS (now Qwant) | [Report](https://lilo.org/rapport-transparence) · [archived data](harmonised-reports/extracted/lilo) | HTML + Excel; Sep – Dec 2025 | verified |

## Browsers, email & portals

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Yahoo (+ AOL) | Yahoo International Limited | [EU DSA hub](https://www.yahooinc.com/transparency/reports/eu-digital-services-act/index.html) · [archived data](harmonised-reports/extracted/yahoo) | HTML + PDF + CSV; 17 Feb – 31 Dec 2025 | verified |
| Mozilla / Firefox | Mozilla Corporation | [Transparency](https://www.mozilla.org/en-US/about/policy/transparency/2024/) | DSA report; CY2024 | verified |
| GMX | 1&1 Mail & Media GmbH | [Transparenzbericht](https://freephone.gmx.net/transparenzbericht) | ODS (Art. 15); 2024 & 2025 | verified |
| Web.de | 1&1 Mail & Media GmbH | [Impressum](https://www.web.de/impressum/) ([2025 XLSX](https://s.uicdn.com/pih/legal/2025TransparencyReport.xlsx)) · [archived data](harmonised-reports/extracted/webde) | XLSX (Art. 15); 2025 | verified |
| Microsoft Edge | Microsoft | [PDF](https://go.microsoft.com/fwlink/?linkid=2304742) · [archived PDF](pdf-reports/microsoft-edge) | PDF; Feb – Dec 2024 | verified |
| Microsoft Outlook | Microsoft | [PDF](https://go.microsoft.com/fwlink/?linkid=2305703) · [archived PDF](pdf-reports/microsoft-outlook) | PDF; Feb – Dec 2024 | verified |

## Reviews & jobs

| Platform | Operating company | Report URL | Format / period | Confidence |
|----------|-------------------|------------|-----------------|------------|
| Trustpilot | Trustpilot A/S | [PDF](https://cdn.trustpilot.net/businesssite/Trustpilot-DSA-Transparency-Report-May-2025.pdf) · [archived PDF](pdf-reports/trustpilot) | PDF; 17 Feb 2024 – 16 Feb 2025 | verified |
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
| Civitai | Civitai, Inc. | [2024 report](https://civitai.com/articles/10372/civitai-2024-transparency-report) | HTML annual report (not DSA template); 2024 | uncertain |
| SAP Community | SAP SE | [DSA report](https://pages.community.sap.com/resources-legal/dsa-transparency-report-2025) | Web/PDF; 17 Feb – 31 Dec 2025 | verified |
| Apple Books | Apple Distribution International | [Report](https://www.apple.com/legal/dsa/transparency/eu/books/2502/) | HTML report (17 Feb – 31 Dec 2024); also a Feb 2026 XLSX template | verified |
| Microsoft Learn | Microsoft | [PDF](https://go.microsoft.com/fwlink/?linkid=2305903) · [archived PDF](pdf-reports/microsoft-learn) | PDF; Feb – Dec 2024 | verified |
| Microsoft Forms | Microsoft | [PDF](https://go.microsoft.com/fwlink/?linkid=2305902) · [archived PDF](pdf-reports/microsoft-forms) | PDF; Feb – Dec 2024 | verified |
| Microsoft Designer | Microsoft | [PDF](https://go.microsoft.com/fwlink/?linkid=2304936) · [archived PDF](pdf-reports/microsoft-designer) | PDF; Feb – Dec 2024 | verified |
| Microsoft Whiteboard | Microsoft | [PDF](https://go.microsoft.com/fwlink/?linkid=2305705) · [archived PDF](pdf-reports/microsoft-whiteboard) | PDF; Feb – Dec 2024 | verified |
| WEBTOON (LINE / Naver Webtoon) | WEBTOON Entertainment Inc. | [EU DSA notice](https://www.webtoons.com/en/notice/detail?noticeNo=3367) | HTML; Art. 15 + 24(2); CY2024 | verified |
| Zepeto | Naver Z Corporation | [DSA page](https://support.zepeto.me/hc/en-us/articles/15675506191769-Digital-Services-Act) | HTML; Art. 24(2) disclosure | uncertain |

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
| LinkedIn | LinkedIn Ireland | [Feb 2026 ZIP](https://content.linkedin.com/content/dam/help/tns/en/report/LinkedIn-February-2026-Digital-Services-Act-Transparency-Report.zip) · [archived data](harmonised-reports/extracted/linkedin) | ZIP (harmonised template); Feb 2026 (H2 2025) | verified |
| Pinterest | Pinterest Europe | [Feb 2026 ZIP](https://cdn.sanity.io/files/26f0hyrt/pinpolicy_prod/2c552b2ce80a75c1f9e9741e83da8bdbb5028579.zip) · [archived data](harmonised-reports/extracted/pinterest) | ZIP (harmonised template); Feb 2026 (H2 2025) | verified |
| Snapchat | Snap Group Ltd | [H2 2025 report](https://values.snap.com/privacy/transparency/european-union-h2-2025) | HTML; H2 2025 | likely |
| TikTok | TikTok Technology Ltd | [DSA hub](https://www.tiktok.com/transparency/en/dsa-transparency/) | Hub; latest H2 2025 | likely |
| X (Twitter) | Twitter International Unlimited Co. | [DSA report](https://transparency.x.com/en/reports/dsa-transparency-report) | Hub + PDF; latest Feb 2026 | likely |
| YouTube | Google Ireland | [Transparency report](https://transparencyreport.google.com/?hl=en) | Hub; PDF + CSV | likely |
| Google Play | Google Ireland | [Transparency report](https://transparencyreport.google.com/?hl=en) | Hub; PDF + CSV | likely |
| Google Maps | Google Ireland | [Transparency report](https://transparencyreport.google.com/?hl=en) | Hub; PDF + CSV | likely |
| Google Shopping | Google Ireland | [Transparency report](https://transparencyreport.google.com/?hl=en) | Hub; PDF + CSV | likely |
| Google Search (VLOSE) | Google Ireland | [Transparency report](https://transparencyreport.google.com/?hl=en) | Hub; PDF + CSV | likely |
| Bing (VLOSE) | Microsoft Ireland | [EU DSA report](https://www.microsoft.com/en-us/corporate-responsibility/eu-dsa-report-bing) · [archived PDF](pdf-reports/bing-vlose) | Latest Feb 2026; prior PDF | likely |
| Zalando | Zalando SE | [Transparency hub](https://corporate.zalando.com/en/investor-relations/corporate-governance/transparency-hub) | Hub; latest H2 2025 | likely |
| Shein | Roadget Business (Shein) | [DSA hub](https://euqs.shein.com/digital-service-act-a-1994.html) | Hub; latest H2 2025 | uncertain |
| Temu | Whaleco / Elementary Innovation | [Transparency center](https://www.temu.com/transparency-center-reports.html) | Hub; Feb 2026 + PDFs | likely |
| Wikipedia | Wikimedia Foundation | [Feb 2026 XLS](https://foundation.wikimedia.org/wiki/File:Wikipedia_-_DSA_transparency_report_2026-02-28.xls) · [archived data](harmonised-reports/extracted/wikipedia) | XLS (harmonised template); Feb 2026 (H2 2025) | verified |
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
- **No findable report:** Allegro, Bol.com, Catawiki, Milanuncios, InfoJobs,
  Omio, eDreams ODIGEO / Opodo, Agoda, Ticketmaster, See Tickets, Trainline,
  Flixbus, Hopper, Klook, Lastminute.com, TheFork,
  OpenTable, TaskRabbit, Freelancer.com, PeoplePerHour, Treatwell, Doctolib,
  ImmobilienScout24, Immowelt, SeLoger, Rightmove, Zoopla, Funda, Pap.fr,
  Logic-Immo, Otomoto, Standvirtual, Heycar, La Centrale, Hemnet, Daft.ie,
  Habitaclia, GitLab, npm, PyPI, Docker Hub, SourceForge, Replit, Notion, Steam,
  GOG, EA, itch.io, Amazon Appstore, Mastodon, VK, Deezer, Rumble,
  Odysee, Triller, Likee, Bigo Live, Tchibo, Bonprix, vidaXL, Conrad,
  eDarling/Parship, DeviantArt, Archive of Our Own, GoFundMe,
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
  Wish, LightInTheBox, Joom, Ankorstore, Metro Markets, Mercateo/Unite,
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
- **Price-comparison engines (no report found):** PriceRunner, Kelkoo, Prisjakt,
  PriceSpy, Billiger.de, Guenstiger.de, Hinta.fi/Vertaa, LeDénicheur, Twenga/LeGuide,
  Shopzilla, Preisvergleich.de (Heureka publishes only the Art. 24(2) AMAR figure).
- **AI chat / companion / generative (no report found; mostly below threshold):**
  Character.AI, Replika, Janitor AI, Chai, SpicyChat, CrushOn.AI, Talkie, Perchance,
  Midjourney, Leonardo.AI, Tensor.Art, PixAI, NightCafe.
- **More adult platforms (fetch-blocked here; EC index lists only the 4 VLOPs):**
  LiveJasmin, Chaturbate, Fansly, Cam4, BongaCams, Flirt4Free, MyDirtyHobby,
  AdultWork, ManyVids, CamSoda, xHamster, YouPorn, RedTube, Brazzers.
- **B2B wholesale / trade directories (no report found):** Europages, Kompass,
  Visable/wlw, Kaufland marketplace, RS Components, Manutan, real.de, Hood.de,
  Yatego, Rakuten.de, Allegro Lokalnie, Solar.
- **Sports / esports / fan communities (no report found):** Transfermarkt (Art. 11
  contact only), Sofascore, FotMob, Futbin, FACEIT/EFG, ESEA, Challengermode,
  Crunchyroll, DAZN, AniList, Kitsu.
- **Music / audio streaming & creator (no report found; mostly below threshold):**
  Tidal (process page only), Qobuz, Napster, Anghami, Audius, DistroKid, TuneCore,
  CD Baby, Boomplay, Believe/Splice.
- **Comparison portals (no report found):** Check24 (sub-45M, contact only), Verivox,
  HolidayCheck, Travelcircus, Urlaubsguru, Zoover, Billiger-mietwagen, Wechselpilot,
  Smava, Finanzcheck, Tarifcheck.
- **National directories / classifieds (no full report found):** DoneDeal.ie,
  Adverts.ie, Gumtree.ie (shared Distilled DSA portal — Art. 24(2)/notice only);
  Gelbe Seiten, Das Örtliche, PagesJaunes/Solocal, Cylex, GoLocal, werkenntden,
  Quoka, Deine-Tierwelt, Bazaraki, Locanto.
- **Messaging (no DSA content-moderation report found):** Signal (government-requests
  only), Threema (Swiss BÜPF only), KakaoTalk (privacy report only), CapCut (DSA info
  page only), Lark, Element/Matrix, Wire, Wickr.
- **Browsers / portals (no report found):** Opera (security report only), Vivaldi,
  Proton (Art. 11 contact only).
- **Big-tech non-VLOP services not separately reported:** Apple Maps, Apple TV, Apple
  Music; Google Chrome Web Store, Google Drive, Blogger, Google News, Google Photos,
  Waze (Google reports these only in its aggregate MAR disclosure); Amazon Prime Video,
  Amazon Music.
- **Japanese / Korean platforms (no own DSA report found):** Rakuten Kobo, Pixiv/BOOTH/
  Skeb, DMM, Niconico, Cookpad, Kakaku.com, Weverse (HYBE), Kakao Webtoon, KakaoPage,
  Lezhin, Tappytoon, Tapas, AfreecaTV/SOOP, Watcha, Wavve, Naver, Bubble/Dear U.
- **Game publishers / console (no report found):** Capcom, SEGA, Take-Two/Rockstar,
  NCsoft, Netmarble, Pearl Abyss, Smilegate, Gameloft, Bandai Namco (Art. 11 contact only).
- **Chinese platforms (no own DSA report found / heavily bot-blocked):** Miravia,
  Vova, Geekbuying, Tomtop, Zaful, Rosegal, PatPat, Cider, Newchic, Halara, Newme,
  Cupshe, Floryday, 1688, Taobao/Tmall, Sammydress; HoYoverse/Genshin (Cognosphere),
  NetEase Games, Lilith, Moonton, Century Games, Kwai/Kuaishou,
  Xiaohongshu/RED, Trip.com, QQ/QZone, Bilibili, Douyin; Vivo, Lenovo, Anker, TCL,
  Huawei Cloud.
- **Indian platforms (no report found; most are India-only / out of DSA scope):**
  EU-present but no findable DSA page — OYO, Pocket FM, Kuku FM, Pratilipi, MakeMyTrip,
  Cleartrip, Ixigo, InMobi/Glance, ShareChat, Moj; Zoho & Freshworks (GDPR/security
  material only, no DSA report). India-only / out of scope — Flipkart, Myntra, Meesho,
  Nykaa, Snapdeal, Ajio, Dream11, MPL, WinZO, Nazara, Gameskraft, Zupee (real-money
  gaming, barred in most EU states), Shaadi.com, BharatMatrimony, Jeevansathi,
  WazirX, CoinDCX, CoinSwitch (crypto → MiCA, not DSA), Naukri, BYJU'S, Unacademy,
  upGrad, JioCinema, JioSaavn, Gaana, Dailyhunt/Josh.
- **Southeast Asia / Latin America / Middle East (out of scope or no report found):**
  Almost all are region-only with no EU recipient base (out of DSA scope) — Shopee
  (exited the EU 2022–23), Lazada, Grab, Gojek/Tokopedia, Traveloka, Carousell,
  Zalora, Bukalapak; MercadoLibre (publishes a LatAm-scoped, non-DSA report),
  Despegar, Rappi, Nubank, Globoplay, Magalu, Americanas; Noon, OpenSooq,
  Namshi, Ounass, Property Finder, Bayut, Jumia (Africa), Yalla. A few have genuine
  EU presence but **no findable DSA report** — Razer (RazerStore/Razer Gold) and
  Hotmart (Hotmart BV, Amsterdam). (Talabat, Careem and dubizzle report
  only via their global parents Delivery Hero / Uber Eats / OLX — already listed.)
- **Russian / Belarusian (out of DSA scope — EU sanctions / no EU operations):**
  Mail.ru, OK.ru/Odnoklassniki, Ozon, Wildberries, RuTube, Dzen, Rambler, Kufar,
  Yango, Nebius.
- **Other CEE / Baltic / Balkan (no findable report; many bot-blocked):** Media Expert,
  RTV Euro AGD, Pracuj.pl, Otodom, Gratka, Slevomat, Datart,
  Modivo/eobuwie, Answear, Bookline; ss.lv, Osta.ee, Skelbiu.lt, Aruodas.lt, City24,
  Njuškalo (HR), Bolha (SI), Index Oglasi, Mimovrste, OLX.bg, Bazar.bg, Car.gr,
  Spitogatos, Publi24, Lajumate, Kainos.lt, Varle.lt, Senukai; KupujemProdajem
  (Serbia, non-EU).
- **Out of scope:** Swiss-only platforms (tutti.ch, ricardo.ch, anibis.ch — not
  EU/EEA); Finn.no (Norway has not transposed the DSA into the EEA agreement);
  Avito (not EU-operating); Gumtree UK, MoneySuperMarket, Confused.com (UK,
  post-Brexit); Comparis (Switzerland).
