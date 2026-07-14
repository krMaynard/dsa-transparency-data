#!/usr/bin/env python3
"""Build turkey-law5651.json from the platforms' Türkiye Law No. 5651 transparency reports.

Türkiye's **Law No. 5651** (Regulation of Broadcasts via Internet and Prevention
of Crimes Committed through Such Broadcasts), as amended, requires social-network
providers with more than one million daily accesses from Türkiye to publish a
**six-monthly transparency report** (Additional Article 4) on the content-removal
and access-blocking decisions notified to them. Two request streams are reported:

- **Individual applications (Art. 9 / 9-A).** Natural or legal persons in Türkiye
  ask the platform to remove content that violates their personality or privacy
  rights, via a dedicated reporting form.
- **Judicial and administrative authorities (Art. 8 / 8-A).** Removal requests from
  the ICTA (Bilgi Teknolojileri ve İletişim Kurumu), the Consumer-Policy channel
  (Pharmaceuticals & Medical Devices Administration, Board of Advertisement, …),
  and court orders received through the Internet Access Providers Union (BTK/EGM).

Three publishers are parsed:

- **Meta** — Facebook and Instagram (``transparency.meta.com/sr/<slug>``). Five
  half-years, H1 2023 → H1 2025. Reports both request streams; the figures are
  embedded in labelled tables and prose that drift across periods, so each metric
  is read from section-scoped anchors and the parser fails loud if a report yields
  none.
- **X / Twitter** — (``transparency.x.com`` country reports). Nine half-years,
  H1 2021 → H1 2025. X reports only the **individual** stream (Art. 9/9-A), but
  broken down by **issue category** (Abuse, Hateful Conduct, Copyright, …) with a
  request volume and an action rate per category, so its rows carry a `category`
  the Meta rows leave blank. Read from the report's data table (``extract_tables``,
  gathered across page breaks so a table split over two pages isn't truncated).
- **TikTok** — the standalone "Bireysel Talepler Raporu" (Individual Applications
  Report) TikTok files for the BTK under Additional Article 4, published as a
  Turkish-only HTML page (``tiktok.com/safety/tr-TR/transparency/btk-raporu``),
  one collapsible section per half-year (2021 H1 → 2025 H2, no 2021 H2 filing).
  It covers **only** the individual stream (Art. 9/9-A) — its tables report the
  half-year's total applications received (Table 1) plus response and rejection
  breakdowns — so, like X, it carries no `authority_requests` rows. As there is no
  PDF/XLSX, the report data is embedded in the page's server-rendered JSON; the
  builder parses a saved snapshot (``raw/tiktok-btk-raporu.html``) and stores the
  headline ``applications_received`` per half-year.

**Google / YouTube** publishes no standalone Law 5651 statistics file — its
Turkish figures appear only inside the global transparency tool
(``transparencyreport.google.com``) as a country slice — so it slots in as a
further parser only if a stable standalone source appears.

Tidy-long output — one row per measured value:

  platform, period, section, category, metric, unit, value

`platform` is the reporting service (`Facebook` / `Instagram` / `X` / `TikTok`);
`period` is the reporting half-year (`2024 H2`), parsed from the report's stated
coverage window; `section` is `individual_requests` (Art. 9/9-A) or `authority_requests`
(Art. 8/8-A); `category` is the per-issue breakdown dimension (X only; blank for
Meta's report-level totals); `unit` is `count` or `percent` (X action rates).
Requests ≠ reported entities ≠ removed entities, and Meta's per-authority request
counts (`requests_icta`/`_consumer_policy`/`_court_orders`) are parts of
`requests_total` — never sum a total with its parts, or a percent with anything;
pin a `section`, `category` and `metric` before aggregating.

Deterministic parse from the archived sources in ``raw/`` — the Meta/X PDFs and
TikTok's HTML snapshot (rows sorted); no wall-clock. ``--download`` refreshes them
from the publishers. Pure stdlib + pdfplumber.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import urllib.parse

import pdfplumber

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, "raw")
OUT_JSON = os.path.join(HERE, "turkey-law5651.json")

SOURCE = "https://transparency.meta.com/reports/regulatory-transparency-reports/"
COLUMNS = ["platform", "period", "section", "category", "metric", "unit", "value"]

# Meta report slug (on transparency.meta.com/sr/) -> (platform, local raw filename).
# The English PDFs carry the same figures as the Turkish ones; we parse English.
_META_BASE = "https://transparency.meta.com/sr/"
META_SLUGS = {
    f"turkey-report-english-{p}-{per}": (plat, f"meta-{p}-{per}.pdf")
    for p, plat in (("fb", "Facebook"), ("ig", "Instagram"))
    for per in ("jul-23", "jan-24", "jul-24", "jan-25", "jul-25")
}

# X / Twitter Türkiye country reports (on transparency.x.com). local filename ->
# source basename. X's report filenames aren't systematic across periods, so the
# map is explicit; the reporting half-year is derived from each report's own
# coverage window (see `_x_period`), not the filename.
_X_BASE = ("https://transparency.x.com/content/dam/transparency-twitter/"
           "country-reports/turkey/")
X_SLUGS = {
    "x-2021-h1.pdf": "2021-Turkey-June-English.pdf",
    "x-2021-h2.pdf": "2021-Turkey-December-English.pdf",
    "x-2022-h1.pdf": "2022-June-English.pdf",
    "x-2022-h2.pdf": "2022-December-English.pdf",
    "x-2023-h1.pdf": "TRTR-Dec-Jun-English.pdf",
    "x-2023-h2.pdf": "TRTR-Jul-Dec-English.pdf",
    "x-2024-h1.pdf": "XTR-Jan-Jun-2024-English.pdf",
    "x-2024-h2.pdf": "XTR-Jul-Dec-2024-English.pdf",
    "x-2025-h1.pdf": "TRTR-July-2025-Public-Report-English.pdf",
}

# TikTok — the standalone "Bireysel Talepler Raporu" for the BTK (Additional
# Article 4), a Turkish-only HTML page with one collapsible section per half-year.
# There is no PDF/XLSX, so we parse a saved snapshot of the page; the report data
# is embedded in its server-rendered JSON as `"title":"<period>","content":"<HTML
# tables>"`. {Turkish section title -> canonical half-year}. No 2021 H2 filing
# (the first report spans Oct 2020 – May 2021).
TIKTOK_SOURCE = "https://www.tiktok.com/safety/tr-TR/transparency/btk-raporu"
TIKTOK_RAW = "tiktok-btk-raporu.html"
TIKTOK_PERIODS = {
    "Eki 2020 - May 2021": "2021 H1",
    "Oca - Haz 2022": "2022 H1",
    "Tem - Ara 2022": "2022 H2",
    "Oca - Haz 2023": "2023 H1",
    "Tem - Ara 2023": "2023 H2",
    "Oca - Haz 2024": "2024 H1",
    "Tem - Ara 2024": "2024 H2",
    "Oca - Haz 2025": "2025 H1",
    "Tem - Ara 2025": "2025 H2",
}

# Glyphs in these PDFs are positioned individually with no space characters, so a
# font-size-relative word gap is needed or whole lines extract run-together.
_X_TOLERANCE_RATIO = 0.1
_NUM = r"(\d{1,3}(?:[.,]\d{3})+|\d+)"  # a reported integer, possibly thousands-separated

_MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august",
     "september", "october", "november", "december"], start=1)}

# X's issue categories (labels kept verbatim). Space-insensitive lookup collapses
# the cases where table extraction drops the internal space ("HatefulConduct").
_X_CATEGORIES = [
    "Abuse", "Hateful Conduct", "User Impersonation", "Brand Impersonation",
    "Copyright", "Incapacitated users", "Deceased Users",
    "Deceased & Incapacitated users", "Trademark", "Privacy Policy",
    "Private Information", "Right to Privacy",
]
_X_CANON = {c.replace(" ", "").lower(): c for c in _X_CATEGORIES}


def _int(s: str) -> int:
    """`2,724` / `2724` -> 2724."""
    return int(s.replace(",", "").replace(".", ""))


def _pages(path: str) -> list[str]:
    with pdfplumber.open(path) as pdf:
        return [p.extract_text(x_tolerance_ratio=_X_TOLERANCE_RATIO) or ""
                for p in pdf.pages]


# ── Meta (Facebook / Instagram) ─────────────────────────────────────────────

def _meta_period(full_text: str, fname: str) -> str:
    """Derive the reporting half-year from the report's stated coverage window.

    Newer reports say "for a period of six months, from <D> to <D>"; the earliest
    say "Between <D> and <D>". Fails loud if neither window is found.
    """
    # The start date is written either "July 1, 2023" (month-first, older reports)
    # or "1 July 2024" (day-first, newer reports).
    m = re.search(r"(?:period of six months,?\s*from|Between)\s+"
                  r"(?:(?P<mf>[A-Za-z]+)\s+\d{1,2},?|\d{1,2}\s+(?P<df>[A-Za-z]+))"
                  r"\s*(?P<year>\d{4})", full_text)
    if not m:
        raise ValueError(f"{fname}: could not find the coverage window")
    month_name = m.group("mf") or m.group("df")
    start_month = _MONTHS.get(month_name.lower())
    if start_month is None:
        raise ValueError(f"{fname}: unrecognised coverage month {month_name!r}")
    half = "H1" if start_month <= 6 else "H2"
    return f"{m.group('year')} {half}"


def _find(scope: str, patterns: list[str], label: str, fname: str,
          required: bool) -> int | None:
    """First integer matched by any of `patterns` within `scope` (a text slice).
    Raises if `required` and nothing matches (fail-loud on template drift)."""
    for pat in patterns:
        m = re.search(pat, scope, re.I | re.S)
        if m:
            return _int(m.group(1))
    if required:
        raise ValueError(f"{fname}: could not extract {label!r}")
    return None


def _split_sections(full: str) -> tuple[str, str | None]:
    """Split the report into the individual-applications scope and the
    judicial/administrative-authorities scope. The earliest reports (H1 2023)
    covered only the individual stream — the authority stream was added from the
    H2 2023 reports on — so the authority scope is `None` when absent."""
    m = re.search(r"REQUESTS RECEIVED FROM JUDICIAL AND ADMINISTRATIVE"
                  r"|INFORMATION REGARDING (?:REMOVAL )?REQUESTS (?:RECEIVED )?"
                  r"FROM JUDICIAL"
                  r"|removal requests from judicial and administrative", full, re.I)
    if not m:
        return full, None
    return full[:m.start()], full[m.start():]


def _parse_meta(path: str, platform: str) -> list[list]:
    pages = _pages(path)
    full = "\n".join(pages)
    fname = os.path.basename(path)
    period = _meta_period(full, fname)
    indiv, auth = _split_sections(full)

    rows: list[list] = []

    def add(section: str, metric: str, value: int | None):
        if value is not None:
            rows.append([platform, period, section, "", metric, "count", value])

    # ── Individual applications (Art. 9 / 9-A) ──────────────────────────────
    add("individual_requests", "applications_received", _find(
        indiv,
        [r"total of\s+" + _NUM + r"\s+applications through the dedicated",
         r"Total number of applications\s+" + _NUM],
        "applications_received", fname, required=True))
    add("individual_requests", "reported_entities", _find(
        indiv,
        [r"Total number of reported (?:content|entities)\s+" + _NUM],
        "individual reported_entities", fname, required=False))
    add("individual_requests", "removed_entities", _find(
        indiv,
        [r"Total number of removed (?:content|entities)\s+" + _NUM],
        "individual removed_entities", fname, required=False))

    # ── Judicial & administrative authorities (Art. 8 / 8-A) ────────────────
    # Absent from the earliest (H1 2023) reports, which covered only individuals.
    if auth is None:
        return rows
    add("authority_requests", "requests_total", _find(
        auth,
        [r"total of\s+" + _NUM + r"\s+removal requests from judicial",
         r"Total number of requests\s+" + _NUM],
        "requests_total", fname, required=True))
    add("authority_requests", "requests_icta", _find(
        auth,
        [r"Total number of ICTA[^\n]*?requests[^\n]*?\s+" + _NUM,
         _NUM + r"\s+of these requests were received from the Information and Communication"],
        "requests_icta", fname, required=False))
    add("authority_requests", "requests_consumer_policy", _find(
        auth,
        [r"Total number of Consumer Policy[^\n]*?\s+" + _NUM],
        "requests_consumer_policy", fname, required=False))
    add("authority_requests", "requests_court_orders", _find(
        auth,
        [r"Total number of court orders\s+" + _NUM],
        "requests_court_orders", fname, required=False))
    add("authority_requests", "reported_entities", _find(
        auth,
        [r"Total number of reported (?:content|entities)\s+" + _NUM],
        "authority reported_entities", fname, required=False))
    add("authority_requests", "entities_removed", _find(
        auth,
        [r"Total number of (?:content|entities) removed for\s*(?:violating)?[^\n]*?\s+" + _NUM],
        "entities_removed", fname, required=False))
    add("authority_requests", "entities_restricted", _find(
        auth,
        [r"Total number of (?:content|entities) restricted in\s+(?:Turkiye|Türkiye)?\s*" + _NUM],
        "entities_restricted", fname, required=False))

    return rows


# ── X / Twitter ─────────────────────────────────────────────────────────────

_X_PCT = re.compile(r"^\d{1,3}(?:\.\d+)?%$")
_X_NUMCELL = re.compile(r"^\d{1,3}(?:,\d{3})*$|^\d+$")
# Tokens X uses when a category's action rate isn't reported (volume still is).
_X_NA = {"n/a", "n/a%", "na", "-", "—", "–", ""}


def _x_period(full: str, fname: str) -> str:
    """Derive the half-year from X's stated coverage window ("...between <D1> and
    <D2>"), keyed on the END date — X uses shifted Dec–May / Jun–Nov windows in the
    older reports, so the end month is what pins the reporting half."""
    m = re.search(r"between\s+.*?\s+and\s+([A-Za-z]+)\s+\d{1,2},?\s+(\d{4})",
                  full, re.I | re.S)
    if not m:
        raise ValueError(f"{fname}: could not find the coverage window")
    month = _MONTHS.get(m.group(1).lower())
    if month is None:
        raise ValueError(f"{fname}: unrecognised coverage month {m.group(1)!r}")
    half = "H1" if month <= 6 else "H2"
    return f"{m.group(2)} {half}"


def _parse_x(path: str) -> list[list]:
    """X reports the individual (Art. 9/9-A) stream broken down by issue category,
    each with a request volume and an action rate. The data lives in a single table
    ("Issue | Volume of Requests | Action Rate %"); gather rows across every page so
    a table split over a page break isn't silently truncated."""
    fname = os.path.basename(path)
    texts: list[str] = []
    # (canonical issue, volume cell, action-rate cell or None if not reported)
    cells: list[tuple[str, str, str | None]] = []
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            texts.append(p.extract_text(x_tolerance_ratio=_X_TOLERANCE_RATIO) or "")
            for tab in p.extract_tables():
                for r in tab:
                    if not r or len(r) < 3:
                        continue
                    cat = (r[0] or "").replace("\n", " ").strip()
                    vol = (r[1] or "").strip()
                    rate = (r[2] or "").strip()
                    if cat in ("Issue", ""):
                        continue
                    canon = _X_CANON.get(cat.replace(" ", "").lower())
                    vol_ok = bool(_X_NUMCELL.match(vol.replace(" ", "")))
                    rate_pct = bool(_X_PCT.match(rate))
                    if canon is None:
                        # An unknown label that still looks like a data row (a
                        # parseable count with a percent or an explicit
                        # "not-available" rate) is a NEW issue category — fail
                        # loud so it gets curated rather than silently dropped.
                        # Anything else is a non-data table artifact — skip it.
                        if vol_ok and (rate_pct or rate.lower() in _X_NA):
                            raise ValueError(
                                f"{fname}: unrecognised X issue category {cat!r}")
                        continue
                    # Known issue: the request volume is the primary metric and
                    # must parse (fail loud on drift). The action rate is
                    # sometimes reported as "n/a" (e.g. Incapacitated users,
                    # 2024 H1) — keep the volume, drop only the absent rate.
                    if not vol_ok:
                        raise ValueError(
                            f"{fname}: malformed volume {vol!r} for known X "
                            f"issue {cat!r}")
                    cells.append((canon, vol, rate if rate_pct else None))
    period = _x_period("\n".join(texts), fname)
    if not cells:
        raise ValueError(f"{fname}: no issue-breakdown rows found")

    rows: list[list] = []
    seen: set[str] = set()
    for canon, vol, rate in cells:
        if canon in seen:
            raise ValueError(f"{fname}: duplicate X issue category {canon!r}")
        seen.add(canon)
        rows.append(["X", period, "individual_requests", canon,
                     "requests", "count", _int(vol.replace(" ", ""))])
        if rate is not None:
            rows.append(["X", period, "individual_requests", canon,
                         "action_rate", "percent", float(rate.rstrip("%"))])
    return rows


# ── TikTok ──────────────────────────────────────────────────────────────────

def _parse_tiktok(path: str) -> list[list]:
    """Applications received per half-year from TikTok's BTK-report HTML snapshot.

    TikTok reports only the individual stream (Art. 9/9-A). Each half-year's
    ``content`` block holds Turkish HTML tables; Table 1 (``Talep Sayısı``) ends
    in a ``Toplam`` (total) — the applications received. The page's JSON is
    URL-encoded and repeats each block, so we decode, take the longest content per
    period title, strip tags, and read that total. Fails loud if a present section
    yields no total (the page layout drifted)."""
    dec = urllib.parse.unquote(open(path, encoding="utf-8").read())
    rows: list[list] = []
    for title, period in TIKTOK_PERIODS.items():
        best = ""
        for m in re.finditer(r'"title":"' + re.escape(title) + r'","content":"(.*?)","', dec):
            if len(m.group(1)) > len(best):
                best = m.group(1)
        if not best:
            print(f"  (skipping TikTok {period}: '{title}' not in snapshot)")
            continue
        text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", best))).strip()
        m = re.search(r"Talep [Ss]ay[ıi]s[ıi].*?Toplam\s+(\d[\d.,]*)", text)
        if not m:
            raise ValueError(f"TikTok {period}: no Table-1 (applications) total found")
        total = int(m.group(1).replace(".", "").replace(",", ""))
        rows.append(["TikTok", period, "individual_requests", "",
                     "applications_received", "count", total])
    return rows


def build(raw_dir: str) -> dict:
    rows: list[list] = []
    for slug, (platform, fname) in sorted(META_SLUGS.items()):
        path = os.path.join(raw_dir, fname)
        if not os.path.isfile(path):
            print(f"  (skipping {fname}: not in {os.path.relpath(raw_dir, HERE)}/)")
            continue
        n_before = len(rows)
        rows.extend(_parse_meta(path, platform))
        print(f"  {fname}: {len(rows) - n_before} values")
    for fname in sorted(X_SLUGS):
        path = os.path.join(raw_dir, fname)
        if not os.path.isfile(path):
            print(f"  (skipping {fname}: not in {os.path.relpath(raw_dir, HERE)}/)")
            continue
        n_before = len(rows)
        rows.extend(_parse_x(path))
        print(f"  {fname}: {len(rows) - n_before} values")
    tpath = os.path.join(raw_dir, TIKTOK_RAW)
    if os.path.isfile(tpath):
        n_before = len(rows)
        rows.extend(_parse_tiktok(tpath))
        print(f"  {TIKTOK_RAW}: {len(rows) - n_before} values")
    else:
        print(f"  (skipping {TIKTOK_RAW}: not in {os.path.relpath(raw_dir, HERE)}/)")
    rows.sort(key=lambda r: (r[0], r[1], r[2], r[3], r[4]))
    periods = sorted({r[1] for r in rows})
    return {
        "source": SOURCE,
        "coverage": (f"{periods[0]}..{periods[-1]}" if len(periods) > 1
                     else periods[0] if periods else ""),
        "columns": COLUMNS,
        "rows": rows,
    }


def _download(raw_dir: str) -> None:
    import time
    import urllib.request
    os.makedirs(raw_dir, exist_ok=True)

    def fetch(url: str, fname: str) -> None:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            blob = resp.read()
        with open(os.path.join(raw_dir, fname), "wb") as f:
            f.write(blob)
        print(f"downloaded {fname} ({len(blob)} bytes)")
        time.sleep(0.5)

    for slug, (_platform, fname) in sorted(META_SLUGS.items()):
        fetch(_META_BASE + slug, fname)
    for fname, src in sorted(X_SLUGS.items()):
        fetch(_X_BASE + src, fname)
    fetch(TIKTOK_SOURCE, TIKTOK_RAW)  # the Türkiye BTK report (one HTML page)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raw", default=RAW_DIR, help="Dir of the archived report PDFs")
    ap.add_argument("--out", default=OUT_JSON, help="Output dataset JSON path")
    ap.add_argument("--download", action="store_true",
                    help="Refresh the raw PDFs from the publishers first")
    args = ap.parse_args()

    if args.download:
        _download(args.raw)

    data = build(args.raw)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    rows = data["rows"]
    print(f"wrote {args.out}: {len(rows)} values across "
          f"{len({r[0] for r in rows})} platforms, "
          f"{len({r[1] for r in rows})} periods (coverage {data['coverage']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
