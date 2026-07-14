#!/usr/bin/env python3
"""Build the Korea Network Act (illegal-sexual-content) transparency dataset.

South Korea's amended **Network Act** (Act on Promotion of Information and
Communications Network Utilization and Information Protection, Art. 64-5) and
**Telecommunications Business Act** (Art. 22-5), from the two bills that passed
on 20 May 2020, require online service providers to implement technical and
managerial measures against the circulation of *illegal sexual content*
(illegally-filmed content, deepfake/"fake" images and videos, and child/youth
sexual-abuse material) and to publish an **annual transparency report** on them.

**Google** publishes one report per calendar year covering **Search and YouTube
jointly**. This builder ingests Google's six publications so far (2020 → 2025,
archived in ``raw/google-korea-network-act-YYYY.pdf``) into a tidy-long
``korea-network-act.json`` — ``{sources, publishers, coverage, columns, rows}``
with columns ``publisher, period, section, category, metric, unit, value``.

Two Korean online-service providers — **Naver** and **Kakao** — are ingested
alongside Google. Unlike Google's own-format report, they file the standardized
정보통신망법 §64-5 / 전기통신사업법 §22-5 template with the KCC (now KMCC), which
publishes each provider's PDF on its board 1156. Those reports give the year's
figures on the standard template rather than Google's own monthly breakdown, so
Naver and Kakao populate only the comparable **annual_summary** series
(``urls_received`` / ``urls_removed``), transcribed from
``raw/{naver,kakao}-korea-network-act-YYYY.pdf`` (2020 → 2025). ``received`` is
the report's 신고접수 소계 (validated against its 피해자등 + 기관·단체 split);
``removed`` is the 삭제·접속차단 total (content deleted / access-blocked by the
provider, including any removed after a 방심위/KCSC review). Their by-reason
splits are *not* stored: the reports mark reasons as 중복계상(可) — a request may be
double-counted across reasons — so they don't partition the total.

The reports come in two shapes:
 * **2024 and 2025** publish a full **monthly** table (§II) broken down by
   complainant, reason and outcome. Those go into the detailed sections
   ``requests_received`` / ``request_reasons`` / ``processed_result`` /
   ``removal_reasons`` with ``period`` a month (``YYYY-MM``). The monthly values
   for 2024 were extracted from the PDF and re-validated here; 2025's were
   transcribed. Every row's twelve months are cross-checked against the report's
   stated annual total, and each section's categories against its grand total —
   the build raises on any mismatch.
 * **2020–2023** are prose-only: they state just the year's headline URL counts
   (2020 covers only 10–31 Dec 2020, the law's implementation date). Those go
   into an ``annual_summary`` section (``period`` = the year ``YYYY``,
   ``category`` = ``All``) with ``metric`` ``urls_received`` / ``urls_removed``.

The ``annual_summary`` section is also emitted for 2024/2025 (rolled up from
their tables) so it holds a single, comparable 2020→2025 series — a cross-year
rollup that sits *beside* the detailed monthly sections, not additive with them.

Design notes for consumers:
 * **Monthly-section ``period`` is a month; annual_summary ``period`` is a year.**
   Within a monthly section, summing over ``period`` gives that year's annual
   total (the report's own "Total" column is used only to validate, never
   stored). Pin a ``section`` before aggregating; the four monthly sections are
   cross-cuts of the same requests and are NOT additive across sections, and
   ``annual_summary`` is a rollup of them (so don't sum it together with them).
 * **Disjoint categories per monthly section.** The report's per-section "Total"
   rows are dropped, so within a section the categories partition it.
"""
from __future__ import annotations

import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "korea-network-act.json")

PUBLISHER = "Google"
SOURCES = {
    "2020": "https://storage.googleapis.com/transparencyreport/report-downloads/south-korea-network-act_2020-12-10_2020-12-31_en_v1.pdf",
    "2021": "https://storage.googleapis.com/transparencyreport/report-downloads/south-korea-network-act_2021-1-1_2021-12-31_en_v1.pdf",
    "2022": "https://storage.googleapis.com/transparencyreport/report-downloads/south-korea-network-act_2022-1-1_2022-12-31_en_v1.pdf",
    "2023": "https://storage.googleapis.com/transparencyreport/report-downloads/south-korea-network-act_2023-1-1_2023-12-31_en_v1.pdf",
    "2024": "https://storage.googleapis.com/transparencyreport/report-downloads/south-korea-network-act_2024-1-1_2024-12-31_en_v1.pdf",
    "2025": "https://storage.googleapis.com/transparencyreport/report-downloads/south-korea-network-act_2025-1-1_2025-12-31_en_v1.pdf",
}

MONTHS = list(range(1, 13))

# ── Detailed monthly tables (§II) — years that publish the full breakdown ────
# {year: {section: {category: [Jan … Dec]}}}. A ``Total`` category per section
# in the source is dropped (derived). 2025 transcribed; 2024 extracted from the
# PDF's §II table (each row re-validated against its printed annual total).
MONTHLY = {
    2025: {
        "requests_received": {
            "Victims etc. (User Requests)": [1549, 1268, 1343, 2201, 1255, 1129, 1310, 1373, 3535, 2094, 2369, 2433],
            "Agency and Org (Gov Requests)": [2377, 2971, 2902, 4482, 5908, 8061, 8269, 6751, 15720, 12310, 14059, 9611],
        },
        "request_reasons": {
            "Illegal Photos and Videos": [3849, 4137, 4181, 6632, 7120, 9108, 9513, 7992, 18795, 14084, 16359, 11933],
            "Fake Images and Videos": [74, 101, 43, 38, 42, 46, 15, 43, 138, 61, 22, 27],
            "Child or Youth Sexual Abuse Content": [3, 1, 21, 13, 1, 36, 51, 89, 322, 259, 47, 84],
        },
        "processed_result": {
            "Removed Voluntarily by the Company": [3089, 3727, 3358, 5343, 6066, 7119, 7801, 6604, 15671, 11390, 12825, 9341],
            "Not Removed - Not Enough Information": [197, 128, 381, 171, 182, 979, 536, 205, 620, 860, 476, 593],
            "Not Removed - Content Already Removed": [102, 78, 94, 214, 198, 96, 119, 99, 418, 311, 234, 247],
            "Not Removed - Content Not Found": [441, 242, 325, 718, 658, 856, 1012, 932, 2045, 1459, 2623, 1530],
            "Not Removed - Other": [97, 64, 87, 237, 59, 140, 111, 284, 501, 384, 270, 333],
            "KCSC Assessment - Removed after the Assessment": [0] * 12,
            "KCSC Assessment - N/A (False Positive, Dismissals etc.)": [0] * 12,
        },
        "removal_reasons": {
            "Illegal Photos and Videos": [3032, 3638, 3331, 5314, 6031, 7073, 7801, 6565, 15542, 11377, 12802, 9324],
            "Fake Images and Videos": [57, 89, 26, 29, 35, 31, 0, 37, 127, 12, 19, 15],
            "Child or Youth Sexual Abuse Content": [0, 0, 1, 0, 0, 15, 0, 2, 2, 1, 4, 2],
        },
    },
    2024: {
        "requests_received": {
            "Victims etc. (User Requests)": [3423, 1910, 1894, 2518, 4784, 2753, 3145, 3260, 3358, 2762, 3207, 1013],
            "Agency and Org (Gov Requests)": [12176, 10803, 14815, 12755, 13268, 12659, 11936, 11367, 6582, 9195, 4095, 4374],
        },
        "request_reasons": {
            "Illegal Photos and Videos": [13090, 11014, 12970, 11575, 15726, 12219, 11915, 12245, 6982, 9595, 5863, 4073],
            "Fake Images and Videos": [58, 18, 22, 12, 9, 517, 3, 183, 118, 3, 16, 5],
            "Child or Youth Sexual Abuse Content": [2451, 1681, 3717, 3686, 2317, 2676, 3163, 2199, 2840, 2359, 1423, 1309],
        },
        "processed_result": {
            "Removed Voluntarily by the Company": [13985, 11898, 15907, 14013, 17046, 13792, 14040, 12773, 8575, 10115, 6052, 4015],
            "Not Removed - Not Enough Information": [227, 136, 82, 114, 61, 176, 88, 89, 168, 345, 170, 566],
            "Not Removed - Content Already Removed": [197, 74, 145, 197, 457, 189, 401, 435, 402, 340, 211, 220],
            "Not Removed - Content Not Found": [505, 512, 473, 648, 349, 420, 451, 1110, 689, 1065, 826, 460],
            "Not Removed - Other": [685, 93, 102, 300, 139, 833, 101, 220, 106, 90, 42, 124],
            "KCSC Assessment - Removed after the Assessment": [0] * 12,
            "KCSC Assessment - N/A (False Positive, Dismissals etc.)": [0] * 12,
        },
        "removal_reasons": {
            "Illegal Photos and Videos": [11648, 10367, 12415, 10702, 14792, 11198, 11044, 10642, 5913, 8057, 4836, 3326],
            "Fake Images and Videos": [48, 0, 17, 1, 8, 51, 1, 142, 96, 1, 9, 1],
            "Child or Youth Sexual Abuse Content": [2289, 1531, 3475, 3310, 2246, 2543, 2995, 1989, 2566, 2057, 1207, 688],
        },
    },
}

SECTION_METRIC = {
    "requests_received": ("requests", "count"),
    "request_reasons": ("requests", "count"),
    "processed_result": ("urls", "count"),
    "removal_reasons": ("urls_removed", "count"),
}

# The report's stated grand total for each (year, section) — the "Total" row /
# column — used to fail loudly on mistranscription. request_reasons has no
# printed total (it equals requests_received's) and removal_reasons equals the
# "Removed" row; both are validated against those below.
EXPECT_SECTION_TOTALS = {
    2025: {"requests_received": 115280, "request_reasons": 115280,
           "processed_result": 115280, "removal_reasons": 92334},
    # 2024's requests-received (158,052) and processed (158,044) differ by 8 —
    # a discrepancy in Google's own report, preserved rather than "fixed".
    2024: {"requests_received": 158052, "request_reasons": 158052,
           "processed_result": 158044, "removal_reasons": 142211},
}

# ── Annual summary — the comparable 2020→2025 headline series ────────────────
# {year: (urls_received, urls_removed)}. 2020–2023 are the prose-only reports'
# stated figures (2020 covers only 10–31 Dec 2020); 2024/2025 are rolled up from
# their tables (received = requests_received total, removed = the "Removed" row).
ANNUAL = {
    2020: (61, 42),
    2021: (31281, 18294),
    2022: (47162, 38908),
    2023: (90616, 81593),
    2024: (158052, 142211),
    2025: (115280, 92334),
}

# ── Naver & Kakao — the KMCC §64-5 template's annual figures ─────────────────
# {publisher: {year: (urls_received, urls_removed)}}. Transcribed from each
# provider's report PDF on KMCC board 1156 (archived in raw/) and visually
# verified against the "3. 불법촬영물등의 신고접수 및 처리결과" table:
#   received = 신고접수 소계 (== 피해자등 + 기관·단체, cross-checked per year);
#   removed  = 삭제·접속차단 total (self-delete/block + any post-방심위 removal).
# 2020 covers only 10–31 Dec 2020 (the law's implementation date), like Google's.
PROVIDER_ANNUAL = {
    "Naver": {2020: (0, 0), 2021: (94, 71), 2022: (56, 9),
              2023: (54, 5), 2024: (91, 4), 2025: (30, 2)},
    "Kakao": {2020: (70, 0), 2021: (169, 168), 2022: (75, 75),
              2023: (51, 51), 2024: (66, 66), 2025: (31, 31)},
}

# Durable provenance: the KMCC board-1156 view page for each report (the
# download.do?fileSeq link needs a session cookie + Referer, so the view page —
# from which the fileSeq is re-resolvable — is the stable pointer). The PDFs
# themselves are archived in raw/.
_KMCC_VIEW = ("https://www.kmcc.go.kr/user.do?mode=view&page=A02061000"
              "&dc=K02061000&boardId=1156&boardSeq=")
PROVIDER_SOURCES = {
    "Naver": {str(y): _KMCC_VIEW + s for y, s in
              {2020: "51020", 2021: "53359", 2022: "55981",
               2023: "62096", 2024: "67287", 2025: "69036"}.items()},
    "Kakao": {str(y): _KMCC_VIEW + s for y, s in
              {2020: "51006", 2021: "53360", 2022: "55964",
               2023: "62105", 2024: "67277", 2025: "69027"}.items()},
}


def build_rows():
    rows = []
    for year, sections in MONTHLY.items():
        for section, cats in sections.items():
            metric, unit = SECTION_METRIC[section]
            section_sum = 0
            for cat, months in cats.items():
                if len(months) != 12:
                    raise ValueError(f"{year}/{section}/{cat}: expected 12 months, got {len(months)}")
                section_sum += sum(months)
                for m, val in zip(MONTHS, months, strict=True):
                    rows.append((PUBLISHER, f"{year}-{m:02d}", section, cat, metric, unit, val))
            expected = EXPECT_SECTION_TOTALS[year][section]
            if section_sum != expected:
                raise ValueError(f"{year}/{section}: categories sum to {section_sum:,} "
                                 f"!= stated section total {expected:,}")
        # cross-check the derived annual against the monthly tables.
        recv = sum(sum(v) for v in sections["requests_received"].values())
        removed = sum(sections["processed_result"]["Removed Voluntarily by the Company"])
        if (recv, removed) != ANNUAL[year]:
            raise ValueError(f"{year}: table rolls up to ({recv:,}, {removed:,}) "
                             f"!= ANNUAL {ANNUAL[year]}")
    for year, (recv, removed) in sorted(ANNUAL.items()):
        rows.append((PUBLISHER, str(year), "annual_summary", "All", "urls_received", "count", recv))
        rows.append((PUBLISHER, str(year), "annual_summary", "All", "urls_removed", "count", removed))
    # Naver & Kakao — annual_summary only (the KMCC template's yearly figures).
    for pub, years in sorted(PROVIDER_ANNUAL.items()):
        for year, (recv, removed) in sorted(years.items()):
            if not 0 <= removed <= recv:  # a transcription typo can't pass this
                raise ValueError(f"{pub} {year}: removed {removed} not in [0, {recv}]")
            rows.append((pub, str(year), "annual_summary", "All", "urls_received", "count", recv))
            rows.append((pub, str(year), "annual_summary", "All", "urls_removed", "count", removed))
    return rows


def main():
    rows = build_rows()
    data = {
        "sources": {PUBLISHER: SOURCES, **PROVIDER_SOURCES},
        "publishers": [PUBLISHER, *sorted(PROVIDER_ANNUAL)],
        "coverage": "2020-12..2025-12",
        "columns": ["publisher", "period", "section", "category", "metric", "unit", "value"],
        "rows": rows,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    print(f"wrote {OUT}: {len(rows)} rows across {len(data['publishers'])} publishers")
    print("rows per section:", dict(Counter(r[2] for r in rows)))
    for pub in data["publishers"]:
        print(f"{pub} annual urls_received:", {int(r[1]): r[6] for r in rows
              if r[0] == pub and r[2] == "annual_summary" and r[4] == "urls_received"})


if __name__ == "__main__":
    main()
