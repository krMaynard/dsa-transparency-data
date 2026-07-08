#!/usr/bin/env python3
"""Build the China CIIRC (12377) online-report-handling dataset.

The Central Cyberspace Administration of China (CAC) Illegal and Harmful
Information Reporting Center — 中央网信办违法和不良信息举报中心, the national
**12377** hotline — publishes a monthly bulletin, "全国网络举报受理情况", on how
many public reports of illegal / harmful online information were handled that
month, split by the receiving body:

- **中央网信办举报中心** — the central reporting center;
- **各地网信举报工作部门** — the provincial / local cyberspace-office departments;
- **全国主要网站平台** — the major national websites & platforms (of which a
  **主要商业网站平台** commercial-platform subset is sometimes broken out).

Their sum is the **national total**. This is coarse (a handful of figures per
month) but a genuine multi-year series — the one major jurisdiction otherwise
absent from this corpus.

`build_ciirc.py --download` scrapes the notices listing (`/tzgg/listN.html`) and
each monthly post from `www.12377.cn`, archiving the raw HTML under ``raw/``;
`build()` then parses the archived pages **offline** (deterministic). Figures are
published in 万 (ten-thousands) and stored as absolute counts.

Output ``china-ciirc.json``, tidy-long:
  publisher, period, section, category, metric, unit, value

Labels drift over the 2019→ series, so the parser keys off the stable
中央网信办 / 各地网信 anchors and reconciles: every post states either the national
total or the platforms figure, so the missing one is derived and — when both are
present — cross-checked (the build raises on a mismatch beyond rounding).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT_JSON = os.path.join(HERE, "china-ciirc.json")
BASE = "https://www.12377.cn"

COLUMNS = ["publisher", "period", "section", "category", "metric", "unit", "value"]
PUBLISHER = "CAC-CIIRC"
SECTION = "reports_received"
METRIC = "reports_received"

_UA = {"User-Agent": "Mozilla/5.0 (transparency-report-archiver)"}


def _fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=_UA)
    with urllib.request.urlopen(req, timeout=30) as response:
        raw = response.read()
    m = re.search(rb"charset=[\"']?([\w-]+)", raw[:2000])
    enc = m.group(1).decode() if m else "utf-8"
    return raw.decode(enc, errors="replace")


def _plain(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _wan(s: str) -> int:
    """万 (ten-thousands, may carry one decimal) → absolute integer count."""
    return round(float(s) * 10000)


# ── scrape (archives raw HTML; not needed for a normal offline build) ──────────
_POST_RE = re.compile(r"(/tzgg/\d{4}/[0-9a-f]+_web\.html)[\"'][^>]*>(?:<[^>]+>)*\s*"
                      r"(20\d\d)年(\d+)月")


def download(raw_dir: str) -> int:
    os.makedirs(raw_dir, exist_ok=True)
    seen: dict[str, str] = {}
    for pg in range(1, 40):
        try:
            html = _fetch(f"{BASE}/tzgg/list{pg}.html")
        except urllib.error.HTTPError as e:  # type: ignore[attr-defined]
            if e.code == 404:
                break
            raise
        found = False
        for path, y, mth in _POST_RE.findall(html):
            found = True
            seen.setdefault(f"{y}-{int(mth):02d}", path)
        if not found:
            break
    for period, path in sorted(seen.items()):
        url = path if path.startswith("http") else BASE + path
        with open(os.path.join(raw_dir, f"ciirc-{period}.html"), "w",
                  encoding="utf-8") as f:
            f.write(_fetch(url))
    return len(seen)


# ── parse (offline, deterministic) ────────────────────────────────────────────
_CENTRAL = re.compile(r"中央网信办(?:（国家互联网信息办公室）)?(?:违法和不良信息)?"
                      r"举报中心受理举报([\d.]+)万件")
_LOCAL = re.compile(r"各地网信(?:办)?举报(?:工作)?部门受理(?:举报)?([\d.]+)万件")
# The breakdown line is "全国主要网站平台受理举报X万件"; the headline-total line
# ("…网信举报工作部门、主要网站平台受理举报X万件") also contains "主要网站平台受理
# 举报", so require the 全国 prefix (no 顿号) to match only the breakdown line.
_PLATFORMS = re.compile(r"全国主要网站平台受理举报([\d.]+)万件")
_COMMERCIAL = re.compile(r"主要商业网站平台受理量([\d.]+)万件")


def _parse_post(path: str) -> list[list]:
    period = re.search(r"ciirc-(20\d\d-\d\d)\.html$", path).group(1)
    # Some bulletins render each glyph space-separated ("1872.2 万件"), so match on
    # a fully whitespace-stripped copy.
    with open(path, encoding="utf-8") as f:
        text = re.sub(r"\s+", "", _plain(f.read()))
    rows = [[PUBLISHER, period, SECTION, "national_total", METRIC, "count", 0]]

    c = _CENTRAL.search(text)
    lo = _LOCAL.search(text)
    if c and lo:
        central, local = _wan(c.group(1)), _wan(lo.group(1))
        pf = _PLATFORMS.search(text)
        platforms = _wan(pf.group(1)) if pf else None
        # National total = the first 万件 figure before the 中央网信办 clause (the
        # opening summary), when the bulletin states one. The newest layout omits
        # it, so fall back to the sum of the receiving-body figures.
        before = re.findall(r"([\d.]+)万件", text[:c.start()])
        total_hd = _wan(before[0]) if before else None
        if not (total_hd is not None and total_hd > central + local):
            total_hd = None  # opening figure was itself the central figure, etc.
        if platforms is None:
            if total_hd is None:
                raise SystemExit(f"{os.path.basename(path)}: no national total "
                                 "and no platforms breakdown line found")
            platforms = total_hd - central - local  # only when not stated
        total = total_hd if total_hd is not None else central + local + platforms
        # Cross-check: the components (each independently rounded to 0.1万) must
        # reconcile with the stated total within rounding slack.
        if total_hd is not None and abs(total_hd - (central + local + platforms)) > 2500:
            raise SystemExit(f"{os.path.basename(path)}: total {total_hd} != "
                             f"central+local+platforms {central+local+platforms}")
        rows[0][-1] = total
        rows += [
            [PUBLISHER, period, SECTION, "central_center", METRIC, "count", central],
            [PUBLISHER, period, SECTION, "local_departments", METRIC, "count", local],
            [PUBLISHER, period, SECTION, "platforms", METRIC, "count", platforms],
        ]
        cm = _COMMERCIAL.search(text)
        if cm:
            rows.append([PUBLISHER, period, SECTION, "commercial_platforms",
                         METRIC, "count", _wan(cm.group(1))])
    else:
        # Total-only bulletin — some months publish just the national headline
        # figure with no receiving-body breakdown.
        figs = re.findall(r"([\d.]+)万件", text)
        if not figs:
            raise SystemExit(f"{os.path.basename(path)}: no 万件 figure found")
        rows[0][-1] = _wan(figs[0])
    return rows


def build(raw_dir: str) -> dict:
    files = sorted(glob.glob(os.path.join(raw_dir, "ciirc-*.html")))
    if not files:
        raise SystemExit(f"no archived posts under {raw_dir} — run --download first")
    rows: list[list] = []
    for path in files:
        rows += _parse_post(path)
    rows.sort(key=lambda r: (r[1], r[3]))
    return {
        "source": "China CAC Illegal & Harmful Information Reporting Center "
                  "(12377) — 全国网络举报受理情况 monthly bulletins (www.12377.cn)",
        "coverage": max(r[1] for r in rows),
        "columns": COLUMNS,
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raw", default=RAW)
    ap.add_argument("--out", default=OUT_JSON)
    ap.add_argument("--download", action="store_true",
                    help="re-scrape www.12377.cn into raw/ before building")
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
          f"months ({months[0]} … {months[-1]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
