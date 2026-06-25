#!/usr/bin/env python3
"""Extract DSA harmonised-template transparency reports into a normalised form.

The EU harmonised machine-readable template (Implementing Regulation (EU)
2024/2835) is an 11-section workbook — the same tables 1-11 used by the VLOP
dataset. Platforms ship it as a single multi-sheet .xlsx/.xls or as a zip of one
CSV per section; sheet names are sometimes localised (DE/FR), but the section
*order* (1..11) is fixed, so we map by position.

For each source under raw/, this writes raw/../extracted/<platform>/NN_<section>.csv
(one canonical CSV per section) and a manifest.json summarising what was found.

Re-run after adding files to raw/:  python3 extract.py
"""
from __future__ import annotations

import csv
import io
import json
import os
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT = os.path.join(HERE, "extracted")

# Canonical section names, in the fixed template order (1..11).
SECTIONS = [
    "report_identification", "categories_names", "member_states_orders",
    "notices", "own_initiative_illegal", "own_initiative_TC",
    "appeals_and_recidivism", "automated_means", "human_resources",
    "AMAR", "qualitative",
]

# platform slug -> (source filename in raw/, kind). kind: xlsx | xls | zipcsv
SOURCES = {
    "aboutyou":  ("aboutyou.csv.xlsx", "xlsx"),
    "aboutyou2": ("aboutyou2.xlsx", "xlsx"),  # AboutYou follow-on period (Dec 2025)
    "dailymotion": ("dailymotion.xlsx", "xlsx"),
    "carrefour": ("carrefour.xlsx", "xlsx"),
    "linkedin":  ("linkedin.zip", "zipcsv"),
    "manomano":  ("manomano.xlsx", "xlsx"),
    "pinterest": ("pinterest.zip", "zipcsv"),
    "veepee":    ("veepee.xlsx", "xlsx"),
    "vinted":    ("vinted.xlsx", "xlsx"),
    "webde":     ("webde.xlsx", "xlsx"),
    "wikipedia": ("wikipedia.xls", "xls"),
    # Added from the hub landing-page sweep (discover_hubs.py / download_hubs.py).
    "ceneo":       ("ceneo.xlsx", "xlsx"),
    "cloudflare":  ("cloudflare.xlsx", "xlsx"),
    "duckduckgo":  ("duckduckgo.xlsx", "xlsx"),
    "expedia":     ("expedia.xlsx", "xlsx"),
    "hometogo":    ("hometogo.xlsx", "xlsx"),
    "hostelworld": ("hostelworld.xlsx", "xlsx"),
    "hostinger":   ("hostinger.xlsx", "xlsx"),
    "hotelscom":   ("hotelscom.xlsx", "xlsx"),
    "imdb":        ("imdb.zip", "zipcsv"),
    "konami":      ("konami.xlsx", "xlsx"),
    "lilo":        ("lilo.xlsx", "xlsx"),
    "matchgroup":  ("matchgroup.xlsx", "xlsx"),
    "niantic":     ("niantic.xlsx", "xlsx"),
    "qwant":       ("qwant.xlsx", "xlsx"),
    "roblox":      ("roblox.xlsx", "xlsx"),
    "shopify":     ("shopify.xlsx", "xlsx"),
    "skroutz":     ("skroutz.xlsx", "xlsx"),
    "vrbo":        ("vrbo.xlsx", "xlsx"),
    "yahoo":       ("yahoo.zip", "zipcsv"),
    # Added from the Zendesk help-center API sweep (browser-blocked landing pages
    # whose attachment files resolve via /api/v2/help_center/.../attachments.json).
    "bumble":      ("bumble.xlsx", "xlsx"),
    "grindr":      ("grindr.xlsx", "xlsx"),
    "vestiaire":   ("vestiaire.xlsx", "xlsx"),
    "whatnot":     ("whatnot.xlsx", "xlsx"),
}

import re as _re
# Leading/embedded section number, e.g. "1_report…", "… - 10. AMAR", "Part 11".
_SEC_NUM = _re.compile(r"(?:^|[-\s_/])(\d{1,2})[._\s]")


def _section_index(name: str) -> int | None:
    nums = [int(n) for n in _SEC_NUM.findall(name) if 1 <= int(n) <= 11]
    return nums[-1] if nums else None


def _to_canonical(named: list[tuple[str, list[list[str]]]]) -> list[list[list[str]]]:
    """Map (sheet/file name, rows) pairs to the 11 canonical section slots.

    Prefer the section number parsed from the name (robust to omitted sections,
    e.g. a non-VLOP that ships 1-8 + 11). Fall back to positional order only when
    no name carries a number and exactly 11 are present.
    """
    idxs = [_section_index(n) for n, _ in named]
    if all(i is not None for i in idxs) and len(set(idxs)) == len(idxs):
        slots: list[list[list[str]]] = [[] for _ in SECTIONS]
        for i, (_, rows) in zip(idxs, named):
            if i and 1 <= i <= 11:
                slots[i - 1] = rows
        return slots
    if len(named) == len(SECTIONS):  # positional fallback (unnumbered, full set)
        return [rows for _, rows in named]
    # Best effort: place the numbered ones, leave the rest empty.
    slots = [[] for _ in SECTIONS]
    for i, (_, rows) in zip(idxs, named):
        if i and 1 <= i <= 11:
            slots[i - 1] = rows
    return slots


def _clean(v: object) -> str:
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()


def read_xlsx(path: str) -> list[tuple[str, list[list[str]]]]:
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True)
    sheets = []
    for name in wb.sheetnames:
        ws = wb[name]
        rows = [[_clean(c) for c in row] for row in ws.iter_rows(values_only=True)]
        while rows and not any(rows[-1]):  # trim trailing empty rows
            rows.pop()
        sheets.append((name, rows))
    wb.close()
    return sheets


def read_xls(path: str) -> list[tuple[str, list[list[str]]]]:
    import xlrd
    from xlrd.xldate import xldate_as_datetime
    wb = xlrd.open_workbook(path)
    sheets = []
    for sh in wb.sheets():
        rows = []
        for r in range(sh.nrows):
            row = []
            for c in range(sh.ncols):
                # Convert legacy-xls date serials to ISO so they match the xlsx
                # files' "YYYY-MM-DD HH:MM:SS" rather than leaking 45839-style serials.
                if sh.cell_type(r, c) == xlrd.XL_CELL_DATE:
                    dt = xldate_as_datetime(sh.cell_value(r, c), wb.datemode)
                    row.append(dt.strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    row.append(_clean(sh.cell_value(r, c)))
            rows.append(row)
        while rows and not any(rows[-1]):
            rows.pop()
        sheets.append((sh.name, rows))
    return sheets


def read_zipcsv(path: str) -> list[tuple[str, list[list[str]]]]:
    """Read the per-section CSVs from a zip as (filename, rows) pairs."""
    out = []
    with zipfile.ZipFile(path) as z:
        for info in z.namelist():
            base = os.path.basename(info)
            # Skip non-CSVs and macOS metadata (the __MACOSX/ dir and the
            # AppleDouble "._name" sidecar files, which are binary, not CSV).
            if (not base.lower().endswith(".csv") or info.startswith("__MACOSX")
                    or base.startswith("._")):
                continue
            with z.open(info) as f:
                text = f.read().decode("utf-8-sig", errors="replace")
            # Parse via StringIO (not splitlines) so newlines *inside* quoted
            # fields — common in the qualitative section — don't split a row.
            rows = list(csv.reader(io.StringIO(text)))
            while rows and not any(c.strip() for c in rows[-1]):
                rows.pop()
            out.append((base, rows))
    return out


READERS = {"xlsx": read_xlsx, "xls": read_xls, "zipcsv": read_zipcsv}


def _trim_cols(rows: list[list[str]]) -> list[list[str]]:
    """Drop trailing all-empty columns (spreadsheets pad rows to the sheet width)."""
    width = 0
    for r in rows:
        last = max((i + 1 for i, c in enumerate(r) if c), default=0)
        width = max(width, last)
    return [r[:width] for r in rows]


# Indicator labels in section 1, across the locales we ingest (EN/DE/FR/EL).
_PROVIDER = ("service provider", "diensteanbieters", "fournisseur", "παρόχου")
_START = ("starting date", "beginn des berichtszeitraums", "date de début",
          "début", "έναρξης")
_END = ("ending date", "ende des berichtszeitraums", "date de fin", "fin", "λήξης")


def _ident(rows: list[list[str]]) -> dict:
    """Pull provider name + reporting period from a section-1 table. The label
    column varies (some files drop the leading 'Applicability' column), so match
    the (localised) indicator text anywhere in the row; the value is the last
    non-empty cell."""
    out = {"provider": "", "period_start": "", "period_end": ""}
    for r in rows[1:]:
        cells = [c.lower() for c in r]
        val = next((c for c in reversed(r) if c), "")
        label = " ".join(cells[:-1])  # everything but the value cell
        if any(k in label for k in _PROVIDER) and not out["provider"]:
            out["provider"] = val
        elif any(k in label for k in _START) and not out["period_start"]:
            out["period_start"] = val[:10]
        elif any(k in label for k in _END) and not out["period_end"]:
            out["period_end"] = val[:10]
    return out


def _amar_total(rows: list[list[str]]) -> str:
    """AMAR EU total (section 10, scope == TOTAL). Empty for non-VLOP services,
    which leave the value blank (so the last non-empty cell is the 'TOTAL' label
    itself) — hence we only return a genuinely numeric value."""
    for r in rows[1:]:
        if any(c.strip().upper() == "TOTAL" for c in r):
            val = next((c for c in reversed(r) if c), "").replace(",", "").replace(" ", "")
            return val if val.isdigit() else ""
    return ""


def extract_one(slug: str, fname: str, kind: str) -> dict:
    path = os.path.join(RAW, fname)
    sheets = [_trim_cols(s) for s in _to_canonical(READERS[kind](path))]
    dest = os.path.join(OUT, slug)
    os.makedirs(dest, exist_ok=True)
    section_rows = {}
    for i, name in enumerate(SECTIONS):
        rows = sheets[i] if i < len(sheets) else []
        with open(os.path.join(dest, f"{i + 1:02d}_{name}.csv"), "w",
                  newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(rows)
        section_rows[name] = max(0, len(rows) - 1)  # minus header row
    ident = _ident(sheets[0]) if sheets and sheets[0] else {}
    amar = _amar_total(sheets[9]) if len(sheets) > 9 else ""
    return {
        "platform": slug,
        "source_file": fname,
        "format": kind,
        "provider": ident.get("provider", ""),
        "period_start": ident.get("period_start", ""),
        "period_end": ident.get("period_end", ""),
        "amar_eu_total": amar,
        "sections_found": sum(1 for i in range(len(SECTIONS))
                              if i < len(sheets) and sheets[i]),
        "data_rows_by_section": section_rows,
    }


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    manifest = []
    for slug, (fname, kind) in sorted(SOURCES.items()):
        if not os.path.exists(os.path.join(RAW, fname)):
            print(f"skip {slug}: {fname} not in raw/")
            continue
        info = extract_one(slug, fname, kind)
        manifest.append(info)
        total = sum(info["data_rows_by_section"].values())
        print(f"{slug:10} {kind:6} {info['sections_found']}/11 sections, "
              f"{total} data rows")
    with open(os.path.join(HERE, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    # Flat cross-platform summary of the headline identification fields.
    with open(os.path.join(HERE, "summary.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["platform", "provider", "period_start", "period_end",
                    "amar_eu_total", "sections_found", "total_data_rows"])
        for m in manifest:
            w.writerow([m["platform"], m["provider"], m["period_start"],
                        m["period_end"], m["amar_eu_total"], m["sections_found"],
                        sum(m["data_rows_by_section"].values())])
    print(f"\nwrote manifest.json + summary.csv ({len(manifest)} platforms) and "
          f"extracted/<platform>/NN_<section>.csv")


if __name__ == "__main__":
    main()
