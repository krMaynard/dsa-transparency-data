# AB 587 quantitative extraction

`extract_quant.py` produces `ca_ab587_normalized.csv`, a conservative extraction
of statutory-category enforcement cells from 12 early AB 587 filings. It covers
Discord, LinkedIn, Reddit, Roblox, Snap, and TikTok across 2023 Q3 through 2024
H1. Every cell retains the original category label, metric, source PDF, page,
unit, grain, and reported geographic scope.

This is a floor, not an exhaustive transcription. PDF layouts are inconsistent;
only tables that can be reproduced without inventing labels are included. Snap's
global and United States tables are separated. Reddit category totals and
breakdowns are distinguished by `grain`. Several post-2024 filings omit the
section 22677(a)(5) statistics following the federal injunction against AB 587,
so absence in later periods is not a zero and is not backfilled.

The five normalized category keys match New York's Stop Hiding Hate Act keys.
Only the category dimension is aligned. Metrics remain the companies' own and
are not necessarily comparable between companies, laws, scopes, or filings.

Rebuild (requires PyMuPDF):

```bash
python3 extract_quant.py
```
