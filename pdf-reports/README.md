# PDF DSA transparency reports (archive)

Original **PDF-format** DSA transparency reports for platforms that publish a
narrative / per-section PDF instead of the Annex I machine-readable workbook, so
they can't be extracted into the 1–11 template (see
[`../harmonised-reports/sources.csv`](../harmonised-reports/sources.csv) — the
`hub-pending` *non-template* group). Kept here as a faithful archive of the
source documents.

Refresh with [`../download_pdfs.py`](../download_pdfs.py).

| Platform | Files | Source |
|----------|-------|--------|
| eToro | 8 per-section PDFs (`Transparency-reports-2…9`) | etoro.com DSA transparency page |
| Eventbrite | `Eventbrite-2025-Transparency-Report.pdf` | eventbrite.com blog |
| OVHcloud | `rapport_de_transparence_dsa_ovhcloud_2025.pdf` | corporate.ovhcloud.com |
| Vestiaire Collective | `…2025-Transparency-Report.pdf` | Zendesk help-center attachment (PDF companion to the extracted XLSX) |
| Whatnot | `Whatnot_DSA-Transparency-Report_2026.pdf`, `Whatnot_DSA-Report_2025.pdf` | Zendesk help-center attachments (PDF companions to the extracted XLSX) |

eToro splits the report into per-section PDFs that mirror the template sections
(2 categories, 3 member-state orders, 4 notices, 5 own-initiative, 6 overall
figures, 7 internal complaints, 8 by country/language, 9 statements). Vestiaire
and Whatnot also ship the harmonised XLSX, which is what
[`../harmonised-reports/`](../harmonised-reports/) extracts; their PDFs are kept
here only for completeness.

All files are public reports fetched with a browser User-Agent over HTTPS;
nothing here is behind a login.
