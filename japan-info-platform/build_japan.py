#!/usr/bin/env python3
"""Build the Japan 情プラ法 (Information Distribution Platform Act) dataset.

Japan's amended Provider Liability Limitation Act ("情報流通プラットフォーム対処法",
in force 1 Apr 2025) requires MIC-designated large providers to publish
implementation-status statistics once a year under Art. 28. Two providers now do:

- **LY Corporation** (LINE / Yahoo! Japan) — its **Media Transparency Report**
  (メディア透明性レポート, FY2024) gives, per service, a quarterly table
  (『四半期ごとの投稿件数・投稿削除件数及び投稿削除割合』) with the FY2024 quarters
  and the annual total: posts, posts removed, and the removal rate. Those five
  tables (archived in ``raw/lycorp-transparency-2024.pdf``) are parsed here.
- **Google (YouTube)** — its **Japan Information Platform Act Transparency
  Report** (26 Jul 2025 – 31 Mar 2026, published May 2026, archived in
  ``raw/youtube-japan-2025h2-{en,ja}.pdf``) gives Japan-specific figures on legal
  removals (requests / items / removals by reason), policy removals (by reason
  and by first-detection source), user flags, channel suspensions, appeals, plus
  headline platform figures. Those tables are transcribed below and each
  breakdown is cross-checked against its stated Total, so a mistranscription
  can't slip through.

Output: ``japan-info-platform.json`` — ``{source, coverage, columns, rows}`` with
columns ``service, period, section, category, metric, unit, value``. LY Corp's
rows sit in section ``posts_activity`` (category ``All``); YouTube's carry a
``section`` per report table and a ``category`` per reason (``Total`` for the
section aggregate). Metrics/units are never comparable across sections, and each
section keeps its ``Total`` beside the breakdown — pin section + category before
aggregating.
"""
from __future__ import annotations

import json
import os
import re

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
LY_PDF = os.path.join(HERE, "raw", "lycorp-transparency-2024.pdf")
OUT = os.path.join(HERE, "japan-info-platform.json")

COLUMNS = ["service", "period", "section", "category", "metric", "unit", "value"]

SOURCE = "https://www.lycorp.co.jp/ja/company/transparencyreport2024.pdf"
LY_COVERAGE = "2024-04..2025-03"  # FY2024 (24年度)

# ── LY Corporation ──────────────────────────────────────────────────────────
# service section (page index, in-report label) -> canonical English name.
SERVICES = [
    (9, "知恵袋", "Yahoo! Chiebukuro"),
    (18, "ファイナンス掲示板", "Yahoo! Finance boards"),
    (26, "オープンチャット", "LINE OpenChat"),
    (36, "VOOM", "LINE VOOM"),
    (45, "ヤフコメ", "Yahoo! News comments"),
]

# FY2024 quarter labels -> coverage window.
QUARTERS = {
    "4-6": "2024-04..2024-06",
    "7-9": "2024-07..2024-09",
    "10-12": "2024-10..2024-12",
    "1-3": "2025-01..2025-03",
}

# Annual-total posts per service, taken from the report's prose summary — used to
# cross-check the parsed 年度合計 row so a table misparse can't slip through.
EXPECT_ANNUAL_POSTS = {
    "Yahoo! Chiebukuro": 66_199_309,
    "Yahoo! Finance boards": 29_415_652,
    "LINE OpenChat": 5_514_828_787,
    "LINE VOOM": 403_331_897,
    "Yahoo! News comments": 113_995_832,
}


def _num(s: str) -> int:
    return int(s.replace(",", ""))


# A cell is "<total> 件（<monthly avg> 件）", optionally with a footnote digit run
# stuck to 件 (e.g. "66,199,309 件10（…"). Parentheses are full-width （） on most
# services but half-width () on OpenChat. We keep the total, drop the avg.
_CELL = r"([\d,]+)\s*件\d*\s*[（(]\s*[\d,]+\s*件\d*\s*[）)]"
_ROW = re.compile(
    r"(4-6|7-9|10-12|1-3|年度合計)\s*(?:月期)?\s*（月平均）\s*"
    + _CELL + r"\s*" + _CELL + r"\s*([\d.]+)\s*[％%]"
)


def parse_service(doc, page_idx: int, label: str, name: str):
    # Some tables split across a page boundary (OpenChat), so read this page and
    # the next, then scope to this service's quarterly table.
    txt = re.sub(r"\s+", " ", doc[page_idx].get_text() + " "
                 + (doc[page_idx + 1].get_text() if page_idx + 1 < doc.page_count else ""))
    m0 = re.search(re.escape(f"[{label}]") + r"\s*四半期ごとの", txt)
    if not m0:
        raise ValueError(f"{name}: quarterly table not found on page {page_idx + 1}")
    chunk = txt[m0.start():m0.start() + 1600]
    rows = []
    for m in _ROW.finditer(chunk):
        qlabel, posts, removed, rate = m.group(1), _num(m.group(2)), _num(m.group(3)), float(m.group(4))
        period = LY_COVERAGE if qlabel == "年度合計" else QUARTERS[qlabel]
        rows.append((name, period, "posts_activity", "All", "posts", "count", posts))
        rows.append((name, period, "posts_activity", "All", "posts_removed", "count", removed))
        rows.append((name, period, "posts_activity", "All", "removal_rate", "percent", rate))
    # sanity: the annual total must be present and match the prose figure
    annual = [r for r in rows if r[1] == LY_COVERAGE and r[4] == "posts"]
    if not annual:
        raise ValueError(f"{name}: no 年度合計 row parsed")
    if name in EXPECT_ANNUAL_POSTS and annual[0][6] != EXPECT_ANNUAL_POSTS[name]:
        raise ValueError(f"{name}: parsed annual posts {annual[0][6]:,} != "
                         f"expected {EXPECT_ANNUAL_POSTS[name]:,}")
    return rows


# ── Google / YouTube ────────────────────────────────────────────────────────
# YouTube's Japan Information Platform Act Transparency Report, 26 Jul 2025 –
# 31 Mar 2026 (raw/youtube-japan-2025h2-{en,ja}.pdf). Transcribed from the report
# tables; each breakdown is validated against its stated Total below.
YT_SERVICE = "YouTube"
YT_PERIOD = "2025-07-26..2026-03-31"

# section, metric, unit, {category: value}, stated Total.
# A 'Total' category row is emitted per section alongside the breakdown.
YT_BREAKDOWNS = [
    # Legal enforcement (Art. 28 (i)(ii)/(iv)).
    ("legal_requests", "requests", "count", {
        "Circumvention": 4, "Counterfeit": 110, "Defamation": 1002,
        "Other Legal": 987, "Privacy": 21, "Trademark": 326}, 2450),
    ("legal_extended_review_notifications", "notifications", "count", {
        "Defamation": 4, "Other Legal": 8}, 12),
    ("legal_items", "items", "count", {
        "Not removed": 3796, "Removed": 289}, 4085),
    ("legal_removals", "items_removed", "count", {
        "Circumvention": 0, "Counterfeit": 3, "Defamation": 155,
        "Other Legal": 13, "Privacy": 1, "Trademark": 117}, 289),
    # Policy enforcement (Art. 28 (iv)).
    ("user_flags", "flags", "count", {
        "Child Abuse": 133852, "Harmful or Dangerous Acts": 683070,
        "Hateful or Abusive": 1470212, "Promotes Terrorism": 236531,
        "Sexual": 672522, "Spam or Misleading": 2861555,
        "Suicide, self-harm, or eating disorders": 116385,
        "Violent or Repulsive": 1519165}, 7693292),
    ("policy_removals", "videos_removed", "count", {
        "Child Safety": 43211, "Harassment and Cyberbullying": 70695,
        "Harmful or Dangerous": 8598, "Hateful or Abusive": 5667,
        "Misinformation": 133, "Nudity or Sexual": 24743, "Other": 215,
        "Promotion of Violence and Violent Extremism": 1774,
        "Spam, Deceptive Practices and Scams": 1007,
        "Violent or Graphic": 6347}, 162390),
    ("policy_detection_source", "videos_removed", "count", {
        "Automated detection": 155131, "Government": 0,
        "Organisation": 1652, "User": 5607}, 162390),
    ("suspensions", "accounts_terminated", "count", {
        "Child Safety": 2026, "Harassment and Cyberbullying": 375,
        "Harmful or Dangerous": 1369, "Hateful or Abusive": 835,
        "Misinformation": 1727, "Multiple policy violations": 110,
        "Nudity or Sexual": 6000, "Other": 26,
        "Promotion of Violence and Violent Extremism": 177,
        "Spam, Deceptive Practices, and Scams": 139405,
        "Violent or Graphic": 53}, 152103),
]

# section, category, metric, unit, value — headline / single-value figures.
YT_SCALARS = [
    ("platform", "All", "monthly_active_users", "count", 106_400_000),
    ("platform", "All", "qualified_reviewers", "count", 293),
    ("platform", "All", "expert_investigation_cases", "count", 6),
    ("platform", "All", "notifications_withheld", "count", 0),
    ("appeals", "All", "appeals", "count", 20_759),
    ("appeals", "All", "reinstatements", "count", 3_090),
]


def build_youtube():
    rows = []
    for section, metric, unit, cats, total in YT_BREAKDOWNS:
        s = sum(cats.values())
        if s != total:
            raise ValueError(f"YouTube {section}: categories sum to {s:,} "
                             f"!= stated Total {total:,}")
        rows.append((YT_SERVICE, YT_PERIOD, section, "Total", metric, unit, total))
        for cat, val in cats.items():
            rows.append((YT_SERVICE, YT_PERIOD, section, cat, metric, unit, val))
    for section, cat, metric, unit, val in YT_SCALARS:
        rows.append((YT_SERVICE, YT_PERIOD, section, cat, metric, unit, val))
    return rows


def main():
    rows = []
    with fitz.open(LY_PDF) as doc:
        for page_idx, label, name in SERVICES:
            rows.extend(parse_service(doc, page_idx, label, name))
    rows.extend(build_youtube())
    data = {
        "source": SOURCE,
        "coverage": LY_COVERAGE,
        "columns": COLUMNS,
        "rows": rows,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {OUT}: {len(rows)} rows")
    from collections import Counter
    print("rows per service:", dict(Counter(r[0] for r in rows)))
    print("YouTube sections:", sorted({r[2] for r in rows if r[0] == YT_SERVICE}))


if __name__ == "__main__":
    main()
