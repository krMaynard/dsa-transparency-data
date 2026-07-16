#!/usr/bin/env python3
"""Build the OVHcloud EU DSA transparency dataset.

**OVHcloud** (OVH Groupe SAS, Roubaix, France) is Europe's largest cloud/hosting
provider — ~450,000 servers across 43 data centres, 1.6 million customers. As a
hosting **intermediary** under the EU Digital Services Act it publishes an annual
transparency report (a narrative PDF, not the Article 15/24 harmonised template),
covering **17 February 2024 – 31 December 2024**. Because OVHcloud is an
infrastructure host — it cannot see or selectively remove customer content — its
report has no content-moderation removals; instead it discloses (i) authority
**orders** received per member state (Art. 9/10/15) and (ii) the **notices** of
allegedly illegal content it received via its Art. 16 abuse form, by category,
with median action time and share handled automatically.

``build_ovhcloud.py --download`` fetches the raw PDF from corporate.ovhcloud.com
into ``raw/``; ``build()`` then parses the archived PDF **offline**
(deterministic, via ``pdfplumber``) into tidy-long rows and cross-checks the two
published reconciliations before writing.

Output ``ovhcloud-transparency.json``, tidy-long:
  publisher, period, section, category, metric, unit, value

Three sections:
  * ``member_state_orders``   — per country: ``orders_received`` (count) and
    ``median_implementation_hours`` (hours). The report's "délai médian de
    notification" column is ``NA`` for every country, so it is not emitted.
  * ``illegal_content_notices`` — per content category: ``notices_received``
    (count), ``median_action_seconds`` (seconds) and ``automated_share_pct``
    (percent). ``personal_data`` reports have ``NA`` for time/automation.
  * ``notice_totals``         — the report-wide ``total_notices_received``,
    ``dsa_scope_notices`` and ``out_of_scope_notices``.

Reconciliations (raise on mismatch):
  * the six per-category ``notices_received`` minus the ``personal_data`` row
    (data-protection reports are not DSA "illegal content") equals
    ``dsa_scope_notices``; and
  * ``dsa_scope_notices`` + ``out_of_scope_notices`` equals
    ``total_notices_received``.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request

try:
    import pdfplumber
except ImportError:  # pragma: no cover
    pdfplumber = None

HERE = os.path.dirname(os.path.abspath(__file__))
# The raw PDF is archived once, in the shared pdf-reports/ tree (the catalogue's
# `[archived PDF](pdf-reports/ovhcloud)` link), so it is not duplicated here.
RAW = os.path.normpath(os.path.join(HERE, "..", "pdf-reports", "ovhcloud"))
OUT_JSON = os.path.join(HERE, "ovhcloud-transparency.json")
PDF_NAME = "rapport_de_transparence_dsa_ovhcloud_2025.pdf"
SOURCE_URL = (
    "https://corporate.ovhcloud.com/sites/default/files/2025-04/"
    "rapport_de_transparence_dsa_ovhcloud_2025.pdf"
)

COLUMNS = ["publisher", "period", "section", "category", "metric", "unit", "value"]
PUBLISHER = "OVHcloud"
PERIOD = "2024"  # report period 2024-02-17 … 2024-12-31

_UA = {"User-Agent": "Mozilla/5.0 (transparency-report-archiver)"}

# French label (normalised, lowercased) → canonical English slug.
_COUNTRIES = {
    "allemagne": "germany",
    "belgique": "belgium",
    "espagne": "spain",
    "france": "france",
    "pologne": "poland",
}
# keyword found in the category cell → canonical slug (order = display order).
_CATEGORIES = [
    ("propriété intellectuelle", "ip_infringement"),
    ("abus sur mineur", "csam"),
    ("violent", "violent_or_shocking"),
    ("données personnelles", "personal_data"),
    ("phishing", "phishing"),
    ("autres", "other"),
]


def _fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers=_UA)
    with urllib.request.urlopen(req, timeout=90) as response:
        return response.read()


def download(raw_dir: str) -> str:
    """Archive the raw PDF from OVHcloud into raw_dir; return its path."""
    os.makedirs(raw_dir, exist_ok=True)
    out = os.path.join(raw_dir, PDF_NAME)
    data = _fetch(SOURCE_URL)  # fetch first, so a failure leaves no file
    with open(out, "wb") as f:
        f.write(data)
    return out


# ── number parsing ────────────────────────────────────────────────────────────
def _int(cell: str) -> int:
    """'794 377' / '3 339' / '2932' → int (drops spaces incl. NBSP/thin space)."""
    digits = re.sub(r"[^\d]", "", cell)
    if not digits:
        raise ValueError(f"no digits in {cell!r}")
    return int(digits)


def _decimal(cell: str) -> float | None:
    """'1,2 s' → 1.2 ; '42,83 %' → 42.83 ; '16h' → 16 ; 'NA' → None."""
    cell = (cell or "").strip()
    if cell.upper() == "NA":
        return None
    m = re.search(r"(\d+(?:[.,]\d+)?)", cell)
    return float(m.group(1).replace(",", ".")) if m else None


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def _find_table(pages, header_kw: str):
    """First table across all pages whose header row contains header_kw."""
    for p in pages:
        for t in p.extract_tables():
            if t and any(header_kw in _norm(c).lower() for c in (t[0] or [])):
                return t
    raise SystemExit(f"table with header {header_kw!r} not found")


def _slug_for(cat_lower: str) -> str:
    for kw, slug in _CATEGORIES:
        if kw in cat_lower:
            return slug
    raise SystemExit(f"unknown content category {cat_lower!r}")


def _parse_totals(pages) -> tuple[int, int, int]:
    for p in pages:
        txt = re.sub(r"\s+", " ", p.extract_text() or "")
        m = re.search(
            r"a reçu\s+([\d  ]+?)\s+signalements.*?"
            r"([\d  ]+?)\s+signalements\s*\(\s*\d+\s*%\).*?"
            r"([\d  ]+?)\s+signalements\s*\(\s*\d+\s*%\)",
            txt)
        if m:
            return _int(m.group(1)), _int(m.group(2)), _int(m.group(3))
    raise SystemExit("report-wide notice totals not found in narrative")


# ── parse (offline, deterministic) ────────────────────────────────────────────
def build(raw_dir: str) -> dict:
    if pdfplumber is None:  # pragma: no cover
        raise SystemExit("pdfplumber is required to parse the OVHcloud PDF")
    path = os.path.join(raw_dir, PDF_NAME)
    if not os.path.exists(path):
        raise SystemExit(f"no archived PDF at {path} — run --download first")

    rows: list[list] = []
    with pdfplumber.open(path) as pdf:
        pages = pdf.pages

        # Section I — member-state authority orders.
        orders = _find_table(pages, "origine des injonctions")
        for row in orders[1:]:
            cell_country, cell_orders, _cell_notif, cell_impl = row[:4]
            slug = _COUNTRIES.get(_norm(cell_country).lower())
            if not slug:
                raise SystemExit(f"unknown country row {cell_country!r}")
            rows.append([PUBLISHER, PERIOD, "member_state_orders", slug,
                         "orders_received", "count", _int(cell_orders)])
            hrs = _decimal(cell_impl)
            if hrs is not None:
                rows.append([PUBLISHER, PERIOD, "member_state_orders", slug,
                             "median_implementation_hours", "hours", hrs])

        # Section II — illegal-content notices by category.
        notices = _find_table(pages, "catégories")
        cat_total = 0
        personal = None
        for row in notices[1:]:
            cell_cat, cell_n, cell_t, cell_a = row[:4]
            slug = _slug_for(_norm(cell_cat).lower())
            n = _int(cell_n)
            cat_total += n
            if slug == "personal_data":
                personal = n
            rows.append([PUBLISHER, PERIOD, "illegal_content_notices", slug,
                         "notices_received", "count", n])
            secs = _decimal(cell_t)
            if secs is not None:
                rows.append([PUBLISHER, PERIOD, "illegal_content_notices", slug,
                             "median_action_seconds", "seconds", secs])
            pct = _decimal(cell_a)
            if pct is not None:
                rows.append([PUBLISHER, PERIOD, "illegal_content_notices", slug,
                             "automated_share_pct", "percent", pct])

        # Report-wide totals (narrative).
        total, dsa_scope, out_scope = _parse_totals(pages)
        for metric, value in (("total_notices_received", total),
                              ("dsa_scope_notices", dsa_scope),
                              ("out_of_scope_notices", out_scope)):
            rows.append([PUBLISHER, PERIOD, "notice_totals", "all",
                         metric, "count", value])

    # ── reconciliations ───────────────────────────────────────────────────────
    if personal is None:
        raise SystemExit("personal_data notices row not found")
    if cat_total - personal != dsa_scope:
        raise SystemExit(
            f"category notices {cat_total} - personal_data {personal} "
            f"= {cat_total - personal} != DSA-scope total {dsa_scope}")
    if dsa_scope + out_scope != total:
        raise SystemExit(
            f"DSA-scope {dsa_scope} + out-of-scope {out_scope} "
            f"= {dsa_scope + out_scope} != total {total}")

    return {
        "source": "OVHcloud (OVH Groupe SAS) — EU DSA transparency report, "
                  "period 2024-02-17 … 2024-12-31, published April 2025 "
                  "(corporate.ovhcloud.com). Hosting intermediary; narrative PDF.",
        "coverage": PERIOD,
        "columns": COLUMNS,
        "rows": rows,
    }


def main() -> int:
    desc = __doc__.splitlines()[0] if __doc__ else "Build the OVHcloud dataset."
    ap = argparse.ArgumentParser(description=desc)
    ap.add_argument("--raw", default=RAW)
    ap.add_argument("--out", default=OUT_JSON)
    ap.add_argument("--download", action="store_true",
                    help="re-fetch the OVHcloud PDF into raw/ before building")
    args = ap.parse_args()
    if args.download:
        p = download(args.raw)
        print(f"downloaded {p}")
    data = build(args.raw)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    print(f"wrote {args.out}: {len(data['rows'])} rows "
          f"({len({r[3] for r in data['rows']})} categories)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
