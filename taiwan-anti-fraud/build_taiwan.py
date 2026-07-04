#!/usr/bin/env python3
"""Build taiwan-anti-fraud.json from data published under Taiwan's Anti-Fraud Act.

Taiwan's 詐欺犯罪危害防制條例 (Fraud Crime Hazard Prevention Act, "打詐專法",
in force July 2024) created two transparency streams:

1. **Government enforcement data.** The National Police Agency's Criminal
   Investigation Bureau publishes — on Taiwan's open-data portal
   (data.gov.tw dataset 176455) — the registry of **fraud websites whose DNS
   resolution was suspended under Article 42** of the Act: one row per blocked
   domain, with the ROC-calendar month, a site-category label (網站性質), the
   legal basis, and the requesting unit. The extractor aggregates that registry
   to a tidy-long table of blocked-site counts per month × category. The raw
   registry (the domain-level CSV) is archived verbatim in raw/.

2. **Platform transparency reports.** The designated online-ad platforms
   (Google/YouTube, Meta Facebook/Instagram, LINE, TikTok — MODA's list under
   Art. 27) must publish an annual 詐欺防制計畫透明度報告 (statistics on
   fraud-ad notifications received and content/accounts actioned under
   Arts. 32–33). The first (2025) round is extracted here from the report
   artifacts archived verbatim in raw/:

   - **Google** — a zh-TW PDF on the Google Transparency Report download
     bucket, covering 2024-07-01..2025-06-30 (Art. 32 removal requests,
     URLs removed by legal/policy basis, ad accounts suspended).
   - **TikTok** — a PDF on TikTok's transparency site, covering
     2025-01-01..2025-09-30 (MODA notifications and their outcomes, plus
     voluntary platform-enforcement figures: proactively removed fraud ads
     and videos, Taiwan and global).
   - **LINE** — LY Corporation's HTML disclosure page, covering
     2024-08-02..2025-09-30 (zero Art. 32 dispositions; Art. 33 account
     suspensions, including a CIB joint-operation subset).
   - **Meta** (Facebook/Instagram) — published on transparency.meta.com but
     **not yet extractable**: the PDF sits behind expiring fbcdn CDN tokens,
     the live site errors for this pipeline, and the only Wayback capture of
     the asset is a 403. Slots in as a fourth parser once retrievable.

   Each parser anchors on the report's own sentences/table labels and crashes
   on drift (fail-loud); values are exact integers as filed.

Tidy-long output — one row per measured value:

  publisher, period, section, category, metric, unit, value

`publisher` is `NPA-165` for the government stream and the platform name
(`Google`/`LINE`/`TikTok`) for the statutory reports; `period` is the
Gregorian month (`YYYY-MM`) for the NPA stream and the report's stated
coverage window (`YYYY-MM..YYYY-MM`) for platform rows; `unit` is `count`.
Platform sections: `afa_transparency_report` (statistics filed under
Arts. 32/33 of the Act) and `platform_enforcement` (voluntary proactive
figures TikTok discloses alongside). Never sum across sections, and pin a
`metric` before aggregating platform rows — requests ≠ URLs ≠ accounts, and
`art33_accounts_suspended_cib_project` is a subset of
`art33_accounts_suspended`.

**Rolling window caveat:** the upstream registry is a live feed covering
roughly the most recent half-year; older months drop out upstream. The
archived raw/ CSV freezes the window captured at vendoring time, and
`--download` refreshes it (union with the existing archive so months that
have rotated out upstream are preserved).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, "raw")
OUT_JSON = os.path.join(HERE, "taiwan-anti-fraud.json")

COLUMNS = ["publisher", "period", "section", "category", "metric", "unit", "value"]

RAW_CSV = "dns-blocked-sites.csv"
# data.gov.tw dataset 176455 — the stable per-resource download endpoint.
DNS_URL = ("https://opdadm.moi.gov.tw/api/v1/no-auth/resource/api/dataset/"
           "29E8E643-88ED-4952-B21E-BD42A3B7108C/resource/"
           "BBA077D2-2AB6-4011-9D61-E2585110AC62/download")
EXPECTED_HEADER = ["民國年月", "網域", "網站性質", "法律依據", "聲請單位"]

# The 2025 statutory platform reports (archived verbatim in raw/; see the
# module docstring for what each covers and why Meta's is absent).
PLATFORM_REPORTS = {
    "Google": ("google-fraud-prevention-report-2025.pdf",
               "https://storage.googleapis.com/transparencyreport/"
               "report-downloads/pdf-report-ll_2024-7-1_2025-6-30_zh_TW_v1.pdf"),
    "TikTok": ("tiktok-fraud-prevention-report-2025.pdf",
               "https://sf16-va.tiktokcdn.com/obj/eden-va2/zayvwlY_fjulyhwzuhy%5B/"
               "ljhwZthlaukjlkulzlp/misc/tw-fraud-prevention-report-2025.pdf"),
    "LINE": ("line-fraud-prevention-report-2025.html",
             "https://tw-af-disclosure.landpress.line.me/2025-AF-Transparency"),
}


def _period(roc_ym: str) -> str:
    """ROC-calendar 民國年月 ('11412') -> Gregorian 'YYYY-MM' ('2025-12')."""
    s = (roc_ym or "").strip()
    if not re.fullmatch(r"\d{4,5}", s):
        raise SystemExit(f"unrecognised 民國年月: {roc_ym!r}")
    year, month = int(s[:-2]) + 1911, int(s[-2:])
    if not 1 <= month <= 12:
        raise SystemExit(f"unrecognised 民國年月: {roc_ym!r}")
    return f"{year:04d}-{month:02d}"


def _read_registry(path: str) -> list[dict[str, str]]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != EXPECTED_HEADER:
            raise SystemExit(f"{path}: unexpected header {reader.fieldnames}; "
                             f"expected {EXPECTED_HEADER}")
        return [r for r in reader if (r.get("網域") or "").strip()]


def _squash(text: str) -> str:
    """Remove ALL whitespace: Google's PDF inserts a space between every CJK
    glyph and the HTML/PDF extractors wrap lines arbitrarily, so anchors match
    against the whitespace-free stream. Digit groups keep their commas."""
    return re.sub(r"\s+", "", text)


def _pdf_text(path: str) -> tuple[str, list[tuple[str, str]]]:
    """(whitespace-squashed full text, normalised label->value table cells)."""
    import pdfplumber  # CI dependency; imported lazily like openpyxl elsewhere
    text_parts: list[str] = []
    cells: list[tuple[str, str]] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text_parts.append(page.extract_text() or "")
            for table in page.extract_tables():
                for row in table:
                    vals = [_squash(c or "") for c in row]
                    if len(vals) >= 2 and vals[0]:
                        cells.append((vals[0], vals[1]))
    return _squash("".join(text_parts)), cells


def _grab(text: str, pattern: str, what: str) -> int:
    m = re.search(pattern, text)
    if not m:
        raise SystemExit(f"{what}: anchor not found (report format drift?): "
                         f"{pattern}")
    return int(m.group(1).replace(",", ""))


def _google_rows(raw_dir: str) -> list[list]:
    """Google's zh-TW PDF: a label/value table + a footnote figure."""
    path = os.path.join(raw_dir, PLATFORM_REPORTS["Google"][0])
    if not os.path.isfile(path):
        raise SystemExit(f"missing expected raw file: {path}")
    text, cells = _pdf_text(path)
    # The table straddles a page break (the last label's trailing 量 lands on
    # the next page), so match labels by a distinctive substring.
    anchors = {
        "government_requests": "政府要求數量",
        "urls_named": "政府要求中列出的網",
        "urls_removed": "移除的網址總數",
        "urls_removed_legal": "依法(即因為違反當地法律命令)移除",
        "urls_removed_policy": "根據政策(即因為違反Google內部防詐政策)移除",
        "ad_accounts_suspended": "中止的廣告帳號總數",
    }
    got: dict[str, int] = {}
    for label, value in cells:
        for metric, anchor in anchors.items():
            if anchor in label and value:
                if metric in got:
                    raise SystemExit(f"google: duplicate table match: {metric}")
                got[metric] = int(value.replace(",", ""))
    missing = sorted(set(anchors) - set(got))
    if missing:
        raise SystemExit(f"google: table anchors not found: {missing}")
    got["urls_not_actioned"] = _grab(
        text, r"其中([\d,]+)個網址無法依政府要求做相應處理", "google")
    if got["urls_removed"] != got["urls_removed_legal"] + got["urls_removed_policy"]:
        raise SystemExit("google: removal split does not sum to the total")
    if got["urls_named"] != got["urls_removed"] + got["urls_not_actioned"]:
        raise SystemExit("google: named URLs != removed + not actioned")
    period = "2024-07..2025-06"
    return [["Google", period, "afa_transparency_report", "", metric,
             "count", got[metric]] for metric in sorted(got)]


def _tiktok_rows(raw_dir: str) -> list[list]:
    """TikTok's PDF: figures embedded in the report narrative."""
    path = os.path.join(raw_dir, PLATFORM_REPORTS["TikTok"][0])
    if not os.path.isfile(path):
        raise SystemExit(f"missing expected raw file: {path}")
    text, _ = _pdf_text(path)
    period = "2025-01..2025-09"
    statutory = {
        "moda_notifications": r"共接獲數位發展部(\d+)件關於詐欺廣告之通報",
        "urls_named": r"涉及(\d+)則連結",
        "notifications_ad_cases": r"其中含有(\d+)件確認為廣告案件",
        "notifications_ugc_cases": r"(\d+)件為使用者產製內容",
        "ads_removed": r"共下架(\d+)則廣告內容",
        "advertiser_accounts_banned": r"上述(\d+)個廣告主帳號",
    }
    voluntary = {
        "fraud_ads_removed_taiwan":
            r"主動偵測並移除共([\d,]+)則針對台灣投放",
        "advertisers_actioned_taiwan": r"共([\d,]+)名廣告主進行處置",
        "videos_removed_global": r"於全球範圍內移除共([\d,]+)則違反《社群守則》之影片",
        "videos_removed_taiwan": r"在台灣部分，TikTok共移除([\d,]+)則違規影片",
        "fraud_videos_removed_taiwan": r"涉及詐欺與詐騙違規之影片共移除([\d,]+)則",
    }
    rows = [["TikTok", period, "afa_transparency_report", "", metric, "count",
             _grab(text, pat, "tiktok")] for metric, pat in statutory.items()]
    rows += [["TikTok", period, "platform_enforcement", "", metric, "count",
              _grab(text, pat, "tiktok")] for metric, pat in voluntary.items()]
    return rows


def _line_rows(raw_dir: str) -> list[list]:
    """LINE's HTML disclosure page: figures embedded in the page prose."""
    path = os.path.join(raw_dir, PLATFORM_REPORTS["LINE"][0])
    if not os.path.isfile(path):
        raise SystemExit(f"missing expected raw file: {path}")
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    import html as html_mod
    text = re.sub(r"<script.*?</script>", " ", raw, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = _squash(html_mod.unescape(re.sub(r"<[^>]+>", " ", text)))
    period = "2024-08..2025-09"
    rows = [
        ["LINE", period, "afa_transparency_report", "", "art32_ad_dispositions",
         "count", _grab(text, r"2024年8月2日（《詐防條例》生效日）至2025年9月30日，"
                              r"敝公司接獲(\d+)件依《詐防條例》第32條第一項第一款", "line")],
        ["LINE", period, "afa_transparency_report", "",
         "art32_service_suspension_dispositions", "count",
         _grab(text, r"2024年8月2日至2025年9月30日，敝公司接獲(\d+)件"
                     r"依《詐防條例》第32條第一項第二款", "line")],
        ["LINE", "2023-06..2025-09", "afa_transparency_report", "",
         "sitc_removal_notices", "count",
         _grab(text, r"自2023年6月28日至2025年9月30日止，敝公司接獲(\d+)件"
                     r"依《證券投資信託及顧問法》第70-1條", "line")],
        ["LINE", period, "afa_transparency_report", "",
         "art33_accounts_suspended", "count",
         _grab(text, r"依《詐防條例》第33條規定通報涉詐用戶帳號，"
                     r"對([\d,]+)筆帳號暫停提供服務", "line")],
        ["LINE", period, "afa_transparency_report", "",
         "art33_accounts_suspended_cib_project", "count",
         _grab(text, r"專案合作所暫停提供服務之([\d,]+)筆涉詐帳號", "line")],
    ]
    return rows


def build(raw_dir: str) -> dict:
    path = os.path.join(raw_dir, RAW_CSV)
    if not os.path.isfile(path):
        raise SystemExit(f"missing expected raw file: {path}")
    registry = _read_registry(path)
    counts: dict[tuple[str, str], int] = {}
    for r in registry:
        period = _period(r.get("民國年月") or "")
        category = re.sub(r"\s+", " ", r.get("網站性質") or "").strip() or "不詳"
        counts[(period, category)] = counts.get((period, category), 0) + 1
    rows = [["NPA-165", period, "dns_blocked_sites", category,
             "sites_blocked", "count", n]
            for (period, category), n in counts.items()]
    if not rows:
        raise SystemExit("parsed zero rows (format drift?)")
    coverage = max(r[1] for r in rows)  # NPA monthly stream only
    rows += _google_rows(raw_dir)
    rows += _tiktok_rows(raw_dir)
    rows += _line_rows(raw_dir)
    rows.sort(key=lambda x: x[:6])
    return {
        "source": "https://data.gov.tw/dataset/176455",
        "coverage": coverage,
        "columns": COLUMNS,
        "rows": rows,
    }


def _download(raw_dir: str) -> None:
    """Refresh the registry, **unioning** with the archived rows: the upstream
    feed is a rolling window, so months that have rotated out are kept."""
    os.makedirs(raw_dir, exist_ok=True)
    path = os.path.join(raw_dir, RAW_CSV)
    old: list[dict[str, str]] = _read_registry(path) if os.path.isfile(path) else []
    req = urllib.request.Request(DNS_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = resp.read().decode("utf-8-sig")
    reader = csv.DictReader(body.splitlines())
    if reader.fieldnames != EXPECTED_HEADER:
        raise SystemExit(f"download: unexpected header {reader.fieldnames}")
    new = [r for r in reader if (r.get("網域") or "").strip()]
    seen = set()
    merged: list[dict[str, str]] = []
    # Normalise every cell to a stripped string for both the dedupe key and the
    # sort key: a short row parses as None here but as "" after a write/re-read
    # round-trip, which would otherwise defeat the dedupe and crash the sort.
    def _key(r: dict[str, str]) -> tuple[str, ...]:
        return tuple((r.get(c) or "").strip() for c in EXPECTED_HEADER)

    for r in new + old:  # fresh rows win; dedupe on the full row
        key = _key(r)
        if key not in seen:
            seen.add(key)
            merged.append(r)
    merged.sort(key=_key)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=EXPECTED_HEADER)
        writer.writeheader()
        writer.writerows(merged)
    print(f"downloaded registry: {len(new)} live rows, {len(merged)} after "
          f"union with archive -> {path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", default=RAW_DIR, help="Dir of the archived registry CSV")
    ap.add_argument("--out", default=OUT_JSON, help="Output dataset JSON path")
    ap.add_argument("--download", action="store_true",
                    help="Refresh raw/ from data.gov.tw (union with the archive)")
    args = ap.parse_args()
    if args.download:
        _download(args.raw)
    data = build(args.raw)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {args.out}: {len(data['rows'])} rows, "
          f"{len({r[1] for r in data['rows']})} periods, "
          f"{len({r[3] for r in data['rows']})} categories "
          f"(coverage {data['coverage']})")


if __name__ == "__main__":
    main()
