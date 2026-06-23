#!/usr/bin/env python3
"""Build a normalised relational database of DSA transparency-report locations.

Single source of truth is REPORT_LOCATIONS.md (the human-editable catalogue).
This script parses its per-category platform tables and emits:

  * dsa_reports.db  — a normalised SQLite database (category / company /
                      platform / report_url), all rows ordered alphabetically.
  * dsa_reports.csv — a flat, alphabetical export (one row per report URL),
                      git-friendly and easy to diff.

Re-run after editing REPORT_LOCATIONS.md:  python3 build_reports_db.py
"""
from __future__ import annotations

import csv
import re
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_MD = HERE / "REPORT_LOCATIONS.md"
DB_PATH = HERE / "dsa_reports.db"
CSV_PATH = HERE / "dsa_reports.csv"

# Sections in REPORT_LOCATIONS.md that are NOT per-platform catalogue tables.
SKIP_SECTIONS = {
    "How this was compiled",
    "Authoritative index / aggregator sources",
    "Searched, not found / out of scope",
}

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
CONF_RE = re.compile(r"^(verified|likely|uncertain)\b(.*)$", re.IGNORECASE)

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE category (
    category_id INTEGER PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE
);

CREATE TABLE company (
    company_id INTEGER PRIMARY KEY,
    name       TEXT NOT NULL UNIQUE
);

CREATE TABLE platform (
    platform_id     INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    company_id      INTEGER NOT NULL REFERENCES company(company_id),
    category_id     INTEGER NOT NULL REFERENCES category(category_id),
    format_period   TEXT,
    confidence      TEXT NOT NULL CHECK (confidence IN ('verified','likely','uncertain')),
    confidence_note TEXT,
    UNIQUE (name, category_id)
);

CREATE TABLE report_url (
    url_id      INTEGER PRIMARY KEY,
    platform_id INTEGER NOT NULL REFERENCES platform(platform_id),
    label       TEXT,
    url         TEXT NOT NULL
);

CREATE INDEX idx_platform_company  ON platform(company_id);
CREATE INDEX idx_platform_category ON platform(category_id);
CREATE INDEX idx_report_platform   ON report_url(platform_id);

-- Convenience flat view, ordered alphabetically by platform name.
CREATE VIEW v_reports AS
SELECT p.name        AS platform,
       co.name       AS company,
       ca.name       AS category,
       p.confidence  AS confidence,
       p.format_period,
       ru.label      AS url_label,
       ru.url        AS url
FROM   platform p
JOIN   company  co ON co.company_id = p.company_id
JOIN   category ca ON ca.category_id = p.category_id
LEFT JOIN report_url ru ON ru.platform_id = p.platform_id
ORDER BY p.name COLLATE NOCASE, ru.url_id;
"""


def parse_markdown(md_text: str):
    """Yield dict rows parsed from the per-category platform tables."""
    current_section = None
    for line in md_text.splitlines():
        if line.startswith("## "):
            current_section = line[3:].strip()
            continue
        if current_section is None or current_section in SKIP_SECTIONS:
            continue
        if not line.startswith("|"):
            continue
        # Split on '|' and drop the empty elements created by the leading and
        # (optional) trailing pipe — robust to empty cells, which strip('|') is not.
        raw_cells = [c.strip() for c in line.split("|")]
        cells = raw_cells[1:-1] if raw_cells and raw_cells[-1] == "" else raw_cells[1:]
        if len(cells) != 5:
            continue
        platform, company, url_cell, fmt, confidence = cells
        # Skip header + separator rows.
        if platform.lower() == "platform" or set(platform) <= {"-", ":"}:
            continue

        links = LINK_RE.findall(url_cell)
        if not links:  # plain-text fallback (no markdown link present)
            links = [("", url_cell)]

        m = CONF_RE.match(confidence)
        if m:
            conf_level = m.group(1).lower()
            conf_note = m.group(2).strip(" ()") or None
        else:  # should not happen, but keep the data rather than drop it
            conf_level, conf_note = "uncertain", confidence

        yield {
            "platform": platform,
            "company": company,
            "category": current_section,
            "format_period": fmt,
            "confidence": conf_level,
            "confidence_note": conf_note,
            "links": [(lbl.strip(), url.strip()) for lbl, url in links],
        }


def build_db(rows):
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA)
        cur = conn.cursor()

        rows = sorted(rows, key=lambda r: (r["platform"].lower(), r["category"].lower()))

        cat_ids: dict[str, int] = {}
        co_ids: dict[str, int] = {}
        for name in sorted({r["category"] for r in rows}, key=str.lower):
            cur.execute("INSERT INTO category(name) VALUES (?)", (name,))
            cat_ids[name] = cur.lastrowid
        for name in sorted({r["company"] for r in rows}, key=str.lower):
            cur.execute("INSERT INTO company(name) VALUES (?)", (name,))
            co_ids[name] = cur.lastrowid

        for r in rows:
            cur.execute(
                """INSERT INTO platform
                   (name, company_id, category_id, format_period, confidence, confidence_note)
                   VALUES (?,?,?,?,?,?)""",
                (r["platform"], co_ids[r["company"]], cat_ids[r["category"]],
                 r["format_period"], r["confidence"], r["confidence_note"]),
            )
            pid = cur.lastrowid
            for label, url in r["links"]:
                cur.execute(
                    "INSERT INTO report_url(platform_id, label, url) VALUES (?,?,?)",
                    (pid, label or None, url),
                )

        conn.commit()
        counts = {
            t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            for t in ("category", "company", "platform", "report_url")
        }
        return counts
    finally:
        conn.close()


def write_csv(rows):
    flat = []
    for r in sorted(rows, key=lambda r: (r["platform"].lower(), r["category"].lower())):
        for label, url in r["links"]:
            flat.append({
                "platform": r["platform"],
                "company": r["company"],
                "category": r["category"],
                "confidence": r["confidence"],
                "format_period": r["format_period"],
                "url_label": label,
                "url": url,
            })
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "platform", "company", "category", "confidence",
            "format_period", "url_label", "url",
        ])
        w.writeheader()
        w.writerows(flat)
    return len(flat)


def main():
    rows = list(parse_markdown(SOURCE_MD.read_text(encoding="utf-8")))
    counts = build_db(rows)
    n_csv = write_csv(rows)
    print(f"Parsed {len(rows)} platforms from {SOURCE_MD.name}")
    print("  " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    print(f"  wrote {DB_PATH.name} and {CSV_PATH.name} ({n_csv} report-URL rows)")


if __name__ == "__main__":
    main()
