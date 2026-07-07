#!/usr/bin/env python3
"""Build the Japan 情プラ法 (Information Distribution Platform Act) dataset.

Source: **LY Corporation's Media Transparency Report** (メディア透明性レポート,
FY2024) — the one designated provider that currently publishes the
implementation-status *statistics* the amended Provider Liability Limitation Act
("情報流通プラットフォーム対処法", in force 1 Apr 2025) requires (Art. 28). The
other designated providers (Google, Meta, TikTok, X) so far publish only the
qualitative Art. 21 criteria/window pages, so this dataset is LY-Corp-only for
now — see README.md.

The report gives, per service, a quarterly table
(『四半期ごとの投稿件数・投稿削除件数及び投稿削除割合』) with the FY2024 quarters
and the annual total: posts, posts removed, and the removal rate. Those five
tables (one per service, archived verbatim in raw/) are parsed here.

Output: ``japan-info-platform.json`` — ``{source, coverage, columns, rows}`` with
columns ``service, period, metric, unit, value``.
"""
from __future__ import annotations

import json
import os
import re

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(HERE, "raw", "lycorp-transparency-2024.pdf")
OUT = os.path.join(HERE, "japan-info-platform.json")

SOURCE = "https://www.lycorp.co.jp/ja/company/transparencyreport2024.pdf"
COVERAGE = "2024-04..2025-03"  # FY2024 (24年度)

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
        period = COVERAGE if qlabel == "年度合計" else QUARTERS[qlabel]
        rows.append((name, period, "posts", "count", posts))
        rows.append((name, period, "posts_removed", "count", removed))
        rows.append((name, period, "removal_rate", "percent", rate))
    # sanity: the annual total must be present and match the prose figure
    annual = [r for r in rows if r[1] == COVERAGE and r[2] == "posts"]
    if not annual:
        raise ValueError(f"{name}: no 年度合計 row parsed")
    if name in EXPECT_ANNUAL_POSTS and annual[0][4] != EXPECT_ANNUAL_POSTS[name]:
        raise ValueError(f"{name}: parsed annual posts {annual[0][4]:,} != "
                         f"expected {EXPECT_ANNUAL_POSTS[name]:,}")
    return rows


def main():
    rows = []
    with fitz.open(PDF) as doc:
        for page_idx, label, name in SERVICES:
            rows.extend(parse_service(doc, page_idx, label, name))
    data = {
        "source": SOURCE,
        "coverage": COVERAGE,
        "columns": ["service", "period", "metric", "unit", "value"],
        "rows": rows,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {OUT}: {len(rows)} rows")
    from collections import Counter
    print("rows per service:", dict(Counter(r[0] for r in rows)))


if __name__ == "__main__":
    main()
