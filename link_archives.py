#!/usr/bin/env python3
"""Annotate REPORT_LOCATIONS.md with links to the files we archived in this repo.

For each catalogue entry whose report we downloaded, append a repo-relative link
to its archived location into the "Report URL" cell:
  * harmonised-reports/extracted/<slug>/  — the extracted 1-11 template CSVs
  * pdf-reports/<slug>/                    — the archived PDF(s)
so the catalogue makes clear what is mirrored here. Idempotent (re-running adds
nothing new). build_reports_db.py carries these into dsa_reports.csv's `archived`
column (as absolute GitHub URLs).

Run after archiving new reports, then rebuild:
    python3 link_archives.py && python3 build_reports_db.py
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(HERE, "REPORT_LOCATIONS.md")

# Harmonised (extracted) platforms: catalogue name -> extracted/<slug>.
HARMONISED = {
    "AboutYou": "aboutyou", "Bumble (Badoo, Fruitz)": "bumble",
    "Carrefour Marketplace": "carrefour", "Ceneo": "ceneo", "Cloudflare": "cloudflare",
    "Dailymotion": "dailymotion", "DuckDuckGo": "duckduckgo", "Expedia": "expedia",
    "Grindr": "grindr", "HomeToGo": "hometogo", "Hostelworld": "hostelworld",
    "Hostinger": "hostinger", "Hotels.com": "hotelscom", "IMDb": "imdb",
    "Konami": "konami", "Lilo": "lilo", "LinkedIn": "linkedin", "ManoMano": "manomano",
    "Match Group (Tinder, Hinge, OkCupid, Meetic, …)": "matchgroup",
    "Niantic (Pokémon GO, …)": "niantic", "Pinterest": "pinterest", "Qwant": "qwant",
    "Roblox": "roblox", "Shopify": "shopify", "Skroutz": "skroutz",
    "Veepee (vente-privee)": "veepee", "Vestiaire Collective": "vestiaire",
    "Vinted": "vinted", "Vrbo": "vrbo", "Web.de": "webde", "Whatnot": "whatnot",
    "Wikipedia": "wikipedia", "Yahoo (+ AOL)": "yahoo",
}
# PDF-archive slugs that aren't slugify(platform).
PDF_SLUG_OVERRIDE = {"eToro (social/copy-trading)": "etoro"}


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def archive_links(platform: str) -> list[tuple[str, str]]:
    """(label, repo-relative path) for each archived artifact of this platform."""
    out = []
    h = HARMONISED.get(platform)
    if h and os.path.isdir(os.path.join(HERE, "harmonised-reports", "extracted", h)):
        out.append(("archived data", f"harmonised-reports/extracted/{h}"))
    p = PDF_SLUG_OVERRIDE.get(platform) or slugify(platform)
    if os.path.isdir(os.path.join(HERE, "pdf-reports", p)):
        out.append(("archived PDF", f"pdf-reports/{p}"))
    return out


def main() -> None:
    with open(MD, encoding="utf-8") as f:
        lines = f.read().split("\n")
    annotated = 0
    for i, line in enumerate(lines):
        if not line.startswith("|"):
            continue
        # Same robust split as build_reports_db.py — tolerate a missing trailing pipe.
        raw = [c.strip() for c in line.split("|")]
        cells = raw[1:-1] if raw and raw[-1] == "" else raw[1:]
        if len(cells) != 5 or cells[0].lower() == "platform" or set(cells[0]) <= {"-", ":"}:
            continue
        links = archive_links(cells[0])
        if not links:
            continue
        if "harmonised-reports/extracted/" in cells[2] or "pdf-reports/" in cells[2]:
            continue  # already annotated
        cells[2] += " · " + " · ".join(f"[{lbl}]({rel})" for lbl, rel in links)
        lines[i] = "| " + " | ".join(cells) + " |"
        annotated += 1
    with open(MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"annotated {annotated} catalogue rows with archive links")


if __name__ == "__main__":
    main()
