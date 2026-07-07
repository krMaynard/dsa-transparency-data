#!/usr/bin/env python3
"""Build the regional content-moderation transparency-law dataset.

Two sub-national / national statutes require platforms to publish periodic
content-moderation transparency reports, filed by Google for YouTube on its
public transparency-report bucket:

- **Texas HB 20** (Texas Business & Commerce Code §120.053) — YouTube's
  half-yearly report of monetization, Community-Guidelines enforcement (videos
  removed / appealed / reinstated), human flags by flagger type, removals by
  source of first detection, by reason, and by country of upload, plus
  coordinated-influence-operation takedowns. The layout was reduced from
  2025-H2 (enforcement figures now point to the global CGER; the report itself
  keeps only monetization + age-restrictions).
- **Austria KoPl-G** (Kommunikationsplattformen-Gesetz) — YouTube's biannual
  §4 report on complaints about allegedly-illegal *textual* content (comments).
  YouTube's own commentary notes the KoPl-G webform "is de facto not used", so
  the figures are sparse (single digits).

Output ``regional-transparency.json``, tidy-long:
  jurisdiction, platform, period, section, category, metric, unit, value

Every figure is transcribed / parsed from the archived PDFs under ``raw/`` with
fail-loud anchor checks (the build raises if a report drifts). Deterministic;
no network. Needs ``pdfplumber`` only for nothing — pure PyMuPDF (``fitz``).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT_JSON = os.path.join(HERE, "regional-transparency.json")

COLUMNS = ["jurisdiction", "platform", "period", "section", "category",
           "metric", "unit", "value"]

TEXAS = "Texas (HB 20)"
AUSTRIA = "Austria (KoPl-G)"


def _pdf_text(path: str) -> str:
    with fitz.open(path) as doc:
        return "\n".join(p.get_text() for p in doc)


def _int(s: str) -> int:
    """Parse a count that may use comma or space thousands separators."""
    return int(re.sub(r"[ ,]", "", s.strip()))


def _need(text: str, pat: str, path: str, label: str) -> re.Match:
    m = re.search(pat, text)
    if not m:
        raise SystemExit(f"{os.path.basename(path)}: {label} anchor not found — "
                         "report format changed?")
    return m


# ── Texas HB 20 (§120.053) ────────────────────────────────────────────────────
# The ten Community-Guidelines removal reasons. YouTube renamed one from 2025-H1
# ("Spam, Misleading and Scams" → "Spam, Deceptive Practices, and Scams"); both
# spellings are accepted and kept verbatim (commas stripped) per report.
_TX_REASONS = re.compile(
    r"(Child Safety|Harassment and Cyberbullying|Harmful or Dangerous|"
    r"Hateful or Abusive|Misinformation|Nudity or Sexual|Other|"
    r"Promotion of Violence and Violent Extremism|"
    r"Spam,? Misleading and Scams|Spam, Deceptive Practices, and Scams|"
    r"Violent or Graphic): ([\d,]+) \(")

# A "Rank / Country / Value" table row: rank, country name, space-separated count.
_TX_COUNTRY = re.compile(r"\n\d+\n([A-Z][A-Za-z .'-]+?)\n([\d][\d ,]*)\n")


def _slice(text: str, start_anchor: str, end_anchor: str) -> str:
    """The text between two heading anchors (empty if the start isn't present).
    Scoping each breakdown to its own section keeps a later block — e.g. a
    channel-terminations-by-reason table that reuses the same category labels —
    from bleeding into the video-removals-by-reason figures."""
    i = text.find(start_anchor)
    if i < 0:
        return ""
    j = text.find(end_anchor, i + len(start_anchor))
    return text[i:j if j >= 0 else len(text)]


def _tx_flag_detection(block: str) -> list[tuple[str, str, int]]:
    """Within the flags/detection block, the flagger-type figures and the
    source-of-first-detection figures both list User / Organization / Government,
    separated by the automation line: User/Org/Gov *before* it are human flags
    received; the automation line + the User/Org/Gov *after* it are removals by
    source of first detection. Labels drift ('Automation detection first flag' vs
    'Automated flagging'; 'Government' vs 'Government agency') so canonicalise."""
    auto = re.search(r"(Automation detection first flag|Automated flagging): "
                     r"([\d,]+) \(", block)
    if not auto:
        return []
    pos = auto.start()
    out: list[tuple[str, str, int]] = []
    src = re.compile(r"(User|Organization|Government)(?: agency)?: ([\d,]+) \(")
    for m in src.finditer(block):
        cat = m.group(1)
        if m.start() < pos:
            out.append(("human_flags", cat, _int(m.group(2))))      # flags received
        else:
            out.append(("removals_by_detection", cat, _int(m.group(2))))
    out.append(("removals_by_detection", "Automated", _int(auto.group(2))))
    return out


def _parse_texas(path: str, period: str) -> list[list]:
    text = _pdf_text(path)
    rows: list[list] = []

    def add(section: str, category: str, metric: str, value: int) -> None:
        rows.append([TEXAS, "YouTube", period, section, category, metric,
                     "count", value])

    flat = " ".join(text.split())
    # Monetization demonetizations — present in every report.
    m = _need(flat, r"demonetizations due to\s*violations of monetization "
              r"policies\s*([\d,]+)", path, "demonetizations")
    add("monetization", "", "demonetizations", _int(m.group(1)))
    # Age restrictions — present from 2025-H2 (the reduced layout).
    m = re.search(r"Age restrictions applied\s*([\d,]+)", flat)
    if m:
        add("age_restrictions", "", "age_restrictions_applied", _int(m.group(1)))

    # Community-Guidelines enforcement headline figures — the full-layout reports
    # (2024-H2, 2025-H1) only; 2025-H2 points to the global CGER instead.
    m = re.search(r"violating its Community Guidelines during the reporting "
                  r"period was ([\d,]+)", flat)
    if m:
        add("enforcement", "", "videos_removed", _int(m.group(1)))
        a = _need(flat, r"number of appeals YouTube received[^0-9]*?was ([\d,]+)",
                  path, "appeals")
        add("enforcement", "", "appeals", _int(a.group(1)))
        r = _need(flat, r"reinstated due to an appeal[^0-9]*?period was ([\d,]+)",
                  path, "reinstatements")
        add("enforcement", "", "reinstatements", _int(r.group(1)))
        # Coordinated influence operations (TAG Bulletin).
        tag = _need(flat, r"show ([\d,]+) YouTube channels across (\d+) separate "
                    r"actions", path, "coordinated_influence")
        add("coordinated_influence", "", "channels", _int(tag.group(1)))
        add("coordinated_influence", "", "actions", _int(tag.group(2)))
        # Removal reasons — scoped to the "Video removals by reason" section so a
        # later channel-terminations-by-reason table (same labels, different
        # denominator) can't leak in. The labels are printed twice (chart legend +
        # value list), so keep the first value per unique label.
        reason_block = _slice(text, "Video removals by reason", "Rank")
        seen: dict[str, int] = {}
        for label, n in _TX_REASONS.findall(reason_block):
            seen.setdefault(label.replace(",", ""), _int(n))
        if len(seen) != 10:
            raise SystemExit(f"{os.path.basename(path)}: expected 10 removal "
                             f"reasons in the video-removals section, got {len(seen)}")
        for label, n in seen.items():
            add("removals_by_reason", label, "videos_removed", n)
        # Human flags + removals by source of first detection — scoped to the
        # flagger-type/detection section.
        flag_block = _slice(text, "Human flags by flagger type",
                            "Video removals by reason")
        for section, cat, n in _tx_flag_detection(flag_block):
            metric = "flags" if section == "human_flags" else "videos_removed"
            add(section, cat, metric, n)
        # Video removals by country of upload (Rank / Country / Value table). The
        # table prints as two side-by-side columns (two "Rank" headers), so a
        # window from the first covers both; the strict row regex ignores non-rows.
        i = text.find("Rank")
        for label, n in _TX_COUNTRY.findall(text[i:i + 1400]) if i >= 0 else []:
            add("removals_by_country", label.strip(), "videos_removed", _int(n))
        # Cross-check: the reason and detection breakdowns each partition the same
        # videos-removed total, so both must sum back to it exactly (a strong
        # signal the right blocks were scoped and nothing leaked or was dropped).
        removed = next(r[7] for r in rows if r[3] == "enforcement"
                       and r[5] == "videos_removed")
        for section in ("removals_by_reason", "removals_by_detection"):
            got = sum(r[7] for r in rows if r[3] == section)
            if got != removed:
                raise SystemExit(f"{os.path.basename(path)}: {section} sums to "
                                 f"{got:,}, expected videos_removed {removed:,}")
    return rows


_TEXAS_REPORTS = [
    ("texas-youtube-2024-h2.pdf", "2024-H2"),
    ("texas-youtube-2025-h1.pdf", "2025-H1"),
    ("texas-youtube-2025-h2.pdf", "2025-H2"),
]


# ── Austria KoPl-G (§4) ───────────────────────────────────────────────────────
def _parse_austria(path: str, period: str) -> list[list]:
    text = _pdf_text(path)
    rep = _need(text, r"Total reported items\s+([\d.,]+)", path, "reported items")
    rem = _need(text, r"Total removed items\s+([\d.,]+)", path, "removed items")
    return [
        [AUSTRIA, "YouTube", period, "complaints", "", "reported_items", "count", _int(rep.group(1))],
        [AUSTRIA, "YouTube", period, "complaints", "", "removed_items", "count", _int(rem.group(1))],
    ]


_AUSTRIA_REPORTS = [
    ("austria-youtube-2021-h2.pdf", "2021-H2"),
    ("austria-youtube-2022-h1.pdf", "2022-H1"),
    ("austria-youtube-2022-h2.pdf", "2022-H2"),
    ("austria-youtube-2023-h1.pdf", "2023-H1"),
]


def build(raw_dir: str) -> dict:
    rows: list[list] = []
    for fname, period in _TEXAS_REPORTS:
        rows += _parse_texas(os.path.join(raw_dir, fname), period)
    for fname, period in _AUSTRIA_REPORTS:
        rows += _parse_austria(os.path.join(raw_dir, fname), period)
    rows.sort(key=lambda r: (r[0], r[2], r[3], r[4], r[5]))
    return {
        "source": "Texas Business & Commerce Code §120.053 (HB 20) + Austria "
                  "Kommunikationsplattformen-Gesetz (KoPl-G) §4 — YouTube reports "
                  "on Google's transparency-report bucket",
        "columns": COLUMNS,
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raw", default=RAW)
    ap.add_argument("--out", default=OUT_JSON)
    args = ap.parse_args()
    if not glob.glob(os.path.join(args.raw, "*.pdf")):
        raise SystemExit(f"no PDFs under {args.raw}")
    data = build(args.raw)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    juris = sorted({r[0] for r in data["rows"]})
    print(f"wrote {args.out}: {len(data['rows'])} rows across {len(juris)} "
          f"jurisdictions ({', '.join(juris)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
