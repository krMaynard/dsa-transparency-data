#!/usr/bin/env python3
"""Archive PDF-format DSA transparency reports.

Many catalogued platforms publish their DSA report as a narrative PDF rather than
the Annex I machine-readable workbook, so they can't be extracted into the 1-11
template. We archive the original PDFs here. Two sources:

1. Every **direct `.pdf` URL** in ../dsa_reports.csv (the catalogue).
2. EXTRA — PDFs not catalogued as a single direct link: eToro's 8 per-section
   PDFs, and the PDF companions Vestiaire/Whatnot ship next to their workbook.

Saved as pdf-reports/<slug>/<file>.pdf. Anything that isn't a real PDF (a 403
bot-wall / HTML error page) is removed, not committed. Some publishers sit behind
Cloudflare/Akamai and will 403 a headless fetch — those are reported and skipped.

Re-run to refresh:  python3 download_pdfs.py
"""
import csv
import os
import re
import subprocess
from urllib.parse import urlsplit, unquote

HERE = os.path.dirname(os.path.abspath(__file__))
CATALOGUE = os.path.join(HERE, "dsa_reports.csv")
OUT = os.path.join(HERE, "pdf-reports")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36")
CA = os.environ.get("CUSTOM_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")

# PDFs that aren't a single catalogued .pdf link. slug -> [(filename, url)].
_ETORO = "https://www.etoro.com/wp-content/uploads/2025/02/"
EXTRA = {
    "etoro": [(f, _ETORO + f) for f in (
        "Transparency-reports-2_categories_names.pdf",
        "Transparency-reports-3_member_states_orders.pdf",
        "Transparency-reports-4_notices.pdf",
        "Transparency-reports-5_own_initiative.pdf",
        "Transparency-reports-6_overall_figures.pdf",
        "Transparency-reports-7_internal_complaints.pdf",
        "Transparency-reports-8_by_country_and_language.pdf",
        "Transparency-reports-9_statements.pdf",
    )],
    "vestiaire": [("Vestiaire-Collective-2025-Transparency-Report.pdf",
                   "https://faq.vestiairecollective.com/hc/article_attachments/34009838733201")],
    "whatnot": [("Whatnot_DSA-Transparency-Report_2026.pdf",
                 "https://help.whatnot.com/hc/article_attachments/43810812885773"),
                ("Whatnot_DSA-Report_2025.pdf",
                 "https://help.whatnot.com/hc/article_attachments/35856106968717")],
}


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _basename(url: str) -> str:
    b = os.path.basename(unquote(urlsplit(url).path))
    return b if b.lower().endswith(".pdf") and len(b) > 8 else ""


def targets() -> list[tuple[str, str, str]]:
    """(slug, filename, url), EXTRA first, then catalogue direct-.pdf rows."""
    out: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str]] = set()
    for slug, files in EXTRA.items():
        for fn, url in files:
            out.append((slug, fn, url))
            seen.add((slug, url))
    with open(CATALOGUE, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            url = (r.get("url") or "").strip()
            if not url.lower().split("?")[0].endswith(".pdf"):
                continue
            slug = slugify(r["platform"])
            if (slug, url) in seen:
                continue
            out.append((slug, _basename(url) or f"{slug}.pdf", url))
            seen.add((slug, url))
    return out


def main() -> None:
    ok = bad = 0
    used: set[str] = set()
    for slug, fn, url in targets():
        dest_dir = os.path.join(OUT, slug)
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, fn)
        # avoid two URLs clobbering the same filename within a platform
        n = 1
        while dest in used:
            stem, ext = os.path.splitext(fn)
            dest = os.path.join(dest_dir, f"{stem}-{n}{ext}")
            n += 1
        used.add(dest)
        cmd = ["curl", "-sS", "-L", "--max-time", "120", "-A", UA,
               "-o", dest, "-w", "%{http_code}", url]
        if os.path.exists(CA):
            cmd.extend(["--cacert", CA])
        p = subprocess.run(cmd, capture_output=True, text=True)
        magic = b""
        try:
            with open(dest, "rb") as fh:
                magic = fh.read(4)
        except OSError:
            pass
        if magic == b"%PDF":
            ok += 1
            print(f"OK   {slug}/{os.path.basename(dest)}  ({p.stdout})")
        else:
            bad += 1
            if os.path.exists(dest):
                try:
                    os.remove(dest)
                except OSError:
                    pass
            print(f"SKIP {slug:24} http={p.stdout or p.stderr.strip()}  {url[:60]}")
    print(f"\n{ok} archived, {bad} skipped (bot-walled / not a PDF)")


if __name__ == "__main__":
    main()
