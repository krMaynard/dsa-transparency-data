#!/usr/bin/env python3
"""Build india-it-rules.json from publishers' monthly India IT-Rules-2021 reports.

India's Information Technology (Intermediary Guidelines and Digital Media Ethics
Code) Rules, 2021 require "significant social media intermediaries" (>5M users)
to publish a MONTHLY compliance report: content actioned proactively (by policy
area, with a proactive-detection rate), user grievances received / actioned (by
category), accounts actioned, Grievance Appellate Committee (GAC) orders, and
law-enforcement / takedown actions.

Each publisher files in its own layout, so this extractor has a small per-publisher
adapter, all feeding one **tidy-long** table — one row per measured value:

  platform, period, section, category, metric, unit, value

`unit` is `count` (exact integer), `approx_count` (Meta's abbreviated "2.3M"/
"448.6K" proactive figures — the company's own rounded best-estimates, not exact),
or `percent` (proactive-detection rates, complaint-split percentages). Never sum
across units, and pin a `section` before aggregating (metrics aren't comparable
across sections) — the same discipline as the Snap/GitHub tidy-long tables.

Covered publishers (v1): **Facebook, Instagram** (Meta PDF), **Twitter/X**
(CDN PDF), **Moj, ShareChat** (static HTML). Google/YouTube, Snap and Telegram
are excluded — their reports are browser-/account-gated (JS-rendered numbers or
a login-gated bot) and aren't fetchable headless. WhatsApp (signed, expiring
fbcdn links) is a planned fast-follow.

Deterministic: builds purely from the archived raw/ files (rows sorted); no
wall-clock. `--download` refreshes raw/ from the curated per-report URLs.
Needs `pdfplumber` (PDF adapters); HTML adapters are pure stdlib.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, "raw")
OUT_JSON = os.path.join(HERE, "india-it-rules.json")

COLUMNS = ["platform", "period", "section", "category", "metric", "unit", "value"]

_MONTH3 = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct",
     "nov", "dec"], start=1)}


def _month_num(name: str) -> int:
    """Month number from a full name or any abbreviation ('September', 'Sept',
    'Sep' all -> 9), matched on the first three letters."""
    key = (name or "").strip().lower()[:3]
    if key not in _MONTH3:
        raise SystemExit(f"unrecognised month: {name!r}")
    return _MONTH3[key]

# ── Curated source registry ──────────────────────────────────────────────────
# Each entry: (raw filename, kind, url). `period` is derived per-adapter (parsed
# from the document for the PDFs, from the month token for the HTML pages), so a
# report can never be mislabelled by a filename typo.
_TW = ("https://transparency.twitter.com/content/dam/transparency-twitter/"
       "country-reports/india/India-ITR-{m}-{y}.pdf")
_META = "https://transparency.meta.com/sr/india-monthly-report-{slug}"

SOURCES: list[tuple[str, str, str]] = [
    # Meta (Facebook + Instagram) — slug = publication date (last day of the
    # month after the covered month). Covered period is parsed from the PDF.
    *[(f"meta-{slug}.pdf", "meta", _META.format(slug=slug)) for slug in (
        "aug31-2022", "oct31-2022", "jan31-2023", "mar31-2023",
        "may31-2023", "jul31-2023", "aug31-2023", "oct31-2023")],
    # Twitter/X — covered window parsed from the PDF (offset 26th-25th window).
    *[(f"twitter-{m}-{y}.pdf", "twitter", _TW.format(m=m, y=y)) for m, y in (
        ("Jul", 2021), ("Aug", 2021), ("Sep", 2021), ("Oct", 2021),
        ("Nov", 2021), ("Dec", 2021), ("Jan", 2022), ("Apr", 2022),
        ("Jul", 2022), ("Oct", 2022), ("Nov", 2022))],
    # Moj + ShareChat — static HTML; period derived from the month token.
    # NB: Moj/ShareChat redesigned their report layout in mid-2022 (extra tables,
    # a leading 'Ban duration' header cell) and later moved Moj's pages to a
    # JS-rendered shell; v1 covers the consistent 2021–early-2022 static layout.
    *[(f"moj-{my}.html", "moj", f"https://help.mojapp.in/transparency-report/{my}/")
      for my in ("june-2021", "july-2021", "october-2021", "january-2022",
                 "april-2022")],
    *[(f"sharechat-{my}.html", "sharechat",
       f"https://help.sharechat.com/transparency-report/{my}/")
      for my in ("july-2021", "october-2021", "january-2022", "february-2022",
                 "march-2022", "april-2022")],
]


# ── value parsing ─────────────────────────────────────────────────────────────
def _int(s: str) -> int | None:
    """Plain or Indian-grouped integer ('19,58,124' -> 1958124)."""
    s = (s or "").strip().replace(",", "")
    if not re.fullmatch(r"-?\d+", s):
        return None
    return int(s)


def _approx(s: str) -> float | None:
    """Meta's abbreviated magnitude: '2.3M' -> 2_300_000, '448.6K' -> 448_600,
    '99' -> 99. Returns a float (these are rounded best-estimates, unit
    'approx_count'); an int-valued result is normalised to int by the caller."""
    s = (s or "").strip().replace(",", "")
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([MK]?)", s, re.I)
    if not m:
        return None
    val = float(m.group(1)) * {"": 1, "K": 1e3, "M": 1e6}[m.group(2).upper()]
    return val


def _pct(s: str) -> float | None:
    s = (s or "").strip().rstrip("%")
    try:
        return float(s)
    except ValueError:
        return None


def _norm_num(v: float) -> float | int:
    return int(v) if float(v).is_integer() else v


def _clean(label: str) -> str:
    """Tidy a category label: de-concatenate is impossible post-hoc, but strip
    trailing footnote digits ('Illegal Activities3' -> 'Illegal Activities'),
    collapse whitespace/newlines, and drop a leading 'N.' index."""
    label = re.sub(r"\s+", " ", (label or "").replace("\n", " ")).strip()
    label = re.sub(r"^\d+\.\s*", "", label)          # leading "1." index
    label = re.sub(r"(?<=[a-z])\d+$", "", label)     # trailing footnote digit
    return label.strip()


def _is_total(label: str) -> bool:
    return _clean(label).lower() in ("total", "grand total", "")


# ── Meta (Facebook + Instagram) PDF adapter ──────────────────────────────────
def _parse_meta(path: str) -> tuple[str, list[list]]:
    import pdfplumber
    rows: list[list] = []
    with pdfplumber.open(path) as pdf:
        full = "\n".join((p.extract_text() or "") for p in pdf.pages)
        # Covered period: "...from 1st June, 2023 to 30th June, 2023".
        mper = re.search(r"from\s+\d+\w*\s+([A-Za-z]+),?\s+(\d{4})\s+to", full)
        if not mper:
            raise SystemExit(f"{path}: could not find covered period")
        period = f"{int(mper.group(2)):04d}-{_month_num(mper.group(1)):02d}"
        # Walk pages in order, tracking the most recent "Table N: <caption>" so
        # each extracted table is classified by its caption (robust to page drift).
        caption = ""
        for page in pdf.pages:
            text = page.extract_text() or ""
            caps = re.findall(r"Table\s*\d+\s*:\s*[^\n]+", text)
            tables = page.extract_tables()
            ci = 0
            for tb in tables:
                if not tb:
                    continue
                header = [(_clean(c)) for c in tb[0]]
                # Advance the caption pointer as tables are consumed on the page.
                if ci < len(caps):
                    caption = caps[ci]
                ci += 1
                low = caption.lower()
                # Meta files FB before IG in a stable table order: 1=FB content,
                # 2=IG content, 3/4=FB grievances (received/tools), 5/6=IG
                # grievances, 7=GAC. The grievance captions don't name the
                # surface, so platform is keyed on the table number; content
                # captions name it explicitly and take precedence.
                mnum = re.search(r"Table\s*(\d+)", caption)
                tnum = int(mnum.group(1)) if mnum else 0
                if "instagram" in low:
                    surface = "Instagram"
                elif "facebook" in low:
                    surface = "Facebook"
                else:
                    surface = "Instagram" if tnum in (2, 5, 6) else "Facebook"
                # Content-actioned + proactive-rate tables (Tables 1 & 2).
                if "proactiverate" in "".join(header).lower() or "proactive" in low:
                    platform = surface
                    for r in tb[1:]:
                        if len(r) < 3 or _is_total(r[0]):
                            continue
                        cat = _clean(r[0])
                        ca, pr = _approx(r[1]), _pct(r[2])
                        if ca is not None:
                            rows.append([platform, period, "content_actioned_proactive",
                                         cat, "content_actioned", "approx_count", _norm_num(ca)])
                        if pr is not None:
                            rows.append([platform, period, "content_actioned_proactive",
                                         cat, "proactive_rate", "percent", _norm_num(pr)])
                # Grievance category tables (Tables 3-6).
                elif "numberofreports" in "".join(header).lower() or "reports received" in low \
                        or "tools were provided" in low or "tools provided" in low:
                    platform = surface
                    section = ("grievances_tools_provided" if "tools" in low
                               else "grievances_received")
                    for r in tb[1:]:
                        if len(r) < 2 or _is_total(r[0]):
                            continue
                        n = _int(r[1])
                        if n is not None:
                            rows.append([platform, period, section, _clean(r[0]),
                                         "reports", "count", n])
                # GAC orders (Table 7) — Meta-level (covers both surfaces).
                elif "orderscompliedwith" in "".join(header).lower() or "appellate" in low:
                    for r in tb[1:] if len(tb) > 1 else []:
                        recv, comp = _int(r[0]) if len(r) > 0 else None, \
                            _int(r[1]) if len(r) > 1 else None
                        if recv is not None:
                            rows.append(["Meta", period, "gac_orders", "",
                                         "orders_received", "count", recv])
                        if comp is not None:
                            rows.append(["Meta", period, "gac_orders", "",
                                         "orders_complied", "count", comp])
    return period, rows


# ── Twitter / X PDF adapter ───────────────────────────────────────────────────
def _parse_twitter(path: str) -> tuple[str, list[list]]:
    import pdfplumber
    rows: list[list] = []
    with pdfplumber.open(path) as pdf:
        full = "\n".join((p.extract_text() or "") for p in pdf.pages)
        # Covered window end: "...through to October 25, 2022" — label by end month.
        mper = re.search(r"through to\s+([A-Za-z]+)\s+\d+,?\s+(\d{4})", full)
        if not mper:
            mper = re.search(r"between\s+([A-Za-z]+)\s+\d+,?\s+(\d{4})", full)
        if not mper:
            raise SystemExit(f"{path}: could not find covered period")
        period = f"{int(mper.group(2)):04d}-{_month_num(mper.group(1)):02d}"
        for page in pdf.pages:
            for tb in page.extract_tables():
                if not tb:
                    continue
                header = " ".join(_clean(c) for c in tb[0]).lower()
                body = tb
                # Grievances by issue type: [issue, #grievances, #URLs actioned].
                if "grievances" in header and "url" in header:
                    body = tb[1:]
                accounts_tbl = ("accounts suspended" in header)
                if accounts_tbl:
                    body = tb[1:]  # drop the header row explicitly
                for r in body:
                    cat = _clean(r[0]) if r else ""
                    if not cat or _is_total(cat):
                        continue
                    if accounts_tbl:
                        n = _int(r[1]) if len(r) > 1 else None
                        if n is not None:
                            rows.append(["Twitter", period, "accounts_actioned", cat,
                                         "accounts_suspended", "count", n])
                    else:
                        # Default: the grievances table (header row may be absent
                        # on continuation pages, so rows flow straight through).
                        g = _int(r[1]) if len(r) > 1 else None
                        u = _int(r[2]) if len(r) > 2 else None
                        if g is not None:
                            rows.append(["Twitter", period, "grievances", cat,
                                         "grievances_received", "count", g])
                        if u is not None:
                            rows.append(["Twitter", period, "grievances", cat,
                                         "urls_actioned", "count", u])
    return period, rows


# ── Moj / ShareChat static-HTML adapter ──────────────────────────────────────
def _html_tables(path: str) -> list[list[list[str]]]:
    """Parse each <table> row-by-row, preserving empty cells so the grid stays
    intact — a flattened, empty-filtered list would silently shift every later
    cell into the wrong column if a value were ever blank."""
    txt = open(path, encoding="utf-8").read()
    out: list[list[list[str]]] = []
    for tb in re.findall(r"<table[\s\S]*?</table>", txt, re.I):
        rows = []
        for tr in re.findall(r"<tr[\s\S]*?</tr>", tb, re.I):
            cells = re.findall(r"<t[dh][^>]*>([\s\S]*?)</t[dh]>", tr, re.I)
            cells = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", c))).strip()
                     for c in cells]
            rows.append(cells)
        if rows:
            out.append(rows)
    return out


def _parse_html_report(path: str, platform: str) -> tuple[str, list[list]]:
    # Period from the month token in the filename (moj-june-2021.html).
    mtok = re.search(r"-([a-z]+)-(\d{4})\.html$", os.path.basename(path), re.I)
    if not mtok:
        raise SystemExit(f"{path}: cannot derive period from filename")
    period = f"{int(mtok.group(2)):04d}-{_month_num(mtok.group(1)):02d}"
    rows: list[list] = []
    le_metric = {"law enforcement requests received": "requests_received",
                 "requests where user data was provided": "data_provided"}
    for tb in _html_tables(path):
        joined = " ".join(c for row in tb for c in row).lower()
        # Law-enforcement: a label row followed by a value row (column-aligned).
        if "law enforcement requests received" in joined and len(tb) >= 2:
            for lab, val in zip(tb[0], tb[1]):
                n = _int(val)
                if n is None:
                    continue
                key = lab.lower()
                metric = next((m for k, m in le_metric.items() if k in key), None)
                if metric is None and "takedown" in key:
                    metric = "takedown_action"
                if metric:
                    rows.append([platform, period, "law_enforcement", "", metric, "count", n])
        # Total complaints: a single label + value.
        elif "total number of user complaints received" in joined:
            for row in tb:
                got = next((n for c in row if (n := _int(c)) is not None), None)
                if got is not None:
                    rows.append([platform, period, "complaints", "",
                                 "complaints_received", "count", got])
                    break
        # Ban matrix: header ['', 'UGC ban', …]; each later row is [duration, v…].
        elif any("ban" in c.lower() for c in tb[0]):
            types = [c.lower().replace(" ban", "").strip().replace(" ", "_") + "_ban"
                     for c in tb[0][1:] if c]
            for row in tb[1:]:
                if not row:
                    continue
                duration = row[0]
                for j, t in enumerate(types):
                    if j + 1 < len(row) and (n := _int(row[j + 1])) is not None:
                        rows.append([platform, period, "account_bans", duration,
                                     t, "count", n])
    return period, rows


# ── driver ────────────────────────────────────────────────────────────────────
def _canon_categories(rows: list[list]) -> None:
    """pdfplumber preserves word spacing in some Meta PDFs and concatenates it in
    others, so one policy area can arrive as both 'Adult Nudity and Sexual
    Activity' and 'AdultNudityandSexualActivity' across months — which would
    fragment a cross-month query. Variants differ only in whitespace, so group by
    the space-stripped key and rewrite every row to the most-readable (most
    spaced) variant. Deterministic; a no-op for already-consistent labels."""
    from collections import defaultdict
    groups: dict[str, list[str]] = defaultdict(list)
    for r in rows:
        groups[re.sub(r"[^a-z0-9]", "", r[3].lower())].append(r[3])
    canon = {k: sorted(set(v), key=lambda s: (-s.count(" "), -len(s), s))[0]
             for k, v in groups.items()}
    for r in rows:
        r[3] = canon[re.sub(r"[^a-z0-9]", "", r[3].lower())]


def build(raw_dir: str) -> dict:
    rows: list[list] = []
    periods: set[str] = set()
    for fname, kind, _url in SOURCES:
        path = os.path.join(raw_dir, fname)
        if not os.path.isfile(path):
            raise SystemExit(f"missing expected report: {path}")
        if kind == "meta":
            period, r = _parse_meta(path)
        elif kind == "twitter":
            period, r = _parse_twitter(path)
        elif kind in ("moj", "sharechat"):
            platform = "Moj" if kind == "moj" else "ShareChat"
            period, r = _parse_html_report(path, platform)
        else:
            raise SystemExit(f"unknown kind {kind!r}")
        if not r:
            raise SystemExit(f"{fname}: parsed zero rows (format drift?)")
        periods.add(period)
        rows.extend(r)
    _canon_categories(rows)
    rows.sort(key=lambda x: (x[0], x[1], x[2], x[3], x[4], x[5]))
    return {
        "source": "https://www.meta.com/ + https://transparency.twitter.com/ + "
                   "https://help.mojapp.in/ + https://help.sharechat.com/",
        "coverage": max(periods) if periods else None,
        "columns": COLUMNS,
        "rows": rows,
    }


def _download(raw_dir: str) -> None:
    os.makedirs(raw_dir, exist_ok=True)
    for fname, _kind, url in SOURCES:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as resp, \
                open(os.path.join(raw_dir, fname), "wb") as f:
            f.write(resp.read())
    print(f"downloaded {len(SOURCES)} reports -> {raw_dir}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", default=RAW_DIR, help="Dir of archived raw reports")
    ap.add_argument("--out", default=OUT_JSON, help="Output dataset JSON path")
    ap.add_argument("--download", action="store_true",
                    help="Refresh raw/ from the curated per-report URLs first")
    args = ap.parse_args()
    if args.download:
        _download(args.raw)
    data = build(args.raw)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        f.write("\n")
    n_plat = len({r[0] for r in data["rows"]})
    print(f"wrote {args.out}: {len(data['rows'])} rows, {n_plat} platforms, "
          f"{len({r[1] for r in data['rows']})} periods (coverage {data['coverage']})")


if __name__ == "__main__":
    main()
