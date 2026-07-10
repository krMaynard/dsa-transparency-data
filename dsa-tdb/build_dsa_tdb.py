#!/usr/bin/env python3
"""Build dsa-tdb.json from the EU DSA Transparency Database (Statements of Reasons).

Every content-moderation decision an in-scope platform takes under the EU Digital
Services Act is filed to the **DSA Transparency Database** as an individual
*Statement of Reasons* (SoR). That database is enormous — billions of SoRs, ~4 TB
of daily dumps — so we do NOT vendor it raw. Instead we use the European
Commission's own toolbox, **dsa-tdb** (https://code.europa.eu/dsa/transparency-database/dsa-tdb),
to fetch its pre-made **global "simple" monthly aggregates**, then RE-AGGREGATE
them into a compact tidy-long snapshot.

The Commission's "simple" aggregate is one row per fine-grained combination of
``platform_name × created_at(day) × category × decision_ground × automated_detection
× automated_decision × source_type × decision_* flags × content-type flags`` with
a ``count``. We roll ``created_at`` day → month and collapse to a handful of
one-dimension cuts per platform × month.

Tidy-long output — one row per measured value:

    section, platform, period, category, metric, unit, value

- **section** — which cut:
  - ``totals``                  — all SoRs (``category='All'``)
  - ``by_category``             — the 14 DSA statement categories
  - ``by_decision_ground``      — Illegal content vs Incompatible with terms
  - ``by_automated_detection``  — was the content detected automatically (Yes/No)
  - ``by_automated_decision``   — Fully / Partially / Not automated decision
  - ``by_source_type``          — Article 16 notice / Trusted flagger / Own-initiative / Other
  - ``by_decision_visibility``  — the restriction applied (removed / disabled / demoted / …)
- **platform** — the reporting platform (``platform_name``), lightly cleaned.
- **period** — reporting month ``YYYY-MM`` (the SoR ``created_at`` month).
- **category** — the dimension value for that section (``All`` for ``totals``).
- **metric** — always ``statements`` (a count of SoRs).
- **unit** — always ``count``.
- **value** — the SoR count.

Aggregation notes / caveats (see also the API CLAUDE.md):
- The single-select cuts (``by_category`` / ``by_decision_ground`` /
  ``by_automated_detection`` / ``by_automated_decision`` / ``by_source_type``)
  each partition the platform-month total, so summing a cut's categories
  reproduces ``totals`` — do NOT sum a cut *together with* ``totals`` (double
  counts). ``by_decision_visibility`` is a **multi-select** facet (one SoR can
  carry several restriction types), so its rows do NOT sum to the total.
- Pin a ``section`` (and usually a ``platform``) before aggregating; SoR volumes
  are dominated by a few marketplaces (Google Shopping / product delistings), so
  cross-platform sums are heavily skewed.

Usage::

    # one-shot: download the aggregates and build in one go (needs `dsa-tdb`)
    python build_dsa_tdb.py --from 2023-09-01 --to 2026-05-01

    # reuse an already-downloaded aggregates dir (skips the download)
    python build_dsa_tdb.py --aggs-dir /tmp/aggs_full

`dsa-tdb` is installed from the Commission's package index (kept out of the API
image — this is a build-time-only dependency, like every other sibling builder)::

    pip install dsa-tdb --index-url https://code.europa.eu/api/v4/projects/943/packages/pypi/simple
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys
import tempfile

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dsa-tdb.json")

SOURCE = "https://transparency.dsa.ec.europa.eu/ (via the Commission's dsa-tdb toolbox)"

# ── label maps (canonical DB codes → readable English) ────────────────────────
GROUND = {
    "DECISION_GROUND_ILLEGAL_CONTENT": "Illegal content",
    "DECISION_GROUND_INCOMPATIBLE_CONTENT": "Incompatible with terms",
}
ADEC = {
    "AUTOMATED_DECISION_FULLY": "Fully automated",
    "AUTOMATED_DECISION_PARTIALLY": "Partially automated",
    "AUTOMATED_DECISION_NOT_AUTOMATED": "Not automated",
}
SRC = {
    "SOURCE_ARTICLE_16": "Article 16 notice",
    "SOURCE_TRUSTED_FLAGGER": "Trusted flagger",
    "SOURCE_VOLUNTARY": "Own-initiative",
    "SOURCE_TYPE_OTHER_NOTIFICATION": "Other notification",
}
VIS = {
    "DECISION_VISIBILITY_CONTENT_REMOVED": "Content removed",
    "DECISION_VISIBILITY_CONTENT_DISABLED": "Access disabled",
    "DECISION_VISIBILITY_CONTENT_DEMOTED": "Demoted",
    "DECISION_VISIBILITY_CONTENT_AGE_RESTRICTED": "Age-restricted",
    "DECISION_VISIBILITY_CONTENT_INTERACTION_RESTRICTED": "Interaction restricted",
    "DECISION_VISIBILITY_CONTENT_LABELLED": "Labelled",
    "DECISION_VISIBILITY_OTHER": "Other visibility restriction",
}


# A few DSA statement-category codes don't read well under the generic rule.
CAT_OVERRIDE = {
    "STATEMENT_CATEGORY_OTHER_VIOLATION_TC": "Other (terms violation)",
    "STATEMENT_CATEGORY_NON_CONSENSUAL_BEHAVIOUR": "Non-consensual behaviour",
}


def _cat(code: str) -> str:
    """STATEMENT_CATEGORY_SCAMS_AND_FRAUD -> 'Scams and fraud'."""
    if code in CAT_OVERRIDE:
        return CAT_OVERRIDE[code]
    return str(code).replace("STATEMENT_CATEGORY_", "").replace("_", " ").capitalize()


def _clean_platform(name: object) -> str:
    return str(name).replace("\\", "").replace('"', "").strip()


def download_aggs(from_date: str, to_date: str) -> str:
    """Fetch the global 'simple' monthly aggregates via dsa-tdb into a temp dir."""
    out = tempfile.mkdtemp(prefix="dsa_tdb_aggs_")
    os.rmdir(out)  # download-aggs wants a non-existent folder
    cmd = [
        "dsa-tdb-cli", "download-aggs", "-o", out, "--format", "csv",
        "--agg-version", "simple", "-i", from_date, "-f", to_date,
    ]
    print(f"[dsa-tdb] {' '.join(cmd)}", file=sys.stderr)
    subprocess.run(cmd, check=True)
    return out


def load_all(aggs_dir: str) -> pd.DataFrame:
    parts = sorted(glob.glob(
        os.path.join(aggs_dir, "aggregated-simple.csv", "created_at_month=*")))
    if not parts:
        raise SystemExit(f"no monthly partitions under {aggs_dir}")
    frames = []
    for p in parts:
        files = glob.glob(os.path.join(p, "part-*.csv.gz"))
        if not files:
            continue
        frames.append(pd.concat(
            [pd.read_csv(f, compression="gzip") for f in files], ignore_index=True))
    df = pd.concat(frames, ignore_index=True)
    df["platform"] = df["platform_name"].map(_clean_platform)
    df["period"] = pd.to_datetime(df["created_at"]).dt.strftime("%Y-%m")
    print(f"[dsa-tdb] loaded {len(df):,} aggregate rows across "
          f"{df['period'].nunique()} months, {df['platform'].nunique()} platforms",
          file=sys.stderr)
    return df


def build_rows(df: pd.DataFrame, top_platforms: int = 60) -> list[list]:
    # Keep only the highest-volume platforms — the long tail of one-off filers is
    # a rounding error (top 60 ≈ 99.97% of all SoRs) and only noises up the
    # snapshot + the dashboard's platform picker.
    vol = df.groupby("platform")["count"].sum().sort_values(ascending=False)
    keep = set(vol.head(top_platforms).index)
    dropped = len(vol) - len(keep)
    if dropped:
        print(f"[dsa-tdb] keeping top {len(keep)} platforms "
              f"({100 * vol.head(top_platforms).sum() / vol.sum():.3f}% of SoRs); "
              f"dropped {dropped} long-tail platforms", file=sys.stderr)
    df = df[df["platform"].isin(keep)]

    rows: list[list] = []

    def single(section: str, col: str, label) -> None:
        sub = df[df[col].notna()]
        g = sub.groupby(["platform", "period", col])["count"].sum().reset_index()
        for _, r in g.iterrows():
            rows.append([section, r["platform"], r["period"], label(r[col]),
                         "statements", "count", int(r["count"])])

    # totals (category = All)
    gt = df.groupby(["platform", "period"])["count"].sum().reset_index()
    for _, r in gt.iterrows():
        rows.append(["totals", r["platform"], r["period"], "All",
                     "statements", "count", int(r["count"])])

    single("by_category", "category", _cat)
    single("by_decision_ground", "decision_ground", lambda v: GROUND.get(v, v))
    single("by_automated_detection", "automated_detection", lambda v: str(v))
    single("by_automated_decision", "automated_decision", lambda v: ADEC.get(v, v))
    single("by_source_type", "source_type", lambda v: SRC.get(v, v))

    # multi-select: decision-visibility flags (a SoR may carry several)
    for col, lbl in VIS.items():
        if col not in df.columns:
            continue
        sub = df[df[col] == True]  # noqa: E712 (pandas boolean mask)
        g = sub.groupby(["platform", "period"])["count"].sum().reset_index()
        for _, r in g.iterrows():
            rows.append(["by_decision_visibility", r["platform"], r["period"],
                         lbl, "statements", "count", int(r["count"])])

    # deterministic order
    rows.sort(key=lambda r: (r[0], r[1], r[2], r[3]))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--aggs-dir", help="pre-downloaded dsa-tdb aggregates dir")
    ap.add_argument("--from", dest="from_date", default="2023-09-01")
    ap.add_argument("--to", dest="to_date", default="2026-05-01")
    ap.add_argument("-o", "--out", default=OUT)
    ap.add_argument("--top-platforms", type=int, default=60,
                    help="keep only the N highest-volume platforms (default 60)")
    args = ap.parse_args()

    aggs_dir = args.aggs_dir or download_aggs(args.from_date, args.to_date)
    df = load_all(aggs_dir)
    rows = build_rows(df, top_platforms=args.top_platforms)

    periods = sorted({r[2] for r in rows})
    coverage = f"{periods[0]}..{periods[-1]}" if periods else ""
    out = {
        "source": SOURCE,
        "coverage": coverage,
        "columns": ["section", "platform", "period", "category", "metric", "unit", "value"],
        "rows": rows,
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    print(f"[dsa-tdb] wrote {len(rows):,} rows -> {args.out} (coverage {coverage})",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
