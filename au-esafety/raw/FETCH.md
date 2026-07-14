# Fetch checklist — eSafety AI companion apps findings (retry from a residential box)

`www.esafety.gov.au` blocks datacenter IPs (WAF resets/hangs). Run these steps
from a **residential/EU-routed persistent browser session** per
[`../../BROWSER-FETCH-RUNBOOK.md`](../../BROWSER-FETCH-RUNBOOK.md) §1–3. Respect
robots.txt and throttle. **Never fabricate a figure** — if a value isn't legible
in the report, leave its row out and note it.

## 1. Save the findings report into this directory

Open each URL in the browser and save the rendered page **and** any linked PDF:

- [ ] Findings page → `raw/findings-october-2025.html` (full rendered text) and,
      if a PDF/download is offered, `raw/findings-october-2025.pdf`
      <https://www.esafety.gov.au/industry/basic-online-safety-expectations/ai-services/findings-october-2025>
- [ ] AI-services hub (index; catch any companion tables/appendix) → `raw/ai-services-hub.html`
      <https://www.esafety.gov.au/industry/basic-online-safety-expectations/ai-services>
- [ ] Media release (survey figures + provider actions) → `raw/media-release.html`
      <https://www.esafety.gov.au/newsroom/media-releases/esafety-report-shows-ai-companions-are-putting-children-at-risk>

If a value lives only in a chart/image (as with several eSafety figures),
transcribe it from the rendered page into `build_esafety.py` with a source
comment — the same approach `singapore-online-safety/build_singapore.py` uses for
the OSAR chart tables.

## 2. Build + verify

```bash
cd au-esafety
python3 build_esafety.py          # reads raw/, writes au-esafety-ai-companion.json
python3 -c "import json;d=json.load(open('au-esafety-ai-companion.json'));print(len(d['rows']),'rows')"
```

`build_esafety.py` **exits non-zero** if `raw/` is empty — it will not emit a
fabricated dataset.

## 3. Wire into the API (transparency-report-api, same branch)

Mirror the Singapore online-safety dataset end-to-end:
`data/au-esafety-ai-companion.json` snapshot → `build_esafety_ai_db` in `seed.py`
→ an `esafety_ai_metrics` `TableSpec` in `main.py` → a `/au-esafety` static page
(English-only, like `/singapore`) → `pytest`. Then update both CLAUDE.md files
and open/refresh the PRs.
