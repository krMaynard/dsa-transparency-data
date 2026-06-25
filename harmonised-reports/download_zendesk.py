#!/usr/bin/env python3
"""Download harmonised-template files from Zendesk-hosted help-center hubs.

Several `hub-pending` platforms host their DSA report on a Zendesk help center
whose landing page is JS-rendered (so the static-HTML crawl in discover_hubs.py
finds no file link) — but Zendesk exposes the article and its attachments over a
public JSON API that needs no browser:

    https://<help-domain>/api/v2/help_center/en-us/articles/<id>.json
    https://<help-domain>/api/v2/help_center/en-us/articles/<id>/attachments.json

The `<id>` is the number in the article URL (…/hc/en-us/articles/<id>-slug). The
attachments endpoint lists each file's `file_name` + `content_url`; we pick the
newest `.xlsx` (the Annex I template) and save it into raw/. Bumble is the odd
one out — no Zendesk attachment, but the article body links a direct CDN file.

Re-run after the period rolls over (article/attachment IDs change):
    python3 download_zendesk.py    # then: python3 extract.py
"""
import os
import subprocess

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36")
CA = os.environ.get("CUSTOM_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")

# slug -> the resolved .xlsx URL (newest Annex I file).
# Discovered via the help_center attachments API (article IDs in comments):
TARGETS = {
    # support.bumble.com article 28718583113757 — direct CDN link in the body.
    "bumble":    "https://bumbcdn.com/i/big/documents/bumble/bumble_transparency_report_feb_2026_annex_i.xlsx",
    # help.grindr.com article 38555862683795 — "2025 Grindr EU DSA Transparency Report.xlsx".
    "grindr":    "https://help.grindr.com/hc/article_attachments/49509549657235",
    # faq.vestiairecollective.com article 34009544661393 — "…DSA_Transparency Report_2026….xlsx".
    "vestiaire": "https://faq.vestiairecollective.com/hc/article_attachments/45307818834193",
    # help.whatnot.com article 23619888476557 — "Whatnot_2026_DSA.xlsx".
    "whatnot":   "https://help.whatnot.com/hc/article_attachments/43810812888717",
    # depophelp.zendesk.com article 13057572688273 — direct CDN link in the body.
    "depop":     "https://assets.depop.com/web/assets/help-center/depop-eu-dsa-transparency-report-2025.xlsx",
    # playersupport.nexon.com article 46401329736084 — "2025 DSA Transparency Report_NEXON.xlsx".
    "nexon":     "https://playersupport.nexon.com/hc/article_attachments/46401329467028",
}


def main() -> None:
    os.makedirs(RAW, exist_ok=True)
    for slug, url in sorted(TARGETS.items()):
        dest = os.path.join(RAW, f"{slug}.xlsx")
        cmd = ["curl", "-sS", "-L", "--max-time", "90", "-A", UA,
               "-o", dest, "-w", "%{http_code} %{content_type} %{size_download}", url]
        if os.path.exists(CA):            # only in the proxy env; curl errors if absent
            cmd.extend(["--cacert", CA])
        p = subprocess.run(cmd, capture_output=True, text=True)
        # A real .xlsx is a zip → starts with "PK"; drop anything else (an HTML
        # error page / 403 body) so a later extract.py run never tries to parse it.
        magic = b""
        try:
            with open(dest, "rb") as f:
                magic = f.read(2)
        except OSError:
            pass
        is_xlsx = magic == b"PK"
        if not is_xlsx and os.path.exists(dest):
            try:
                os.remove(dest)
            except OSError:
                pass
        print(f"{slug:11} {p.stdout or p.stderr.strip()}  {'OK' if is_xlsx else 'NOT-XLSX'}")


if __name__ == "__main__":
    main()
