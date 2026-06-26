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
    "Wikipedia": "wikipedia", "Yahoo (+ AOL)": "yahoo", "Depop": "depop", "Nexon": "nexon",
    "Nintendo eShop": "nintendo", "Square Enix": "squareenix", "Alibaba Cloud": "alibabacloud",
    # Miniclip ships one report per game in a single zip -> one extracted dir each.
    "Miniclip": ["miniclip-8-ball-pool", "miniclip-agar-io", "miniclip-baseball-clash",
                 "miniclip-mini-football", "miniclip-mini-tennis", "miniclip-paint-brawl",
                 "miniclip-speed-stars", "miniclip-ultimate-golf"],
}
# PDF-archive slugs that aren't slugify(platform).
PDF_SLUG_OVERRIDE = {"eToro (social/copy-trading)": "etoro"}


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _has_files(rel: str) -> bool:
    d = os.path.join(HERE, rel)
    return os.path.isdir(d) and any(not n.startswith(".") for n in os.listdir(d))


def archive_links(platform: str) -> list[tuple[str, str]]:
    """(label, repo-relative path) for each *non-empty* archived artifact dir.
    A platform maps to one harmonised slug, or a list of them (Miniclip's games)."""
    out = []
    h = HARMONISED.get(platform)
    slugs = h if isinstance(h, list) else [h] if h else []
    for s in slugs:
        if _has_files(f"harmonised-reports/extracted/{s}"):
            # label per-game when there are several (else just "archived data")
            label = "archived data" if len(slugs) == 1 else s.split("-", 1)[-1].replace("-", " ")
            out.append((label, f"harmonised-reports/extracted/{s}"))
    p = PDF_SLUG_OVERRIDE.get(platform) or slugify(platform)
    if _has_files(f"pdf-reports/{p}"):
        out.append(("archived PDF", f"pdf-reports/{p}"))
    return out


# Existing archive annotations, so a re-run reconciles (removes stale links whose
# dir went away, adds new ones) rather than only appending.
_ARCHIVE_RE = re.compile(r"(?: · \[archived[^\]]*\]\([^)]*\))+")


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
        base = _ARCHIVE_RE.sub("", cells[2]).rstrip()   # strip any prior annotation
        links = archive_links(cells[0])
        new = base + ("" if not links else " · " + " · ".join(f"[{lbl}]({rel})" for lbl, rel in links))
        if new != cells[2]:
            cells[2] = new
            lines[i] = "| " + " | ".join(cells) + " |"
            annotated += 1
    with open(MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"reconciled {annotated} catalogue rows' archive links")


if __name__ == "__main__":
    main()
