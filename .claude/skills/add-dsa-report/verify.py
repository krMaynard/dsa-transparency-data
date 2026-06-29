#!/usr/bin/env python3
"""Verify a newly-added DSA harmonised-template report landed end-to-end.

Two independent checks:
  [data] harmonised-reports/extracted/<slug>/NN_*.csv exist and have rows
         (+ the manifest entry: provider / period / sections_found), and
  [api]  the sibling transparency-report-api's seeded demo.db makes the report
         queryable — a services row for the display name with fact rows across
         t3..t11, and a reports row carrying its period + tier.

This queries the actual seeded SQLite DB the API serves (read-only) — it's the
"is it really queryable" check, not a re-run of the extractor. Uses only the
Python stdlib (sqlite3), so it needs no extra tooling.

Usage:
    python3 verify.py <slug> ["Display Name"]
    python3 verify.py gemini "Gemini"

Exit 0 = extracted and queryable (or extracted with a clear note to reseed).
Exit 1 = a check failed.
"""
import glob
import json
import os
import sqlite3
import sys
from contextlib import closing

HERE = os.path.dirname(os.path.abspath(__file__))
# .claude/skills/add-dsa-report/ -> data-repo root is three levels up.
DATA_REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EXTRACTED = os.path.join(DATA_REPO, "harmonised-reports", "extracted")
MANIFEST = os.path.join(DATA_REPO, "harmonised-reports", "manifest.json")
API_REPO = os.path.abspath(os.path.join(DATA_REPO, "..", "transparency-report-api"))
DB = os.path.join(API_REPO, "demo.db")

TABLES = ["t3_member_state_orders", "t4_notices", "t5_own_initiative_illegal",
          "t6_own_initiative_tos", "t7_appeals_recidivism", "t8_automated_means",
          "t9_human_resources", "t10_amar", "t11_qualitative"]


def fail(msg: str) -> None:
    print("FAIL: " + msg)
    sys.exit(1)


def main() -> None:
    if len(sys.argv) < 2:
        fail('usage: verify.py <slug> ["Display Name"]')
    slug = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else None

    # ── [data] extraction ────────────────────────────────────────────────────
    d = os.path.join(EXTRACTED, slug)
    if not os.path.isdir(d):
        fail(f"no extracted dir: {d}\n  -> add it to harmonised-reports/extract.py "
             f"SOURCES (+ SHEET_MAP if format-variant), then run extract.py")
    csvs = sorted(glob.glob(os.path.join(d, "[0-9]*_*.csv")))
    with_rows = []
    for c in csvs:
        with open(c, encoding="utf-8") as fh:
            if sum(1 for _ in fh) > 1:
                with_rows.append(os.path.basename(c))
    if not with_rows:
        fail(f"extracted/{slug}: all {len(csvs)} section CSVs are empty")
    print(f"[data] extracted/{slug}: {len(with_rows)}/{len(csvs)} sections have rows")
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as fh:
            manifest = json.load(fh)
        m = next((x for x in manifest if x["platform"] == slug), None)
        if m:
            print(f"[data] manifest: provider={m.get('provider') or '?'} "
                  f"period={m['period_start']}..{m['period_end']} "
                  f"sections={m['sections_found']}/11")
        else:
            print(f'[data] WARN: no manifest entry for "{slug}" (re-run extract.py)')

    # ── [api] queryable in the seeded DB ──────────────────────────────────────
    if not os.path.exists(DB):
        print(f"[api] no demo.db at {DB}")
        print("[api] reseed first (in transparency-report-api):")
        print("        python seed.py --source data/vlop-dsa.json "
              "--report-locations data/report-locations.csv")
        return
    with closing(sqlite3.connect(DB)) as db:
        if name:
            svc = db.execute("SELECT id, name, platform FROM services WHERE name = ?",
                             (name,)).fetchone()
        else:
            svc = db.execute("SELECT id, name, platform FROM services WHERE name LIKE ?",
                             (f"%{slug}%",)).fetchone()
        if not svc:
            who = f'name="{name}"' if name else f'slug~"{slug}"'
            fail(f"no services row for {who} — check seed_harmonised.SLUG_META, then reseed")
        sid, sname, splat = svc
        print(f'[api] service: id={sid} name="{sname}" platform="{splat}"')
        total = 0
        for t in TABLES:
            n = db.execute(f"SELECT COUNT(*) FROM {t} WHERE service_id = ?", (sid,)).fetchone()[0]
            if n:
                print(f"[api]   {t}: {n}")
                total += n
        if not total:
            fail(f'service "{sname}" has no fact rows in any t3..t11 table')
        rep = db.execute(
            "SELECT period_start, period_end, tier FROM reports WHERE id = "
            "(SELECT report_id FROM t4_notices WHERE service_id = ? LIMIT 1)", (sid,)).fetchone()
        if rep:
            print(f"[api] report: {rep[0]} .. {rep[1]}  tier={rep[2]}")
        print(f'\nOK: "{sname}" is extracted and queryable ({total} fact rows across t3..t11).')


if __name__ == "__main__":
    main()
