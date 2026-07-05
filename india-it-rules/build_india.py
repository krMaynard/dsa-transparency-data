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

Covered publishers: **Facebook, Instagram** (Meta PDF), **Twitter/X**
(CDN PDF), **Moj, ShareChat** (static HTML), **Roblox** (CDN PDF),
**Google/YouTube** (static GCS-bucket PDF, all SSMI surfaces, Apr 2021 →), and
**Pinterest** (one JSON-in-HTML page, all months). Snap and Telegram are excluded
(JS-rendered numbers / a login-gated bot); Reddit and Quora sit behind Cloudflare;
WhatsApp (signed, expiring fbcdn links) is a planned fast-follow.

Deterministic: builds purely from the archived raw/ files (rows sorted); no
wall-clock. `--download` refreshes raw/ from the curated per-report URLs.
Needs `pdfplumber` (PDF adapters); HTML adapters are pure stdlib.
"""
from __future__ import annotations

import argparse
import calendar
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
_RBLX = "https://cms-media.roblox.com/assets/{slug}.pdf"
_GOOG = ("https://storage.googleapis.com/transparencyreport/report-downloads/"
         "india-intermediary-guidelines_{y}-{m}-1_{y}-{m}-{last}_en_v1.pdf")
_PINT = "https://policy.pinterest.com/en/india-transparency-report"


def _google_months() -> list[tuple[int, int]]:
    """Every month Google has filed, April 2021 → the latest published (bump
    `end` as new reports land; Google publishes on a ~1-month lag)."""
    start, end = (2021, 4), (2026, 5)
    out, y, m = [], *start
    while (y, m) <= end:
        out.append((y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


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
    # Roblox — CDN PDF; covered period parsed from the document. Roblox's asset
    # slugs are inconsistent month-to-month (some gain an `india-`/`-1` token), so
    # the exact slug is curated per report while `roblox-YYYY-MM.pdf` names the
    # archive. First filed for March 2025 (grievance officer appointed early 2025).
    *[(f"roblox-{ym}.pdf", "roblox", _RBLX.format(slug=slug)) for ym, slug in (
        ("2025-03", "march-2025-information-technology-rules-report"),
        ("2025-04", "april-2025-information-technology-rules-report"),
        ("2025-05", "may-2025-information-technology-rules-report-1"),
        ("2025-06", "june-2025-information-technology-rules-report"),
        ("2025-07", "july-2025-information-technology-rules-report"),
        ("2025-08", "august-2025-india-information-technology-rules-report"),
        ("2025-09", "september-2025-india-information-technology-rules-report"),
        ("2025-10", "october-2025-india-information-technology-rules-report"),
        ("2025-11", "november-2025-india-information-technology-rules-report"),
        ("2025-12", "december-2025-india-information-technology-rules-report"),
        # 2026: Feb onward is the redesigned layout (year-month cover header,
        # two-page grievance table, revised taxonomy). May-2026's asset is an
        # opaque CDN key (no templated filename), so refreshing it needs a live
        # viewer-page scrape — the archived raw file is authoritative regardless.
        ("2026-01", "january-2026-india-information-technology-rules-report"),
        ("2026-02", "february-2026-india-information-technology-rules-report"),
        ("2026-03", "march-2026-india-information-technology-rules-report"),
        ("2026-04", "april-2026-india-information-technology-rules-report"),
        ("2026-05", "8fb0de4d-ac0b-4ce9-8925-197e12ecec64"))],
    # Google / YouTube — static, text-embedded PDFs on a public GCS bucket, one
    # per month (Apr 2021 →), covering all of Google's SSMI surfaces. Covered
    # period is parsed from the PDF. The report layout was redesigned c. 2025
    # (percentage lines → 'Category Count' tables); both eras are handled.
    *[(f"google-{y:04d}-{m:02d}.pdf", "google",
       _GOOG.format(y=y, m=m, last=calendar.monthrange(y, m)[1]))
      for y, m in _google_months()],
    # Pinterest — a single page carrying every month's tables, embedded as JSON in
    # the Next.js payload (grievance 'Reports' + proactive 'Voluntary actions', by
    # policy × object type). One archived HTML file; all periods parsed from it.
    ("pinterest-india-transparency.html", "pinterest", _PINT),
]


# ── value parsing ─────────────────────────────────────────────────────────────
def _int(s: str) -> int | None:
    """Plain or Indian-grouped integer ('19,58,124' -> 1958124)."""
    s = (s or "").strip().replace(",", "")
    if not re.fullmatch(r"-?\d+", s):
        return None
    return int(s)


def _int_or_nil(s: str) -> int | None:
    """Like `_int`, but a dash placeholder ('-', '—', '–', 'N/A') reads as an
    explicit 0 rather than a parse miss — Roblox uses a dash for a nil count and
    switched to a literal '0' in later months, so both should land as 0."""
    t = (s or "").strip()
    if t in ("-", "—", "–", "N/A", "n/a", "NA"):
        return 0
    return _int(t)


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
    label = (label or "").replace("\n", " ")
    # Drop private-use-area glyphs (e.g. a bullet Roblox renders as U+E081) and
    # other control chars that some PDFs leak into cell text.
    label = re.sub(r"[\ue000-\uf8ff\x00-\x1f]", " ", label)
    label = re.sub(r"\s+", " ", label).strip()
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


# ── Roblox PDF adapter ────────────────────────────────────────────────────────
def _is_month(name: str) -> bool:
    return (name or "").strip().lower()[:3] in _MONTH3


def _roblox_period(full: str) -> str:
    """Covered month, robust to Roblox's three layouts:
      * 2025 / Jan-2026 body — '…covers the period October 1 - 31 st, 2025';
      * Feb-2026 — a 'Reporting Period: Feb 1, 2026 - Feb 28, 2026' header;
      * Mar-2026 onward — a leading '2026 March' (year-month) cover title.
    The reporting-period start (not the 'Report Date' publication line) is the
    covered month; the month word is validated so a stray 4-digit run can't pose
    as a period."""
    # (regex, month-group, year-group, haystack). Each pattern is evaluated
    # independently: a match whose captured word isn't a real month falls through
    # to the next pattern rather than blocking it.
    head = full[:400]
    for pat, mo_i, yr_i, hay in (
            (r"covers the period\s+([A-Za-z]+)\s+\d+\s*[-–].*?(\d{4})", 1, 2, full),
            (r"Reporting Period:\s+([A-Za-z]+)\s+\d+,?\s+(\d{4})", 1, 2, full),
            (r"\b(\d{4})\s+([A-Za-z]{3,9})\b", 2, 1, head),
            (r"\b([A-Za-z]{3,9})\s+(\d{4})\b", 1, 2, head)):
        m = re.search(pat, hay)
        if m and _is_month(m.group(mo_i)):
            return f"{int(m.group(yr_i)):04d}-{_month_num(m.group(mo_i)):02d}"
    raise SystemExit("Roblox: could not find covered period")


def _parse_roblox(path: str) -> tuple[str, list[list]]:
    """Roblox's monthly report (from March 2025) has two tables: grievance reports
    received + enforcement actions by category (Table 1), and a single global
    proactive-content-moderation total (Table 2, explicitly worldwide, not just
    India). A `-` cell means nil; later months switched to `0`. Both map to 0 so a
    category's time series is gap-free. The Feb-2026 redesign splits Table 1 across
    two pages (each repeating the header) and revised the category taxonomy — both
    handled: every table whose header names 'number of reports' contributes rows."""
    import pdfplumber
    rows: list[list] = []
    with pdfplumber.open(path) as pdf:
        full = "\n".join((p.extract_text() or "") for p in pdf.pages)
        period = _roblox_period(full)
        for page in pdf.pages:
            for tb in page.extract_tables():
                if not tb:
                    continue
                header = " ".join(_clean(c) for c in tb[0]).lower()
                # Table 1: grievances by category — [category, #reports, #actions].
                if "number of reports" in header:
                    for r in tb[1:]:
                        cat = _clean(r[0]) if r and r[0] else ""
                        if not cat or _is_total(cat):
                            continue
                        rep = _int_or_nil(r[1]) if len(r) > 1 else None
                        act = _int_or_nil(r[2]) if len(r) > 2 else None
                        if rep is not None:
                            rows.append(["Roblox", period, "grievances", cat,
                                         "grievances_received", "count", rep])
                        if act is not None:
                            rows.append(["Roblox", period, "grievances", cat,
                                         "enforcement_actions", "count", act])
                # Table 2: single global proactive-moderation total.
                elif header.startswith("category") and "total" in header:
                    for r in tb[1:]:
                        n = _int(r[-1]) if r else None
                        if n is not None:
                            rows.append(["Roblox", period, "content_actioned_proactive",
                                         "", "content_actioned", "count", n])
    return period, rows


# ── Google / YouTube PDF adapter ──────────────────────────────────────────────
# Google reports two figures per month, each broken down by the same fixed set of
# complaint reasons: complaints received from users, and removal actions taken on
# those complaints. Reasons are matched by their known labels, so the parser is
# indifferent to the layout switch (2021-era "Copyright: 26,707 (96.2%)" lines vs
# the 2025-era "Category Count" table "Copyright 19,969").
_GOOG_REASONS = ["Copyright", "Trademark", "Defamation", "Other Legal", "Counterfeit",
                 "Circumvention", "Court Order", "Impersonation", "Graphic Sexual Content"]
_GOOG_RE = re.compile(r"(" + "|".join(re.escape(c) for c in _GOOG_REASONS) + r")\s*:?\s*([\d,]+)")


def _parse_google(path: str) -> tuple[str, list[list]]:
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        full = "\n".join((p.extract_text() or "") for p in pdf.pages)
    mp = (re.search(r"period from\s+([A-Za-z]+)\s+\d+,\s*(\d{4})", full)
          or re.search(r"Complaints received\s+([A-Za-z]+)\s+(\d{4})", full))
    if not mp or not _is_month(mp.group(1)):
        raise SystemExit(f"{path}: could not find covered period")
    period = f"{int(mp.group(2)):04d}-{_month_num(mp.group(1)):02d}"
    # Split at the removals heading: everything before is complaint-reason data,
    # everything after (up to the FAQ / automated-detection section) is removals.
    idx = full.find("Removal actions taken on complaints")
    comp, rem = (full[:idx], full[idx:]) if idx > 0 else (full, "")
    # Truncate the removals block at the next section heading — matched only at the
    # start of a line, so the same phrases appearing inline in the intro prose (e.g.
    # "…as a result of automated detection…") can't cut a short month's data short.
    stop = re.search(r"\n\s*(?:Frequently asked|Removal actions taken as a result of "
                     r"automated detection|Removal actions taken as a result)", rem, re.I)
    if stop:
        rem = rem[:stop.start()]

    def reasons(block: str) -> dict:
        out: dict[str, int] = {}
        for m in _GOOG_RE.finditer(block):
            out.setdefault(m.group(1), int(m.group(2).replace(",", "")))
        return out

    rows: list[list] = []
    for cat, n in reasons(comp).items():
        rows.append(["Google", period, "complaints_received", cat, "complaints", "count", n])
    for cat, n in reasons(rem).items():
        rows.append(["Google", period, "removal_actions", cat, "removal_actions", "count", n])
    return period, rows


# ── Pinterest single-page JSON adapter ────────────────────────────────────────
# The grievance ('Reports') tables say "deactivated"; the proactive ('Voluntary
# actions') tables say "deactivations" for the same measure — fold both to one
# metric so a policy's series isn't split by wording (the `section` dimension
# already distinguishes grievance vs. proactive).
_PINT_ACT = {"deactivated": "deactivated", "deactivations": "deactivated",
             "limited distribution": "limited_distribution"}
_PINT_CELL = re.compile(r"([\d,]+)\s+(deactivated|deactivations|limited distribution)")


def _pint_cell_text(cell: dict) -> str:
    """A table cell's text lives in a nested draft.js-blocks JSON string."""
    raw = cell.get("content")
    if not raw:
        return ""
    try:
        return " ".join(b.get("text", "") for b in json.loads(raw).get("blocks", [])).strip()
    except (ValueError, AttributeError):
        return ""


def _pint_grid(table_json: str) -> list[list[str]]:
    """Pinterest's `pttable` value is a JSON string: a list of row objects, each a
    {columns:[cell,…]}; every cell carries its own row/column index. Rebuild the
    dense grid so a blank cell can't shift the columns."""
    grid: dict[tuple[int, int], str] = {}
    maxr = maxc = 0
    for ro in json.loads(table_json):
        for c in ro.get("columns", []):
            r, cc = c.get("row", 0), c.get("column", 0)
            grid[(r, cc)] = _pint_cell_text(c)
            maxr, maxc = max(maxr, r), max(maxc, cc)
    return [[grid.get((r, cc), "") for cc in range(maxc + 1)] for r in range(maxr + 1)]


def _parse_pinterest(path: str) -> tuple[str, list[list]]:
    """One page holds every month. Each month is an `accordion` whose tabs carry a
    'Reports' (grievance) and a 'Voluntary actions' (proactive) `pttable`, laid out
    as policy × object type (Pins/Boards/Accounts/Comments); each cell is a count
    per action ('4 deactivated 2 limited distribution')."""
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', txt, re.S)
    if not m:
        raise SystemExit(f"{path}: no __NEXT_DATA__ payload")
    try:
        blocks = json.loads(m.group(1))["props"]["pageProps"]["content"]["content"]
    except (ValueError, KeyError, TypeError) as e:
        raise SystemExit(f"{path}: unexpected __NEXT_DATA__ shape: {e}")
    rows: list[list] = []
    periods: set[str] = set()
    for blk in blocks or []:
        if not isinstance(blk, dict) or blk.get("_type") != "accordion":
            continue
        for tab in blk.get("accordionTabs") or []:
            mm = re.match(r"([A-Za-z]+)\s+(\d{4})", tab.get("accordionTabTitle") or "")
            if not mm or not _is_month(mm.group(1)):
                continue
            period = f"{int(mm.group(2)):04d}-{_month_num(mm.group(1)):02d}"
            periods.add(period)
            for cont in tab.get("accordionTabContent") or []:
                section = ""
                for b in cont.get("dataContent") or []:
                    if b.get("_type") == "block" and b.get("style") == "h4":
                        kids = b.get("children") or []
                        label = _clean("".join(c.get("text", "") for c in kids if isinstance(c, dict)))
                        section = label.lower().replace(" ", "_")
                    elif b.get("_type") == "pttable":
                        grid = _pint_grid(b["table"])
                        if not grid:
                            continue
                        header = [_clean(x).lower() for x in grid[0]]
                        if header and header[0] == "policy":
                            objects = header[1:]
                            for r in grid[1:]:
                                cat = _clean(r[0])
                                if not cat:
                                    continue
                                for ci, obj in enumerate(objects):
                                    cell = r[ci + 1] if ci + 1 < len(r) else ""
                                    for n, act in _PINT_CELL.findall(cell):
                                        rows.append(["Pinterest", period, section, cat,
                                                     f"{obj}_{_PINT_ACT[act]}", "count",
                                                     int(n.replace(",", ""))])
                        else:  # a small side table, e.g. "Pending IP form reports"
                            for r in grid:
                                if len(r) >= 2 and re.fullmatch(r"[\d,]+", r[1].strip()):
                                    metric = _clean(r[0]).lower().replace(" ", "_")
                                    rows.append(["Pinterest", period, section, "", metric,
                                                 "count", int(r[1].replace(",", ""))])
    if not rows:
        raise SystemExit(f"{path}: parsed zero Pinterest rows")
    return max(periods), rows


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
        elif kind == "roblox":
            period, r = _parse_roblox(path)
        elif kind == "google":
            period, r = _parse_google(path)
        elif kind == "pinterest":
            period, r = _parse_pinterest(path)
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
                   "https://help.mojapp.in/ + https://help.sharechat.com/ + "
                   "https://about.roblox.com/ + https://transparencyreport.google.com/ + "
                   "https://policy.pinterest.com/",
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
