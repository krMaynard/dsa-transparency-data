#!/usr/bin/env python3
"""Build the China 12321 report-handling dataset.

The **12321 网络不良与垃圾信息举报受理中心** (12321 Internet Bad & Spam
Information Reporting Center), run by the Internet Society of China (中国互联网协会)
under the Ministry of Industry and Information Technology (MIIT), was China's
national hotline for reporting telecom/internet **nuisance and spam** — junk &
illegal SMS, harassment/fraud calls, malicious apps, bad websites and spam
email. From 2016-09 to 2019-02 it published a monthly bulletin,
"12321 举报中心工作情况月报 / 12321举报受理情况播报", tallying how many public
reports it received that month per category. The series was **discontinued after
Feb 2019** (12321 kept operating, folded into the MIIT nuisance-call system).

This is the telecom-spam complement to the CAC/12377 content-reporting series
(``china-ciirc``): a different agency (MIIT/ISC, not CAC), a different remit
(spam & nuisance, not "illegal & harmful information"), and a distinct — if now
frozen — multi-year monthly series.

``build_12321.py --download`` scrapes the report listing (``/report``) and each
monthly PDF from ``www.12321.cn``, archiving the raw PDFs under ``raw/``;
``build()`` then parses the archived PDFs **offline** (deterministic). Early
(2016) bulletins state raw integer counts (件次); from 2017 the figures are
rounded to 万 (ten-thousands) — stored as absolute counts, with ``unit`` marking
the 万-rounded values ``approx_count``.

Output ``china-12321.json``, tidy-long:
  publisher, period, section, category, metric, unit, value

Each category is the count of reports **received** that month. The three SMS
rows overlap — ``sms`` is the monthly total and ``sms_spam`` (垃圾类) +
``sms_illegal`` (涉嫌违法类) are its two disjoint parts — so summing them
double-counts; the build cross-checks that ``sms_spam + sms_illegal`` reconciles
to ``sms`` within 万-rounding slack and raises on a real mismatch.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import urllib.error
import urllib.request

try:
    import fitz  # PyMuPDF
except ImportError:  # pragma: no cover
    fitz = None

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT_JSON = os.path.join(HERE, "china-12321.json")
BASE = "https://www.12321.cn"

COLUMNS = ["publisher", "period", "section", "category", "metric", "unit", "value"]
PUBLISHER = "12321-ISC"
SECTION = "reports_received"
METRIC = "reports_received"

_UA = {"User-Agent": "Mozilla/5.0 (transparency-report-archiver)"}

# Running page header/footer injected mid-text once whitespace is squashed, e.g.
# "…违法类的2017年第2期总第101期5/11共0.3万件次" — strip it so anchors reach figures.
_HEADER = re.compile(r"20\d\d年第\d+期总第\d+期\d*/?\d*")


def _fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers=_UA)
    with urllib.request.urlopen(req, timeout=90) as response:
        return response.read()


def _fetch_html(url: str) -> str:
    raw = _fetch(url)
    m = re.search(rb"charset=[\"']?([\w-]+)", raw[:3000])
    enc = m.group(1).decode() if m else "utf-8"
    return raw.decode(enc, errors="replace")


# ── scrape (archives raw PDFs; not needed for a normal offline build) ──────────
_LINK_RE = re.compile(r'href="(/Uploads/pdf/[^"]+\.pdf)"[^>]*>(?:<[^>]+>)*\s*([^<]{0,60})')
_PER_RE = re.compile(r"(20\d\d)年(\d+)(?:-(\d+))?月12321举报受理情况播报")


def download(raw_dir: str) -> int:
    os.makedirs(raw_dir, exist_ok=True)
    found: dict[str, str] = {}
    for page in (f"{BASE}/report", f"{BASE}/report?p=2"):
        for path, title in _LINK_RE.findall(_fetch_html(page)):
            m = _PER_RE.search(title.strip())
            if not m:
                continue
            y, m1, m2 = m.group(1), int(m.group(2)), m.group(3)
            key = f"{y}-{m1:02d}" + (f"_{int(m2):02d}" if m2 else "")
            found[key] = path
    got = 0
    for key, path in sorted(found.items()):
        out = os.path.join(raw_dir, f"12321-{key}.pdf")
        if os.path.exists(out) and os.path.getsize(out) > 1000:
            continue
        try:
            with open(out, "wb") as f:
                f.write(_fetch(BASE + path))
            got += 1
        except urllib.error.HTTPError as e:  # a couple of listing links 404 at source
            print(f"  ! {key}: source link {path} returned {e.code}, skipping")
            if os.path.exists(out):
                os.remove(out)
    return got


# ── parse (offline, deterministic) ────────────────────────────────────────────
def _val(numstr: str, wan: str | None) -> tuple[int, str]:
    """(number, 万-or-None) → (absolute count, unit). 万 figures are rounded."""
    if wan:
        return round(float(numstr) * 10000), "approx_count"
    return round(float(numstr)), "count"


# Each category: an anchor bridging (non-greedy, within one sentence) to its
# first "…N(万)?件" received figure. Keyed off stable section wording.
_APP = re.compile(r"APP应用举报情况[^。]{0,40}?举报[^。]{0,20}?([\d.]+)(万)?余?件")
_SMS_TOTAL = re.compile(r"共收到举报短信([\d.]+)(万)?余?件")
_SMS_SPAM = re.compile(r"(?:内容)?为?垃圾类的(?:短信息举报)?(?:约)?([\d.]+)(万)?余?件")
_SMS_ILLEGAL = re.compile(r"涉嫌违法类的?(?:共|短信息举报约?)?([\d.]+)(万)?余?件")
_CALLS = re.compile(r"骚扰电话[^。]{0,30}?([\d.]+)(万)?余?件")
_SITES = re.compile(r"不良网站[^。]{0,30}?([\d.]+)(万)?余?件")
_FRAUD = re.compile(r"通讯信息诈骗(?:约)?([\d.]+)(万)?余?件")
_EMAIL = re.compile(r"垃圾邮件的?举报(?:约)?([\d.]+)(万)?余?件")

# category → (compiled anchor, required?). Only sms + calls + sites + app are
# present every month; fraud_comms & spam_email are 2016-era only.
_CATS = [
    ("app", _APP, False),
    ("sms", _SMS_TOTAL, True),
    ("sms_spam", _SMS_SPAM, False),
    ("sms_illegal", _SMS_ILLEGAL, False),
    ("harassment_calls", _CALLS, True),
    ("bad_websites", _SITES, False),
    ("fraud_comms", _FRAUD, False),
    ("spam_email", _EMAIL, False),
]


def _first_body_match(pat: re.Pattern, text: str):
    """First match whose span isn't a table-of-contents entry (dotted leader)."""
    for m in pat.finditer(text):
        if "……" in m.group(0) or "．" in m.group(0):
            continue
        return m
    return None


def _parse_pdf(path: str) -> list[list]:
    if fitz is None:  # pragma: no cover
        raise SystemExit("PyMuPDF (fitz) is required to parse the 12321 PDFs")
    period = re.search(r"12321-(.+)\.pdf$", path).group(1)
    if "_" in period:  # combined-month bulletin, e.g. 2017-05_06 → 2017-05..2017-06
        y, m1, m2 = re.match(r"(20\d\d)-(\d\d)_(\d\d)", period).groups()
        period = f"{y}-{m1}..{y}-{m2}"
    with fitz.open(path) as doc:
        raw = "".join(page.get_text() for page in doc)
    text = _HEADER.sub("", re.sub(r"\s+", "", raw))

    figs: dict[str, tuple[int, str]] = {}
    for cat, pat, required in _CATS:
        m = _first_body_match(pat, text)
        if m:
            figs[cat] = _val(m.group(1), m.group(2))
        elif required:
            raise SystemExit(f"{os.path.basename(path)}: no '{cat}' figure found")

    # Cross-check: the two SMS parts reconcile with the SMS total (each rounded
    # independently to 0.1万 in later years, so allow rounding slack).
    if {"sms", "sms_spam", "sms_illegal"} <= figs.keys():
        total = figs["sms"][0]
        parts = figs["sms_spam"][0] + figs["sms_illegal"][0]
        if abs(total - parts) > max(1500, total * 0.06):
            raise SystemExit(
                f"{os.path.basename(path)}: SMS parts {parts} != total {total}")

    return [
        [PUBLISHER, period, SECTION, cat, METRIC, unit, value]
        for cat, (value, unit) in figs.items()
    ]


def build(raw_dir: str) -> dict:
    files = sorted(glob.glob(os.path.join(raw_dir, "12321-*.pdf")))
    if not files:
        raise SystemExit(f"no archived PDFs under {raw_dir} — run --download first")
    rows: list[list] = []
    for path in files:
        rows += _parse_pdf(path)
    order = {cat: i for i, (cat, _, _) in enumerate(_CATS)}
    rows.sort(key=lambda r: (r[1], order.get(r[3], 99)))
    return {
        "source": "China 12321 Internet Bad & Spam Information Reporting Center "
                  "(Internet Society of China / MIIT) — monthly report-handling "
                  "bulletins, 2016-09 … 2019-02 (www.12321.cn)",
        "coverage": max(r[1] for r in rows),
        "columns": COLUMNS,
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raw", default=RAW)
    ap.add_argument("--out", default=OUT_JSON)
    ap.add_argument("--download", action="store_true",
                    help="re-scrape www.12321.cn into raw/ before building")
    args = ap.parse_args()
    if args.download:
        n = download(args.raw)
        print(f"downloaded {n} monthly bulletins into {args.raw}")
    data = build(args.raw)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    months = sorted({r[1] for r in data["rows"]})
    print(f"wrote {args.out}: {len(data['rows'])} rows across {len(months)} "
          f"bulletins ({months[0]} … {months[-1]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
