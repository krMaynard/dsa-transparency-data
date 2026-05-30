# DSA Transparency Data

Archive of EU [Digital Services Act](https://eur-lex.europa.eu/eli/reg/2022/2065/oj) transparency reports for 33 services covering **H2 2025 (1 July – 31 December 2025)**, published February 2026. This covers every designated VLOP/VLOSE that reported for the period — including the adult-content platforms Pornhub, XVideos, and XNXX — plus lower-tier online platforms operated by VLOP parents (the non-VLOP Apple and Wikimedia services). Stripchat, designated in December 2023, was [de-designated in May 2025](https://digital-strategy.ec.europa.eu/en/policies/list-designated-vlops-and-vloses) and is therefore not included.

Each report follows the DSA Implementing Regulation [(EU) 2025/40](https://eur-lex.europa.eu/eli/reg_impl/2025/40/oj) template (tables 1–11). Files are stored in their original publisher format (CSV bundle, `.xlsx`, or `.xls`).

## Layout

```
.
├── aliexpress/         (CSVs)
├── amazon/             (CSVs)
├── apple/
│   ├── app-store.xlsx
│   ├── books.xlsx
│   ├── icloud-storage.xlsx
│   └── podcasts.xlsx
├── booking-com/        (CSVs)
├── google/
│   ├── maps/           (CSVs + source xlsx)
│   ├── multi-services/
│   ├── play/
│   ├── search/
│   ├── shopping/
│   └── youtube/
├── meta/
│   ├── facebook/       (CSVs)
│   └── instagram/      (CSVs)
├── microsoft/
│   ├── bing.xlsx
│   └── linkedin/       (CSVs)
├── pinterest/          (CSVs)
├── shein.xlsx
├── snapchat/           (CSVs)
├── temu/               (CSVs)
├── tiktok/             (CSVs)
├── wikimedia/
│   ├── commons.xls
│   ├── wikidata.xls
│   ├── wikipedia.xls
│   ├── wikiversity.xls
│   ├── wikivoyage.xls
│   └── wiktionary.xls
├── x/                  (CSVs)
├── zalando/            (CSVs)
│
│   # adult-content VLOPs (original publisher folder names)
├── PH_DSA_Transparency_Report_FH26_1776436263/          (Pornhub — CSVs)
├── XNXX+-+Transparency+report+-+July-December+2025/      (XNXX — CSVs)
└── XVideos+-+Transparency+report+-+July-December+2025/   (XVideos — CSVs)
```

CSV bundles contain the standard 11 tables:

| # | Table |
|---|---|
| 1 | Report identification |
| 2 | Categories of illegal content / ToS violations |
| 3 | Member State orders |
| 4 | Notices |
| 5 | Own-initiative actions on illegal content |
| 6 | Own-initiative actions on ToS violations |
| 7 | Appeals & recidivism |
| 8 | Automated means |
| 9 | Human resources |
| 10 | Average Monthly Active Recipients (AMAR) |
| 11 | Qualitative description |

## convert.py

`convert.py` flattens tables 3–7 from all 33 services into a single compact JSON file used by a separate dashboard project. It writes to `../krMaynard.github.io/data/vlop-dsa.json` by default — adjust `OUT_FILE` in the script if you want it elsewhere.

```
python3 convert.py
```

Requires `openpyxl` and `xlrd`.

### append_platforms.py

`append_platforms.py` incrementally appends any `SERVICE_DEFS` entries that are not yet present to an **existing** `vlop-dsa.json`, leaving the services already in the file untouched. It reuses `convert.py`'s table parsers. Use this when you want to add new services without regenerating (and potentially perturbing) the existing ones — the committed JSON predates this archive and a full `convert.py` rebuild does not reproduce it exactly for the Google services.

```
python3 append_platforms.py
```

## Source

Reports are published by each VLOP on their own transparency page; aggregated index at the EU [DSA Transparency Database](https://transparency.dsa.ec.europa.eu/).
