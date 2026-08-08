#!/usr/bin/env python3
"""Build the California AB 587 Terms-of-Service report catalogue.

California's **AB 587** (Bus. & Prof. Code §§ 22675-22681) requires social-media
companies with >$100M revenue to file a **semiannual Terms-of-Service Report**
with the California Attorney General describing how their terms of service define
and enforce categories of content (hate speech, extremism, disinformation,
harassment, foreign political interference), how automated moderation works, and
data on terms-of-service violations. The AG publishes every filing in a public
repository:

  https://oag.ca.gov/ab587/submissions

This is the California analogue of New York's Stop-Hiding-Hate-Act ToS reports —
same content categories, a US-state Attorney-General filing repository, archived
PDFs. This script scrapes that repository into a flat catalogue (one row per
filing) and mirrors the PDFs, exactly like the NY ToS catalogue.

`build_ab587.py` parses the archived listing page (`raw/submissions.html`) into
`ca_ab587_reports.csv`. With `--download` it first refreshes the listing and
downloads every report PDF into `pdfs/`, recording each file's sha256 + size.
Companion `extract_narrative.py` pulls the prose of those PDFs for full-text
search.

Catalogue columns:

  company, platform, period, period_original, access, source_url, filename,
  archived, sha256, bytes

- **company** — the filer, as it appears in the repository (kept verbatim).
- **platform** — a normalised brand for grouping (Discord / TikTok / X / …),
  derived from the company + filename via `PLATFORMS`; "" when unrecognised.
- **period** — the reporting half-year, normalised (`2025 H2`); the partial
  first filings stay `2023 Q3` / `2023 Q4`.
- **period_original** — the repository's own label (`Q3/Q4 2025`).
- **access** — always `public` (the AG mirrors every filing).
- **source_url** — the PDF on oag.ca.gov (the authoritative, stable location).
- **filename** — the local filename under `pdfs/` used by `extract_narrative.py`.
- **archived / sha256 / bytes** — populated when the PDF exists in the repository
  mirror under ``pdfs/``.

Deterministic from `raw/submissions.html` and the archived PDFs. `--download` is
the only networked path. Pure stdlib.
"""
from __future__ import annotations

import argparse
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import html as _html
import os
import re
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_HTML = os.path.join(HERE, "raw", "submissions.html")
PDF_DIR = os.path.join(HERE, "pdfs")
OUT_CSV = os.path.join(HERE, "ca_ab587_reports.csv")
REPO_RAW = (
    "https://github.com/krMaynard/dsa-transparency-data/blob/main/"
    "ca-ab587/pdfs/"
)

LISTING_URL = "https://oag.ca.gov/ab587/submissions"
COLUMNS = ["company", "platform", "period", "period_original", "access",
           "source_url", "filename", "archived", "sha256", "bytes"]

# Normalised brand for grouping, matched (case-insensitive substring) against the
# company + filename. First match wins, so order the more specific ones first.
PLATFORMS = [
    ("BAND", ("band", "naver")), ("Discord", ("discord",)),
    ("GitHub", ("github",)), ("Goodreads", ("goodreads",)),
    ("Hudl", ("hudl", "agile sports")), ("LinkedIn", ("linkedin",)),
    ("Meta", ("meta", "facebook", "instagram")), ("Microsoft", ("microsoft",)),
    ("Nextdoor", ("nextdoor",)), ("Peloton", ("peloton",)),
    ("Pinterest", ("pinterest",)), ("Reddit", ("reddit",)),
    ("Roblox", ("roblox",)), ("Sketchfab", ("sketchfab",)),
    ("ArtStation", ("artstation",)), ("Snap", ("snap",)),
    ("Strava", ("strava",)), ("TikTok", ("tiktok",)),
    ("Vimeo", ("vimeo",)), ("X", ("x corp",)), ("YouTube", ("youtube",)),
]


def _platform(company: str, filename: str) -> str:
    hay = (company + " " + filename).lower()
    for brand, needles in PLATFORMS:
        if any(n in hay for n in needles):
            return brand
    return ""


def _period(original: str) -> str:
    """`Q1/Q2 2025` -> `2025 H1`; `Q3/Q4 2025` -> `2025 H2`; keep single-quarter
    partial filings as `2023 Q3` / `2023 Q4`."""
    m = re.match(r"Q1/Q2\s+(\d{4})", original)
    if m:
        return f"{m.group(1)} H1"
    m = re.match(r"Q3/Q4\s+(\d{4})", original)
    if m:
        return f"{m.group(1)} H2"
    m = re.match(r"Q([1-4])\s+(\d{4})", original)
    if m:
        return f"{m.group(2)} Q{m.group(1)}"
    return original


def _slug(company: str, period: str, url: str) -> str:
    """A stable, filesystem-safe local filename for the archived PDF."""
    base = f"{_platform(company, url) or company} {period}".lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    # Disambiguate same-platform-same-period filings with a short URL hash.
    tag = hashlib.sha256(url.encode()).hexdigest()[:6]
    return f"{base}-{tag}.pdf"


def _parse_listing(html_text: str) -> list[dict]:
    rows: list[dict] = []
    seen: set[str] = set()
    for tr in re.findall(r"<tr[^>]*>.*?</tr>", html_text, re.S):
        if ".pdf" not in tr:
            continue
        cells = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        if len(cells) < 3:
            continue
        company = _html.unescape(re.sub(r"<[^>]+>", "", cells[0])).strip()
        original = _html.unescape(re.sub(r"<[^>]+>", "", cells[1])).strip()
        href = re.search(r'href="([^"]+\.pdf)', tr)
        if not href:
            continue
        url = _html.unescape(href.group(1))
        if url in seen:
            continue
        seen.add(url)
        period = _period(original)
        filename = _slug(company, period, url)
        rows.append({
            "company": company,
            "platform": _platform(company, url),
            "period": period,
            "period_original": original,
            "access": "public",
            "source_url": url,
            "filename": filename,
        })
    rows.sort(key=lambda r: (r["platform"] or r["company"], r["period"], r["source_url"]))
    return rows


def _fetch(url: str, attempts: int = 6) -> bytes:
    """GET with retry/backoff using curl's proven proxy/TLS path."""
    for i in range(attempts):
        p = subprocess.run(
            ["curl", "-fLsS", "--connect-timeout", "20", "--max-time", "180",
             "-A", "dsa-transparency-data/1.0", url],
            capture_output=True,
        )
        if p.returncode == 0 and p.stdout:
            return p.stdout
        error = p.stderr.decode(errors="replace").strip() or f"curl exit {p.returncode}"
        if i == attempts - 1:
            raise RuntimeError(error)
        print(f"  retry {i + 1} after {error}")
        time.sleep(2 ** i)
    raise RuntimeError("unreachable")


def _fetch_to(url: str, dest: str, attempts: int = 6) -> int:
    """Stream a large response to disk and atomically publish it at ``dest``."""
    part = dest + ".part"
    for i in range(attempts):
        resume = ["--continue-at", "-"] if os.path.isfile(part) else []
        p = subprocess.run(
            ["curl", "-fLsS", "--connect-timeout", "20", "--max-time", "300",
             "-A", "dsa-transparency-data/1.0", *resume, "-o", part, url],
            capture_output=True,
        )
        if p.returncode == 0 and os.path.isfile(part) and os.path.getsize(part) > 0:
            os.replace(part, dest)
            return os.path.getsize(dest)
        # Exit 33 means the server rejected the range request. Restart that file
        # on the next attempt. Timeouts retain the partial response for resume.
        if p.returncode == 33:
            try:
                os.remove(part)
            except FileNotFoundError:
                pass
        error = p.stderr.decode(errors="replace").strip() or f"curl exit {p.returncode}"
        if i == attempts - 1:
            try:
                os.remove(part)
            except FileNotFoundError:
                pass
            raise RuntimeError(error)
        print(f"  retry {i + 1} after {error}")
        time.sleep(2 ** i)
    raise RuntimeError("unreachable")


def _download(rows: list[dict], pdf_dir: str, jobs: int = 1) -> int:
    """Mirror every report PDF into `pdf_dir`, skipping ones already present.
    A file that exhausts its retries is logged and skipped (not fatal) so one
    run gets through as many as it can; re-run to pick up the stragglers.
    Returns the number of files still missing after the pass."""
    os.makedirs(pdf_dir, exist_ok=True)
    pending: list[dict] = []
    for r in rows:
        dest = os.path.join(pdf_dir, r["filename"])
        if os.path.isfile(dest) and os.path.getsize(dest) > 0:
            try:
                os.remove(dest + ".part")
            except FileNotFoundError:
                pass
            continue  # resume: already mirrored
        pending.append(r)

    def fetch_one(r: dict) -> tuple[dict, int | None, str | None]:
        dest = os.path.join(pdf_dir, r["filename"])
        try:
            size = _fetch_to(r["source_url"], dest)
        except Exception as e:  # server/proxy kept resetting — skip, re-run later
            return r, None, str(e)
        return r, size, None

    missing = 0
    with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        futures = [pool.submit(fetch_one, r) for r in pending]
        for future in as_completed(futures):
            r, size, error = future.result()
            if error:
                print(f"  SKIP {r['filename']}: {error}")
                missing += 1
            else:
                print(f"downloaded {r['filename']} ({size} bytes)")
    return missing


def _refresh_listing() -> None:
    blob = _fetch(LISTING_URL)  # reuse the retry/backoff — the listing host resets too
    os.makedirs(os.path.dirname(RAW_HTML), exist_ok=True)
    with open(RAW_HTML, "wb") as f:
        f.write(blob)
    print(f"refreshed {RAW_HTML} ({len(blob)} bytes)")


def build(pdf_dir: str = PDF_DIR) -> list[dict]:
    """Build the listing and attach deterministic metadata for mirrored PDFs."""
    with open(RAW_HTML, encoding="utf-8", errors="replace") as f:
        rows = _parse_listing(f.read())
    for r in rows:
        path = os.path.join(pdf_dir, r["filename"])
        if not os.path.isfile(path):
            r["archived"] = r["sha256"] = r["bytes"] = ""
            continue
        h = hashlib.sha256()
        size = 0
        with open(path, "rb") as f:
            if f.read(4) != b"%PDF":
                raise ValueError(f"mirrored file is not a PDF: {path}")
            f.seek(0)
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
                size += len(chunk)
        r["archived"] = REPO_RAW + r["filename"]
        r["sha256"] = h.hexdigest()
        r["bytes"] = str(size)
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=OUT_CSV, help="Output catalogue CSV path")
    ap.add_argument("--pdfs", default=PDF_DIR, help="Dir of the archived PDFs")
    ap.add_argument("--download", action="store_true",
                    help="Refresh the listing + download every report PDF first")
    ap.add_argument("--jobs", type=int, default=1,
                    help="Concurrent PDF downloads (default: 1; 4 is polite and faster)")
    args = ap.parse_args()

    missing = 0
    if args.download:
        _refresh_listing()
        with open(RAW_HTML, encoding="utf-8", errors="replace") as f:
            missing = _download(_parse_listing(f.read()), args.pdfs, jobs=args.jobs)

    rows = build(args.pdfs)
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    archived = sum(1 for r in rows if r["archived"])
    print(f"wrote {args.out}: {len(rows)} filings, "
          f"{len({r['platform'] or r['company'] for r in rows})} platforms, "
          f"{archived} archived")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
