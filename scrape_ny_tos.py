#!/usr/bin/env python3
"""Scrape + archive New York's Social Media Terms-of-Service reports.

New York's **Stop Hiding Hate Act** (S895B / A6789B) requires social-media
platforms with over $100M in annual revenue and NY users to file twice-yearly
*terms-of-service* reports with the state Attorney General, describing how they
define and moderate hateful conduct, disinformation, harassment, etc. The AG
publishes every filing as a narrative policy PDF at:

    https://ag.ny.gov/resources/organizations/social-media-tos-reporting/reports

These are qualitative policy documents, **not** the EU DSA Annex-I machine
-readable workbooks, so they don't fit the 1-11 template extraction — we archive
the original PDFs (like ``download_pdfs.py`` does for PDF-format DSA reports) and
build a flat catalogue alongside them.

Outputs (all regenerated from the live AG site):

* ``ny-tos-reports/pdfs/<period>-<company>[-<platform>].pdf`` — the archived PDFs
* ``ny_tos_reports.csv`` / ``ny_tos_reports.json`` — the catalogue, one row per
  filing (company, platform, period, upload date, source URL, archived path,
  sha256, bytes)

Re-run to refresh:  ``python3 scrape_ny_tos.py``  (network required; like the
other ``download_*`` / ``scrape_*`` scripts it is *not* exercised by CI).
"""
import csv
import hashlib
import html as ihtml
import json
import os
import re
import subprocess
from urllib.parse import urljoin

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "ny-tos-reports")
PDF_DIR = os.path.join(OUT_DIR, "pdfs")
CSV_PATH = os.path.join(HERE, "ny_tos_reports.csv")
JSON_PATH = os.path.join(HERE, "ny_tos_reports.json")

BASE = "https://ag.ny.gov"
INDEX = BASE + "/resources/organizations/social-media-tos-reporting/reports"
REPO_RAW = ("https://github.com/krMaynard/dsa-transparency-data/blob/main/"
            "ny-tos-reports/pdfs/")

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36")
CA = os.environ.get("CUSTOM_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")

FIELDNAMES = ["company", "platform", "period", "upload_date", "access",
              "source_url", "filename", "archived", "sha256", "bytes"]


def _curl(url: str, dest: str | None = None) -> tuple[int, bytes]:
    """Fetch ``url``; if ``dest`` is given save there. Returns (http_code, body)."""
    cmd = ["curl", "-sS", "-L", "--max-time", "120", "-A", UA, "-w", "%{http_code}"]
    if os.path.exists(CA):
        cmd += ["--cacert", CA]
    if dest:
        cmd += ["-o", dest]
    cmd.append(url)
    p = subprocess.run(cmd, capture_output=True)
    if dest:
        code = int(p.stdout.decode(errors="replace").strip() or 0)
        return code, b""
    # body + trailing 3-digit code on stdout
    body = p.stdout
    code = 0
    tail = body[-3:].decode(errors="replace")
    if tail.isdigit():
        code = int(tail)
        body = body[:-3]
    return code, body


def _clean(s: str) -> str:
    return ihtml.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def parse_rows(html: str) -> list[dict]:
    """Parse the AG reports table into raw {company, platform, period, ...} dicts."""
    m = re.search(r"<table.*?</table>", html, re.S)
    if not m:
        return []
    rows = re.findall(r"<tr.*?</tr>", m.group(0), re.S)
    out = []
    for tr in rows:
        def cell(field: str) -> str:
            c = re.search(r"views-field-field-" + field + r'"[^>]*>(.*?)</td>',
                          tr, re.S)
            return c.group(1) if c else ""
        href = re.search(r'href="([^"]*\.pdf)"', cell("media-file-1"))
        if not href:                       # header row / no file
            continue
        out.append({
            "company": _clean(cell("social-media-company")),
            "platform": _clean(cell("child-companies")),
            "period": _clean(cell("submission-period")),
            "upload_date": _clean(cell("upload-date")),
            "source_url": urljoin(BASE, href.group(1)),
        })
    return out


def fetch_index() -> list[dict]:
    """Walk every pager page of the index and collect all report rows."""
    rows: list[dict] = []
    page = 0
    while True:
        url = INDEX if page == 0 else f"{INDEX}?page={page}"
        code, body = _curl(url)
        if code != 200 or not body:
            break
        got = parse_rows(body.decode("utf-8", errors="replace"))
        if not got:
            break
        rows.extend(got)
        # stop when the pager has no higher page link than the current one
        if not re.search(rf'[?&]page={page + 1}\b',
                         body.decode("utf-8", errors="replace")):
            break
        page += 1
    return rows


def local_filename(row: dict, taken: set[str]) -> str:
    """Deterministic, collision-free local name: period-company[-platform].pdf.

    Some companies file separate reports for different child platforms under the
    same source filename (e.g. Amazon's Twitch vs GoodReads Q4 reports), so the
    platform is appended whenever it adds a distinction.
    """
    period = slugify(row["period"])                       # 2025-q4
    parts = [period, slugify(row["company"])]
    plat = slugify(row["platform"])
    if plat and plat != "other":
        parts.append(plat)
    base = "-".join(p for p in parts if p)
    name = f"{base}.pdf"
    n = 2
    while name in taken:                                  # last-resort guard
        name = f"{base}-{n}.pdf"
        n += 1
    taken.add(name)
    return name


def main() -> None:
    os.makedirs(PDF_DIR, exist_ok=True)
    rows = fetch_index()
    print(f"{len(rows)} reports listed on the AG index")

    taken: set[str] = set()
    catalogue: list[dict] = []
    ok = gated = 0
    for row in sorted(rows, key=lambda r: (r["period"], r["company"], r["platform"])):
        fn = local_filename(row, taken)
        dest = os.path.join(PDF_DIR, fn)
        code, _ = _curl(row["source_url"], dest)
        magic = b""
        try:
            with open(dest, "rb") as fh:
                magic = fh.read(4)
        except OSError:
            pass
        rec = {
            "company": row["company"],
            "platform": row["platform"],
            "period": row["period"],
            "upload_date": row["upload_date"],
            "source_url": row["source_url"],
        }
        if magic == b"%PDF":
            data = open(dest, "rb").read()
            rec.update(access="public", filename=fn, archived=REPO_RAW + fn,
                       sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
            ok += 1
            print(f"OK    {fn:55} ({code}, {len(data):>9,} B)")
        else:
            # The AG serves newer filings from a private Drupal webform directory
            # that 302-redirects anonymous requests to a login page, so they
            # can't be archived — catalogue them with their source URL only.
            if os.path.exists(dest):
                os.remove(dest)
            rec.update(access="auth-required", filename="", archived="",
                       sha256="", bytes="")
            gated += 1
            print(f"GATED {fn:55} (login-walled at source)")
        catalogue.append(rec)

    catalogue.sort(key=lambda r: (r["period"], r["company"], r["platform"]))
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(catalogue)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(catalogue, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\n{ok} archived, {gated} login-gated (catalogued only) → "
          f"{os.path.relpath(CSV_PATH, HERE)}, {os.path.relpath(JSON_PATH, HERE)}")


if __name__ == "__main__":
    main()
