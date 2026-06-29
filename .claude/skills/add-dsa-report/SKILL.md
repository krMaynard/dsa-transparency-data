---
name: add-dsa-report
description: Add / ingest a new DSA transparency report (an EU harmonised-template workbook or zip — e.g. a newly-published Article 15/24 report) into the dsa-transparency-data + transparency-report-api repos so it becomes queryable. Use when given a new platform's harmonised-template .xlsx/.zip/.xls and asked to add, ingest, onboard, or surface it.
---

# Add a new DSA transparency report

A new report is an **EU harmonised-template** workbook (Implementing Regulation
2024/2835 — the fixed 11-section tables 1–11) published by a platform, as a
multi-sheet `.xlsx`/`.xls` or a `.zip` of one CSV per section. Adding it spans
**two sibling repos**:

- **`dsa-transparency-data`** (this repo) — extract the workbook into the
  canonical `extracted/<slug>/NN_<section>.csv`, archive the raw file, and
  record it in the catalogue.
- **`transparency-report-api`** (`../transparency-report-api`) — name the
  platform in `SLUG_META`, re-vendor the snapshot, and reseed so it's queryable.

Paths below are **relative to this repo's root** (`dsa-transparency-data/`).
The mechanical steps run the existing pipeline scripts; the judgment steps
(display name, tier, catalogue category, format-variant mapping) are called out.

## The driver (verify it landed)

After the steps below, confirm the report extracted **and** became queryable
with the bundled checker — it reads the canonical CSVs and queries the API's
seeded `demo.db` (read-only, stdlib `sqlite3` only — there is no `sqlite3` CLI
in this container):

```bash
python3 .claude/skills/add-dsa-report/verify.py <slug> "<Display Name>"
# worked example:
python3 .claude/skills/add-dsa-report/verify.py gemini "Gemini"
```

Exit 0 + an `OK: "<name>" is extracted and queryable (N fact rows…)` line means
done. Run it last; it's also how you confirm a reseed worked.

## 1. Classify the report

Look before you touch anything — these answers decide the steps:

```bash
ZIP=/path/to/report.zip            # or .xlsx
python3 - "$ZIP" <<'PY'
import sys, zipfile, os
f = sys.argv[1]
if f.endswith(".zip"):
    names = zipfile.ZipFile(f).namelist()
    print("zip entries:"); [print("  ", n) for n in names]
else:
    import openpyxl
    print("sheets:", openpyxl.load_workbook(f, read_only=True).sheetnames)
PY
```

- **Numbered section CSVs** (`1_report_identification.csv` … `11_qualitative.csv`)
  or numbered sheets → `zipcsv` / `xlsx`, mapped automatically by the section
  number in each name. **No `SHEET_MAP` needed.** (Gemini ships exactly this.)
- **Unnumbered or renumbered** sheet/file names → a **format variant**; it needs
  a `SHEET_MAP` entry (see `harmonised-reports/extract.py` — LINE and Discord are
  the examples). If the file isn't the Annex I template at all (a free-form
  summary, or a different report like DMCA/gov requests), **stop** — archive it
  but don't force it into 1–11.
- Read `1_report_identification.csv` (or sheet 1) for the **provider** and
  **reporting period**; check section 10 (`AMAR`): blank values + "Only for
  VLOPs and VLOSEs" ⇒ a **non-VLOP** report (tier ≠ `vlop`).

## 2. Extract (data repo)

Pick a lowercase `<slug>` (e.g. `gemini`). Stage the raw file under its slug and
register it in `SOURCES`:

```bash
cp "$ZIP" harmonised-reports/raw/gemini.zip
```

Add one line to the `SOURCES` dict in `harmonised-reports/extract.py`
(`xlsx` | `xls` | `zipcsv`; `zipmulti` only for a multi-product zip like Miniclip):

```python
    "gemini":      ("gemini.zip", "zipcsv"),
```

Then extract and eyeball the result:

```bash
cd harmonised-reports && python3 extract.py 2>&1 | grep -iE "gemini|error|traceback"
# -> gemini  zipcsv  11/11 sections, 4625 data rows
for f in extracted/gemini/*.csv; do n=$(($(wc -l < "$f")-1)); [ "$n" -gt 0 ] && echo "  $(basename $f): $n"; done
cd ..
```

`extract.py` rewrites `manifest.json` + `summary.csv`. Confirm the manifest's
`provider`/`period_start`/`period_end` look right (it parses them from section 1).

## 3. Catalogue + archive (data repo)

1. **`harmonised-reports/sources.csv`** — add `Gemini,extracted,<report-url>`.
2. **`REPORT_LOCATIONS.md`** — add a row under the right `## <category>` section
   (Platform | Operating company | `[label](url)` | Format/period | Confidence).
   If no category fits (Gemini is a generative-AI assistant — none did), add a
   new `## <category>` section; the category set is data-driven, so it flows
   through. Don't add the `· [archived …]` link by hand — the next step injects it.
3. **`link_archives.py`** — add `"Gemini": "gemini",` to the `HARMONISED` dict
   (catalogue display name → extracted slug).
4. Reconcile the catalogue links and rebuild the catalogue DB/CSV:

```bash
python3 link_archives.py && python3 build_reports_db.py 2>&1 | tail -1
grep -E "^Gemini," dsa_reports.csv   # expect harmonised_template=yes + a github archive URL
```

5. Bump the counts + extracted list in `harmonised-reports/README.md`.

## 4. Surface in the API (`../transparency-report-api`)

1. **`seed_harmonised.py`** `SLUG_META` — add `"gemini": ("Gemini", "online-platform"),`
   (`online-platform` | `hosting` | `intermediary` — tier is informational; pick
   by what the service is. Non-VLOP, so never `vlop`.)
2. Re-vendor the snapshot + catalogue from this data repo, then reseed:

```bash
cd ../transparency-report-api
python scripts/revendor_data.py --summary-out -   # must say "All extracted platforms are curated in SLUG_META. ✅"
python seed.py --source data/vlop-dsa.json --report-locations data/report-locations.csv 2>&1 | tail -2
```

If `revendor_data.py` lists the slug under "need a `SLUG_META` entry", you
missed step 4.1 — add it and re-run.

## 5. Verify + ship

```bash
cd ../dsa-transparency-data
python3 .claude/skills/add-dsa-report/verify.py gemini "Gemini"   # expect exit 0, OK line
```

Then commit on the working branch and open PRs in **both** repos (data repo:
extractor + extracted/ + raw/ + catalogue + this skill; API repo: `SLUG_META`
+ re-vendored `data/`). The API CI runs `pyflakes`/`mypy`/`pytest`; run
`python -m pytest test_api.py -q` locally first.

## Gotchas

- **Numbered names need no `SHEET_MAP`.** `extract.py` maps by the section number
  parsed from each sheet/file name; a zip of `1_…csv … 11_…csv` (Gemini) Just
  Works as `zipcsv`. Only reach for `SHEET_MAP` when names are unnumbered (LINE)
  or renumbered (Discord).
- **Non-VLOP ⇒ AMAR (section 10) is blank** and tagged "Only for VLOPs and
  VLOSEs". That's expected; `manifest.amar_eu_total` stays empty. Don't treat the
  blank section as a parse failure.
- **Row counts shrink between extract and seed.** The seeder drops aggregate
  "total" rows / mis-parsed junk and flags `is_total` (e.g. Gemini t8 35→30,
  t11 181→17). Fewer fact rows than CSV rows is correct, not data loss.
- **`_Ads` sibling files are an ads-surface breakdown, not a duplicate.** A few
  Google zips (Hotels, Workspace) ship `NN_<section>_Ads.csv` alongside the base
  `NN_<section>.csv` for sections 6–8. Both label their `Applicability` column
  `All`, but in Google's own VLOP reporting these are the additive, non-overlapping
  **Core** and **Ads** surfaces (there is no aggregate `All` surface). `extract.py`
  (`_merge_ads_surfaces`) folds the `_Ads` rows into the base section with a
  trailing `Surface` column (`Core` for the base, `Ads` for the `_Ads` rows); the
  API seeder reads that last cell. Don't "fix" the apparent section-number
  collision by dropping the `_Ads` file — that silently discards the ads figures.
- **A genuinely new platform type is fine.** Gemini had no matching catalogue
  category, so a new `## AI assistants & generative AI` section was added — the
  catalogue + API facet categories dynamically, so nothing else needs editing.
- **`link_archives.py` is reconcile, not append**, and matches injected links by
  their repo path (not the label) — so re-running is idempotent and multi-file
  rows (Miniclip's per-game links) don't duplicate. Safe to re-run any time.
- **No `sqlite3` CLI in this container** — `verify.py` uses Python's stdlib
  `sqlite3`. Don't rewrite it to shell out to a `sqlite3` binary.
- **The API `demo.db` is git-ignored** and built by `seed.py`. `verify.py`'s
  `[api]` check needs a fresh reseed (step 4.2) to reflect the new report.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `extract.py` puts rows in the wrong section (or 0 sections found) | Names lack a usable section number → add a `SHEET_MAP[slug]` mapping each name to its canonical 1–11, like LINE/Discord. |
| `revendor_data.py` flags the slug as needing a `SLUG_META` entry | Add it to `seed_harmonised.py SLUG_META` and re-run revendor. |
| `verify.py` `[data]` ok but `[api]` says "no services row" | You didn't reseed after editing `SLUG_META` (step 4.2), or the display name passed to `verify.py` doesn't match `SLUG_META`. |
| Catalogue row shows `harmonised_template` ≠ `yes` | The `Format / period` cell in `REPORT_LOCATIONS.md` needs a keyword like "harmonised template" / "Art. 15 template" (`build_reports_db.py` derives the flag from it). |
