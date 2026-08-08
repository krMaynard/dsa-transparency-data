# Fetch record: eSafety AI companion apps findings

`www.esafety.gov.au` blocks datacenter IPs (WAF resets/hangs). Run these steps
from a **residential/EU-routed persistent browser session** per
[`../../BROWSER-FETCH-RUNBOOK.md`](../../BROWSER-FETCH-RUNBOOK.md) §1–3. Respect
robots.txt and throttle. **Never fabricate a figure** — if a value isn't legible
in the report, leave its row out and note it.

## 1. Saved sources

Open each URL in the browser and save the rendered page **and** any linked PDF:

- [x] Findings page → `raw/findings-october-2025.html` (full rendered page) and,
      if a PDF/download is offered, `raw/findings-october-2025.pdf`
      <https://www.esafety.gov.au/industry/basic-online-safety-expectations/ai-services/findings-october-2025>
- [x] AI-services hub (index; catch any companion tables/appendix) → `raw/ai-services-hub.html`
      <https://www.esafety.gov.au/industry/basic-online-safety-expectations/ai-services>
- [x] Media release (survey figures + provider actions) → `raw/media-release.html`
      <https://www.esafety.gov.au/newsroom/media-releases/esafety-report-shows-ai-companions-are-putting-children-at-risk>

Captured in Chrome on 8 August 2026. The site offered no separate PDF; the
findings report is the rendered HTML page. Chart values were transcribed from
the page's accessible text versions into `build_esafety.py`.

## 2. Build + verify

```bash
cd au-esafety
python3 build_esafety.py          # reads raw/, writes au-esafety-ai-companion.json
python3 -c "import json;d=json.load(open('au-esafety-ai-companion.json'));print(len(d['rows']),'rows')"
```

`build_esafety.py` **exits non-zero** if `raw/` is empty — it will not emit a
fabricated dataset.

## 3. API status

The API's `data/esafety-bose.json` already includes the same recovered numeric
facts in its combined BOSE dataset and exposes them through
`esafety_bose_metrics`.
