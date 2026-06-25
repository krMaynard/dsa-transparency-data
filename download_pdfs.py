#!/usr/bin/env python3
"""Archive the PDF-format DSA transparency reports.

Some catalogued platforms publish their DSA report as a narrative PDF (or split
per-section PDFs) rather than the Annex I machine-readable workbook, so they
can't be extracted into the 1-11 template (see ../harmonised-reports/sources.csv,
the `hub-pending` non-template group). We still archive the original PDFs here
for the record. Saved as pdf-reports/<platform>/<file>.pdf.

Re-run to refresh:  python3 download_pdfs.py
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36")
CA = os.environ.get("CUSTOM_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")

# platform -> [(saved filename, source URL)]. PDF-only publishers, plus the PDF
# copies that Vestiaire/Whatnot ship alongside their (already-extracted) workbook.
_ETORO = "https://www.etoro.com/wp-content/uploads/2025/02/"
TARGETS = {
    "eventbrite": [("Eventbrite-2025-Transparency-Report.pdf",
                    "https://www.eventbrite.com/blog/wp-content/uploads/2026/03/Eventbrite-2025-Transparency-Report.pdf")],
    "ovhcloud":   [("rapport_de_transparence_dsa_ovhcloud_2025.pdf",
                    "https://corporate.ovhcloud.com/sites/default/files/2025-04/rapport_de_transparence_dsa_ovhcloud_2025.pdf")],
    # eToro publishes the report as 8 per-section PDFs.
    "etoro": [(f.rsplit("/", 1)[-1], _ETORO + f.rsplit("/", 1)[-1]) for f in (
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


def main() -> None:
    for platform, files in sorted(TARGETS.items()):
        out = os.path.join(HERE, "pdf-reports", platform)
        os.makedirs(out, exist_ok=True)
        for name, url in files:
            dest = os.path.join(out, name)
            cmd = ["curl", "-sS", "-L", "--max-time", "120", "-A", UA,
                   "-o", dest, "-w", "%{http_code} %{size_download}", url]
            if os.path.exists(CA):
                cmd.extend(["--cacert", CA])
            p = subprocess.run(cmd, capture_output=True, text=True)
            magic = b""
            try:
                with open(dest, "rb") as f:
                    magic = f.read(4)
            except OSError:
                pass
            ok = magic == b"%PDF"
            if not ok and os.path.exists(dest):
                try:
                    os.remove(dest)
                except OSError:
                    pass
            print(f"{platform}/{name:55} {p.stdout or p.stderr.strip()}  {'OK' if ok else 'NOT-PDF'}")


if __name__ == "__main__":
    main()
