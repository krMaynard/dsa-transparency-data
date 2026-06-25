# PDF DSA transparency reports (archive)

Original **PDF-format** DSA transparency reports for platforms that publish a
narrative / per-section PDF instead of the Annex I machine-readable workbook, so
they can't be extracted into the 1–11 template. Kept here as a faithful archive
of the source documents. Saved as `pdf-reports/<slug>/<file>.pdf`.

Refresh with [`../download_pdfs.py`](../download_pdfs.py), which pulls:
1. every **direct `.pdf` URL** in [`../dsa_reports.csv`](../dsa_reports.csv), and
2. a small **EXTRA** set not catalogued as a single link — eToro's 8 per-section
   PDFs, and the PDF companions Vestiaire/Whatnot ship next to their workbook.

Downloads that aren't a real PDF (a 403 bot-wall / HTML error page) are removed,
not committed.

## Archived (28 platforms, 37 PDFs)

Airbnb · AutoScout24 · AWS · Back Market · BlaBlaCar · Bumble · Deliveroo ·
eToro (8 per-section PDFs) · Eventbrite · FinCompare · GitHub · Happn ·
Hugging Face · Leboncoin · Lovoo · Marktplaats · OVHcloud · Squarespace ·
Start.gg / GroupMe · Trendyol (2024 + 2025) · Trivago · Trustpilot · Viator ·
Wolt · Xbox · zooplus — plus the PDF companions for **Vestiaire Collective** and
**Whatnot** (whose Annex I workbooks are extracted under
[`../harmonised-reports/`](../harmonised-reports/)).

## Not archived (bot-walled)

**Boulanger** and **Rakuten France** sit behind Akamai/Cloudflare and reset or
`403` a headless fetch — they need a real browser session / EU egress. Apple
(App Store / Books / Podcasts / iCloud), GMX, Flickr and Riot publish the report
as rendered HTML (no PDF file to archive).

All files are public reports fetched with a browser User-Agent over HTTPS;
nothing here is behind a login.
